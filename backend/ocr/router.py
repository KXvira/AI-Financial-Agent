"""
OCR Router - API endpoints for receipt processing and expense management
"""
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import FileResponse
import logging

import sys
import os

# Add backend directory to Python path for backend modules
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from auth.middleware import get_current_user, get_auth_service
from auth.models import User
from database.mongodb import Database
from .models import (
    Receipt, ReceiptUpdate, ExpenseFilter, ExpenseSummary,
    ProcessingStatus, ExpenseCategory, PaymentMethod, VerificationStatus,
    FileUploadResponse
)
from .service import OCRService
from .uploader import FileUploader

logger = logging.getLogger("financial-agent.ocr.router")

router = APIRouter(
    prefix="/api/receipts",
    tags=["OCR & Expenses"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"}, 
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

def get_ocr_service(request) -> OCRService:
    """Get OCR service instance"""
    db = request.app.state.db if hasattr(request.app.state, 'db') else None
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not available"
        )
    return OCRService(db)

@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload receipt for OCR processing",
    description="Upload a receipt image or PDF for OCR processing and expense extraction"
)
async def upload_receipt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> FileUploadResponse:
    """Upload and process receipt file"""
    try:
        logger.info(f"Receipt upload initiated by user: {current_user.id}")
        
        # Upload file
        uploader = FileUploader()
        upload_response = await uploader.upload_file(file, current_user.id)
        
        # Create receipt record in database
        file_path = uploader.get_file_path(current_user.id, upload_response.filename)
        
        receipt = await ocr_service.create_receipt_record(
            user_id=current_user.id,
            file_path=str(file_path),
            original_filename=file.filename or "unknown",
            file_size=upload_response.file_size,
            mime_type=file.content_type or "unknown"
        )
        
        # Process receipt in background
        background_tasks.add_task(
            ocr_service.process_receipt_async,
            receipt.id
        )
        
        logger.info(f"Receipt upload successful: {receipt.id}")
        
        return FileUploadResponse(
            receipt_id=receipt.id,
            filename=upload_response.filename,
            file_size=upload_response.file_size,
            upload_status="success",
            message="Receipt uploaded successfully and processing started",
            processing_status=ProcessingStatus.PENDING
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Receipt upload error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload receipt: {str(e)}"
        )

@router.get(
    "/",
    response_model=List[Receipt],
    summary="Get user receipts",
    description="Get all receipts for the current user with optional filtering"
)
async def get_receipts(
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    category: Optional[ExpenseCategory] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    min_amount: Optional[float] = Query(None, ge=0),
    max_amount: Optional[float] = Query(None, ge=0),
    vendor_name: Optional[str] = Query(None),
    payment_method: Optional[PaymentMethod] = Query(None),
    verification_status: Optional[VerificationStatus] = Query(None),
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> List[Receipt]:
    """Get user receipts with filtering options"""
    try:
        # Build filters
        filters = ExpenseFilter()
        
        if start_date:
            from datetime import datetime
            filters.start_date = datetime.fromisoformat(start_date)
        if end_date:
            from datetime import datetime
            filters.end_date = datetime.fromisoformat(end_date)
        if category:
            filters.category = category
        if min_amount is not None:
            filters.min_amount = min_amount
        if max_amount is not None:
            filters.max_amount = max_amount
        if vendor_name:
            filters.vendor_name = vendor_name
        if payment_method:
            filters.payment_method = payment_method
        if verification_status:
            filters.verification_status = verification_status
        
        receipts = await ocr_service.get_user_receipts(
            current_user.id, 
            filters, 
            limit=limit, 
            skip=skip
        )
        
        return receipts
        
    except Exception as e:
        logger.error(f"Get receipts error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipts"
        )

@router.get(
    "/{receipt_id}",
    response_model=Receipt,
    summary="Get receipt by ID",
    description="Get detailed information about a specific receipt"
)
async def get_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> Receipt:
    """Get receipt by ID"""
    try:
        receipt = await ocr_service.get_receipt(receipt_id)
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        # Check ownership
        if receipt.user_id != current_user.id and current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this receipt"
            )
        
        return receipt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get receipt error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipt"
        )

