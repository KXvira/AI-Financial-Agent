"""
Authentication router with endpoints for user management
"""
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
import logging

from .models import (
    UserCreate, UserLogin, User, Token, UserProfile, 
    PasswordReset, PasswordChange, AuditLog
)
from .service import AuthService
from .middleware import (
    get_auth_service, get_current_user, get_current_user_optional,
    get_client_ip, get_user_agent
)

logger = logging.getLogger("financial-agent.auth.router")

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

@router.post(
    "/register",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account with email verification"
)
async def register(
    user_data: UserCreate,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Register a new user"""
    try:
        # Get client info for audit
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Register user (returns user and tokens)
        registration_result = await auth_service.register_user(user_data, client_ip, user_agent)
        user = registration_result['user']
        tokens = registration_result['tokens']
        
        logger.info(f"User registered successfully: {user.email}")
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.company_name,
                "role": user.role,
                "is_active": user.status == "active",
                "is_verified": user.email_verified
            },
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type
        }
        
    except ValueError as e:
        logger.warning(f"Registration validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )

@router.post(
    "/login",
    response_model=Dict[str, Any],
    summary="Login user",
    description="Authenticate user with email and password"
)
async def login(
    credentials: UserLogin,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Authenticate user login"""
    try:
        # Get client info for audit
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Authenticate user
        login_response = await auth_service.login_user(
            credentials, 
            client_ip, 
            user_agent
        )
        
        user = login_response["user"]
        tokens = login_response["tokens"]
        
        logger.info(f"User logged in successfully: {user.email}")
        
        return {
            "message": "Login successful",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.company_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "is_verified": user.email_verified
            },
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type
        }
        
    except ValueError as e:
        logger.warning(f"Login validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post(
    "/refresh",
    response_model=Dict[str, str],
    summary="Refresh access token",
    description="Get new access token using refresh token"
)
async def refresh_token(
    token_data: Dict[str, str],
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Refresh access token"""
    try:
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refresh token is required"
            )
        
        # Get client info for audit
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Refresh token
        new_tokens = await auth_service.refresh_token(
            refresh_token, 
            client_ip, 
            user_agent
        )
        
        return {
            "access_token": new_tokens["access_token"],
            "refresh_token": new_tokens["refresh_token"],
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user",
    description="Get current authenticated user profile"
)
async def get_me(
    current_user: User = Depends(get_current_user)
) -> UserProfile:
    """Get current user profile"""
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        phone_number=current_user.phone_number,
        business_name=current_user.business_name
    )

@router.put(
    "/me",
    response_model=Dict[str, Any],
    summary="Update current user",
    description="Update current authenticated user profile"
)
async def update_me(
    user_updates: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Update current user profile"""
    try:
        # Only allow specific fields to be updated
        allowed_fields = ["full_name", "phone_number", "business_name"]
        updates = {k: v for k, v in user_updates.items() if k in allowed_fields}
        
        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid fields to update"
            )
        
        # Update user
        updated_user = await auth_service.update_user(current_user.id, updates)
        
        return {
            "message": "Profile updated successfully",
            "user": {
                "id": str(updated_user.id),
                "email": updated_user.email,
                "full_name": updated_user.full_name,
                "phone_number": updated_user.phone_number,
                "business_name": updated_user.business_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.post(
    "/change-password",
    response_model=Dict[str, str],
    summary="Change password",
    description="Change current user password"
)
async def change_password(
    password_data: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Change user password"""
    try:
        # Get client info for audit
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Change password
        await auth_service.change_password(
            current_user.id,
            password_data.current_password,
            password_data.new_password,
            client_ip,
            user_agent
        )
        
        return {"message": "Password changed successfully"}
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )

@router.post(
    "/logout",
    response_model=Dict[str, str],
    summary="Logout user",
    description="Logout current user and invalidate tokens"
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Logout user"""
    try:
        # Get client info for audit
        client_ip = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Log audit event
        await auth_service.log_audit_event(
            current_user.id,
            "logout",
            {"ip_address": client_ip, "user_agent": user_agent},
            client_ip
        )
        
        # In a complete implementation, you would:
        # 1. Add tokens to a blacklist
        # 2. Clear any server-side sessions
        # 3. Update last_logout timestamp
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get(
    "/audit-logs",
    response_model=Dict[str, Any],
    summary="Get audit logs",
    description="Get audit logs for current user (owner role can see all)"
)
async def get_audit_logs(
    limit: int = 50,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Get audit logs"""
    try:
        # Determine user filter based on role
        user_id_filter = None if current_user.role.value == "owner" else current_user.id
        
        # Get audit logs
        logs = await auth_service.get_audit_logs(
            user_id=user_id_filter,
            limit=limit,
            skip=skip
        )
        
        return {
            "logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id),
                    "action": log.action,
                    "details": log.details,
                    "ip_address": log.ip_address,
                    "timestamp": log.timestamp.isoformat()
                }
                for log in logs
            ],
            "total": len(logs),
            "limit": limit,
            "skip": skip
        }
        
    except Exception as e:
        logger.error(f"Audit logs error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit logs"
        )

@router.get(
    "/health",
    summary="Authentication health check",
    description="Check authentication service health"
)
async def health_check(
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, str]:
    """Authentication service health check"""
    try:
        # Basic health check - verify database connection
        await auth_service.db.command("ping")
        
        return {
            "status": "healthy",
            "service": "authentication",
            "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Auth health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable"
        )