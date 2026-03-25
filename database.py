import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Retrieve MongoDB URI and Database Name
# Render will pull these from the Environment Group you created
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "expense_tracker")

# 3. Validation and Connection
if not MONGO_URI:
    print("❌ CRITICAL ERROR: MONGO_URI not found. Check Render Environment Variables!")

# 4. Create the MongoDB client with Production settings
# tlsAllowInvalidCertificates is essential for some cloud network configurations
client = AsyncIOMotorClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True, 
    retryWrites=True,
    serverSelectionTimeoutMS=5000  # Fails fast (5s) instead of hanging if URI is wrong
)

# 5. Get the database instance
db = client[MONGO_DB_NAME]

# Function to get the database (used with FastAPI Depends in routes)
def get_db() -> AsyncIOMotorDatabase:
    """
    Returns the database instance for dependency injection.
    """
    return db