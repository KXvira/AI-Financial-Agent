"""
Authentication Router
Handles user authentication, registration, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta
import logging

from .security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_active_user,
    User,
    Token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

logger = logging.getLogger("financial-agent.auth")

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

# Request/Response Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    role: str
    is_active: bool

# Mock user database (replace with real database in production)
users_db = {
    "demo": {
        "user_id": "demo-user-001",
        "username": "demo",
        "email": "demo@example.com",
        "hashed_password": get_password_hash("demo123"),
        "role": "user",
        "is_active": True
    },
    "admin": {
        "user_id": "admin-user-001",
        "username": "admin",
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin",
        "is_active": True
    }
}

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user
    
    - **username**: Unique username
    - **email**: User email address
    - **password**: User password (will be hashed)
    - **full_name**: Optional full name
    """
    # Check if user already exists
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create new user
    user_id = f"user-{len(users_db) + 1:03d}"
    
    users_db[user_data.username] = {
        "user_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "role": "user",
        "is_active": True
    }
    
    logger.info(f"New user registered: {user_data.username}")
    
    return UserResponse(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        role="user",
        is_active=True
    )

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login and receive JWT access token
    
    - **username**: Username
    - **password**: Password
    
    Returns:
    - **access_token**: JWT token for authentication
    - **token_type**: Bearer token type
    - **expires_in**: Token expiration time in seconds
    """
    # Get user from database
    user = users_db.get(login_data.username)
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "user_id": user["user_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        },
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {login_data.username}")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user information
    
    Requires authentication via Bearer token
    """
    return UserResponse(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so actual logout is handled client-side
    by discarding the token. This endpoint is for logging purposes.
    """
    logger.info(f"User logged out: {current_user.username}")
    
    return {
        "message": "Successfully logged out",
        "username": current_user.username
    }

@router.get("/test-token")
async def test_token(current_user: User = Depends(get_current_active_user)):
    """
    Test endpoint to verify JWT token is valid
    
    Returns current user information
    """
    return {
        "message": "Token is valid",
        "user": {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": current_user.email,
            "role": current_user.role
        }
    }
