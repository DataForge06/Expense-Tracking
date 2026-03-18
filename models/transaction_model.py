from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    id: Optional[str] = None
    transaction_number: Optional[int] = None
    title: str = Field(..., example="Grocery shopping")
    amount: float = Field(..., example=150.75)
    category: str = Field(..., example="Food")
    type: str = Field(..., example="expense")  # "income" or "expense"
    date: datetime = Field(default_factory=datetime.utcnow, example="2026-02-12T15:30:00")
