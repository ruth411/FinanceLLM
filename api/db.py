import os
from sqlmodel import SQLModel, create_engine, Session

DB_PATH = os.getenv("DB_PATH", "/data/finance.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    return Session(engine)