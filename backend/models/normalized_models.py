"""
Pydantic Models for Normalized MongoDB Schema

These models define the structure for the normalized database schema.
Use these models with FastAPI and Motor (async MongoDB driver).

Based on: docs/MONGODB_NORMALIZATION_ANALYSIS.md
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId


# Custom type for MongoDB ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# ============================================================================
# ENUMS
# ============================================================================

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    VIEWER = "viewer"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PARTIAL = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    INITIATED = "initiated"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class ReconciliationStatus(str, Enum):
    PENDING = "pending"
    MATCHED = "matched"
    PARTIAL = "partial"
    UNMATCHED = "unmatched"
    NEEDS_REVIEW = "needs_review"


class PaymentGateway(str, Enum):
    MPESA = "mpesa"
    AIRTEL = "airtel"
    BANK = "bank"
    CASH = "cash"
    OTHER = "other"


# ============================================================================
# EMBEDDED SCHEMAS (used within documents)
# ============================================================================

class Address(BaseModel):
    """Embedded address schema"""
    street: str = ""
    city: str = "Nairobi"
    postal_code: str = "00100"
    country: str = "Kenya"


class AIPreferences(BaseModel):
    """Embedded AI preferences schema"""
    invoice_template: str = "professional"
    language: str = "english"
    include_tax: bool = True
    default_currency: str = "KES"


class ProductSnapshot(BaseModel):
    """Snapshot of product at time of invoice creation"""
    product_id: Optional[str] = None
    name: Optional[str] = None
    sku: Optional[str] = None
    category: Optional[str] = None
    standard_price: Optional[float] = None


# ============================================================================
# USER MODELS
# ============================================================================

class User(BaseModel):
    """User model (normalized)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    email: EmailStr
    password_hash: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    status: UserStatus = UserStatus.ACTIVE
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    custom_permissions: List[str] = Field(default_factory=list)
    
    # Security
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class UserSession(BaseModel):
    """User session model (NEW)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: PyObjectId
    token_hash: str
    ip_address: str
    user_agent: str
    device_type: str = "desktop"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    revoked_reason: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class AuditLog(BaseModel):
    """Audit log model (NEW)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: Optional[PyObjectId] = None
    action: str
    resource_type: str
    resource_id: Optional[PyObjectId] = None
    
    changes: Dict[str, Any] = {}
    
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[PyObjectId] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    success: bool = True
    error_message: Optional[str] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# CUSTOMER MODELS
# ============================================================================

class Customer(BaseModel):
    """Customer model (normalized)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    customer_id: str
    
    name: str
    email: EmailStr
    phone: str
    secondary_email: Optional[EmailStr] = None
    secondary_phone: Optional[str] = None
    
    address: Address = Field(default_factory=Address)
    
    business_type: str = "general"
    tax_id: Optional[str] = None
    
    preferred_payment_method: str = "mpesa"
    payment_terms: str = "net_30"
    credit_limit: Optional[float] = None
    
    auto_send_invoices: bool = False
    send_reminders: bool = True
    
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences)
    
    status: str = "active"
    
    notes: str = ""
    tags: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# PRODUCT MODELS
# ============================================================================

class Product(BaseModel):
    """Product/Service model (NEW)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    product_id: str
    
    name: str
    description: str = ""
    sku: Optional[str] = None
    category: str = "general"
    
    unit_price: float
    currency: str = "KES"
    tax_rate: float = 0.16
    
    is_service: bool = False
    track_inventory: bool = False
    current_stock: Optional[int] = None
    reorder_level: Optional[int] = None
    
    status: str = "active"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# INVOICE MODELS
# ============================================================================

class Invoice(BaseModel):
    """Invoice model (normalized)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    invoice_number: str
    
    # ✅ REFERENCE to customer (not embedded)
    customer_id: PyObjectId
    
    date_issued: datetime = Field(default_factory=datetime.utcnow)
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
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    sent_at: Optional[datetime] = None
    sent_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class InvoiceItem(BaseModel):
    """Invoice item model (NEW - separated from invoice)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    invoice_id: PyObjectId
    product_id: Optional[PyObjectId] = None
    
    line_number: int
    description: str
    quantity: float
    unit_price: float
    
    subtotal: float
    discount_rate: float = 0
    discount_amount: float = 0
    tax_rate: float = 0.16
    tax_amount: float = 0
    total: float
    
    # ✅ SNAPSHOT of product at time of invoice
    product_snapshot: Optional[ProductSnapshot] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# PAYMENT MODELS
# ============================================================================

class Payment(BaseModel):
    """Payment model (unified & normalized)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    payment_id: str
    
    amount: float
    currency: str = "KES"
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    
    gateway: PaymentGateway
    gateway_reference: Optional[str] = None
    
    customer_id: Optional[PyObjectId] = None
    payer_name: Optional[str] = None
    payer_phone: Optional[str] = None
    payer_email: Optional[EmailStr] = None
    
    invoice_id: Optional[PyObjectId] = None
    allocated_amount: Optional[float] = None
    
    status: PaymentStatus = PaymentStatus.INITIATED
    
    reconciliation_status: ReconciliationStatus = ReconciliationStatus.PENDING
    reconciliation_date: Optional[datetime] = None
    reconciliation_confidence: Optional[float] = None
    reconciliation_method: Optional[str] = None
    reconciliation_notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class PaymentGatewayData(BaseModel):
    """Payment gateway-specific data (NEW)"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    payment_id: PyObjectId
    gateway: PaymentGateway
    
    gateway_data: Dict[str, Any] = {}
    raw_request: Dict[str, Any] = {}
    raw_response: Dict[str, Any] = {}
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# RECEIPT MODELS
# ============================================================================

