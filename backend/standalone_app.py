"""
AI Financial Agent - Standalone FastAPI Backend
Includes: M-Pesa, Reconciliation, AI Insights, Customers, AI Invoice, and Email Service
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

# Try to import dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed")

# Import routers
try:
    from mpesa.router import router as mpesa_router
    print("✅ M-Pesa router imported")
except ImportError as e:
    print(f"❌ M-Pesa router import failed: {e}")
    mpesa_router = None

try:
    from reconciliation.router import router as reconciliation_router
    print("✅ Reconciliation router imported")
except ImportError as e:
    print(f"❌ Reconciliation router import failed: {e}")
    reconciliation_router = None

try:
    from ai_insights.router import router as ai_insights_router
    print("✅ AI Insights router imported")
except ImportError as e:
    print(f"❌ AI Insights router import failed: {e}")
    ai_insights_router = None

try:
    from customers.router import router as customers_router
    print("✅ Customers router imported")
except ImportError as e:
    print(f"❌ Customers router import failed: {e}")
    customers_router = None

try:
    from ai_invoice.router import router as ai_invoice_router
    print("✅ AI Invoice router imported")
except ImportError as e:
    print(f"❌ AI Invoice router import failed: {e}")
    ai_invoice_router = None

try:
    from email_service.router import router as email_router
    print("✅ Email Service router imported")
except ImportError as e:
    print(f"❌ Email Service router import failed: {e}")
    email_router = None

try:
    from reporting.router import router as reporting_router
    print("✅ Reporting router imported")
except ImportError as e:
    print(f"❌ Reporting router import failed: {e}")
    reporting_router = None

try:
    from database.mongodb import Database
    print("✅ Database imported")
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    Database = None

# Initialize FastAPI app
app = FastAPI(
    title="AI Financial Agent",
    description="Backend API for financial management with AI capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if mpesa_router:
    app.include_router(mpesa_router, prefix="/api")
    print("✅ M-Pesa routes added")

if reconciliation_router:
    app.include_router(reconciliation_router, prefix="/api")
    print("✅ Reconciliation routes added")

if ai_insights_router:
    app.include_router(ai_insights_router, prefix="/api")
    print("✅ AI Insights routes added")

if customers_router:
    app.include_router(customers_router, prefix="/api")
    print("✅ Customers routes added")

if ai_invoice_router:
    app.include_router(ai_invoice_router, prefix="/api")
    print("✅ AI Invoice routes added")

if email_router:
    app.include_router(email_router, prefix="/api")
    print("✅ Email Service routes added")

if reporting_router:
    app.include_router(reporting_router, prefix="/api")
    print("✅ Reporting routes added")

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "AI Financial Agent API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "M-Pesa Integration",
            "Transaction Reconciliation",
            "AI Insights",
            "Customer Management",
            "AI Invoice Generation",
            "Email Service",
            "Financial Reports"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "mpesa": mpesa_router is not None,
            "reconciliation": reconciliation_router is not None,
            "ai_insights": ai_insights_router is not None,
            "customers": customers_router is not None,
            "ai_invoice": ai_invoice_router is not None,
            "email": email_router is not None,
            "reporting": reporting_router is not None,
            "database": Database is not None
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("\n" + "="*50)
    print("🚀 AI Financial Agent Backend Starting...")
    print("="*50)
    
    # Initialize database connection if available
    if Database:
        try:
            db = Database.get_instance()
            mongo_uri = os.getenv('MONGO_URI', 'Not configured')
            if mongo_uri != 'Not configured':
                print(f"✅ Connected to MongoDB: {mongo_uri[:50]}...")
            else:
                print(f"⚠️  MongoDB URI not configured")
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
    
    print("\n📡 Available Services:")
    if mpesa_router:
        print("   ✅ M-Pesa Integration")
    if reconciliation_router:
        print("   ✅ Reconciliation Engine")
    if ai_insights_router:
        print("   ✅ AI Insights")
    if customers_router:
        print("   ✅ Customer Management")
    if ai_invoice_router:
        print("   ✅ AI Invoice Generation")
    if email_router:
        print("   ✅ Email Service")
    
    print("\n📬 Email Configuration:")
    sendgrid_key = os.getenv('SENDGRID_API_KEY')
    if sendgrid_key:
        print(f"   ✅ SendGrid API Key: {sendgrid_key[:10]}...")
    else:
        print("   ⚠️  SendGrid API Key not set (using mock mode)")
    
    from_email = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@example.com')
    from_name = os.getenv('SENDGRID_FROM_NAME', 'Financial Agent')
    print(f"   📧 From: {from_name} <{from_email}>")
    
    print("\n" + "="*50)
    print("✅ Server Ready!")
    print("📍 API Docs: http://localhost:8000/docs")
    print("="*50 + "\n")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n🛑 Shutting down AI Financial Agent Backend...")
    print("✅ Cleanup complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "standalone_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
