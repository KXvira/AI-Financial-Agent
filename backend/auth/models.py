"""
Authentication models for user management and JWT tokens
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from enum import Enum

class UserRole(str, Enum):
    """User roles for role-based access control"""
    ADMIN = "admin"          # System administrator - full access
    MANAGER = "manager"      # Manager - can manage users and view all data
    OWNER = "owner"          # Business owner - full access to own company
    ACCOUNTANT = "accountant" # Accountant - create/edit financial records
    VIEWER = "viewer"        # Viewer - read-only access

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    company_name: str = Field(..., min_length=2, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+254[0-9]{9}$')
    role: UserRole = UserRole.OWNER
    is_active: bool = True

class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    class Config:
        schema_extra = {
            "example": {
                "email": "owner@company.co.ke",
                "password": "SecurePass123!",
                "confirm_password": "SecurePass123!",
                "company_name": "SME Solutions Ltd",
                "phone_number": "+254712345678",
                "role": "owner"
            }
        }

class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "owner@company.co.ke",
                "password": "SecurePass123!"
            }
        }

class UserUpdate(BaseModel):
    """User update model for admin operations"""
    company_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "Updated Company Name",
                "role": "accountant",
                "status": "active"
            }
        }

class User(UserBase):
    """Complete user model"""
    id: Optional[str] = Field(None, alias="_id")
    password_hash: str
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    email_verified: bool = False
    phone_verified: bool = False
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


# Role-based permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # All permissions - system administrator
    UserRole.OWNER: ["*"],  # All permissions - business owner (same as admin)
    UserRole.MANAGER: [
        "users.view", "users.create", "users.edit", "users.delete",
        "reports.view", "reports.generate", "reports.schedule",
        "invoices.view", "invoices.create", "invoices.edit", "invoices.delete",
        "receipts.view", "receipts.create", "receipts.edit", "receipts.delete",
        "payments.view", "payments.create", "payments.edit", "payments.delete",
        "customers.view", "customers.create", "customers.edit", "customers.delete",
        "dashboard.view", "settings.view", "settings.edit",
        "activity_logs.view", "audit.view", "system.view"
    ],
    UserRole.ACCOUNTANT: [
        "invoices.create", "invoices.edit", "invoices.view",
        "receipts.create", "receipts.edit", "receipts.view",
        "payments.create", "payments.view", "payments.edit",
        "customers.view", "customers.edit",
        "reports.view", "reports.generate",
        "dashboard.view"
    ],
    UserRole.VIEWER: [
        "dashboard.view",
        "reports.view",
        "invoices.view",
        "receipts.view",
        "payments.view",
        "customers.view"
    ]
}

class UserProfile(BaseModel):
    """User profile for responses"""
    id: str
    email: str
    company_name: str
    phone_number: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login: Optional[datetime]
    email_verified: bool
    phone_verified: bool

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserProfile

class TokenData(BaseModel):
    """Token data for JWT payload"""
    user_id: str
    email: str
    role: UserRole
    exp: datetime
    iat: datetime
    type: str  # "access" or "refresh"

class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

class PasswordChange(BaseModel):
    """Password change for authenticated users"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

class AuditLog(BaseModel):
    """Audit log for authentication events"""
    id: Optional[str] = Field(None, alias="_id")
    user_id: Optional[str] = None
    email: Optional[str] = None
    action: str  # login, logout, register, password_change, etc.
    ip_address: str
    user_agent: str
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool
    failure_reason: Optional[str] = None
    metadata: dict = {}
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True