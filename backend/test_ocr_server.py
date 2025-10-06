#!/usr/bin/env python3
"""
Simple test server for OCR functionality
This bypasses complex dependencies for quick testing
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import json
from datetime import datetime
from typing import Dict, Any
import uuid

app = FastAPI(title="OCR Test Server", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage for testing
receipts_store = {}

def mock_ocr_processing(file_content: bytes, filename: str) -> Dict[str, Any]:
    """Mock OCR processing for testing purposes"""
    # Simulate OCR results based on filename patterns
    if "receipt" in filename.lower():
        return {
            "vendor": "Sample Store Ltd",
            "total": 1250.50,
            "date": "2024-10-06",
            "category": "Office Supplies",
            "items": [
                {"name": "Paper A4", "price": 500.00, "quantity": 2},
                {"name": "Pens", "price": 250.50, "quantity": 1}
            ],
            "confidence": 0.85
        }
    elif "fuel" in filename.lower():
        return {
            "vendor": "Shell Station",
            "total": 3500.00,
            "date": "2024-10-06",
            "category": "Transport",
            "items": [
                {"name": "Petrol", "price": 3500.00, "quantity": 25}
            ],
            "confidence": 0.92
        }
    else:
        return {
            "vendor": "Unknown Vendor",
            "total": 750.00,
            "date": "2024-10-06",
            "category": "Other",
            "items": [],
            "confidence": 0.65
        }

@app.post("/api/ocr/upload-receipt")
async def upload_receipt(file: UploadFile = File(...)):
    """Upload and process receipt"""
    try:
        # Validate file type
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        file_content = await file.read()
        
        # Generate unique ID
        receipt_id = str(uuid.uuid4())
        
        # Mock OCR processing
        ocr_result = mock_ocr_processing(file_content, file.filename)
        
        # Store receipt data
        receipt_data = {
            "id": receipt_id,
            "filename": file.filename,
            "status": "completed",
            "uploaded_at": datetime.now().isoformat(),
            "parsed_data": ocr_result,
            "file_size": len(file_content)
        }
        
        receipts_store[receipt_id] = receipt_data
        
        return {
            "success": True,
            "receipt_id": receipt_id,
            "parsed_data": ocr_result,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/ocr/receipts")
async def get_receipts():
    """Get all receipts"""
    return {
        "receipts": list(receipts_store.values()),
        "total": len(receipts_store)
    }

@app.get("/api/ocr/receipts/{receipt_id}")
async def get_receipt(receipt_id: str):
    """Get specific receipt"""
    if receipt_id not in receipts_store:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipts_store[receipt_id]

@app.get("/api/ocr/expense-summary")
async def get_expense_summary():
    """Get expense summary"""
    receipts = list(receipts_store.values())
    
    total_expenses = sum(r["parsed_data"]["total"] for r in receipts)
    monthly_total = total_expenses  # Simplified for demo
    
    # Category summary
    category_summary = {}
    for receipt in receipts:
        category = receipt["parsed_data"]["category"]
        amount = receipt["parsed_data"]["total"]
        category_summary[category] = category_summary.get(category, 0) + amount
    
    # Recent expenses
    recent_expenses = [
        {
            "id": r["id"],
            "date": r["parsed_data"]["date"],
            "vendor": r["parsed_data"]["vendor"],
            "amount": r["parsed_data"]["total"],
            "category": r["parsed_data"]["category"],
            "status": r["status"]
        }
        for r in receipts[-10:]  # Last 10 receipts
    ]
    
    return {
        "totalExpenses": total_expenses,
        "monthlyTotal": monthly_total,
        "categorySummary": category_summary,
        "recentExpenses": recent_expenses
    }

@app.get("/api/ocr/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "receipts_count": len(receipts_store),
        "ocr_service": "mock_active"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OCR Test Server is running",
        "endpoints": [
            "/api/ocr/upload-receipt",
            "/api/ocr/receipts",
            "/api/ocr/expense-summary",
            "/api/ocr/health"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting OCR Test Server...")
    print("📊 Dashboard: http://localhost:8000")
    print("📁 Upload endpoint: http://localhost:8000/api/ocr/upload-receipt")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)