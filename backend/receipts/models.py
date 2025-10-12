"""
Receipt Data Models

Defines Pydantic models for receipt generation, storage, and management.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReceiptType(str, Enum):
    """Receipt type enumeration"""
    PAYMENT = "payment"
    INVOICE = "invoice"
    REFUND = "refund"
    EXPENSE = "expense"
    PARTIAL_PAYMENT = "partial_payment"


class ReceiptStatus(str, Enum):
    """Receipt status enumeration"""
    DRAFT = "draft"
    GENERATED = "generated"
    SENT = "sent"
    VIEWED = "viewed"
    DOWNLOADED = "downloaded"
    VOIDED = "voided"


class PaymentMethod(str, Enum):
    """Payment method enumeration"""
    MPESA = "mpesa"
    BANK_TRANSFER = "bank_transfer"
    CASH = "cash"
    CARD = "card"
    OTHER = "other"


class TaxBreakdown(BaseModel):
    """Tax breakdown for receipt"""
    subtotal: float = Field(..., description="Amount before tax")
    vat_rate: float = Field(default=0.16, description="VAT rate (default 16%)")
    vat_amount: float = Field(..., description="VAT amount")
    total: float = Field(..., description="Total amount including VAT")


class CustomerInfo(BaseModel):
    """Customer information for receipt"""
    customer_id: Optional[str] = None
    name: str = Field(..., description="Customer name")
    email: Optional[str] = None
    phone: Optional[str] = None
    kra_pin: Optional[str] = Field(None, description="Customer KRA PIN")
    address: Optional[str] = None


class LineItem(BaseModel):
    """Individual line item on receipt"""
    description: str = Field(..., description="Item description")
    quantity: float = Field(default=1.0, description="Quantity")
    unit_price: float = Field(..., description="Unit price")
    total: float = Field(..., description="Total price")
    tax_rate: float = Field(default=0.16, description="Tax rate")


class ReceiptMetadata(BaseModel):
    """Additional metadata for receipt"""
    invoice_id: Optional[str] = None
    payment_id: Optional[str] = None
    transaction_id: Optional[str] = None
    mpesa_receipt: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)


class Receipt(BaseModel):
    """Main receipt model"""
    id: Optional[str] = Field(None, alias="_id")
    receipt_number: str = Field(..., description="Unique receipt number (e.g., RCP-2025-0001)")
    receipt_type: ReceiptType
    status: ReceiptStatus = ReceiptStatus.DRAFT
    
    # Customer information
    customer: CustomerInfo
    
    # Transaction details
    payment_method: PaymentMethod
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Financial details
    line_items: List[LineItem] = Field(default_factory=list)
    tax_breakdown: TaxBreakdown
    
    # Business information
    business_name: str = Field(default="FinGuard Business")
    business_kra_pin: Optional[str] = Field(None, description="Business KRA PIN")
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    
    # PDF and QR code
    pdf_path: Optional[str] = None
    qr_code_data: Optional[str] = None
    
    # Metadata
    metadata: ReceiptMetadata = Field(default_factory=ReceiptMetadata)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    generated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    voided_at: Optional[datetime] = None
    
    # Audit
    created_by: Optional[str] = None
    voided_by: Optional[str] = None
    void_reason: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "receipt_number": "RCP-2025-0001",
                "receipt_type": "payment",
                "customer": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "0712345678"
                },
                "payment_method": "mpesa",
                "tax_breakdown": {
                    "subtotal": 10000.00,
                    "vat_rate": 0.16,
                    "vat_amount": 1600.00,
                    "total": 11600.00
                }
            }
        }


class ReceiptGenerateRequest(BaseModel):
    """Request model for generating a receipt"""
    receipt_type: ReceiptType
    customer: CustomerInfo
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    
    # Financial details
    amount: float = Field(..., description="Total amount (including VAT)")
    description: Optional[str] = Field(None, description="Payment description")
    line_items: Optional[List[LineItem]] = None
    include_vat: bool = Field(default=True, description="Whether to calculate VAT")
    
    # Business information (optional overrides)
    business_name: Optional[str] = None
    business_kra_pin: Optional[str] = None
    
    # Metadata
    metadata: Optional[ReceiptMetadata] = None
    
    # Options
    send_email: bool = Field(default=False, description="Send receipt via email")
    template_id: Optional[str] = Field(None, description="Custom template ID")


class ReceiptTemplate(BaseModel):
    """Receipt template model"""
    id: Optional[str] = Field(None, alias="_id")
    name: str = Field(..., description="Template name")
    description: Optional[str] = None
    
    # Design elements
    logo_path: Optional[str] = None
    primary_color: str = Field(default="#1a56db", description="Primary color hex")
    secondary_color: str = Field(default="#e5e7eb", description="Secondary color hex")
    font_family: str = Field(default="Helvetica", description="Font family")
    
    # Layout options
    show_logo: bool = True
    show_qr_code: bool = True
    show_tax_breakdown: bool = True
    show_line_items: bool = True
    
    # Business defaults
    business_name: Optional[str] = None
    business_kra_pin: Optional[str] = None
    business_address: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[str] = None
    
    # Footer
    footer_text: Optional[str] = Field(
        default="Thank you for your business!",
        description="Footer text"
    )
    terms_and_conditions: Optional[str] = None
    
    # Metadata
    is_default: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ReceiptSequence(BaseModel):
    """Receipt numbering sequence model"""
    id: Optional[str] = Field(None, alias="_id")
    year: int = Field(..., description="Year for sequence")
    prefix: str = Field(default="RCP", description="Receipt prefix")
    current_number: int = Field(default=0, description="Current sequence number")
    last_receipt_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ReceiptAuditLog(BaseModel):
    """Audit log for receipt actions"""
    id: Optional[str] = Field(None, alias="_id")
    receipt_id: str = Field(..., description="Receipt ID")
    receipt_number: str = Field(..., description="Receipt number")
    action: str = Field(..., description="Action performed (viewed, downloaded, sent, voided)")
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True


class ReceiptListResponse(BaseModel):
    """Response model for listing receipts"""
    receipts: List[Receipt]
    total: int
    page: int
    page_size: int


class ReceiptStatistics(BaseModel):
    """Receipt statistics model"""
    total_receipts: int
    receipts_by_type: Dict[str, int]
    receipts_by_status: Dict[str, int]
    receipts_by_month: Dict[str, int]
    total_amount: float
    average_amount: float
    receipts_sent: int
    receipts_voided: int
