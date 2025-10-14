from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from typing import List, Optional
from datetime import datetime

from backend.auth.models import User, UserCreate, UserUpdate, UserRole, UserStatus
from backend.auth.middleware import get_current_user, get_auth_service
from backend.auth.service import AuthService

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_permission(permission: str):
    """Decorator to check permissions"""
    async def dependency(
        request: Request,
        current_user: User = Depends(get_current_user)
    ):
        auth_service = get_auth_service(request)
        if not auth_service.check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission}"
            )
        return current_user
    return dependency


@router.get("/users", response_model=dict)
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_permission("users.view"))
):
    """List all users with pagination and filters"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        # Build query
        query = {}
        if role:
            query["role"] = role
        if status:
            query["status"] = status
        if search:
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"company_name": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await auth_service.users_collection.count_documents(query)
        
        # Get paginated users
        skip = (page - 1) * limit
        cursor = auth_service.users_collection.find(query).skip(skip).limit(limit)
        users_data = await cursor.to_list(length=limit)
        
        # Remove sensitive data
        for user_data in users_data:
            user_data.pop("password_hash", None)
            user_data["_id"] = str(user_data["_id"])
        
        return {
            "users": users_data,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list users: {str(e)}"
        )


@router.get("/users/{user_id}", response_model=dict)
async def get_user(
    request: Request,
    user_id: str,
    current_user: User = Depends(require_permission("users.view"))
):
    """Get user details by ID"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        from bson import ObjectId
        user_data = await auth_service.users_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Remove sensitive data
        user_data.pop("password_hash", None)
        user_data["_id"] = str(user_data["_id"])
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}"
        )


@router.post("/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_create: UserCreate,
    current_user: User = Depends(require_permission("users.create"))
):
    """Create a new user"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        # Check if user exists
        existing_user = await auth_service.users_collection.find_one({"email": user_create.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Hash password
        password_hash = auth_service._hash_password(user_create.password)
        
        # Create user document
        user_doc = {
            "email": user_create.email,
            "company_name": user_create.company_name,
            "phone_number": user_create.phone_number,
            "role": user_create.role or UserRole.VIEWER,
            "password_hash": password_hash,
            "status": "active",
            "is_active": True,
            "email_verified": False,
            "phone_verified": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "created_by": str(current_user.id),
            "failed_login_attempts": 0
        }
        
        result = await auth_service.users_collection.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        user_doc.pop("password_hash", None)
        
        # Log audit event
        await auth_service._log_audit_event(
            action="user_created",
            ip_address="",
            user_agent="",
            success=True,
            user_id=str(current_user.id),
            email=current_user.email,
            metadata={"created_user_email": user_create.email, "role": user_create.role}
        )
        
        return user_doc
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.put("/users/{user_id}", response_model=dict)
async def update_user(
    request: Request,
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_permission("users.edit"))
):
    """Update user details"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        from bson import ObjectId
        
        # Check if user exists
        existing_user = await auth_service.users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build update document
        update_data = {}
        if user_update.company_name is not None:
            update_data["company_name"] = user_update.company_name
        if user_update.phone_number is not None:
            update_data["phone_number"] = user_update.phone_number
        if user_update.role is not None:
            update_data["role"] = user_update.role
        if user_update.status is not None:
            update_data["status"] = user_update.status
            update_data["is_active"] = user_update.status == "active"
        
        update_data["updated_at"] = datetime.now()
        update_data["updated_by"] = str(current_user.id)
        
        # Update user
        await auth_service.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Get updated user
        updated_user = await auth_service.users_collection.find_one({"_id": ObjectId(user_id)})
        updated_user["_id"] = str(updated_user["_id"])
        updated_user.pop("password_hash", None)
        
        # Log audit event
        await auth_service._log_audit_event(
            action="user_updated",
            ip_address="",
            user_agent="",
            success=True,
            user_id=str(current_user.id),
            email=current_user.email,
            metadata={"updated_user_email": existing_user["email"], "updates": update_data}
        )
        
        return updated_user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    user_id: str,
    current_user: User = Depends(require_permission("users.delete"))
):
    """Delete a user (soft delete by setting status to inactive)"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        from bson import ObjectId
        
        # Check if user exists
        existing_user = await auth_service.users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if str(existing_user["_id"]) == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Soft delete: set status to inactive
        await auth_service.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "status": "inactive",
                    "is_active": False,
                    "deleted_at": datetime.now(),
                    "deleted_by": str(current_user.id)
                }
            }
        )
        
        # Log audit event
        await auth_service._log_audit_event(
            action="user_deleted",
            ip_address="",
            user_agent="",
            success=True,
            user_id=str(current_user.id),
            email=current_user.email,
            metadata={"deleted_user_email": existing_user["email"]}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )


@router.get("/stats", response_model=dict)
async def get_admin_stats(
    request: Request,
    current_user: User = Depends(require_permission("system.view"))
):
    """Get admin dashboard statistics"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        # User counts by role
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}}
        ]
        role_counts = await auth_service.users_collection.aggregate(pipeline).to_list(length=10)
        users_by_role = {item["_id"]: item["count"] for item in role_counts}
        
        # Total users
        total_users = sum(users_by_role.values())
        
        # Active users
        active_users = await auth_service.users_collection.count_documents({"is_active": True})
        
        # Recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.now() - timedelta(days=1)
        recent_activity = await auth_service.audit_logs_collection.count_documents(
            {"timestamp": {"$gte": yesterday}}
        )
        
        # Failed login attempts today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        failed_logins = await auth_service.audit_logs_collection.count_documents({
            "action": "login",
            "success": False,
            "timestamp": {"$gte": today_start}
        })
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "users_by_role": users_by_role,
            "recent_activity_24h": recent_activity,
            "failed_logins_today": failed_logins
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )


