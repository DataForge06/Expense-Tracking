from fastapi import APIRouter, Depends, Body, HTTPException, Query
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging
from pydantic import BaseModel
from datetime import datetime
import calendar

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.transaction_service import (
    create_transaction,
    get_all_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    delete_history_transaction,
    update_history_transaction,
    archive_monthly_data
)
from utils.serialize import serialize_doc, serialize_docs
from database import get_db
from models.transaction_model import Transaction

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

@router.get("/ping")
async def ping_server():
    logger.info("Bot pinged the server successfully!")
    return {"status": "awake", "message": "Pong! Server is ready."}

# ==========================================
# HISTORY MANAGEMENT (FIXED ROUTES TO MATCH DART)
# ==========================================
@router.get("/history/{user_email}", response_model=List[Transaction])
async def fetch_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    clean_email = user_email.strip().lower()
    cursor = db["history"].find({"user_email": clean_email}).sort("date", -1)
    history_txs = await cursor.to_list(length=2000)
    return serialize_docs(history_txs)

# Fixed: Match Dart's URL /history-delete/{email}/{transactionNumber}
@router.delete("/history-delete/{email}/{transaction_number}")
async def delete_single_history_item(
    email: str,
    transaction_number: int, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    deleted = await delete_history_transaction(db, email.strip().lower(), transaction_number)
    if deleted:
        return {"message": "Deleted from history"}
    raise HTTPException(status_code=404, detail="History record not found")

# Fixed: Match Dart's URL /history/{email}/clear_all
@router.delete("/history/{email}/clear_all")
async def clear_history(email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    await db["history"].delete_many({"user_email": email.strip().lower()})
    return {"message": "History cleared"}

@router.put("/history/{transaction_number}")
async def edit_history_transaction_route(
    transaction_number: int, 
    user_email: str = Query(...),
    data: dict = Body(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    if "user_email" in data:
        data["user_email"] = data["user_email"].strip().lower()
    updated = await update_history_transaction(db, transaction_number, data)
    if updated:
        return {"message": "History transaction updated"}
    raise HTTPException(status_code=404, detail="History transaction not found")

# ==========================================
# ARCHIVE / RESET MONTHLY DATA (FIXED ROUTE)
# ==========================================
# Fixed: Match Dart's URL /reset-month?user_email=...&year=...&month=...
@router.delete("/reset-month")
async def archive_month_route(
    user_email: str = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    count = await archive_monthly_data(db, user_email.strip().lower(), year, month)
    if count == 0:
        raise HTTPException(status_code=404, detail="No active transactions found to archive")
    return {"message": "Archived successfully", "count": count}

# ==========================================
# STANDARD CRUD FOR ACTIVE TRANSACTIONS
# ==========================================
@router.put("/{transaction_number}")
async def edit_transaction_route(
    transaction_number: int, 
    user_email: str = Query(None), 
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

@router.get("/filter/")
async def filter_txs(
    user_email: str = Query(...),
    category: str = Query(None),
    minAmount: float = Query(None),
    maxAmount: float = Query(None),
    startDate: str = Query(None),
    endDate: str = Query(None),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    from services.transaction_service import filter_transactions
    sd = datetime.fromisoformat(startDate.replace("Z", "+00:00")) if startDate else None
    ed = datetime.fromisoformat(endDate.replace("Z", "+00:00")) if endDate else None
    txs = await filter_transactions(db, user_email.strip().lower(), category, sd, ed, minAmount, maxAmount)
    return serialize_docs(txs)