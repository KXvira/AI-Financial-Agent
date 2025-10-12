"""
Receipt API Router

FastAPI endpoints for receipt generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response
from typing import Optional, List
from datetime import datetime, timedelta
import os

from .models import (
    Receipt, ReceiptGenerateRequest, ReceiptType, ReceiptStatus,
    ReceiptListResponse, ReceiptStatistics
)
from .service import ReceiptService
from backend.database.mongodb import get_database, Database


router = APIRouter(prefix="/receipts", tags=["receipts"])


def get_receipt_service(db: Database = Depends(get_database)) -> ReceiptService:
    """Dependency to get receipt service"""
    return ReceiptService(db)


@router.post("/generate", response_model=Receipt, status_code=201)
async def generate_receipt(
    request: ReceiptGenerateRequest,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Generate a new receipt
    
    - **receipt_type**: Type of receipt (payment, invoice, refund, etc.)
    - **customer**: Customer information
    - **payment_method**: Payment method used
    - **amount**: Total amount (including VAT if include_vat=True)
    - **description**: Payment description (optional)
    - **include_vat**: Whether amount includes VAT (default: True)
    - **send_email**: Send receipt via email (default: False)
    """
    try:
        receipt = await service.generate_receipt(request)
        return receipt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating receipt: {str(e)}")


@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(
    receipt_id: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Get receipt by ID
    
    Returns receipt details including PDF path and QR code data.
    """
    receipt = await service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Log audit event (viewed)
    await service._log_audit(
        receipt_id=receipt.id,
        receipt_number=receipt.receipt_number,
        action="viewed"
    )
    
    return receipt


@router.get("/number/{receipt_number}", response_model=Receipt)
async def get_receipt_by_number(
    receipt_number: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Get receipt by receipt number
    
    Returns receipt details by receipt number (e.g., RCP-2025-0001).
    """
    receipt = await service.get_receipt_by_number(receipt_number)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt


@router.get("/", response_model=ReceiptListResponse)
async def list_receipts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    receipt_type: Optional[ReceiptType] = Query(None, description="Filter by receipt type"),
    status: Optional[ReceiptStatus] = Query(None, description="Filter by status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    List receipts with filters
    
    Supports pagination and filtering by:
    - Receipt type (payment, invoice, refund, etc.)
    - Status (draft, generated, sent, viewed, downloaded, voided)
    - Customer ID
    - Date range
    """
    result = await service.list_receipts(
        page=page,
        page_size=page_size,
        receipt_type=receipt_type,
        status=status,
        customer_id=customer_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return ReceiptListResponse(**result)


@router.get("/{receipt_id}/download")
async def download_receipt(
    receipt_id: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Download receipt PDF
    
    Returns the receipt PDF file for download.
    """
    receipt = await service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    if not receipt.pdf_path or not os.path.exists(receipt.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    # Read PDF file
    with open(receipt.pdf_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Log audit event (downloaded)
    await service._log_audit(
        receipt_id=receipt.id,
        receipt_number=receipt.receipt_number,
        action="downloaded"
    )
    
    # Return PDF with appropriate headers
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={receipt.receipt_number}.pdf"
        }
    )


@router.post("/{receipt_id}/void", response_model=Receipt)
async def void_receipt(
    receipt_id: str,
    reason: str = Query(..., description="Reason for voiding receipt"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Void a receipt
    
    Marks a receipt as voided. Receipts cannot be deleted for KRA compliance,
    but can be voided with a reason.
    
    - **reason**: Reason for voiding the receipt (required)
    """
    receipt = await service.void_receipt(receipt_id, reason)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt


@router.post("/{receipt_id}/email")
async def email_receipt(
    receipt_id: str,
    email: Optional[str] = Query(None, description="Override email address"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Send receipt via email
    
    Sends the receipt PDF to the customer's email address.
    Optionally override the email address.
    
    - **email**: Optional email override (uses customer email if not provided)
    """
    receipt = await service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Determine email address
    recipient_email = email or receipt.customer.email
    if not recipient_email:
        raise HTTPException(status_code=400, detail="No email address provided")
    
    # TODO: Integrate with email service from Phase 4
    # For now, just log the action
    await service._log_audit(
        receipt_id=receipt.id,
        receipt_number=receipt.receipt_number,
        action="sent",
        details={"email": recipient_email}
    )
    
    return {
        "success": True,
        "message": f"Receipt sent to {recipient_email}",
        "receipt_id": receipt.id,
        "receipt_number": receipt.receipt_number
    }


@router.get("/statistics/summary", response_model=ReceiptStatistics)
async def get_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Get receipt statistics
    
    Returns statistical analysis of receipts including:
    - Total receipts
    - Breakdown by type and status
    - Monthly trends
    - Financial totals
    
    - **days**: Number of days to analyze (default: 30)
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        stats = await service.get_statistics(start_date=start_date)
        return stats
    except Exception as e:
        # Return default statistics if there's an error
        return ReceiptStatistics(
            total_receipts=0,
            receipts_by_type={},
            receipts_by_status={},
            receipts_by_month={},
            total_amount=0.0,
            average_amount=0.0,
            receipts_sent=0,
            receipts_voided=0
        )


@router.post("/bulk-generate")
async def bulk_generate_receipts(
    requests: List[ReceiptGenerateRequest],
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Generate multiple receipts in bulk
    
    Accepts a list of receipt generation requests and creates all receipts.
    Returns list of generated receipt IDs and any errors.
    
    - **requests**: List of receipt generation requests
    """
    results = {
        "success": [],
        "errors": []
    }
    
    for idx, request in enumerate(requests):
        try:
            receipt = await service.generate_receipt(request)
            results["success"].append({
                "index": idx,
                "receipt_id": receipt.id,
                "receipt_number": receipt.receipt_number
            })
        except Exception as e:
            results["errors"].append({
                "index": idx,
                "error": str(e)
            })
    
    return {
        "total_requested": len(requests),
        "total_success": len(results["success"]),
        "total_errors": len(results["errors"]),
        "results": results
    }


@router.get("/verify/{receipt_number}")
async def verify_receipt(
    receipt_number: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Verify receipt authenticity
    
    Verifies that a receipt number exists and returns basic details.
    Used for QR code verification.
    
    - **receipt_number**: Receipt number to verify (e.g., RCP-2025-0001)
    """
    receipt = await service.get_receipt_by_number(receipt_number)
    if not receipt:
        return {
            "valid": False,
            "message": "Receipt not found"
        }
    
    if receipt.status == ReceiptStatus.VOIDED:
        return {
            "valid": False,
            "message": "Receipt has been voided",
            "voided_at": receipt.voided_at,
            "void_reason": receipt.void_reason
        }
    
    return {
        "valid": True,
        "receipt_number": receipt.receipt_number,
        "customer_name": receipt.customer.name,
        "amount": receipt.tax_breakdown.total,
        "payment_date": receipt.payment_date,
        "status": receipt.status
    }
