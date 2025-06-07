"""
Database schemas for MongoDB models
"""
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TransactionStatus(str, Enum):
    """Transaction status enum"""
    INITIATED = "initiated"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    
class ReconciliationStatus(str, Enum):
    """Reconciliation status enum"""
    PENDING = "pending"
    MATCHED = "matched"
    PARTIAL = "partial_match"
    UNMATCHED = "unmatched"
    NEEDS_REVIEW = "needs_review"

class PaymentGateway(str, Enum):
    """Payment gateway enum"""
    MPESA = "mpesa"
    AIRTEL = "airtel"
    BANK = "bank"
    OTHER = "other"

class InvoiceStatus(str, Enum):
    """Invoice status enum"""
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class MpesaTransactionSchema(BaseModel):
    """Schema for storing M-Pesa transactions in MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    reference: str
    gateway: str = "mpesa"
    amount: float
    phone_number: str
    customer_name: Optional[str] = None
    status: str
    gateway_reference: Optional[str] = None  # M-Pesa receipt number
    gateway_data: Dict[str, Any] = {}  # Raw data from gateway
    request_timestamp: datetime
    completion_timestamp: Optional[datetime] = None
    reconciliation_status: str = "pending"
    matched_invoice_id: Optional[str] = None
    confidence_score: Optional[float] = None
    needs_review: bool = False
    review_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class InvoiceItemSchema(BaseModel):
    """Schema for invoice item in MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    description: str
    quantity: float
    unit_price: float
    amount: float
    tax_rate: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_rate: Optional[float] = None
    discount_amount: Optional[float] = None
    metadata: Dict[str, Any] = {}

class CustomerSchema(BaseModel):
    """Schema for customer in MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "Kenya"
    metadata: Dict[str, Any] = {}

class InvoiceSchema(BaseModel):
    """Schema for invoice in MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    invoice_number: str
    customer: Dict[str, Any]  # Customer data
    items: List[Dict[str, Any]] = []  # Invoice items
    date_issued: datetime
    due_date: Optional[datetime] = None
    subtotal: float
    tax_total: float = 0
    discount_total: float = 0
    total: float
    amount_paid: float = 0
    balance: float = 0
    status: str = "draft"
    notes: Optional[str] = None
    terms: Optional[str] = None
    payment_reference: Optional[str] = None
    payment_gateway: Optional[str] = None
    payment_transactions: List[str] = []  # Transaction IDs
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True

class ReconciliationLogSchema(BaseModel):
    """Schema for reconciliation logs in MongoDB"""
    id: Optional[str] = Field(None, alias="_id")
    payment_data: Dict[str, Any]
    result: Dict[str, Any]
    timestamp: datetime
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
