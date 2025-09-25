from __future__ import annotations
import io
import pandas as pd
from dateutil import parser as dtp
from sqlmodel import select
from models import Transaction, BudgetRule
from db import get_session

NORMAL_COLS = ["date", "description", "amount", "category", "account"]

MAPPINGS = [
    {"date": "Date", "description": "Description", "amount": "Amount", "category": "Category", "account": "Account"},
    {"date": "Transaction Date", "description": "Details", "amount": "Debit/Credit", "category": "Category", "account": "Account Name"},
    {"date": "Posted Date", "description": "Payee", "amount": "Amount", "category": "Category", "account": "Account"},
]

def _coerce(df: pd.DataFrame) -> pd.DataFrame:
    for mapping in MAPPINGS:
        if all(col in df.columns for col in mapping.values()):
            df = df.rename(columns={v: k for k, v in mapping.items()})
            break
    if "date" in df:
        df["date"] = df["date"].apply(lambda x: dtp.parse(str(x)).date())
    if "amount" in df:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    for col in NORMAL_COLS:
        if col not in df:
            df[col] = None
    return df[NORMAL_COLS]

def apply_budget_rules(tx: Transaction, session) -> Transaction:
    rules = session.exec(select(BudgetRule)).all()
    desc = (tx.description or "").lower()
    for r in rules:
        if r.pattern.lower() in desc:
            tx.category = r.category
            break
    return tx

def ingest_csv_bytes(blob: bytes, account_hint: str | None = None) -> int:
    df = pd.read_csv(io.BytesIO(blob))
    df = _coerce(df)
    count = 0
    with get_session() as s:
        for row in df.itertuples(index=False):
            tx = Transaction(
                date=row.date,
                description=row.description or "",
                category=row.category,
                amount=float(row.amount),
                account=row.account or account_hint,
                raw=None,
            )
            tx = apply_budget_rules(tx, s)
            s.add(tx)
            count += 1
        s.commit()
    return count