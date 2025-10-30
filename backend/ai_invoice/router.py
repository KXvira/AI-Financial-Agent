"""
AI Invoice Generation API Router
Endpoints for generating invoice drafts using AI
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from database.mongodb import get_database
from .service import AIInvoiceService

router = APIRouter(prefix="/api/ai-invoice", tags=["AI Invoice"])


# Request/Response Models
class GenerateInvoiceRequest(BaseModel):
    """Request to generate invoice using AI"""
    customer_id: str = Field(..., description="Customer ID")
    prompt: str = Field(..., description="Natural language description of what to invoice", min_length=5)
    due_days: Optional[int] = Field(None, description="Number of days until due date")
    currency: Optional[str] = Field("KES", description="Currency code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-0001",
                "prompt": "Invoice for web development services, 40 hours at $50/hour",
                "due_days": 30,
                "currency": "KES"
            }
        }


class InvoiceItem(BaseModel):
    """Invoice line item"""
    description: str
    quantity: float
    unit_price: float
    total: float


class InvoiceDraftResponse(BaseModel):
    """Invoice draft response"""
    draft_id: Optional[str] = None
    customer_id: str
    customer_name: str
    issue_date: str
    due_date: str
    items: List[InvoiceItem]
    subtotal: float
    tax_rate: float
    tax_amount: float
    total_amount: float
    currency: str
    notes: str
    status: str
    generated_by: str
    generated_at: str


class UpdateDraftRequest(BaseModel):
    """Request to update draft"""
    items: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    due_date: Optional[str] = None


class CustomerContextResponse(BaseModel):
    """Customer context for AI generation"""
    customer: Dict[str, Any]
    recent_invoices: List[Dict[str, Any]]
    patterns: Dict[str, Any]
    preferences: Dict[str, Any]


# Dependency to get service
async def get_ai_invoice_service():
    """Dependency to get AI invoice service"""
    db = await get_database()
    return AIInvoiceService(db)


# Endpoints
@router.post("/generate", response_model=InvoiceDraftResponse)
async def generate_invoice(
    request: GenerateInvoiceRequest,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """
    Generate an invoice draft using AI based on natural language input
    
    This endpoint uses Gemini AI to:
    1. Analyze customer history and patterns
    2. Interpret the natural language request
    3. Generate appropriate invoice items with pricing
    4. Calculate totals and taxes
    
    The generated draft can be reviewed, edited, and then converted to an actual invoice.
    """
    try:
        options = {
            "currency": request.currency,
        }
        if request.due_days is not None:
            options["due_days"] = request.due_days
        
        draft = await service.generate_invoice_draft(
            customer_id=request.customer_id,
            user_input=request.prompt,
            options=options
        )
        
        # Save the draft
        draft_id = await service.save_draft(draft)
        draft["draft_id"] = draft_id
        draft["_id"] = draft_id
        
        return draft
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate invoice: {str(e)}")


@router.get("/context/{customer_id}", response_model=CustomerContextResponse)
async def get_customer_context(
    customer_id: str,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """
    Get customer context for AI invoice generation
    
    Returns:
    - Customer details
    - Recent invoices
    - Payment patterns
    - AI preferences
    
    This information is used by the AI to generate contextually appropriate invoices.
    """
    try:
        context = await service.get_customer_context(customer_id)
        return context
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get context: {str(e)}")


@router.get("/drafts", response_model=List[InvoiceDraftResponse])
async def list_drafts(
    customer_id: Optional[str] = None,
    limit: int = 50,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """
    List invoice drafts
    
    Optionally filter by customer_id to see drafts for a specific customer.
    """
    try:
        drafts = await service.list_drafts(customer_id=customer_id, limit=limit)
        
        # Add draft_id from _id
        for draft in drafts:
            draft["draft_id"] = draft.get("_id")
        
        return drafts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list drafts: {str(e)}")


@router.get("/drafts/{draft_id}", response_model=InvoiceDraftResponse)
async def get_draft(
    draft_id: str,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """Get a specific invoice draft by ID"""
    try:
        draft = await service.get_draft(draft_id)
        if not draft:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        draft["draft_id"] = draft.get("_id")
        return draft
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get draft: {str(e)}")


@router.put("/drafts/{draft_id}", response_model=InvoiceDraftResponse)
async def update_draft(
    draft_id: str,
    request: UpdateDraftRequest,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """
    Update an invoice draft
    
    Allows editing of:
    - Invoice items
    - Notes
    - Due date
    
    Recalculates totals automatically when items are updated.
    """
    try:
        # Build updates dict
        updates = {}
        
        if request.items is not None:
            updates["items"] = request.items
            
            # Recalculate totals
            subtotal = sum(item.get("total", 0) for item in request.items)
            tax_amount = subtotal * 0.16  # 16% VAT
            total_amount = subtotal + tax_amount
            
            updates["subtotal"] = subtotal
            updates["tax_amount"] = tax_amount
            updates["total_amount"] = total_amount
        
        if request.notes is not None:
            updates["notes"] = request.notes
        
        if request.due_date is not None:
            updates["due_date"] = request.due_date
        
        # Update the draft
        success = await service.update_draft(draft_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Draft not found or update failed")
        
        # Return updated draft
        draft = await service.get_draft(draft_id)
        draft["draft_id"] = draft.get("_id")
        return draft
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update draft: {str(e)}")


@router.delete("/drafts/{draft_id}")
async def delete_draft(
    draft_id: str,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """Delete an invoice draft"""
    try:
        success = await service.delete_draft(draft_id)
        if not success:
            raise HTTPException(status_code=404, detail="Draft not found")
        
        return {"message": "Draft deleted successfully", "draft_id": draft_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete draft: {str(e)}")


@router.post("/drafts/{draft_id}/convert")
async def convert_draft_to_invoice(
    draft_id: str,
    service: AIInvoiceService = Depends(get_ai_invoice_service)
):
    """
    Convert a draft to an actual invoice
    
    This will:
    1. Create a new invoice with a unique invoice ID
    2. Update customer financial totals
    3. Delete the draft
    
    Returns the new invoice ID.
    """
    try:
        invoice_id = await service.convert_draft_to_invoice(draft_id)
        
        return {
            "message": "Draft converted to invoice successfully",
            "invoice_id": invoice_id,
            "draft_id": draft_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert draft: {str(e)}")
