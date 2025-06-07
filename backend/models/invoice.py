"""
Invoice models for reconciliation with payments
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

class InvoiceStatus(str, Enum):
    """Invoice status enum"""
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class InvoiceItem(BaseModel):
    """Invoice item/line model"""
    id: Optional[str] = None
    description: str
    quantity: float
    unit_price: float
    amount: float
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_rate: Optional[float] = None
    discount_amount: Optional[float] = None
    metadata: Dict[str, Any] = {}

class Customer(BaseModel):
    """Customer model"""
    id: Optional[str] = None
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Kenya"
    metadata: Dict[str, Any] = {}

class Invoice(BaseModel):
    """Invoice model"""
    id: Optional[str] = None
    invoice_number: str
    customer: Customer
    items: List[InvoiceItem] = []
    date_issued: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    subtotal: float
    tax_total: float = 0
    discount_total: float = 0
    total: float
    amount_paid: float = 0
    balance: float = 0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    notes: Optional[str] = None
    terms: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_gateway: Optional[str] = None
    payment_transactions: List[str] = []  # Transaction IDs
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
