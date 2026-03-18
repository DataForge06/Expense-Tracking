from bson import ObjectId
from datetime import datetime

# FIX: Added this helper to ensure even single-fetch is secure
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
    # Mandatory filter ensures isolation: only records matching this email are returned
    return await db.transactions.find({"user_email": user_email}).sort("transaction_number", -1).to_list(length=1000)

async def filter_transactions(db, user_email, category=None, start_date=None, end_date=None, min_amount=None, max_amount=None):
    # CRITICAL: We start the filter with the user_email to ensure isolation
    query = {"user_email": user_email}
    
    if category:
        query["category"] = category
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
    if not user_email:
        raise ValueError("user_email required for security")

    data.pop('_id', None)
    if "date" in data and isinstance(data["date"], str):
        data["date"] = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

    # Security: Match both number AND email
    result = await db.transactions.update_one(
        {"transaction_number": transaction_number, "user_email": user_email},
        {"$set": data}
    )
    
    if result.modified_count or result.matched_count:
        return await db.transactions.find_one({"transaction_number": transaction_number, "user_email": user_email})
    return None

async def delete_transaction(db, transaction_number: int, user_email: str):
    # Security: Match both number AND email to prevent cross-user deletion
    result = await db.transactions.delete_one({
        "transaction_number": transaction_number, 
        "user_email": user_email
    })
    return result.deleted_count > 0