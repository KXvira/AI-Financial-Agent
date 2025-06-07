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

# Import application modules
try:
    from mpesa.router import router as mpesa_router
    from reconciliation.router import router as reconciliation_router
    from database.mongodb import Database
    
    # Flag to track if all imports were successful
    all_imports_successful = True
except ImportError as e:
    print(f"Error importing application modules: {e}")
    print("Some features may not be available.")
    all_imports_successful = False

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

# Include routers if imports were successful
if all_imports_successful:
    app.include_router(mpesa_router)
    app.include_router(reconciliation_router)
    
    # Initialize database connection
    @app.on_event("startup")
    async def startup_db_client():
        logger.info("Initializing database connection...")
        app.db = Database.get_instance()
        
    @app.on_event("shutdown")
    async def shutdown_db_client():
        logger.info("Closing database connection...")
        if hasattr(app, "db"):
            await app.db.close()

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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)