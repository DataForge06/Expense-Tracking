import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "expense_tracker")

if not MONGO_URI:
    print("❌ CRITICAL ERROR: MONGO_URI not found.")

# INCREASED serverSelectionTimeoutMS for Render
# 5000ms (5s) is too fast for a "Cold Start". We'll use 30000ms (30s).
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True, 
    retryWrites=True,
    serverSelectionTimeoutMS=30000  
)

db = client[MONGO_DB_NAME]

def get_db() -> AsyncIOMotorDatabase:
    # FIXED: Removed the comma that was turning this into a tuple
    return db