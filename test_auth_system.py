"""
Test suite for authentication system
"""
import pytest
import asyncio
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
import sys
import os

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.models import UserCreate, UserLogin, UserRole
from auth.service import AuthService
from auth.config import auth_config
from database.mongodb import Database

class TestAuthenticationSystem:
    """Test cases for authentication system"""
    
    @pytest.fixture(scope="class")
    async def auth_service(self):
        """Create auth service for testing"""
        # Use test database
        db = Database.get_instance()
        service = AuthService(db)
        yield service
        
        # Cleanup - drop test collections
        try:
            await db.drop_collection("test_users")
            await db.drop_collection("test_audit_logs")
        except Exception:
            pass
    
    @pytest.fixture
    def test_user_data(self):
        """Sample user data for testing"""
        return UserCreate(
            email="test@example.com",
            password="TestPassword123!",
            full_name="Test User",
            phone_number="+254700000000",
            business_name="Test Business"
        )
    
    @pytest.mark.asyncio
    async def test_user_registration(self, auth_service, test_user_data):
        """Test user registration"""
        # Register user
        user = await auth_service.register_user(
            test_user_data, 
            "127.0.0.1", 
            "test-agent"
        )
        
        # Verify user creation
        assert user.email == test_user_data.email
        assert user.full_name == test_user_data.full_name
        assert user.role == UserRole.OWNER
        assert user.is_active is True
        assert user.is_verified is False
        
        # Verify password is hashed
        assert user.password_hash != test_user_data.password
        
    @pytest.mark.asyncio
    async def test_duplicate_email_registration(self, auth_service, test_user_data):
        """Test duplicate email registration fails"""
        # First registration should succeed
        await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Second registration should fail
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
    
    @pytest.mark.asyncio
    async def test_password_validation(self, auth_service):
        """Test password validation"""
        weak_passwords = [
            "short",  # Too short
            "nouppercase123!",  # No uppercase
            "NOLOWERCASE123!",  # No lowercase
            "NoNumbers!",  # No numbers
            "NoSpecialChars123"  # No special characters
        ]
        
        for password in weak_passwords:
            invalid_data = UserCreate(
                email=f"test_{password}@example.com",
                password=password,
                full_name="Test User"
            )
            
            with pytest.raises(ValueError, match="Password must"):
                await auth_service.register_user(invalid_data, "127.0.0.1", "test-agent")
    
    @pytest.mark.asyncio
    async def test_user_login_success(self, auth_service, test_user_data):
        """Test successful user login"""
        # Register user first
        await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Login
        user = await auth_service.login_user(
            test_user_data.email,
            test_user_data.password,
            "127.0.0.1",
            "test-agent"
        )
        
        assert user.email == test_user_data.email
        assert user.last_login is not None
        assert user.failed_login_attempts == 0
    
    @pytest.mark.asyncio
    async def test_user_login_invalid_password(self, auth_service, test_user_data):
        """Test login with invalid password"""
        # Register user first
        await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Login with wrong password
        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login_user(
                test_user_data.email,
                "wrongpassword",
                "127.0.0.1",
                "test-agent"
            )
    
    @pytest.mark.asyncio
    async def test_account_lockout(self, auth_service, test_user_data):
        """Test account lockout after failed attempts"""
        # Register user first
        await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Make multiple failed login attempts
        for i in range(auth_config.MAX_LOGIN_ATTEMPTS + 1):
            try:
                await auth_service.login_user(
                    test_user_data.email,
                    "wrongpassword",
                    "127.0.0.1",
                    "test-agent"
                )
            except ValueError:
                pass
        
        # Next attempt should indicate account is locked
        with pytest.raises(ValueError, match="Account is locked"):
            await auth_service.login_user(
                test_user_data.email,
                test_user_data.password,
                "127.0.0.1",
                "test-agent"
            )
    
    def test_jwt_token_creation(self, auth_service):
        """Test JWT token creation"""
        tokens = auth_service.create_tokens("test_user_id", "test@example.com")
        
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        assert isinstance(tokens["access_token"], str)
        assert isinstance(tokens["refresh_token"], str)
    
    def test_jwt_token_verification(self, auth_service):
        """Test JWT token verification"""
        user_id = "test_user_id"
        email = "test@example.com"
        
        # Create token
        tokens = auth_service.create_tokens(user_id, email)
        access_token = tokens["access_token"]
        
        # Verify token
        token_data = auth_service.verify_token(access_token)
        
        assert token_data.user_id == user_id
        assert token_data.email == email
        assert token_data.type == "access"
    
    def test_expired_token_verification(self, auth_service):
        """Test expired token verification fails"""
        # Create token with very short expiry
        user_id = "test_user_id"
        email = "test@example.com"
        
        # Mock expired token by creating with past expiry
        import jwt
        from datetime import timezone
        
        payload = {
            "user_id": user_id,
            "email": email,
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),  # Already expired
            "iat": datetime.now(timezone.utc) - timedelta(minutes=2)
        }
        
        expired_token = jwt.encode(payload, auth_config.SECRET_KEY, algorithm=auth_config.ALGORITHM)
        
        # Verification should fail
        with pytest.raises(ValueError, match="Token has expired"):
            auth_service.verify_token(expired_token)
    
    @pytest.mark.asyncio
    async def test_password_change(self, auth_service, test_user_data):
        """Test password change"""
        # Register user
        user = await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Change password
        new_password = "NewPassword456!"
        await auth_service.change_password(
            user.id,
            test_user_data.password,
            new_password,
            "127.0.0.1",
            "test-agent"
        )
        
        # Login with new password should work
        updated_user = await auth_service.login_user(
            test_user_data.email,
            new_password,
            "127.0.0.1",
            "test-agent"
        )
        
        assert updated_user.email == test_user_data.email
    
    @pytest.mark.asyncio
    async def test_audit_logging(self, auth_service, test_user_data):
        """Test audit logging"""
        # Register user
        user = await auth_service.register_user(test_user_data, "127.0.0.1", "test-agent")
        
        # Perform login to generate audit log
        await auth_service.login_user(
            test_user_data.email,
            test_user_data.password,
            "127.0.0.1",
            "test-agent"
        )
        
        # Check audit logs
        logs = await auth_service.get_audit_logs(user_id=user.id, limit=10)
        
        assert len(logs) > 0
        assert any(log.action == "register" for log in logs)
        assert any(log.action == "login" for log in logs)

# Integration tests for API endpoints
class TestAuthenticationAPI:
    """Test authentication API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from app import app
        return TestClient(app)
    
    def test_register_endpoint(self, client):
        """Test registration endpoint"""
        user_data = {
            "email": "api_test@example.com",
            "password": "TestPassword123!",
            "full_name": "API Test User",
            "phone_number": "+254700000000"
        }
        
        response = client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == user_data["email"]
    
    def test_login_endpoint(self, client):
        """Test login endpoint"""
        # First register a user
        user_data = {
            "email": "login_test@example.com",
            "password": "TestPassword123!",
            "full_name": "Login Test User"
        }
        
        client.post("/api/auth/register", json=user_data)
        
        # Then login
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        response = client.post("/api/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == user_data["email"]
    
    def test_protected_endpoint_access(self, client):
        """Test accessing protected endpoint"""
        # Register and login to get token
        user_data = {
            "email": "protected_test@example.com",
            "password": "TestPassword123!",
            "full_name": "Protected Test User"
        }
        
        register_response = client.post("/api/auth/register", json=user_data)
        token = register_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == user_data["email"]
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])