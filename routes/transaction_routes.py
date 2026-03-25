from fastapi import APIRouter, Depends, Body, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

# Setup logging to see errors in Render Dashboard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# ---------------------------------------------------------
# 1. RESET MONTHLY DATA (Move Active -> History)
# ---------------------------------------------------------
@router.delete("/reset-month")
async def reset_month_route(
    user_email: str = Query(...), 
    year: int = Query(...), 
    month: int = Query(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # This creates a pattern like "2026-03" to match your MongoDB screenshot format
    month_str = f"{year}-{month:02d}"
    
    # We clean the email to ensure no hidden spaces are breaking the match
    clean_email = user_email.strip().lower()
    
    query = {
        "user_email": clean_email,
        "date": {"$regex": f"^{month_str}"}
    }
    
    logger.info(f"🚀 RESET TRIGGERED: Email={clean_email}, Pattern={month_str}")

    # Access collections explicitly by name
    active_col = db["transactions"]
    history_col = db["history"]

    # 1. Fetch current records
    cursor = active_col.find(query)
    active_txs = await cursor.to_list(length=1000)

    if not active_txs:
        logger.warning(f"❌ NO DATA FOUND: Tried to find records for {clean_email} starting with {month_str}")
        raise HTTPException(
            status_code=404, 
            detail=f"No transactions found for {clean_email} in {month_str}"
        )

    # 2. Prepare for Move (Remove MongoDB _id to prevent duplicate key errors)
    for tx in active_txs:
        tx.pop("_id", None)

    try:
        # 3. Insert into History Collection
        await history_col.insert_many(active_txs)
        
        # 4. Delete from Active Transactions
        await active_col.delete_many(query)
        
        logger.info(f"✅ SUCCESS: Moved {len(active_txs)} transactions to History.")
        return {"message": "Success", "count": len(active_txs)}
        
    except Exception as e:
        logger.error(f"💥 DB ERROR during move: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to archive data.")

# ---------------------------------------------------------
# 2. GET HISTORY DATA (For HistoryScreen.dart)
# ---------------------------------------------------------
@router.get("/history/{user_email}", response_model=List[Transaction])
async def fetch_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_email = user_email.strip().lower()
    history_col = db["history"]
    
    # Return all archived data for this user, newest first
    cursor = history_col.find({"user_email": clean_email}).sort("date", -1)
    history_txs = await cursor.to_list(length=2000)
    
    return serialize_docs(history_txs)

# ---------------------------------------------------------
# 3. DELETE HISTORY MONTH (From History Tab)
# ---------------------------------------------------------
@router.delete("/history/{user_email}/delete_month")
async def remove_history_month(
    user_email: str, 
    payload: dict = Body(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    clean_email = user_email.strip().lower()
    month_year = payload.get("month_year") # Expects e.g. "March 2026"
    
    if not month_year:
        raise HTTPException(status_code=400, detail="month_year is required")

    try:
        parts = month_year.split(" ")
        m_num = datetime.strptime(parts[0], "%B").month
        y_num = parts[1]
        month_str = f"{y_num}-{m_num:02d}"

        history_col = db["history"]
        result = await history_col.delete_many({
            "user_email": clean_email,
            "date": {"$regex": f"^{month_str}"}
        })
        return {"message": f"Deleted {result.deleted_count} history records."}
    except Exception:
        raise HTTPException(status_code=400, detail="Format must be 'Month Year'")

# ---------------------------------------------------------
# 4. CLEAR ALL HISTORY (Wipe History Tab)
# ---------------------------------------------------------
@router.delete("/history/{user_email}/clear_all")
async def clear_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_email = user_email.strip().lower()
    history_col = db["history"]
    result = await history_col.delete_many({"user_email": clean_email})
    return {"message": f"Deleted all {result.deleted_count} history records."}

# ---------------------------------------------------------
# BASIC CRUD ROUTES
# ---------------------------------------------------------

@router.post("/", response_model=Transaction)
async def add_transaction(transaction: Transaction = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    transaction_dict = transaction.dict(exclude={"id", "transaction_number"})
    inserted_id = await create_transaction(db, transaction_dict)
    if inserted_id:
        created = await get_transaction_by_id(db, inserted_id)
        return serialize_doc(created)
    raise HTTPException(status_code=500, detail="Could not save")

@router.get("/", response_model=List[Transaction])
async def fetch_transactions(
    user_email: str = Query(..., description="Email of the user"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    transactions = await get_all_transactions(db, user_email.strip().lower())
    return serialize_docs(transactions)

@router.delete("/{transaction_number}")
async def remove_transaction(
    transaction_number: int, 
    user_email: str = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    deleted = await delete_transaction(db, transaction_number, user_email.strip().lower())
    if deleted:
        return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Not found")

@router.get("/filter", response_model=List[Transaction])
async def filter_transaction_route(
    user_email: str = Query(...),
    category: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    min_amount: Optional[float] = Query(None),
    max_amount: Optional[float] = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    transactions = await filter_transactions(db, user_email.strip().lower(), category, start_date, end_date, min_amount, max_amount)
    return serialize_docs(transactions)