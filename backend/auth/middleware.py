"""
JWT middleware and authentication dependencies
"""
from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from .service import AuthService
from .models import User, UserRole, TokenData

logger = logging.getLogger("financial-agent.auth.middleware")

class JWTBearer(HTTPBearer):
    """JWT Bearer token authentication"""
    
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
            
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token or expired token"
                )
            
            return credentials
        else:
            return None
    
    def verify_jwt(self, token: str) -> bool:
        """Verify JWT token format"""
        try:
            # Basic token format validation
            parts = token.split('.')
            return len(parts) == 3
        except Exception:
            return False

# Dependency injection instances
security = JWTBearer()

# Global auth service instance
_auth_service: Optional[AuthService] = None

async def get_auth_service() -> AuthService:
    """Get initialized auth service instance"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
        await _auth_service.initialize()
    return _auth_service

def get_auth_service(request: Request) -> AuthService:
    """Get authentication service instance"""
    # Get database from app state
    db = request.app.state.db if hasattr(request.app.state, 'db') else None
    if not db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection not available"
        )
    return AuthService(db)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Get current authenticated user"""
    try:
        # Verify token and get token data
        token_data: TokenData = auth_service.verify_token(credentials.credentials)
        
        # Check if this is an access token
        if token_data.type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user from database
        user = await auth_service.get_user_by_id(token_data.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

def require_role(required_roles: list[UserRole]):
    """Dependency to require specific user roles"""
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {[role.value for role in required_roles]}"
            )
        return current_user
    
    return role_checker

# Convenience functions for common role requirements
def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Require owner role"""
    return require_role([UserRole.OWNER])(current_user)

def require_owner_or_accountant(current_user: User = Depends(get_current_user)) -> User:
    """Require owner or accountant role"""
    return require_role([UserRole.OWNER, UserRole.ACCOUNTANT])(current_user)

def require_any_role(current_user: User = Depends(get_current_user)) -> User:
    """Require any authenticated user"""
    return current_user

# Optional authentication (for public endpoints with optional auth)
async def get_current_user_optional(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        token_data: TokenData = auth_service.verify_token(token)
        
        if token_data.type != "access":
            return None
        
        user = await auth_service.get_user_by_id(token_data.user_id)
        if not user or not user.is_active:
            return None
        
        return user
        
    except Exception:
        # Silently fail for optional authentication
        return None

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers (common in production behind proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    """Get user agent from request"""
    return request.headers.get("User-Agent", "unknown")