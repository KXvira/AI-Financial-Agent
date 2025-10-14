"""
Email Service API Router
Endpoints for sending invoices via email
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any

from database.mongodb import get_database
from .service import EmailService

router = APIRouter(prefix="/api/email", tags=["Email"])


# Request/Response Models
class SendInvoiceEmailRequest(BaseModel):
    """Request to send invoice via email"""
    invoice_id: str = Field(..., description="Invoice ID to send")
    recipient_email: EmailStr = Field(..., description="Recipient email address")
    recipient_name: Optional[str] = Field(None, description="Recipient name")
    cc_emails: Optional[List[EmailStr]] = Field(None, description="CC email addresses")
    custom_message: Optional[str] = Field(None, description="Custom message to include")
    attach_pdf: bool = Field(True, description="Attach PDF invoice")
    
    class Config:
        json_schema_extra = {
            "example": {
                "invoice_id": "INV-0001",
                "recipient_email": "customer@example.com",
                "recipient_name": "John Doe",
                "cc_emails": ["accounting@example.com"],
                "custom_message": "Thank you for your business!",
                "attach_pdf": True
            }
        }


class EmailSendResponse(BaseModel):
    """Email send response"""
    success: bool
    message: str
    method: str
    recipient: str
    sent_at: str
    status_code: Optional[int] = None


class EmailHistoryItem(BaseModel):
    """Email history item"""
    invoice_id: str
    recipient: str
    success: bool
    method: str
    sent_at: str
    status_code: Optional[int] = None


# Dependency to get service
def get_email_service():
    """Dependency to get email service"""
    db = get_database()
    return EmailService(db)


# Endpoints
@router.post("/send-invoice", response_model=EmailSendResponse)
async def send_invoice(
    request: SendInvoiceEmailRequest,
    service: EmailService = Depends(get_email_service)
):
    """
    Send an invoice via email with PDF attachment
    
    This endpoint will:
    1. Retrieve the invoice from the database
    2. Generate a professional PDF (if attach_pdf=True)
    3. Create an HTML email with invoice details
    4. Send via SendGrid (or mock if not configured)
    5. Log the send attempt
    
    Note: Requires SENDGRID_API_KEY environment variable for real sending.
    """
    try:
        result = await service.send_invoice_email(
            invoice_id=request.invoice_id,
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            cc_emails=request.cc_emails,
            custom_message=request.custom_message,
            attach_pdf=request.attach_pdf
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.get("/history", response_model=List[EmailHistoryItem])
async def get_email_history(
    invoice_id: Optional[str] = None,
    limit: int = 50,
    service: EmailService = Depends(get_email_service)
):
    """
    Get email send history
    
    Optionally filter by invoice_id to see emails sent for a specific invoice.
    """
    try:
        history = await service.get_email_history(invoice_id=invoice_id, limit=limit)
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/history/{invoice_id}", response_model=List[EmailHistoryItem])
async def get_invoice_email_history(
    invoice_id: str,
    service: EmailService = Depends(get_email_service)
):
    """Get email history for a specific invoice"""
    try:
        history = await service.get_email_history(invoice_id=invoice_id, limit=100)
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/test")
async def test_email_config(service: EmailService = Depends(get_email_service)):
    """
    Test email configuration
    
    Returns information about email service status
    """
    sendgrid_configured = service.sendgrid_client is not None
    
    return {
        "sendgrid_configured": sendgrid_configured,
        "from_email": service.from_email,
        "from_name": service.from_name,
        "mode": "production" if sendgrid_configured else "mock",
        "message": "SendGrid is configured and ready" if sendgrid_configured else "SendGrid not configured. Emails will be mocked."
    }
