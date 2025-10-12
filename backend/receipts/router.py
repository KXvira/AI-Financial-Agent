"""
Receipt API Router

FastAPI endpoints for receipt generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os

from .models import (
    Receipt, ReceiptGenerateRequest, ReceiptType, ReceiptStatus,
    ReceiptListResponse, ReceiptStatistics, ReceiptTemplate
)
from .service import ReceiptService
from .templates_service import ReceiptTemplateService
from backend.database.mongodb import get_database, Database


router = APIRouter(prefix="/receipts", tags=["receipts"])


def get_receipt_service(db: Database = Depends(get_database)) -> ReceiptService:
    """Dependency to get receipt service"""
    return ReceiptService(db)


def get_template_service(db: Database = Depends(get_database)) -> ReceiptTemplateService:
    """Dependency to get template service"""
    return ReceiptTemplateService(db)


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
    try:
        result = await service.send_receipt_email(receipt_id, email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


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


@router.post("/bulk-email")
async def bulk_email_receipts(
    receipt_ids: List[str] = Body(..., description="List of receipt IDs to email"),
    email: str = Body(..., description="Recipient email address"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Send multiple receipts in one email
    
    Sends multiple receipt PDFs attached to a single email.
    Useful for sending monthly statements or multiple transactions.
    
    - **receipt_ids**: List of receipt IDs to include
    - **email**: Recipient email address
    """
    try:
        result = await service.send_bulk_receipts_email(receipt_ids, email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending bulk email: {str(e)}")


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


# =============================================================================
# RECEIPT TEMPLATE ENDPOINTS
# =============================================================================

@router.get("/templates/", tags=["templates"])
async def list_templates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    List all receipt templates
    
    Returns available templates for receipt customization.
    """
    result = await service.list_templates(
        page=page,
        page_size=page_size,
        is_active=is_active
    )
    return result


@router.post("/templates/", response_model=ReceiptTemplate, status_code=201, tags=["templates"])
async def create_template(
    template: ReceiptTemplate,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Create a new receipt template
    
    Creates a custom receipt template with branding and styling options.
    """
    try:
        created = await service.create_template(template)
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")


@router.get("/templates/{template_id}", response_model=ReceiptTemplate, tags=["templates"])
async def get_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Get template by ID
    
    Returns template details for customization.
    """
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=ReceiptTemplate, tags=["templates"])
async def update_template(
    template_id: str,
    updates: Dict[str, Any] = Body(..., description="Fields to update"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Update a receipt template
    
    Updates template settings and styling options.
    """
    template = await service.update_template(template_id, updates)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}", tags=["templates"])
async def delete_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Delete a receipt template
    
    Soft deletes a template by marking it as inactive.
    """
    success = await service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"success": True, "message": "Template deleted successfully"}


@router.get("/templates/default/get", response_model=ReceiptTemplate, tags=["templates"])
async def get_default_template(
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Get the default receipt template
    
    Returns the currently active default template.
    """
    template = await service.get_default_template()
    if not template:
        raise HTTPException(status_code=404, detail="No default template found")
    return template


@router.post("/templates/{template_id}/set-default", response_model=ReceiptTemplate, tags=["templates"])
async def set_default_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Set a template as default
    
    Makes this template the default for all new receipts.
    """
    template = await service.set_default_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates/seed/defaults", tags=["templates"])
async def seed_default_templates(
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Seed default receipt templates
    
    Creates default templates if none exist.
    """
    templates = await service.seed_default_templates()
    return {
        "success": True,
        "message": f"Created {len(templates)} default templates" if templates else "Templates already exist",
        "templates_created": len(templates)
    }


@router.post("/templates/{template_id}/duplicate", response_model=ReceiptTemplate, tags=["templates"])
async def duplicate_template(
    template_id: str,
    new_name: str = Query(..., description="Name for the duplicated template"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Duplicate an existing template
    
    Creates a copy of a template with a new name.
    """
    template = await service.duplicate_template(template_id, new_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template
