"""
Authentication & Authorization Module
Implements JWT-based authentication for API endpoints
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
from pydantic import BaseModel

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Models
class TokenData(BaseModel):
    user_id: str
    username: str
    email: str
    role: str = "user"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class User(BaseModel):
    user_id: str
    username: str
    email: str
    role: str = "user"
    is_active: bool = True

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

# JWT utilities
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        TokenData with user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        username: str = payload.get("username")
        email: str = payload.get("email")
        role: str = payload.get("role", "user")
        
        if user_id is None or username is None:
            raise credentials_exception
        
        return TokenData(
            user_id=user_id,
            username=username,
            email=email,
            role=role
        )
    except JWTError:
        raise credentials_exception

# Dependency functions
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Dependency for protected endpoints
    """
    token = credentials.credentials
    token_data = decode_access_token(token)
    
    return User(
        user_id=token_data.user_id,
        username=token_data.username,
        email=token_data.email,
        role=token_data.role
    )

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user
    
    Dependency that checks if user is active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

# Role-based access control
def require_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_role("admin"))])
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{required_role}' required"
            )
        return current_user
    
    return role_checker

# API Key authentication (alternative/additional)
async def verify_api_key(x_api_key: str = Header(None)) -> bool:
    """
    Verify API key from header
    
    Alternative authentication method for service-to-service communication
    """
    valid_api_keys = os.getenv("API_KEYS", "").split(",")
    
    if not x_api_key or x_api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    return True

# Rate limiting decorator
from functools import wraps
from time import time

rate_limit_store: Dict[str, list] = {}

def rate_limit(max_requests: int, window_seconds: int):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_seconds: Time window in seconds
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user identifier (from request)
            user_id = kwargs.get("current_user", User(user_id="anonymous", username="anonymous", email="")).user_id
            
            current_time = time()
            
            # Clean old requests
            if user_id in rate_limit_store:
                rate_limit_store[user_id] = [
                    req_time for req_time in rate_limit_store[user_id]
                    if current_time - req_time < window_seconds
                ]
            else:
                rate_limit_store[user_id] = []
            
            # Check rate limit
            if len(rate_limit_store[user_id]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window_seconds} seconds"
                )
            
            # Add current request
            rate_limit_store[user_id].append(current_time)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator
