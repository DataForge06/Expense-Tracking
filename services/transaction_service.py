from bson import ObjectId
from datetime import datetime

async def create_transaction(db, transaction: dict):
    try:
        # Ensure user_email is present before saving
        if not transaction.get("user_email"):
            raise ValueError("user_email is required to save data")

        # 1. Date Conversion: Handle ISO strings from Flutter
        if "date" in transaction and isinstance(transaction["date"], str):
            try:
                transaction["date"] = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
            except ValueError:
                transaction["date"] = datetime.utcnow()

        # 2. USER-SPECIFIC Auto-increment logic
        # This ensures User B doesn't skip numbers because of User A
        user_email = transaction.get("user_email")
        last = await db.transactions.find({"user_email": user_email}).sort("transaction_number", -1).limit(1).to_list(length=1)
        
        transaction_number = (last[0]["transaction_number"] + 1) if last else 1
        transaction["transaction_number"] = transaction_number
        
        # 3. Insert into MongoDB
        result = await db.transactions.insert_one(transaction)
        return str(result.inserted_id)
    except Exception as e:
        print(f"!!! DB ERROR in create_transaction: {e} !!!")
        raise e

async def get_all_transactions(db, user_email: str):
    try:
        # Mandatory filter ensures isolation
        return await db.transactions.find({"user_email": user_email}).sort("transaction_number", -1).to_list(length=1000)
    except Exception as e:
        print(f"!!! DB ERROR: {e} !!!")
        raise e

async def update_transaction(db, transaction_number: int, data: dict):
    try:
        user_email = data.get("user_email")
        if not user_email:
            raise ValueError("user_email required for security")

        data.pop('_id', None)
        data.pop('id', None)

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
    except Exception as e:
        raise e

async def delete_transaction(db, transaction_number: int, user_email: str):
    try:
        # Security: Prevent cross-user deletion
        result = await db.transactions.delete_one({
            "transaction_number": transaction_number, 
            "user_email": user_email
        })
        return result.deleted_count > 0
    except Exception as e:
        raise e