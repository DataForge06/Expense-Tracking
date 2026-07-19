from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from database import Base

# ==========================================
# 1. SQLALCHEMY ORM MODELS (Database Tables)
# ==========================================
class TransactionDB(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_number = Column(BigInteger, unique=True, index=True)
    user_email = Column(String, index=True)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

class HistoryDB(Base):
    __tablename__ = "history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_number = Column(BigInteger, unique=True, index=True)
    user_email = Column(String, index=True)
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    type = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, nullable=True)

# ==========================================
# 2. PYDANTIC SCHEMAS (API Data Validation)
# ==========================================
class TransactionSchema(BaseModel):
    transaction_number: Optional[int] = None 
    title: str
    amount: float
    category: str
    type: str  
    date: datetime
    user_email: str 
    notes: Optional[str] = None

    class Config:
        from_attributes = True # Converts SQLAlchemy ORM models to JSON automatically
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }