from datetime import date
from typing import Optional
from sqlmodel import SQLModel, Field

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: date
    description: str
    category: Optional[str] = None
    amount: float  # negative = expense, positive = income
    account: Optional[str] = None
    raw: Optional[str] = None

class BudgetRule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pattern: str
    category: str