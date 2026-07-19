from fastapi import APIRouter, Depends, Body, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import extract, delete

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from database import get_db, engine, Base
from models.transaction_model import TransactionSchema, TransactionDB, HistoryDB

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])

# ==========================================
# AUTO-CREATE TABLES ON STARTUP
# ==========================================
@router.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("PostgreSQL Tables verified/created successfully!")

@router.get("/ping")
async def ping_server():
    logger.info("Bot pinged the server successfully!")
    return {"status": "awake", "message": "Pong! Server is ready."}

# ==========================================
# STANDARD CRUD FOR ACTIVE TRANSACTIONS
# ==========================================
@router.post("/", response_model=TransactionSchema)
async def add_transaction(transaction: TransactionSchema = Body(...), db: AsyncSession = Depends(get_db)):
    new_tx = TransactionDB(
        transaction_number=transaction.transaction_number,
        user_email=transaction.user_email.strip().lower(),
        title=transaction.title,
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        date=transaction.date,
        notes=transaction.notes
    )
    db.add(new_tx)
    # Automatic commit happens via get_db dependency
    return new_tx

@router.get("/", response_model=List[TransactionSchema])
async def fetch_transactions(user_email: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TransactionDB)
        .where(TransactionDB.user_email == user_email.strip().lower())
        .order_by(TransactionDB.date.desc())
    )
    return result.scalars().all()

@router.put("/{transaction_number}", response_model=TransactionSchema)
async def edit_transaction_route(
    transaction_number: int, 
    user_email: str = Query(None), 
    data: dict = Body(...), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(TransactionDB).where(TransactionDB.transaction_number == transaction_number))
    db_tx = result.scalar_one_or_none()
    
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update only provided fields
    if "title" in data: db_tx.title = data["title"]
    if "amount" in data: db_tx.amount = data["amount"]
    if "category" in data: db_tx.category = data["category"]
    if "type" in data: db_tx.type = data["type"]
    if "date" in data: db_tx.date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
    if "notes" in data: db_tx.notes = data["notes"]
    if "user_email" in data: db_tx.user_email = data["user_email"].strip().lower()
    
    return db_tx

@router.delete("/{transaction_number}")
async def remove_transaction(transaction_number: int, user_email: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TransactionDB).where(
            TransactionDB.transaction_number == transaction_number,
            TransactionDB.user_email == user_email.strip().lower()
        )
    )
    db_tx = result.scalar_one_or_none()
    
    if db_tx:
        await db.delete(db_tx)
        return {"message": "Deleted"}
    
    raise HTTPException(status_code=404, detail="Not found")

# ==========================================
# ARCHIVE / RESET MONTHLY DATA
# ==========================================
@router.delete("/reset-month")
async def archive_month_route(
    user_email: str = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    db: AsyncSession = Depends(get_db)
):
    clean_email = user_email.strip().lower()
    result = await db.execute(
        select(TransactionDB).where(
            TransactionDB.user_email == clean_email,
            extract('year', TransactionDB.date) == year,
            extract('month', TransactionDB.date) == month
        )
    )
    transactions = result.scalars().all()
    
    if not transactions:
        raise HTTPException(status_code=404, detail="No active transactions found to archive")

    count = 0
    # ACID Transaction: Everything moves at once, or nothing moves
    for t in transactions:
        history_tx = HistoryDB(
            transaction_number=t.transaction_number,
            user_email=t.user_email,
            title=t.title,
            amount=t.amount,
            category=t.category,
            type=t.type,
            date=t.date,
            notes=t.notes
        )
        db.add(history_tx)
        await db.delete(t)
        count += 1
        
    return {"message": "Archived successfully", "count": count}

# ==========================================
# HISTORY MANAGEMENT
# ==========================================
@router.get("/history/{user_email}", response_model=List[TransactionSchema])
async def fetch_history(user_email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(HistoryDB)
        .where(HistoryDB.user_email == user_email.strip().lower())
        .order_by(HistoryDB.date.desc())
    )
    return result.scalars().all()

@router.delete("/history-delete/{email}/{transaction_number}")
async def delete_single_history_item(
    email: str,
    transaction_number: int, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(HistoryDB).where(
            HistoryDB.transaction_number == transaction_number,
            HistoryDB.user_email == email.strip().lower()
        )
    )
    db_tx = result.scalar_one_or_none()
    
    if db_tx:
        await db.delete(db_tx)
        return {"message": "Deleted from history"}
        
    raise HTTPException(status_code=404, detail="History record not found")

@router.delete("/history/{email}/clear_all")
async def clear_history(email: str, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(HistoryDB).where(HistoryDB.user_email == email.strip().lower()))
    return {"message": "History cleared"}

@router.put("/history/{transaction_number}")
async def edit_history_transaction_route(
    transaction_number: int, 
    user_email: str = Query(...),
    data: dict = Body(...), 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(HistoryDB).where(HistoryDB.transaction_number == transaction_number))
    db_tx = result.scalar_one_or_none()
    
    if not db_tx:
        raise HTTPException(status_code=404, detail="History transaction not found")

    if "title" in data: db_tx.title = data["title"]
    if "amount" in data: db_tx.amount = data["amount"]
    if "category" in data: db_tx.category = data["category"]
    if "type" in data: db_tx.type = data["type"]
    if "date" in data: db_tx.date = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))
    if "notes" in data: db_tx.notes = data["notes"]
    if "user_email" in data: db_tx.user_email = data["user_email"].strip().lower()
    
    return {"message": "History transaction updated"}

# ==========================================
# ADVANCED FILTERING
# ==========================================
@router.get("/filter/", response_model=List[TransactionSchema])
async def filter_txs(
    user_email: str = Query(...),
    category: str = Query(None),
    minAmount: float = Query(None),
    maxAmount: float = Query(None),
    startDate: str = Query(None),
    endDate: str = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(TransactionDB).where(TransactionDB.user_email == user_email.strip().lower())
    
    if category:
        query = query.where(TransactionDB.category == category)
    if minAmount is not None:
        query = query.where(TransactionDB.amount >= minAmount)
    if maxAmount is not None:
        query = query.where(TransactionDB.amount <= maxAmount)
    if startDate:
        sd = datetime.fromisoformat(startDate.replace("Z", "+00:00"))
        query = query.where(TransactionDB.date >= sd)
    if endDate:
        ed = datetime.fromisoformat(endDate.replace("Z", "+00:00"))
        query = query.where(TransactionDB.date <= ed)

    query = query.order_by(TransactionDB.date.desc())
    result = await db.execute(query)
    
    return result.scalars().all()