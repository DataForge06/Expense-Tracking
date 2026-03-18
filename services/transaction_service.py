# services/transaction_service.py
from bson import ObjectId
from datetime import datetime

async def create_transaction(db, transaction: dict):
    try:
        print("--- DB: Starting Create Transaction ---")
        
        # 1. Date Conversion: Ensure the date is a Python datetime object
        # This is crucial for the home screen graphs to sort and display data correctly.
        if "date" in transaction and isinstance(transaction["date"], str):
            try:
                # Handle ISO strings from Flutter (e.g., 2026-03-17T...)
                transaction["date"] = datetime.fromisoformat(transaction["date"].replace("Z", "+00:00"))
            except ValueError:
                print("--- DB: Date format issue, using current time ---")
                transaction["date"] = datetime.utcnow()

        # 2. Resilient Auto-increment logic
        last = await db.transactions.find().sort("transaction_number", -1).limit(1).to_list(length=1)
        transaction_number = (last[0]["transaction_number"] + 1) if last and "transaction_number" in last[0] else 1
        transaction["transaction_number"] = transaction_number
        
        print(f"--- DB: Assigned Transaction Number: {transaction_number} ---")

        # 3. Insert into MongoDB
        result = await db.transactions.insert_one(transaction)
        print(f"--- DB: Successfully Inserted. ID: {result.inserted_id} ---")
        
        return str(result.inserted_id)
    except Exception as e:
        print(f"!!! DB ERROR in create_transaction: {e} !!!")
        raise e

async def get_all_transactions(db):
    try:
        print("--- DB: Fetching All Transactions ---")
        # Sorting by transaction_number descending ensures newest appear first on Home Screen
        return await db.transactions.find().sort("transaction_number", -1).to_list(length=1000)
    except Exception as e:
        print(f"!!! DB ERROR in get_all_transactions: {e} !!!")
        raise e

async def get_transaction_by_id(db, transaction_id: str):
    try:
        return await db.transactions.find_one({"_id": ObjectId(transaction_id)})
    except Exception:
        return None

async def update_transaction(db, transaction_number: int, data: dict):
    try:
        print(f"--- DB: Updating Transaction #{transaction_number} ---")
        
        # Clean data: MongoDB will fail if you try to update the immutable _id field
        data.pop('_id', None)
        data.pop('id', None)

        # Ensure date is converted if it's being updated
        if "date" in data and isinstance(data["date"], str):
            data["date"] = datetime.fromisoformat(data["date"].replace("Z", "+00:00"))

        result = await db.transactions.update_one(
            {"transaction_number": transaction_number},
            {"$set": data}
        )
        
        if result.modified_count or result.matched_count:
            return await db.transactions.find_one({"transaction_number": transaction_number})
        return None
    except Exception as e:
        print(f"!!! DB ERROR in update_transaction: {e} !!!")
        raise e

async def delete_transaction(db, transaction_number: int):
    try:
        print(f"--- DB: Deleting Transaction #{transaction_number} ---")
        result = await db.transactions.delete_one({"transaction_number": transaction_number})
        return result.deleted_count > 0
    except Exception as e:
        print(f"!!! DB ERROR in delete_transaction: {e} !!!")
        raise e

async def filter_transactions(db, category=None, start_date=None, end_date=None, min_amount=None, max_amount=None):
    try:
        print("--- DB: Running Filtered Query ---")
        query = {}
        
        if category:
            query["category"] = category
            
        # Date range filtering for the "Predictions" and "Filter" screens
        if start_date or end_date:
            query["date"] = {}
            if start_date:
                query["date"]["$gte"] = start_date
            if end_date:
                query["date"]["$lte"] = end_date
        
        if min_amount is not None:
            query["amount"] = {"$gte": min_amount}
        if max_amount is not None:
            if "amount" not in query:
                query["amount"] = {}
            query["amount"]["$lte"] = max_amount
        
        return await db.transactions.find(query).sort("transaction_number", -1).to_list(length=1000)
    except Exception as e:
        print(f"!!! DB ERROR in filter_transactions: {e} !!!")
        raise e