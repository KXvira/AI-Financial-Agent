"""
Authentication module for JWT-based user management
"""

from .models import (
    UserRole, UserStatus, UserBase, UserCreate, UserLogin, UserUpdate,
    User, UserProfile, Token, TokenData, PasswordReset, 
    PasswordChange, AuditLog
)
from .service import AuthService
from .middleware import (
    JWTBearer, get_auth_service, get_current_user, 
    get_current_user_optional, require_role, require_owner,
    require_owner_or_accountant, require_any_role,
    get_client_ip, get_user_agent
)
from .router import router as auth_router

__all__ = [
    # Models
    "UserRole", "UserStatus", "UserBase", "UserCreate", "UserLogin", "UserUpdate",
    "User", "UserProfile", "Token", "TokenData", "PasswordReset",
    "PasswordChange", "AuditLog",
    
    # Service
    "AuthService",
    
    # Middleware
    "JWTBearer", "get_auth_service", "get_current_user", 
    "get_current_user_optional", "require_role", "require_owner",
    "require_owner_or_accountant", "require_any_role",
    "get_client_ip", "get_user_agent",
    
    # Router
    "auth_router"
]