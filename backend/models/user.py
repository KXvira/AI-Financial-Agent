"""
User Models
User authentication and authorization models
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, EmailStr


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"          # Full system access
    MANAGER = "manager"      # Can manage users, view all reports
    ACCOUNTANT = "accountant" # Can create/edit financial records
    VIEWER = "viewer"        # Read-only access


class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


# Permission definitions
ROLE_PERMISSIONS = {
    UserRole.ADMIN: ["*"],  # All permissions
    UserRole.MANAGER: [
        "users.view", "users.create", "users.edit",
        "reports.view", "reports.generate", "reports.schedule",
        "invoices.view", "invoices.edit", "invoices.delete",
        "receipts.view", "receipts.edit", "receipts.delete",
        "payments.view", "payments.edit",
        "customers.view", "customers.edit",
        "dashboard.view", "settings.view",
        "activity_logs.view"
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


class User(BaseModel):
    """User model"""
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    full_name: str
    password_hash: str
    role: UserRole = Field(default=UserRole.VIEWER)
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    # Permissions
    custom_permissions: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    created_by: Optional[str] = None  # User ID of creator
    
    # Session tracking
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    full_name: str
    password: str
    role: UserRole = Field(default=UserRole.VIEWER)
    department: Optional[str] = None
    phone: Optional[str] = None
    custom_permissions: List[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    custom_permissions: Optional[List[str]] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (without sensitive data)"""
    id: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    department: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse


class PasswordReset(BaseModel):
    """Password reset schema"""
    token: str
    new_password: str


class PasswordChange(BaseModel):
    """Password change schema"""
    current_password: str
    new_password: str
