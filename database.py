import os
import json
import firebase_admin
from firebase_admin import credentials
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "expense_tracker")
FIREBASE_CONFIG_STR = os.getenv("FIREBASE_CONFIG")

if not MONGO_URI:
    print("❌ CRITICAL ERROR: MONGO_URI not found.")

# INCREASED serverSelectionTimeoutMS for Render
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True, 
    retryWrites=True,
    serverSelectionTimeoutMS=30000  
)

db = client[MONGO_DB_NAME]

def get_db() -> AsyncIOMotorDatabase:
    return db

# Initialize Firebase Securely
if not firebase_admin._apps:
    try:
        if FIREBASE_CONFIG_STR:
            firebase_dict = json.loads(FIREBASE_CONFIG_STR)
            cred = credentials.Certificate(firebase_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Connected Successfully via .env!")
        else:
            print("⚠️ FIREBASE_CONFIG not found in .env")
    except Exception as e:
        print(f"❌ Firebase Connection Error: {e}")