"""
AI Financial Agent - FastAPI Backend
Main application entry point
"""
from fastapi import FastAPI, Request, HTTPException, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
import uvicorn
import os
import logging
from datetime import datetime
import json

# Try to import dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed. Environment variables need to be set manually.")

# Import application modules individually
auth_router = None
ocr_router = None
mpesa_router = None
reconciliation_router = None
ai_insights_router = None
Database = None

# Import auth router (priority)
try:
    from auth.router import router as auth_router
    print("✅ Auth router imported successfully")
except ImportError as e:
    print(f"❌ Auth router import failed: {e}")

# Import other routers
try:
    from database.mongodb import Database
    print("✅ Database imported successfully")
except ImportError as e:
    print(f"❌ Database import failed: {e}")

try:
    from ocr.router import router as ocr_router
    print("✅ OCR router imported successfully")
except ImportError as e:
    print(f"❌ OCR router import failed: {e}")

try:
    from mpesa.router import router as mpesa_router
    print("✅ M-Pesa router imported successfully")
except ImportError as e:
    print(f"❌ M-Pesa router import failed: {e}")

try:
    from reconciliation.router import router as reconciliation_router
    print("✅ Reconciliation router imported successfully")
except ImportError as e:
    print(f"❌ Reconciliation router import failed: {e}")

try:
    from ai_insights.router import router as ai_insights_router
    print("✅ AI Insights router imported successfully")
except ImportError as e:
    print(f"❌ AI Insights router import failed: {e}")

# Flag to track if all imports were successful
all_imports_successful = all([
    auth_router is not None,
    Database is not None,
    ocr_router is not None,
    mpesa_router is not None,
    reconciliation_router is not None,
    ai_insights_router is not None
])

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("financial-agent")

app = FastAPI(
    title="AI Financial Agent",
    description="AI-powered financial management system with M-Pesa integration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers that were successfully imported
if auth_router:
    app.include_router(auth_router)
    print("✅ Auth router included in app")

if ocr_router:
    app.include_router(ocr_router)
    print("✅ OCR router included in app")

if mpesa_router:
    app.include_router(mpesa_router)
    print("✅ M-Pesa router included in app")

if reconciliation_router:
    app.include_router(reconciliation_router)
    print("✅ Reconciliation router included in app")

if ai_insights_router:
    app.include_router(ai_insights_router)
    print("✅ AI Insights router included in app")
    
# Initialize database connection and state (if database was imported)
if Database:
    @app.on_event("startup")
    async def startup_db_client():
        logger.info("Initializing database connection...")
        db_instance = Database.get_instance()
        app.db = db_instance
        # Make database available in app state for dependency injection
        app.state.db = db_instance
        
    @app.on_event("shutdown")
    async def shutdown_db_client():
        logger.info("Closing database connection...")
        if hasattr(app, "db"):
            await app.db.close()
else:
    logger.warning("Database not available - database operations will not work")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "AI Financial Agent",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat()
    }

# Environment info endpoint for debugging
@app.get("/api/env", tags=["system"])
async def env_info():
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "production":
        return {
            "environment": env,
            "debug": False
        }
    else:
        return {
            "environment": env,
            "debug": True,
            "mongo_uri": os.environ.get("MONGO_URI", "Not set"),
            "mpesa_env": os.environ.get("MPESA_ENV", "sandbox"),
            "gemini_model": os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        }

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)