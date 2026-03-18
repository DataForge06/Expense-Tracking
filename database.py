# database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv
import ssl

# 1. Load environment variables from the .env file
load_dotenv()

# 2. Retrieve MongoDB URI and Database Name
# It is better to leave the default as None to catch connection errors early
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "expense_tracker")

# 3. Validation: Check if the URI exists before attempting to connect
if not MONGO_URI:
    print("CRITICAL ERROR: MONGO_URI not found in .env file.")
    print("Ensure you have a .env file with MONGO_URI=mongodb+srv://...")
    # For local development fallback if needed:
    # MONGO_URI = "mongodb://localhost:27017/expense_tracker"

# 4. Create the MongoDB client
# 'tlsAllowInvalidCertificates' can help if you face SSL/Certificate issues locally
client = AsyncIOMotorClient(MONGO_URI)

# 5. Get the database instance
db = client[MONGO_DB_NAME]

# Function to get the database (used with FastAPI Depends in routes)
def get_db() -> AsyncIOMotorDatabase:
    """
    Returns the database instance for dependency injection.
    """
    return db