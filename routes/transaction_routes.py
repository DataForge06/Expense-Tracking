from fastapi import APIRouter, Depends, Body, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.transaction_service import (
    create_transaction,
    get_all_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    delete_history_transaction # Ensure this matches your service file
)
from utils.serialize import serialize_doc, serialize_docs
from database import get_db
from models.transaction_model import Transaction

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

# ---------------------------------------------------------
# 1. HISTORY MANAGEMENT (Unique paths to avoid 405 conflicts)
# ---------------------------------------------------------

@router.get("/history/{user_email}", response_model=List[Transaction])
async def fetch_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_email = user_email.strip().lower()
    cursor = db["history"].find({"user_email": clean_email}).sort("date", -1)
    history_txs = await cursor.to_list(length=2000)
    return serialize_docs(history_txs)

# NEW UNIQUE PATH: Added /history-delete/ to prevent overlap with standard CRUD
@router.delete("/history-delete/{user_email}/{transaction_number}")
async def delete_single_history_item(
    user_email: str, 
    transaction_number: int, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    logger.info(f"🗑️ DELETE HISTORY ATTEMPT: User={user_email}, No={transaction_number}")
    
    # Call the service logic targeting the 'history' collection
    deleted = await delete_history_transaction(db, user_email.strip().lower(), transaction_number)

    if deleted:
        logger.info(f"✅ HISTORY DELETE SUCCESS: No.{transaction_number}")
        return {"message": "Deleted from history"}
    
    logger.warning(f"❌ HISTORY DELETE FAILED: No.{transaction_number} not found")
    raise HTTPException(status_code=404, detail="History record not found")

@router.delete("/history/{user_email}/clear_all")
async def clear_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["history"].delete_many({"user_email": user_email.strip().lower()})
    return {"message": "History cleared"}

# ---------------------------------------------------------
# 2. RESET MONTHLY DATA
# ---------------------------------------------------------
@router.delete("/reset-month")
async def reset_month_route(
    user_email: str = Query(...), 
    year: int = Query(...), 
    month: int = Query(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    clean_email = user_email.strip().lower()
    month_str = f"{year}-{month:02d}"
    
    query = {
        "user_email": clean_email,
        "$or": [
            {"date": {"$regex": f"^{year}-{month:02d}"}},
            {"date": {"$regex": f"^{year}-{month}"}},
            {
                "$expr": {
                    "$and": [
                        {"$eq": [{"$year": {"$toDate": "$date"}}, year]},
                        {"$eq": [{"$month": {"$toDate": "$date"}}, month]}
                    ]
                }
            }
        ]
    }
    
    logger.info(f"🚀 RESET ATTEMPT: Email={clean_email}, Target={month_str}")

    active_col = db["transactions"]
    history_col = db["history"]

    cursor = active_col.find(query)
    active_txs = await cursor.to_list(length=1000)

    if not active_txs:
        raise HTTPException(status_code=404, detail="No transactions found for this period.")

    for tx in active_txs:
        tx.pop("_id", None)

    try:
        await history_col.insert_many(active_txs)
        await active_col.delete_many(query)
        logger.info(f"✅ SUCCESS: Moved {len(active_txs)} records.")
        return {"message": "Success", "count": len(active_txs)}
    except Exception as e:
        logger.error(f"💥 DB ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to move data")

# ---------------------------------------------------------
# 3. STANDARD CRUD (Put at bottom)
# ---------------------------------------------------------

@router.put("/{transaction_number}")
async def edit_transaction_route(
    transaction_number: int, 
    data: dict = Body(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if "user_email" in data:
        data["user_email"] = data["user_email"].strip().lower()

    updated = await update_transaction(db, transaction_number, data)
    if updated:
        return serialize_doc(updated)
    raise HTTPException(status_code=404, detail="Transaction not found")

@router.post("/", response_model=Transaction)
async def add_transaction(transaction: Transaction = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    tx_dict = transaction.dict(exclude={"id", "transaction_number"})
    tx_dict['user_email'] = tx_dict['user_email'].strip().lower()
    
    inserted_id = await create_transaction(db, tx_dict)
    if inserted_id:
        created = await get_transaction_by_id(db, inserted_id)
        return serialize_doc(created)
    raise HTTPException(status_code=500, detail="Failed to save")

@router.get("/", response_model=List[Transaction])
async def fetch_transactions(user_email: str = Query(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    transactions = await get_all_transactions(db, user_email.strip().lower())
    return serialize_docs(transactions)

@router.delete("/{transaction_number}")
async def remove_transaction(transaction_number: int, user_email: str = Query(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    deleted = await delete_transaction(db, transaction_number, user_email.strip().lower())
    if deleted: return {"message": "Deleted"}
    raise HTTPException(status_code=404, detail="Not found")