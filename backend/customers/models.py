"""
Customer data models and schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class Address(BaseModel):
    """Address information"""
    street: str = ""
    city: str = "Nairobi"
    postal_code: str = "00100"
    country: str = "Kenya"


class AIPreferences(BaseModel):
    """AI invoice generation preferences"""
    invoice_template: str = "professional"  # professional, simple, detailed
    language: str = "english"  # english, swahili
    include_tax: bool = True
    default_currency: str = "KES"


class CustomerBase(BaseModel):
    """Base customer model"""
    name: str = Field(..., min_length=1, max_length=200)
    email: EmailStr
    phone: str = Field(..., pattern=r"^254\d{9}$")  # Kenyan phone format
    secondary_email: Optional[EmailStr] = None
    secondary_phone: Optional[str] = None
    
    address: Address = Field(default_factory=Address)
    business_type: str = "general"
    tax_id: Optional[str] = None
    
    preferred_payment_method: str = "mpesa"  # mpesa, bank, cash
    payment_terms: str = "net_30"  # net_15, net_30, net_60
    credit_limit: Optional[float] = None
    
    auto_send_invoices: bool = False
    send_reminders: bool = True
    
    ai_preferences: AIPreferences = Field(default_factory=AIPreferences)
    notes: str = ""
    tags: List[str] = Field(default_factory=list)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating a customer (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r"^254\d{9}$")
    secondary_email: Optional[EmailStr] = None
    secondary_phone: Optional[str] = None
    
    address: Optional[Address] = None
    business_type: Optional[str] = None
    tax_id: Optional[str] = None
    
    preferred_payment_method: Optional[str] = None
    payment_terms: Optional[str] = None
    credit_limit: Optional[float] = None
    
    status: Optional[str] = None  # active, inactive, suspended
    auto_send_invoices: Optional[bool] = None
    send_reminders: Optional[bool] = None
    
    ai_preferences: Optional[AIPreferences] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class CustomerFinancialSummary(BaseModel):
    """Financial summary for a customer"""
    total_invoices: int
    total_billed: float
    total_paid: float
    outstanding_balance: float
    average_payment_days: Optional[float] = None
    payment_score: Optional[float] = None


class Customer(CustomerBase):
    """Full customer model with computed fields"""
    customer_id: str
    status: str = "active"  # active, inactive, suspended
    payment_status: str = "good"  # good, warning, overdue
    
    # Financial summary
    total_invoices: int = 0
    total_billed: float = 0.0
    total_paid: float = 0.0
    outstanding_balance: float = 0.0
    
    # Metadata
    created_at: datetime
    updated_at: datetime
    last_invoice_date: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "customer_id": "CUST-0001",
                "name": "Tech Solutions Ltd",
                "email": "info@techsolutions.com",
                "phone": "254722123456",
                "address": {
                    "street": "123 Kimathi Street",
                    "city": "Nairobi",
                    "postal_code": "00100",
                    "country": "Kenya"
                },
                "business_type": "technology",
                "total_invoices": 45,
                "total_billed": 2500000.00,
                "total_paid": 2100000.00,
                "outstanding_balance": 400000.00,
                "status": "active",
                "payment_status": "good"
            }
        }


class CustomerListItem(BaseModel):
    """Simplified customer model for list views"""
    customer_id: str
    name: str
    email: EmailStr
    phone: str
    total_invoices: int
    outstanding_balance: float
    payment_status: str
    status: str
    last_invoice_date: Optional[datetime] = None


class CustomerStats(BaseModel):
    """Overall customer statistics"""
    total_customers: int
    active_customers: int
    inactive_customers: int
    total_outstanding: float
    customers_with_overdue: int
    average_outstanding: float
    top_customers: List[dict]  # Top 5 by revenue