@router.get("/activity", response_model=dict)
async def get_activity_logs(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = None,
    user_email: Optional[str] = None,
    success: Optional[bool] = None,
    current_user: User = Depends(require_permission("system.view"))
):
    """Get audit/activity logs"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        # Build query
        query = {}
        if action:
            query["action"] = action
        if user_email:
            query["email"] = user_email
        if success is not None:
            query["success"] = success
        
        # Get total count
        total = await auth_service.audit_logs_collection.count_documents(query)
        
        # Get paginated logs
        skip = (page - 1) * limit
        cursor = auth_service.audit_logs_collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
        logs = await cursor.to_list(length=limit)
        
        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])
        
        return {
            "logs": logs,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get activity logs: {str(e)}"
        )


@router.post("/users/{user_id}/reset-password", response_model=dict)
async def admin_reset_password(
    request: Request,
    user_id: str,
    new_password: str,
    current_user: User = Depends(require_permission("users.edit"))
):
    """Admin reset user password"""
    auth_service = get_auth_service(request)
    try:
        await auth_service.initialize()
        
        from bson import ObjectId
        
        # Check if user exists
        existing_user = await auth_service.users_collection.find_one({"_id": ObjectId(user_id)})
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        password_hash = auth_service._hash_password(new_password)
        
        # Update password
        await auth_service.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(),
                    "password_reset_by": str(current_user.id),
                    "failed_login_attempts": 0,
                    "account_locked_until": None
                }
            }
        )
        
        # Log audit event
        await auth_service._log_audit_event(
            action="admin_password_reset",
            ip_address="",
            user_agent="",
            success=True,
            user_id=str(current_user.id),
            email=current_user.email,
            metadata={"reset_user_email": existing_user["email"]}
        )
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )


@router.get("/permissions", response_model=dict)
async def get_user_permissions(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Get current user's permissions"""
    auth_service = get_auth_service(request)
    permissions = auth_service.get_user_permissions(current_user)
    
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "permissions": permissions
    }
