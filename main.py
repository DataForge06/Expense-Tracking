import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional

# 1. Load Environment Variables
load_dotenv()

# 2. Initialize Firebase Admin (Render-Friendly)
# Locally: Uses serviceAccountKey.json
# Render: Paste the JSON content into FIREBASE_CONFIG env var
firebase_config = os.getenv("FIREBASE_CONFIG")
if firebase_config:
    try:
        cred_dict = json.loads(firebase_config)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"❌ Error loading FIREBASE_CONFIG: {e}")
else:
    # Local Fallback
    service_key_path = "serviceAccountKey.json"
    if os.path.exists(service_key_path):
        cred = credentials.Certificate(service_key_path)
        firebase_admin.initialize_app(cred)
    else:
        print("⚠️ WARNING: No Firebase credentials found. Auth will fail.")

# Import routes AFTER initializing Firebase/Env
from routes.transaction_routes import router as transaction_router
from routes.calculator_routes import router as calculator_router
from database import client

app = FastAPI(title="Expense Tracker API")

# 3. Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Security Dependency: Verify Firebase Token
# This ensures that only logged-in users can access your Render API
async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authentication Token")
    
    token = authorization.split("Bearer ")[1]
    try:
        # Verifies the token with Google/Firebase servers
        decoded_token = auth.verify_id_token(token)
        return decoded_token['email']
    except Exception:
        raise HTTPException(status_code=444, detail="Invalid or Expired Token")

# 5. Include Routers
app.include_router(transaction_router)
app.include_router(calculator_router, prefix="/api/calculator", tags=["Calculator"])

@app.get("/")
async def root():
    return {"message": "Expense Tracker API is Live on Render! 🚀"}

@app.get("/mongo-check")
async def mongo_check():
    try:
        await client.admin.command("ping")
        return {"status": "success", "message": "MongoDB is connected ✅"}
    except Exception as e:
        return {"status": "fail", "error": str(e)}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # host '0.0.0.0' is REQUIRED for Render/Docker traffic
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)