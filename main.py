import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional
from sqlalchemy import text # For PostgreSQL health check

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Firebase Admin (Safe Check for Redeploys)
if not firebase_admin._apps:
    firebase_config = os.getenv("FIREBASE_CONFIG")
    if firebase_config:
        try:
            cred_dict = json.loads(firebase_config)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase Admin initialized successfully!")
        except Exception as e:
            print(f"❌ Error loading FIREBASE_CONFIG: {e}")
    else:
        # Local Fallback
        service_key_path = "serviceAccountKey.json"
        if os.path.exists(service_key_path):
            cred = credentials.Certificate(service_key_path)
            firebase_admin.initialize_app(cred)
            print("🔥 Firebase initialized using local file!")
        else:
            print("⚠️ WARNING: No Firebase credentials found.")

# 3. Import routes and NEW PostgreSQL Database Session
from routes.transaction_routes import router as transaction_router
from routes.calculator_routes import router as calculator_router
from database import AsyncSessionLocal 

app = FastAPI(title="Bot Expense Tracker API")

# 4. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Root route for Render Health Checks (Handles GET and HEAD to prevent 521/405 errors)
@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"message": "Expense Tracker API is Live on Render! 🚀", "status": "Online"}

# NEW: PostgreSQL (Supabase) Health Check (Replaces mongo-check)
@app.get("/postgres-check")
async def postgres_check():
    try:
        # Pinging Supabase to verify connection
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "success", "message": "PostgreSQL (Supabase) is connected ✅"}
    except Exception as e:
        return {"status": "fail", "error": str(e)}

# 6. Include Routers
app.include_router(transaction_router)
app.include_router(calculator_router, prefix="/api/calculator", tags=["Calculator"])

if __name__ == "__main__":
    # CRITICAL: Dynamic port binding for Render
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)