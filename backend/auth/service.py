"""
Authentication service for user management and JWT operations
"""
import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
import secrets
import string
import logging

from .models import (
    User, UserCreate, UserLogin, UserProfile, Token, 
    TokenData, UserRole, UserStatus, AuditLog
)
from .database import auth_db_service
from bson import ObjectId

logger = logging.getLogger("financial-agent.auth.service")

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self, db: AsyncIOMotorDatabase = None):
        self.db = db
        self.users_collection = None
        self.audit_logs_collection = None
        self._initialized = False
        
        # JWT Configuration
        self.jwt_secret = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
        
        # Security Configuration
        self.max_login_attempts = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.lockout_duration_minutes = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
    
    async def initialize(self):
        """Initialize database connections"""
        if not self._initialized:
            if self.db is None:
                self.db = await auth_db_service.get_database()
            self.users_collection = await auth_db_service.get_users_collection()
            self.audit_logs_collection = await auth_db_service.get_audit_logs_collection()
            self._initialized = True
        
    async def register_user(self, user_data: UserCreate, ip_address: str, user_agent: str) -> Dict[str, Any]:
        """Register a new user with comprehensive validation"""
        try:
            await self.initialize()
            # Validate password confirmation
            if user_data.password != user_data.confirm_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords do not match"
                )
            
            # Check if user already exists
            existing_user = await self.users_collection.find_one({"email": user_data.email})
            if existing_user:
                await self._log_audit_event(
                    action="register_attempt",
                    email=user_data.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Email already exists"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # Validate password strength
            self._validate_password_strength(user_data.password)
            
            # Hash password
            password_hash = self._hash_password(user_data.password)
            
            # Create user document
            user_doc = {
                "email": user_data.email,
                "password_hash": password_hash,
                "company_name": user_data.company_name,
                "phone_number": user_data.phone_number,
                "role": user_data.role,
                "status": UserStatus.ACTIVE,
                "is_active": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "failed_login_attempts": 0,
                "email_verified": False,
                "phone_verified": False
            }
            
            # Insert user
            result = await self.users_collection.insert_one(user_doc)
            user_id = str(result.inserted_id)
            
            # Log successful registration
            await self._log_audit_event(
                action="register",
                user_id=user_id,
                email=user_data.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            # Get user profile
            user = await self.get_user_by_id(user_id)
            
            # Generate tokens
            tokens = await self._generate_tokens(user)
            
            logger.info(f"New user registered: {user_data.email}")
            
            return {
                "message": "User registered successfully",
                "user": self._create_user_profile(user),
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def login_user(self, login_data: UserLogin, ip_address: str, user_agent: str) -> Token:
        """Authenticate user and return JWT tokens"""
        try:
            await self.initialize()
            # Get user by email
            user_doc = await self.users_collection.find_one({"email": login_data.email})
            
            if not user_doc:
                await self._log_audit_event(
                    action="login_attempt",
                    email=login_data.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Email not found"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            user = User(**user_doc)
            
            # Check if account is locked
            if await self._is_account_locked(user):
                await self._log_audit_event(
                    action="login_attempt",
                    user_id=str(user.id),
                    email=user.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Account locked"
                )
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail="Account is temporarily locked due to multiple failed login attempts"
                )
            
            # Check if account is active
            if user.status != UserStatus.ACTIVE:
                await self._log_audit_event(
                    action="login_attempt",
                    user_id=str(user.id),
                    email=user.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason=f"Account status: {user.status}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account is {user.status}"
                )
            
            # Verify password
            if not self._verify_password(login_data.password, user.password_hash):
                # Increment failed attempts
                await self._increment_failed_attempts(user)
                
                await self._log_audit_event(
                    action="login_attempt",
                    user_id=str(user.id),
                    email=user.email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason="Invalid password"
                )
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Reset failed attempts on successful login
            await self._reset_failed_attempts(user)
            
            # Update last login
            await self.users_collection.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {"last_login": datetime.now()}}
            )
            
            # Generate tokens
            tokens = await self._generate_tokens(user)
            
            # Log successful login
            await self._log_audit_event(
                action="login",
                user_id=str(user.id),
                email=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True
            )
            
            logger.info(f"User logged in: {user.email}")
            
            # Return both user info and tokens
            return {
                "user": user,
                "tokens": tokens
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )
            
            # Get user
            user = await self.get_user_by_id(user_id)
            if not user or user.status != UserStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Generate new access token
            access_token = self._create_access_token(user)
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            from bson import ObjectId
            user_doc = await self.users_collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            user_doc = await self.users_collection.find_one({"email": email})
            if user_doc:
                user_doc["_id"] = str(user_doc["_id"])
                return User(**user_doc)
            return None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    def verify_token(self, token: str) -> TokenData:
        """Verify JWT token and return token data"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            user_id = payload.get("user_id")
            email = payload.get("email")
            role = payload.get("role")
            token_type = payload.get("type")
            
            if not all([user_id, email, role]):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            return TokenData(
                user_id=user_id,
                email=email,
                role=UserRole(role),
                exp=datetime.fromtimestamp(payload.get("exp")),
                iat=datetime.fromtimestamp(payload.get("iat")),
                type=token_type
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    # Private helper methods
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def _validate_password_strength(self, password: str) -> None:
        """Validate password strength"""
        if len(password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one uppercase letter, lowercase letter, digit, and special character"
            )
    
    def _create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    def _create_refresh_token(self, user: User) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
    
    async def _generate_tokens(self, user: User) -> Token:
        """Generate both access and refresh tokens"""
        access_token = self._create_access_token(user)
        refresh_token = self._create_refresh_token(user)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.access_token_expire_minutes * 60,
            user=self._create_user_profile(user)
        )
    
    def _create_user_profile(self, user: User) -> UserProfile:
        """Create user profile from user model"""
        return UserProfile(
            id=str(user.id),
            email=user.email,
            company_name=user.company_name,
            phone_number=user.phone_number,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
            last_login=user.last_login,
            email_verified=user.email_verified,
            phone_verified=user.phone_verified
        )
    
    async def _is_account_locked(self, user: User) -> bool:
        """Check if account is locked due to failed login attempts"""
        if user.account_locked_until and user.account_locked_until > datetime.now():
            return True
        return False
    
    async def _increment_failed_attempts(self, user: User) -> None:
        """Increment failed login attempts and lock account if necessary"""
        failed_attempts = user.failed_login_attempts + 1
        update_data = {"failed_login_attempts": failed_attempts}
        
        if failed_attempts >= self.max_login_attempts:
            lockout_until = datetime.now() + timedelta(minutes=self.lockout_duration_minutes)
            update_data["account_locked_until"] = lockout_until
        
        await self.users_collection.update_one(
            {"_id": user.id},
            {"$set": update_data}
        )
    
    async def _reset_failed_attempts(self, user: User) -> None:
        """Reset failed login attempts"""
        await self.users_collection.update_one(
            {"_id": user.id},
            {"$set": {
                "failed_login_attempts": 0,
                "account_locked_until": None
            }}
        )
    
    async def _log_audit_event(self, action: str, ip_address: str, user_agent: str, 
                             success: bool, user_id: Optional[str] = None, 
                             email: Optional[str] = None, failure_reason: Optional[str] = None,
                             metadata: Dict[str, Any] = None) -> None:
        """Log authentication audit event"""
        try:
            audit_log = AuditLog(
                user_id=user_id,
                email=email,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                failure_reason=failure_reason,
                metadata=metadata or {}
            )
            
            await self.audit_logs_collection.insert_one(audit_log.dict(by_alias=True))
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")