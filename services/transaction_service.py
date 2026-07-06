from bson import ObjectId
from datetime import datetime
import calendar

async def get_transaction_by_id(db, inserted_id: str):
    return await db.transactions.find_one({"_id": ObjectId(inserted_id)})

async def create_transaction(db, transaction: dict):
    try:
        if not transaction.get("user_email"):
            raise ValueError("user_email is required to save data")

        if "date" in transaction and isinstance(transaction["date"], str):
            try:
                transaction["date"] = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
            except ValueError:
                transaction["date"] = datetime.utcnow()

        user_email = transaction.get("user_email")
        last = await db.transactions.find({"user_email": user_email}).sort("transaction_number", -1).limit(1).to_list(length=1)
        
        transaction_number = (last[0]["transaction_number"] + 1) if last else 1
        transaction["transaction_number"] = transaction_number
        
        result = await db.transactions.insert_one(transaction)
        return str(result.inserted_id)
    except Exception as e:
        print(f"!!! DB ERROR in create_transaction: {e} !!!")
        raise e

async def get_all_transactions(db, user_email: str):
    return await db.transactions.find({"user_email": user_email}).sort("transaction_number", -1).to_list(length=1000)

async def filter_transactions(db, user_email, category=None, start_date=None, end_date=None, min_amount=None, max_amount=None):
    query = {"user_email": user_email}
    if category: query["category"] = category
    if start_date or end_date:
        query["date"] = {}
        if start_date: query["date"]["$gte"] = start_date
        if end_date: query["date"]["$lte"] = end_date
    if min_amount or max_amount:
        query["amount"] = {}
        if min_amount: query["amount"]["$gte"] = min_amount
        if max_amount: query["amount"]["$lte"] = max_amount
    return await db.transactions.find(query).sort("date", -1).to_list(length=1000)

async def update_transaction(db, transaction_number: int, data: dict):
    user_email = data.get("user_email")
    data.pop('_id', None)
    if "date" in data and isinstance(data["date"], str):
        data["date"] = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

    result = await db.transactions.update_one(
        {"transaction_number": transaction_number, "user_email": user_email},
        {"$set": data}
    )
    if result.modified_count or result.matched_count:
        return await db.transactions.find_one({"transaction_number": transaction_number, "user_email": user_email})
    return None

async def delete_transaction(db, transaction_number: int, user_email: str):
    result = await db.transactions.delete_one({
        "transaction_number": transaction_number, 
        "user_email": user_email
    })
    return result.deleted_count > 0

async def update_history_transaction(db, transaction_number: int, data: dict):
    user_email = data.get("user_email")
    data.pop('_id', None)
    if "date" in data and isinstance(data["date"], str):
        data["date"] = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

    result = await db["history"].update_one(
        {"transaction_number": transaction_number, "user_email": user_email},
        {"$set": data}
    )
    return result.modified_count > 0

async def delete_history_transaction(db, user_email: str, transaction_number: int):
    try:
        result = await db["history"].delete_one({
            "user_email": user_email.strip().lower(),
            "transaction_number": transaction_number
        })
        return result.deleted_count > 0
    except Exception as e:
        print(f"!!! DB ERROR in delete_history_transaction: {e} !!!")
        raise e

async def archive_monthly_data(db, user_email: str, year: int, month: int):
    try:
        start_date = datetime(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day, 23, 59, 59)

        query = {
            "user_email": user_email.strip().lower(),
            "date": {"$gte": start_date, "$lte": end_date}
        }
        
        active_txs = await db.transactions.find(query).to_list(length=1000)
        if active_txs:
            for tx in active_txs:
                tx.pop("_id", None)
            await db["history"].insert_many(active_txs)
            result = await db.transactions.delete_many(query)
            return result.deleted_count
        return 0
    except Exception as e:
        print(f"!!! DB ERROR in archive_monthly_data: {e} !!!")
        raise e