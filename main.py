import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# 1. Load the .env file first
load_dotenv()

# Import your routes and database logic
# These must come AFTER load_dotenv so they can read the MONGO_URI
from routes.transaction_routes import router as transaction_router
from routes.calculator_routes import router as calculator_router
from database import client

app = FastAPI(title="Expense Tracker API")

# 2. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Include Routers
app.include_router(transaction_router)
app.include_router(calculator_router, prefix="/api/calculator", tags=["Calculator"])

@app.get("/")
async def root():
    return {"message": "Expense Tracker API is Running Successfully 🚀"}

# 4. MongoDB Connectivity Check
@app.get("/mongo-check")
async def mongo_check():
    try:
        await client.admin.command("ping")
        return {"status": "success", "message": "MongoDB is connected ✅"}
    except Exception as e:
        return {"status": "fail", "message": "MongoDB connection error", "error": str(e)}

# --- MOVE THIS TO THE VERY BOTTOM ---
if __name__ == "__main__":
    # Get port from .env or default to 8000
    port = int(os.getenv("PORT", 8000))
    # host '0.0.0.0' is REQUIRED for the Pixel 4 Emulator to connect
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)