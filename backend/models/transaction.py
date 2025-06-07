"""
Transaction models for M-Pesa payments and reconciliation
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field

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

class MpesaRequest(BaseModel):
    """M-Pesa STK Push request data"""
    merchant_request_id: str
    checkout_request_id: str
    response_code: str
    response_description: str
    customer_message: str
    phone_number: str
    amount: float
    reference: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
class MpesaCallback(BaseModel):
    """M-Pesa callback data"""
    merchant_request_id: str
    checkout_request_id: str
    result_code: str
    result_desc: str
    amount: Optional[float] = None
    mpesa_receipt_number: Optional[str] = None
    transaction_date: Optional[str] = None
    phone_number: Optional[str] = None
    
class Transaction(BaseModel):
    """Transaction model for all payment types"""
    id: Optional[str] = None
    reference: str
    gateway: PaymentGateway
    amount: float
    phone_number: str
    customer_name: Optional[str] = None
    status: TransactionStatus = TransactionStatus.INITIATED
    gateway_reference: Optional[str] = None  # e.g., M-Pesa receipt number
    gateway_data: Dict[str, Any] = {}  # Raw data from gateway
    request_timestamp: datetime = Field(default_factory=datetime.now)
    completion_timestamp: Optional[datetime] = None
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.PENDING
    matched_invoice_id: Optional[str] = None
    confidence_score: Optional[float] = None
    needs_review: bool = False
    review_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True