class Receipt(BaseModel):
    """Receipt model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    receipt_number: str
    
    payment_id: Optional[PyObjectId] = None
    invoice_id: Optional[PyObjectId] = None
    customer_id: Optional[PyObjectId] = None
    
    amount: float
    payment_method: str
    receipt_date: datetime = Field(default_factory=datetime.utcnow)
    
    pdf_url: Optional[str] = None
    
    status: str = "issued"
    
    sent_to_email: Optional[EmailStr] = None
    sent_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# OCR MODELS
# ============================================================================

class OCRResult(BaseModel):
    """OCR result model"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    
    image_path: str
    file_hash: Optional[str] = None
    
    engine: str
    status: str
    confidence: float
    processing_time: float
    
    extracted_text: str
    structured_data: Dict[str, Any] = {}
    
    created_invoice_id: Optional[PyObjectId] = None
    created_expense_id: Optional[PyObjectId] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[PyObjectId] = None
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_invoice_with_details(db, invoice_id: ObjectId):
    """
    Get invoice with customer and items populated
    
    Example usage:
        invoice = await get_invoice_with_details(db, ObjectId("..."))
        print(invoice["customer"]["name"])
        print(invoice["items"][0]["description"])
    """
    pipeline = [
        {"$match": {"_id": invoice_id}},
        {
            "$lookup": {
                "from": "customers",
                "localField": "customer_id",
                "foreignField": "_id",
                "as": "customer"
            }
        },
        {"$unwind": "$customer"},
        {
            "$lookup": {
                "from": "invoice_items",
                "localField": "_id",
                "foreignField": "invoice_id",
                "as": "items"
            }
        },
        {
            "$sort": {"items.line_number": 1}
        }
    ]
    
    result = await db.invoices.aggregate(pipeline).to_list(1)
    return result[0] if result else None


async def get_customer_with_stats(db, customer_id: ObjectId):
    """
    Get customer with computed financial statistics
    
    Example usage:
        customer = await get_customer_with_stats(db, ObjectId("..."))
        print(f"Total invoices: {customer['total_invoices']}")
        print(f"Outstanding: {customer['outstanding_balance']}")
    """
    pipeline = [
        {"$match": {"_id": customer_id}},
        {
            "$lookup": {
                "from": "invoices",
                "localField": "_id",
                "foreignField": "customer_id",
                "as": "invoices"
            }
        },
        {
            "$addFields": {
                "total_invoices": {"$size": "$invoices"},
                "total_billed": {"$sum": "$invoices.total"},
                "total_paid": {"$sum": "$invoices.amount_paid"},
                "outstanding_balance": {"$sum": "$invoices.balance"}
            }
        },
        {"$project": {"invoices": 0}}
    ]
    
    result = await db.customers.aggregate(pipeline).to_list(1)
    return result[0] if result else None


async def create_invoice_with_items(db, invoice_data: dict, items_data: list):
    """
    Create invoice and items atomically using transactions
    
    Example usage:
        invoice_data = {
            "invoice_number": "INV-001",
            "customer_id": ObjectId("..."),
            "total": 5800
        }
        items_data = [
            {"description": "Item 1", "amount": 5000},
            {"description": "Item 2", "amount": 800}
        ]
        
        invoice_id = await create_invoice_with_items(db, invoice_data, items_data)
    """
    async with await db.client.start_session() as session:
        async with session.start_transaction():
            # Insert invoice
            invoice_result = await db.invoices.insert_one(
                invoice_data,
                session=session
            )
            invoice_id = invoice_result.inserted_id
            
            # Add invoice_id to all items
            for item in items_data:
                item["invoice_id"] = invoice_id
            
            # Insert items
            await db.invoice_items.insert_many(
                items_data,
                session=session
            )
            
            return invoice_id


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
Example 1: Create a customer

customer = Customer(
    customer_id="CUST-0001",
    name="Acme Corp",
    email="acme@example.com",
    phone="254712345678"
)
await db.customers.insert_one(customer.dict(by_alias=True, exclude_unset=True))


Example 2: Create invoice with items

invoice = Invoice(
    invoice_number="INV-2025-10-0001",
    customer_id=ObjectId("..."),
    total=5800
)

items = [
    InvoiceItem(
        invoice_id=invoice_id,
        line_number=1,
        description="Office Supplies",
        quantity=5,
        unit_price=1000,
        total=5000
    )
]

invoice_id = await create_invoice_with_items(
    db,
    invoice.dict(by_alias=True, exclude_unset=True),
    [item.dict(by_alias=True, exclude_unset=True) for item in items]
)


Example 3: Query invoice with details

invoice = await get_invoice_with_details(db, ObjectId("..."))
print(f"Customer: {invoice['customer']['name']}")
print(f"Items: {len(invoice['items'])}")


Example 4: Get customer statistics

customer = await get_customer_with_stats(db, ObjectId("..."))
print(f"Outstanding: KES {customer['outstanding_balance']:,.2f}")
"""