@router.put(
    "/{receipt_id}",
    response_model=Receipt,
    summary="Update receipt",
    description="Update receipt information (user corrections and verification)"
)
async def update_receipt(
    receipt_id: str,
    update_data: ReceiptUpdate,
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> Receipt:
    """Update receipt with user corrections"""
    try:
        # Check if receipt exists and user has access
        existing_receipt = await ocr_service.get_receipt(receipt_id)
        if not existing_receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        if existing_receipt.user_id != current_user.id and current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this receipt"
            )
        
        # Update receipt
        updated_receipt = await ocr_service.update_receipt(receipt_id, update_data)
        
        if not updated_receipt:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update receipt"
            )
        
        return updated_receipt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update receipt error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update receipt"
        )

@router.delete(
    "/{receipt_id}",
    summary="Delete receipt",
    description="Delete receipt and associated file"
)
async def delete_receipt(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> Dict[str, str]:
    """Delete receipt"""
    try:
        success = await ocr_service.delete_receipt(receipt_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found or access denied"
            )
        
        return {"message": "Receipt deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete receipt error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete receipt"
        )

@router.get(
    "/{receipt_id}/image",
    response_class=FileResponse,
    summary="Get receipt image",
    description="Download the original receipt image file"
)
async def get_receipt_image(
    receipt_id: str,
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> FileResponse:
    """Get receipt image file"""
    try:
        receipt = await ocr_service.get_receipt(receipt_id)
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        # Check ownership
        if receipt.user_id != current_user.id and current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this receipt"
            )
        
        # Check if file exists
        from pathlib import Path
        file_path = Path(receipt.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt file not found"
            )
        
        return FileResponse(
            path=str(file_path),
            filename=receipt.original_filename,
            media_type=receipt.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get receipt image error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve receipt image"
        )

@router.post(
    "/{receipt_id}/reprocess",
    response_model=Receipt,
    summary="Reprocess receipt",
    description="Reprocess receipt with OCR and AI (useful for failed processing)"
)
async def reprocess_receipt(
    receipt_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> Receipt:
    """Reprocess receipt"""
    try:
        receipt = await ocr_service.get_receipt(receipt_id)
        
        if not receipt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found"
            )
        
        if receipt.user_id != current_user.id and current_user.role != "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this receipt"
            )
        
        # Reset status to pending
        await ocr_service.update_receipt_status(receipt_id, ProcessingStatus.PENDING)
        
        # Process in background
        background_tasks.add_task(
            ocr_service.process_receipt_async,
            receipt_id
        )
        
        return await ocr_service.get_receipt(receipt_id)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reprocess receipt error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reprocess receipt"
        )

@router.get(
    "/analytics/summary",
    response_model=ExpenseSummary,
    summary="Get expense summary",
    description="Get expense analytics and summary for the current user"
)
async def get_expense_summary(
    category: Optional[ExpenseCategory] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    ocr_service: OCRService = Depends(get_ocr_service)
) -> ExpenseSummary:
    """Get expense summary and analytics"""
    try:
        # Build filters
        filters = ExpenseFilter()
        
        if start_date:
            from datetime import datetime
            filters.start_date = datetime.fromisoformat(start_date)
        if end_date:
            from datetime import datetime
            filters.end_date = datetime.fromisoformat(end_date)
        if category:
            filters.category = category
        
        summary = await ocr_service.get_expense_summary(current_user.id, filters)
        return summary
        
    except Exception as e:
        logger.error(f"Get expense summary error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate expense summary"
        )

