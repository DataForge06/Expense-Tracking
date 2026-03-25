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
# 1. RESET MONTHLY DATA (Move Active -> History)
# -------------------------
@router.delete("/reset-month")
async def reset_month_route(
    user_email: str = Query(...), 
    year: int = Query(...), 
    month: int = Query(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    # This creates a pattern like "2026-03" to match your DB screenshot
    month_str = f"{year}-{month:02d}"
    
    # Using $regex to find any date starting with "YYYY-MM"
    # Added .strip() to user_email to prevent errors from accidental spaces
    query = {
        "user_email": user_email.strip(),
        "date": {"$regex": f"^{month_str}"}
    }
    
    # Log this so you can check Render Dashboard -> Logs
    print(f"DEBUG: Running Reset for {user_email} on pattern {month_str}")

    # 1. Find transactions in 'transactions' collection
    cursor = db.transactions.find(query)
    active_txs = await cursor.to_list(length=1000)

    if not active_txs:
        # We include the query details in the error so we can debug exactly why it failed
        raise HTTPException(
            status_code=404, 
            detail=f"No active transactions found for {user_email} in {month_str}"
        )

    # 2. Move to 'history' collection
    for tx in active_txs:
        tx.pop("_id", None) # Remove ID to allow re-insertion

    await db.history.insert_many(active_txs)

    # 3. Wipe from 'transactions' collection
    await db.transactions.delete_many(query)

    return {"message": f"Successfully moved {len(active_txs)} transactions to History."}

# -------------------------
# 2. GET HISTORY DATA
# -------------------------
@router.get("/history/{user_email}", response_model=List[Transaction])
async def fetch_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    cursor = db.history.find({"user_email": user_email.strip()}).sort("date", -1)
    history_txs = await cursor.to_list(length=2000)
    return serialize_docs(history_txs)

# -------------------------
# 3. DELETE HISTORY MONTH
# -------------------------
@router.delete("/history/{user_email}/delete_month")
async def remove_history_month(
    user_email: str, 
    payload: dict = Body(...), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    month_year = payload.get("month_year") # Expects "March 2026"
    if not month_year:
        raise HTTPException(status_code=400, detail="month_year is required")

    parts = month_year.split(" ")
    m_name = parts[0]
    y_num = parts[1]
    
    # Convert "March" to "03"
    m_num = datetime.strptime(m_name, "%B").month
    month_str = f"{y_num}-{m_num:02d}"

    result = await db.history.delete_many({
        "user_email": user_email.strip(),
        "date": {"$regex": f"^{month_str}"}
    })
    return {"message": f"Deleted {result.deleted_count} records from history."}

# -------------------------
# 4. CLEAR ALL HISTORY
# -------------------------
@router.delete("/history/{user_email}/clear_all")
async def clear_history(user_email: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await db.history.delete_many({"user_email": user_email.strip()})
    return {"message": f"Cleared all {result.deleted_count} records."}

# --- EXISTING ROUTES BELOW ---

@router.post("/", response_model=Transaction)
async def add_transaction(transaction: Transaction = Body(...), db: AsyncIOMotorDatabase = Depends(get_db)):
    transaction_dict = transaction.dict(exclude={"id", "transaction_number"})
    inserted_id = await create_transaction(db, transaction_dict)
    if inserted_id:
        created = await get_transaction_by_id(db, inserted_id)
        return serialize_doc(created)
    raise HTTPException(status_code=500, detail="Could not save to database")

@router.get("/", response_model=List[Transaction])
async def fetch_transactions(
    user_email: str = Query(..., description="Email of the user"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    transactions = await get_all_transactions(db, user_email)
    return serialize_docs(transactions)

@router.delete("/{transaction_number}")
async def remove_transaction(
    transaction_number: int, 
    user_email: str = Query(..., description="Email of the owner"),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    deleted = await delete_transaction(db, transaction_number, user_email)
    if deleted:
        return {"message": f"Transaction {transaction_number} deleted successfully"}
    raise HTTPException(status_code=404, detail="Transaction not found or unauthorized")