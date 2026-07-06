from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Transaction(BaseModel):
    # Optional because MongoDB generates this via our service logic
    transaction_number: Optional[int] = None 
    title: str
    amount: float
    category: str
    type: str  # e.g., "Income" or "Expense"
    date: datetime
    # CRITICAL: This links every record to the logged-in user
    user_email: str 
    notes: Optional[str] = None

    class Config:
        # Allows compatibility with database row objects
        from_attributes = True
        # Ensures JSON conversion handles datetime correctly
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }