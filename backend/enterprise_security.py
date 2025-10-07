"""
Sprint 8: Enterprise Security & Multi-Tenancy System
Advanced RBAC, audit logging, and enterprise-grade security
"""

import json
import logging
import hashlib
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid
from contextlib import asynccontextmanager

class UserRole(Enum):
    """Available user roles"""
    SUPER_ADMIN = "super_admin"
    TENANT_ADMIN = "tenant_admin"
    FINANCE_MANAGER = "finance_manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    API_USER = "api_user"

class Permission(Enum):
    """Available permissions"""
    # Data permissions
    READ_FINANCIAL_DATA = "read_financial_data"
    WRITE_FINANCIAL_DATA = "write_financial_data"
    DELETE_FINANCIAL_DATA = "delete_financial_data"
    
    # Analytics permissions
    VIEW_ANALYTICS = "view_analytics"
    CREATE_REPORTS = "create_reports"
    EXPORT_DATA = "export_data"
    
    # Forecasting permissions
    VIEW_FORECASTS = "view_forecasts"
    CREATE_FORECASTS = "create_forecasts"
    MODIFY_MODELS = "modify_models"
    
    # System permissions
    MANAGE_USERS = "manage_users"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    SYSTEM_CONFIG = "system_config"
    
    # API permissions
    API_ACCESS = "api_access"
    WEBHOOK_MANAGE = "webhook_manage"

class AuditAction(Enum):
    """Audit log action types"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    FORECAST = "forecast"
    CONFIG_CHANGE = "config_change"
    PERMISSION_CHANGE = "permission_change"

@dataclass
class Tenant:
    """Multi-tenant organization"""
    tenant_id: str
    name: str
    domain: str
    plan_type: str = "standard"  # free, standard, premium, enterprise
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    settings: Dict[str, Any] = field(default_factory=dict)
    limits: Dict[str, int] = field(default_factory=dict)

@dataclass
class User:
    """User entity with role-based access"""
    user_id: str
    tenant_id: str
    email: str
    username: str
    role: UserRole
    permissions: Set[Permission] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    password_hash: str = ""
    mfa_enabled: bool = False
    session_token: Optional[str] = None

@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    tenant_id: str
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    tenant_id: str
    password_min_length: int = 12
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    session_timeout_minutes: int = 480  # 8 hours
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    mfa_required: bool = False
    ip_whitelist: List[str] = field(default_factory=list)

class EnterpriseSecurityManager:
    """
    Enterprise-grade security and multi-tenancy management system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # In-memory storage (replace with database in production)
        self.tenants: Dict[str, Tenant] = {}
        self.users: Dict[str, User] = {}
        self.audit_logs: List[AuditLog] = []
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        
        # JWT configuration
        self.jwt_secret = secrets.token_urlsafe(32)
        self.jwt_algorithm = "HS256"
        
        # Initialize role permissions
        self.role_permissions = self._initialize_role_permissions()
        
        # Rate limiting storage
        self.rate_limits: Dict[str, List[datetime]] = {}

    def _initialize_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Initialize default permissions for each role"""
        return {
            UserRole.SUPER_ADMIN: set(Permission),  # All permissions
            
            UserRole.TENANT_ADMIN: {
                Permission.READ_FINANCIAL_DATA,
                Permission.WRITE_FINANCIAL_DATA,
                Permission.DELETE_FINANCIAL_DATA,
                Permission.VIEW_ANALYTICS,
                Permission.CREATE_REPORTS,
                Permission.EXPORT_DATA,
                Permission.VIEW_FORECASTS,
                Permission.CREATE_FORECASTS,
                Permission.MANAGE_USERS,
                Permission.MANAGE_ROLES,
                Permission.VIEW_AUDIT_LOGS,
                Permission.API_ACCESS,
                Permission.WEBHOOK_MANAGE
            },
            
            UserRole.FINANCE_MANAGER: {
                Permission.READ_FINANCIAL_DATA,
                Permission.WRITE_FINANCIAL_DATA,
                Permission.VIEW_ANALYTICS,
                Permission.CREATE_REPORTS,
                Permission.EXPORT_DATA,
                Permission.VIEW_FORECASTS,
                Permission.CREATE_FORECASTS,
                Permission.API_ACCESS
            },
            
            UserRole.ANALYST: {
                Permission.READ_FINANCIAL_DATA,
                Permission.VIEW_ANALYTICS,
                Permission.CREATE_REPORTS,
                Permission.VIEW_FORECASTS,
                Permission.CREATE_FORECASTS,
                Permission.API_ACCESS
            },
            
            UserRole.VIEWER: {
                Permission.READ_FINANCIAL_DATA,
                Permission.VIEW_ANALYTICS,
                Permission.VIEW_FORECASTS
            },
            
            UserRole.API_USER: {
                Permission.API_ACCESS,
                Permission.READ_FINANCIAL_DATA,
                Permission.VIEW_ANALYTICS
            }
        }

    async def create_tenant(self, name: str, domain: str, admin_email: str, 
                          plan_type: str = "standard") -> Dict[str, Any]:
        """Create a new tenant organization"""
        try:
            tenant_id = str(uuid.uuid4())
            
            # Create tenant
            tenant = Tenant(
                tenant_id=tenant_id,
                name=name,
                domain=domain,
                plan_type=plan_type,
                limits=self._get_plan_limits(plan_type)
            )
            
            self.tenants[tenant_id] = tenant
            
            # Create default security policy
            self.security_policies[tenant_id] = SecurityPolicy(tenant_id=tenant_id)
            
            # Create tenant admin user
            admin_user = await self.create_user(
                tenant_id=tenant_id,
                email=admin_email,
                username=admin_email.split('@')[0],
                role=UserRole.TENANT_ADMIN,
                password="temp_password_123!"  # Should be changed on first login
            )
            
            await self._audit_log(
                tenant_id=tenant_id,
                user_id="system",
                action=AuditAction.CREATE,
                resource_type="tenant",
                resource_id=tenant_id,
                details={"name": name, "domain": domain, "plan": plan_type},
                ip_address="system",
                user_agent="system"
            )
            
            return {
                "tenant_id": tenant_id,
                "admin_user_id": admin_user["user_id"],
                "status": "created",
                "message": "Tenant created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Tenant creation failed: {str(e)}")
            raise

    def _get_plan_limits(self, plan_type: str) -> Dict[str, int]:
        """Get limits based on plan type"""
        limits = {
            "free": {
                "users": 3,
                "api_calls_per_month": 1000,
                "data_retention_days": 90,
                "forecasting_models": 1
            },
            "standard": {
                "users": 10,
                "api_calls_per_month": 10000,
                "data_retention_days": 365,
                "forecasting_models": 3
            },
            "premium": {
                "users": 50,
                "api_calls_per_month": 100000,
                "data_retention_days": 1095,  # 3 years
                "forecasting_models": 10
            },
            "enterprise": {
                "users": -1,  # Unlimited
                "api_calls_per_month": -1,  # Unlimited
                "data_retention_days": -1,  # Unlimited
                "forecasting_models": -1  # Unlimited
            }
        }
        
        return limits.get(plan_type, limits["standard"])

    async def create_user(self, tenant_id: str, email: str, username: str, 
                         role: UserRole, password: str) -> Dict[str, Any]:
        """Create a new user with role-based permissions"""
        try:
            # Validate tenant exists
            if tenant_id not in self.tenants:
                raise ValueError("Tenant not found")
            
            # Check tenant user limits
            tenant = self.tenants[tenant_id]
            current_users = len([u for u in self.users.values() if u.tenant_id == tenant_id])
            
            if tenant.limits.get("users", 0) > 0 and current_users >= tenant.limits["users"]:
                raise ValueError("Tenant user limit exceeded")
            
            # Validate password
            await self._validate_password(password, tenant_id)
            
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            
            # Create user
            user = User(
                user_id=user_id,
                tenant_id=tenant_id,
                email=email,
                username=username,
                role=role,
                permissions=self.role_permissions.get(role, set()),
                password_hash=password_hash
            )
            
            self.users[user_id] = user
            
            await self._audit_log(
                tenant_id=tenant_id,
                user_id="system",
                action=AuditAction.CREATE,
                resource_type="user",
                resource_id=user_id,
                details={"email": email, "role": role.value},
                ip_address="system",
                user_agent="system"
            )
            
            return {
                "user_id": user_id,
                "email": email,
                "role": role.value,
                "permissions": [p.value for p in user.permissions],
                "status": "created"
            }
            
        except Exception as e:
            self.logger.error(f"User creation failed: {str(e)}")
            raise

    async def authenticate_user(self, email: str, password: str, 
                              ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Authenticate user and create session"""
        try:
            # Find user by email
            user = None
            for u in self.users.values():
                if u.email == email and u.is_active:
                    user = u
                    break
            
            if not user:
                await self._audit_log(
                    tenant_id="unknown",
                    user_id="unknown",
                    action=AuditAction.LOGIN,
                    resource_type="authentication",
                    resource_id=None,
                    details={"email": email, "result": "user_not_found"},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )
                raise ValueError("Invalid credentials")
            
            # Check rate limiting
            await self._check_rate_limit(f"login_{user.user_id}", 5, 300)  # 5 attempts per 5 minutes
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                await self._audit_log(
                    tenant_id=user.tenant_id,
                    user_id=user.user_id,
                    action=AuditAction.LOGIN,
                    resource_type="authentication",
                    resource_id=None,
                    details={"result": "invalid_password"},
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False
                )
                raise ValueError("Invalid credentials")
            
            # Check security policy
            policy = self.security_policies.get(user.tenant_id, SecurityPolicy(user.tenant_id))
            
            # IP whitelist check
            if policy.ip_whitelist and ip_address not in policy.ip_whitelist:
                raise ValueError("IP address not authorized")
            
            # Create JWT token
            token_payload = {
                "user_id": user.user_id,
                "tenant_id": user.tenant_id,
                "email": user.email,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "exp": datetime.utcnow() + timedelta(minutes=policy.session_timeout_minutes),
                "iat": datetime.utcnow(),
                "jti": str(uuid.uuid4())  # JWT ID for token revocation
            }
            
            access_token = jwt.encode(token_payload, self.jwt_secret, algorithm=self.jwt_algorithm)
            
            # Create session
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = {
                "user_id": user.user_id,
                "tenant_id": user.tenant_id,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "token_jti": token_payload["jti"]
            }
            
            # Update user login time
            user.last_login = datetime.now()
            user.session_token = session_id
            
            await self._audit_log(
                tenant_id=user.tenant_id,
                user_id=user.user_id,
                action=AuditAction.LOGIN,
                resource_type="authentication",
                resource_id=None,
                details={"result": "success", "session_id": session_id},
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": policy.session_timeout_minutes * 60,
                "user": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "role": user.role.value,
                    "tenant_id": user.tenant_id,
                    "permissions": [p.value for p in user.permissions]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user info"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            user_id = payload.get("user_id")
            user = self.users.get(user_id)
            
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")
            
            # Check if session is still active
            session_id = user.session_token
            if session_id not in self.active_sessions:
                raise ValueError("Session expired")
            
            # Update last activity
            self.active_sessions[session_id]["last_activity"] = datetime.now()
            
            return {
                "user_id": user.user_id,
                "tenant_id": user.tenant_id,
                "email": user.email,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions]
            }
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has specific permission"""
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        return permission in user.permissions

    async def require_permission(self, user_id: str, permission: Permission):
        """Require specific permission or raise exception"""
        if not await self.check_permission(user_id, permission):
            user = self.users.get(user_id)
            await self._audit_log(
                tenant_id=user.tenant_id if user else "unknown",
                user_id=user_id,
                action=AuditAction.READ,
                resource_type="permission_check",
                resource_id=None,
                details={"permission": permission.value, "result": "denied"},
                ip_address="unknown",
                user_agent="unknown",
                success=False
            )
            raise PermissionError(f"Permission required: {permission.value}")

    @asynccontextmanager
    async def require_permissions(self, user_id: str, *permissions: Permission):
        """Context manager for permission checking"""
        for permission in permissions:
            await self.require_permission(user_id, permission)
        yield

    async def update_user_role(self, user_id: str, new_role: UserRole, 
                             admin_user_id: str) -> Dict[str, Any]:
        """Update user role and permissions"""
        try:
            # Check admin permissions
            await self.require_permission(admin_user_id, Permission.MANAGE_ROLES)
            
            user = self.users.get(user_id)
            if not user:
                raise ValueError("User not found")
            
            old_role = user.role
            user.role = new_role
            user.permissions = self.role_permissions.get(new_role, set())
            
            await self._audit_log(
                tenant_id=user.tenant_id,
                user_id=admin_user_id,
                action=AuditAction.PERMISSION_CHANGE,
                resource_type="user_role",
                resource_id=user_id,
                details={
                    "old_role": old_role.value,
                    "new_role": new_role.value,
                    "permissions": [p.value for p in user.permissions]
                },
                ip_address="system",
                user_agent="system"
            )
            
            return {
                "user_id": user_id,
                "old_role": old_role.value,
                "new_role": new_role.value,
                "permissions": [p.value for p in user.permissions],
                "status": "updated"
            }
            
        except Exception as e:
            self.logger.error(f"Role update failed: {str(e)}")
            raise

    async def _audit_log(self, tenant_id: str, user_id: str, action: AuditAction,
                        resource_type: str, resource_id: Optional[str],
                        details: Dict[str, Any], ip_address: str, user_agent: str,
                        success: bool = True):
        """Create audit log entry"""
        log_entry = AuditLog(
            log_id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
        
        self.audit_logs.append(log_entry)
        
        # Keep only recent logs (last 10000 entries)
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]

    async def get_audit_logs(self, tenant_id: str, user_id: str, 
                           filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get audit logs with filtering"""
        await self.require_permission(user_id, Permission.VIEW_AUDIT_LOGS)
        
        # Filter by tenant
        logs = [log for log in self.audit_logs if log.tenant_id == tenant_id]
        
        # Apply additional filters
        if filters:
            if "action" in filters:
                logs = [log for log in logs if log.action.value == filters["action"]]
            if "user_id" in filters:
                logs = [log for log in logs if log.user_id == filters["user_id"]]
            if "resource_type" in filters:
                logs = [log for log in logs if log.resource_type == filters["resource_type"]]
            if "start_date" in filters:
                start_date = datetime.fromisoformat(filters["start_date"])
                logs = [log for log in logs if log.timestamp >= start_date]
            if "end_date" in filters:
                end_date = datetime.fromisoformat(filters["end_date"])
                logs = [log for log in logs if log.timestamp <= end_date]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Convert to dict format
        return [
            {
                "log_id": log.log_id,
                "user_id": log.user_id,
                "action": log.action.value,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
                "success": log.success
            }
            for log in logs
        ]

    async def _validate_password(self, password: str, tenant_id: str):
        """Validate password against security policy"""
        policy = self.security_policies.get(tenant_id, SecurityPolicy(tenant_id))
        
        if len(password) < policy.password_min_length:
            raise ValueError(f"Password must be at least {policy.password_min_length} characters")
        
        if policy.password_require_uppercase and not any(c.isupper() for c in password):
            raise ValueError("Password must contain uppercase letters")
        
        if policy.password_require_numbers and not any(c.isdigit() for c in password):
            raise ValueError("Password must contain numbers")
        
        if policy.password_require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            raise ValueError("Password must contain special characters")

    def _hash_password(self, password: str) -> str:
        """Hash password using secure method"""
        salt = secrets.token_hex(32)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return computed_hash.hex() == hash_hex
        except ValueError:
            return False

    async def _check_rate_limit(self, key: str, max_requests: int, window_seconds: int):
        """Check rate limiting"""
        now = datetime.now()
        window_start = now - timedelta(seconds=window_seconds)
        
        if key not in self.rate_limits:
            self.rate_limits[key] = []
        
        # Clean old entries
        self.rate_limits[key] = [
            timestamp for timestamp in self.rate_limits[key] 
            if timestamp > window_start
        ]
        
        # Check limit
        if len(self.rate_limits[key]) >= max_requests:
            raise ValueError("Rate limit exceeded")
        
        # Add current request
        self.rate_limits[key].append(now)

    async def logout_user(self, user_id: str):
        """Logout user and invalidate session"""
        user = self.users.get(user_id)
        if user and user.session_token:
            # Remove session
            if user.session_token in self.active_sessions:
                del self.active_sessions[user.session_token]
            
            # Clear user session token
            user.session_token = None
            
            await self._audit_log(
                tenant_id=user.tenant_id,
                user_id=user_id,
                action=AuditAction.LOGOUT,
                resource_type="authentication",
                resource_id=None,
                details={"result": "success"},
                ip_address="system",
                user_agent="system"
            )

    async def get_tenant_users(self, tenant_id: str, requester_user_id: str) -> List[Dict[str, Any]]:
        """Get all users for a tenant"""
        await self.require_permission(requester_user_id, Permission.MANAGE_USERS)
        
        tenant_users = [
            {
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
            for user in self.users.values()
            if user.tenant_id == tenant_id
        ]
        
        return tenant_users

    async def get_system_status(self) -> Dict[str, Any]:
        """Get system security status"""
        return {
            "total_tenants": len(self.tenants),
            "total_users": len(self.users),
            "active_sessions": len(self.active_sessions),
            "audit_log_entries": len(self.audit_logs),
            "security_policies": len(self.security_policies),
            "system_health": "operational",
            "last_updated": datetime.now().isoformat()
        }

# Initialize the enterprise security manager
enterprise_security = EnterpriseSecurityManager()