# Real expense summary endpoint (no auth required for now)
@router.get(
    "/demo/summary",
    summary="Get expense summary from database",
    description="Get expense summary from real database (no auth required)"
)
async def get_demo_expense_summary():
    """Get expense summary from database without authentication"""
    try:
        from database.mongodb import Database
        from datetime import datetime, timedelta
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Get receipts collection
        receipts = db.receipts
        
        # Calculate date range (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get all receipts for calculations
        cursor = receipts.find({"status": "processed"})
        
        total_expenses_amount = 0.0
        total_receipts_count = 0
        monthly_total = 0.0
        category_summary = {}
        recent_expenses = []
        
        async for receipt in cursor:
            total_receipts_count += 1
            ocr_data = receipt.get('ocr_data', {})
            extracted_data = ocr_data.get('extracted_data', {})
            
            amount = extracted_data.get('total_amount', 0.0)
            category = extracted_data.get('category', receipt.get('category', 'Other'))
            created_at = receipt.get('created_at', datetime.utcnow())
            
            # Add to total expenses amount
            total_expenses_amount += amount
            
            # Add to monthly if within date range
            if created_at >= start_date:
                monthly_total += amount
            
            # Add to category summary
            if category not in category_summary:
                category_summary[category] = 0.0
            category_summary[category] += amount
        
        # Get recent 10 receipts for the table
        cursor = receipts.find({"status": "processed"}).sort("created_at", -1).limit(10)
        
        async for receipt in cursor:
            ocr_data = receipt.get('ocr_data', {})
            extracted_data = ocr_data.get('extracted_data', {})
            
            recent_expenses.append({
                "id": str(receipt.get('_id')),
                "date": receipt.get('created_at', datetime.utcnow()).strftime("%Y-%m-%d"),
                "vendor": extracted_data.get('vendor_name', 'Unknown Vendor'),
                "amount": extracted_data.get('total_amount', 0.0),
                "category": extracted_data.get('category', receipt.get('category', 'Other')),
                "status": "Verified" if receipt.get('status') == 'processed' else "Pending"
            })
        
        return {
            "totalExpenses": round(total_expenses_amount, 2),
            "totalReceipts": total_receipts_count,
            "monthlyTotal": round(monthly_total, 2),
            "categorySummary": {k: round(v, 2) for k, v in category_summary.items()},
            "recentExpenses": recent_expenses
        }
        
    except Exception as e:
        logger.error(f"Error fetching expense summary: {str(e)}")
        # Return empty data structure instead of error
        return {
            "totalExpenses": 0,
            "monthlyTotal": 0.0,
            "categorySummary": {},
            "recentExpenses": []
        }

@router.get(
    "/categories",
    summary="Get expense categories",
    description="Get list of available expense categories"
)
async def get_expense_categories() -> Dict[str, List[Dict[str, str]]]:
    """Get available expense categories"""
    categories = [
        {"value": cat.value, "label": cat.value.replace('_', ' ').title()}
        for cat in ExpenseCategory
    ]
    
    return {"categories": categories}

@router.get(
    "/health",
    summary="OCR service health check",
    description="Check OCR service health and dependencies"
)
async def health_check() -> Dict[str, Any]:
    """OCR service health check"""
    try:
        import pytesseract
        import cv2
        
        # Check Tesseract
        try:
            version = pytesseract.get_tesseract_version()
            tesseract_status = "available"
            tesseract_version = str(version)
        except Exception:
            tesseract_status = "unavailable"
            tesseract_version = "unknown"
        
        # Check OpenCV
        opencv_version = cv2.__version__
        
        # Check file upload directory
        uploader = FileUploader()
        storage_stats = uploader.get_storage_stats()
        
        return {
            "status": "healthy",
            "service": "ocr",
            "dependencies": {
                "tesseract": {
                    "status": tesseract_status,
                    "version": tesseract_version
                },
                "opencv": {
                    "status": "available",
                    "version": opencv_version
                }
            },
            "storage": storage_stats,
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"OCR health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OCR service unavailable"
        )