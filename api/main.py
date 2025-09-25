from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from sqlmodel import select, func
from db import init_db, get_session
from models import Transaction, BudgetRule
from ingest import ingest_csv_bytes
from llm import chat

app = FastAPI(title="FinanceLLM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    return {"status": "ok"}

class RuleIn(BaseModel):
    pattern: str
    category: str

@app.post("/rules")
def add_rule(rule: RuleIn):
    with get_session() as s:
        r = BudgetRule(pattern=rule.pattern, category=rule.category)
        s.add(r)
        s.commit()
        s.refresh(r)
        return r

@app.get("/summary/monthly")
def monthly_summary(year: Optional[int] = None):
    with get_session() as s:
        stmt = select(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            func.sum(Transaction.amount).label("net")
        )
        if year:
            stmt = stmt.where(func.strftime("%Y", Transaction.date) == str(year))
        stmt = stmt.group_by("month").order_by("month")
        rows = s.exec(stmt).all()
        return [{"month": m, "net": float(n or 0)} for m, n in rows]

@app.get("/summary/by_category")
def by_category(month: Optional[str] = Query(None, description="YYYY-MM")):
    with get_session() as s:
        stmt = select(Transaction.category, func.sum(Transaction.amount))
        if month:
            stmt = stmt.where(func.strftime("%Y-%m", Transaction.date) == month)
        stmt = stmt.group_by(Transaction.category)
        rows = s.exec(stmt).all()
        return [{"category": c or "(uncategorized)", "net": float(n or 0)} for c, n in rows]

@app.get("/transactions")
def list_transactions(limit: int = 200):
    with get_session() as s:
        rows = s.exec(select(Transaction).order_by(Transaction.date.desc()).limit(limit)).all()
        return rows

@app.post("/ingest")
async def ingest(file: UploadFile = File(...), account: Optional[str] = None):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file")
    blob = await file.read()
    count = ingest_csv_bytes(blob, account_hint=account)
    return {"inserted": count}

class NLQIn(BaseModel):
    question: str

@app.post("/ask")
def ask(q: NLQIn):
    with get_session() as s:
        total = s.exec(select(func.sum(Transaction.amount))).one()
        latest5 = s.exec(select(Transaction).order_by(Transaction.date.desc()).limit(5)).all()
    context = [
        f"Total net: {float(total or 0):.2f}",
        "Latest 5 transactions:",
    ] + [f" - {t.date} {t.description} {t.amount:.2f} [{t.category or 'uncat'}]" for t in latest5]
    prompt = (
        "You are a cautious finance assistant. Use ONLY the provided context to answer. "
        "If the answer isn't derivable, say what else you need.\n\n"
        f"Context:\n{chr(10).join(context)}\n\nUser: {q.question}\n"
    )
    answer = chat(prompt)
    return {"answer": answer}