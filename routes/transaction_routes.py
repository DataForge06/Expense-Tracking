from fastapi import APIRouter, Depends, Body, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from services.transaction_service import (
    create_transaction,
    get_all_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    filter_transactions
)
from utils.serialize import serialize_doc, serialize_docs
from database import get_db
from models.transaction_model import Transaction

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

# -------------------------
# Add a new transaction
# -------------------------
@router.post("/", response_model=Transaction)
async def add_transaction(transaction: Transaction = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    # exclude={"id"} prevents manual ID injection
    transaction_dict = transaction.dict(exclude={"id", "transaction_number"})
    
    inserted_id = await create_transaction(db, transaction_dict)
    
    if inserted_id:
        created = await get_transaction_by_id(db, inserted_id)
        return serialize_doc(created)
    
    raise HTTPException(status_code=500, detail="Could not save to database")

# -------------------------
# Get all transactions
# -------------------------
@router.get("/", response_model=List[Transaction])
async def fetch_transactions(db: AsyncIOMotorDatabase = Depends(get_db)):
    transactions = await get_all_transactions(db)
    return serialize_docs(transactions)

# -------------------------
# Update transaction
# -------------------------
@router.put("/{transaction_number}")
async def edit_transaction(transaction_number: int, data: dict = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    # Pass the transaction_number to locate the record
    updated = await update_transaction(db, transaction_number, data)
    
    if updated:
        return serialize_doc(updated)
    raise HTTPException(status_code=404, detail="Transaction not found")

# -------------------------
# Delete transaction
# -------------------------
@router.delete("/{transaction_number}")
async def remove_transaction(transaction_number: int, db: AsyncIOMotorDatabase = Depends(get_db)):
    deleted = await delete_transaction(db, transaction_number)
    if deleted:
        return {"message": f"Transaction {transaction_number} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Transaction not found")

# -------------------------
# Filter transactions
# -------------------------
@router.get("/filter", response_model=List[Transaction])
async def filter_transaction_route(
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    transactions = await filter_transactions(db, category, start_date, end_date, min_amount, max_amount)
    return serialize_docs(transactions) 