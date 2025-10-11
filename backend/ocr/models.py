"""
OCR Data Models for Receipt Processing and Expense Management
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
import uuid

class ProcessingStatus(str, Enum):
    """Receipt processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_REVIEW = "needs_review"

class ExpenseCategory(str, Enum):
    """Kenyan SME expense categories"""
    OFFICE_SUPPLIES = "office_supplies"
    TRANSPORT = "transport"
    MEALS = "meals"
    UTILITIES = "utilities"
    RENT = "rent"
    FUEL = "fuel"
    MAINTENANCE = "maintenance"
    MARKETING = "marketing"
    TELECOMMUNICATIONS = "telecommunications"
    PROFESSIONAL_SERVICES = "professional_services"
    EQUIPMENT = "equipment"
    INVENTORY = "inventory"
    INSURANCE = "insurance"
    TAXES = "taxes"
    BANKING = "banking"
    TRAVEL = "travel"
    TRAINING = "training"
    LICENSES = "licenses"
    RAW_MATERIALS = "raw_materials"
    OTHER = "other"

class PaymentMethod(str, Enum):
    """Payment methods"""
    CASH = "cash"
    MPESA = "mpesa"
    BANK_TRANSFER = "bank_transfer"
    CREDIT_CARD = "credit_card"
    CHEQUE = "cheque"
    OTHER = "other"

class VerificationStatus(str, Enum):
    """Human verification status"""
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    FLAGGED = "flagged"
    CORRECTED = "corrected"

# Base Models
class OCRResult(BaseModel):
    """OCR text extraction result"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    raw_text: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    language_detected: str = "en"
    processing_time: float
    preprocessed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)

class ExpenseItem(BaseModel):
    """Individual expense item from receipt"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: float
    category: Optional[ExpenseCategory] = None
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)

class VendorInfo(BaseModel):
    """Vendor/merchant information"""
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    tax_number: Optional[str] = None  # KRA PIN for Kenyan businesses
    confidence_score: float = Field(ge=0.0, le=1.0, default=0.0)

class ReceiptBase(BaseModel):
    """Base receipt model"""
    vendor: VendorInfo = Field(default_factory=VendorInfo)
    transaction_date: Optional[datetime] = None
    receipt_number: Optional[str] = None
    total_amount: float = Field(ge=0.0)
    currency: str = Field(default="KES")
    tax_amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    category: ExpenseCategory = ExpenseCategory.OTHER
    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    """Receipt creation model"""
    pass

class Receipt(ReceiptBase):
    """Complete receipt model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    file_path: str
    original_filename: str
    file_size: int
    mime_type: str
    
    # OCR processing
    ocr_result: Optional[OCRResult] = None
    items: List[ExpenseItem] = Field(default_factory=list)
    
    # AI processing
    ai_extracted_data: Dict[str, Any] = Field(default_factory=dict)
    classification_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    
    # Status tracking
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None

    @field_validator('total_amount')
    @classmethod
    def validate_positive_amount(cls, v):
        if v < 0:
            raise ValueError('Total amount must be positive')
        return v

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        allowed_currencies = ['KES', 'USD', 'EUR', 'GBP']
        if v not in allowed_currencies:
            raise ValueError(f'Currency must be one of {allowed_currencies}')
        return v

class ReceiptUpdate(BaseModel):
    """Receipt update model"""
    vendor: Optional[VendorInfo] = None
    transaction_date: Optional[datetime] = None
    receipt_number: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    tax_amount: Optional[float] = None
    payment_method: Optional[PaymentMethod] = None
    category: Optional[ExpenseCategory] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None

class ExpenseFilter(BaseModel):
    """Expense filtering model"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[ExpenseCategory] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    vendor_name: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    verification_status: Optional[VerificationStatus] = None
    tags: Optional[List[str]] = None

class ExpenseSummary(BaseModel):
    """Expense summary statistics"""
    total_amount: float
    total_count: int
    category_breakdown: Dict[str, float]
    monthly_trend: List[Dict[str, Any]]
    top_vendors: List[Dict[str, Any]]
    average_expense: float
    currency: str = "KES"

class OCRConfig(BaseModel):
    """OCR processing configuration"""
    language: str = "eng"
    enable_preprocessing: bool = True
    confidence_threshold: float = 0.5
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: List[str] = Field(default_factory=lambda: ['.jpg', '.jpeg', '.png', '.pdf'])
    output_format: str = "json"

class FileUploadResponse(BaseModel):
    """File upload response"""
    receipt_id: str
    filename: str
    file_size: int
    upload_status: str
    message: str
    processing_status: ProcessingStatus