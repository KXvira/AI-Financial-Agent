"""
Authentication configuration settings
"""
import os
from typing import Optional

class AuthConfig:
    """Authentication configuration settings"""
    
    # JWT Settings
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Password Settings
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_SPECIAL: bool = True
    PASSWORD_REQUIRE_UPPER: bool = True
    PASSWORD_REQUIRE_LOWER: bool = True
    PASSWORD_REQUIRE_DIGIT: bool = True
    
    # Account Security
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = int(os.getenv("ACCOUNT_LOCKOUT_DURATION_MINUTES", "30"))
    
    # Database Collections
    USERS_COLLECTION: str = "users"
    AUDIT_LOGS_COLLECTION: str = "audit_logs"
    
    # Email Settings (for future email verification)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@finagent.com")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate critical configuration settings"""
        if cls.SECRET_KEY == "your-secret-key-change-in-production":
            return False
        if len(cls.SECRET_KEY) < 32:
            return False
        return True
    
    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL from environment"""
        return os.getenv("MONGO_URI", "mongodb://localhost:27017/financial_agent")

# Global config instance
auth_config = AuthConfig()