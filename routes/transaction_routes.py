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
    # This creates a pattern like "2026-03" or "2026-3" 
    # We use a regex that matches either format to be safe
    month_padded = f"{month:02d}"
    month_unpadded = f"{month}"
    regex_pattern = f"^{year}-({month_padded}|{month_unpadded})"
    
    clean_email = user_email.strip().lower()
    
    query = {
        "user_email": clean_email,
        "date": {"$regex": regex_pattern}
    }
    
    logger.info(f"🚀 RESET ATTEMPT: Email={clean_email}, Regex={regex_pattern}")

    active_col = db["transactions"]
    history_col = db["history"]

    # 1. Fetch current records
    cursor = active_col.find(query)
    active_txs = await cursor.to_list(length=1000)

    # 2. DEBUG: If still not found, try finding ANY transaction for this user 
    # to see what their date format actually looks like in the logs
    if not active_txs:
        debug_tx = await active_col.find_one({"user_email": clean_email})
        if debug_tx:
            logger.warning(f"❌ DATA MISMATCH: Found a tx for user, but date was {debug_tx.get('date')}")
        else:
            logger.warning(f"❌ USER NOT FOUND: No transactions at all for {clean_email}")
            
        raise HTTPException(
            status_code=404, 
            detail=f"No transactions found for {clean_email} in month {month}"
        )

    # 3. Prepare for Move
    for tx in active_txs:
        tx.pop("_id", None)

    try:
        await history_col.insert_many(active_txs)
        result = await active_col.delete_many(query)
        logger.info(f"✅ SUCCESS: Moved {len(active_txs)} transactions.")
        return {"message": "Success", "count": len(active_txs)}
        
    except Exception as e:
        logger.error(f"💥 DB ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Database move failed")

# ---------------------------------------------------------
# 2. GET HISTORY DATA
# ---------------------------------------------------------
@router.get("/history/{user_email}", response_model=List[Transaction])
async def fetch_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_email = user_email.strip().lower()
    history_col = db["history"]
    cursor = history_col.find({"user_email": clean_email}).sort("date", -1)
    history_txs = await cursor.to_list(length=2000)
    return serialize_docs(history_txs)

# ---------------------------------------------------------
# 3. DELETE HISTORY MONTH
# ---------------------------------------------------------
@router.delete("/history/{user_email}/delete_month")
async def remove_history_month(
    user_email: str, 
    payload: dict = Body(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    clean_email = user_email.strip().lower()
    month_year = payload.get("month_year") 
    
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
        return {"message": "Deleted"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid format")

# ---------------------------------------------------------
# 4. CLEAR ALL HISTORY
# ---------------------------------------------------------
@router.delete("/history/{user_email}/clear_all")
async def clear_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    history_col = db["history"]
    result = await history_col.delete_many({"user_email": user_email.strip().lower()})
    return {"message": "Cleared"}

# ---------------------------------------------------------
# CRUD ROUTES
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
    user_email: str = Query(...),
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
    if deleted: return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Not found")