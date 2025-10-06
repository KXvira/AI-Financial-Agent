# Authentication System Documentation

## Overview

The AI Financial Agent implements a comprehensive JWT-based authentication system to secure API endpoints and manage user access. The system includes user registration, login, role-based access control, password security, account protection, and audit logging.

## Architecture

### Components

1. **Models** (`auth/models.py`)
   - User data models and validation schemas
   - JWT token models
   - Audit logging models

2. **Service** (`auth/service.py`)
   - Business logic for authentication operations
   - Password hashing and verification
   - JWT token management
   - Account security and lockout

3. **Middleware** (`auth/middleware.py`)
   - JWT token validation
   - User authentication dependencies
   - Role-based access control

4. **Router** (`auth/router.py`)
   - API endpoints for authentication
   - Request/response handling
   - Client IP and audit logging

5. **Configuration** (`auth/config.py`)
   - Environment-based settings
   - Security parameters
   - Database configuration

## Features

### User Management

- **Registration**: Create new user accounts with validation
- **Login**: Authenticate users with email/password
- **Profile Management**: Update user information
- **Password Management**: Secure password change with validation

### Security Features

- **JWT Tokens**: Stateless authentication with access/refresh tokens
- **Password Hashing**: bcrypt with salt for secure password storage
- **Account Lockout**: Protection against brute force attacks
- **Audit Logging**: Comprehensive tracking of security events
- **Role-Based Access**: Owner, Accountant, Employee roles

### Token System

- **Access Tokens**: Short-lived (30 minutes) for API access
- **Refresh Tokens**: Long-lived (7 days) for token renewal
- **Token Verification**: Signature and expiry validation
- **Automatic Refresh**: Seamless token renewal

## API Endpoints

### Public Endpoints

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "phone_number": "+254700000000",
  "business_name": "Doe Enterprises"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "owner",
    "is_active": true,
    "is_verified": false
  },
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/auth/login
Authenticate user with credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "owner",
    "is_active": true,
    "is_verified": false
  },
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response:**
```json
{
  "access_token": "new_jwt_access_token",
  "refresh_token": "new_jwt_refresh_token",
  "token_type": "bearer"
}
```

### Protected Endpoints

#### GET /api/auth/me
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer jwt_access_token
```

**Response:**
```json
{
  "id": "user_id",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "owner",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z",
  "phone_number": "+254700000000",
  "business_name": "Doe Enterprises"
}
```

#### PUT /api/auth/me
Update current user profile.

**Request Body:**
```json
{
  "full_name": "John H. Doe",
  "phone_number": "+254700000001",
  "business_name": "Doe & Associates"
}
```

#### POST /api/auth/change-password
Change user password.

**Request Body:**
```json
{
  "current_password": "CurrentPassword123!",
  "new_password": "NewPassword456!"
}
```

#### POST /api/auth/logout
Logout current user.

#### GET /api/auth/audit-logs
Get audit logs (owner role sees all, others see own).

#### GET /api/auth/health
Authentication service health check.

## Usage Examples

### Frontend Integration

```typescript
// API client setup
class AuthAPI {
  private baseURL = 'http://localhost:8000/api/auth';
  private token: string | null = null;

  async register(userData: RegisterData) {
    const response = await fetch(`${this.baseURL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData)
    });
    const data = await response.json();
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    
    if (data.access_token) {
      this.setToken(data.access_token);
    }
    
    return data;
  }

  async getCurrentUser() {
    return await this.authenticatedRequest('/me');
  }

  private async authenticatedRequest(endpoint: string, options?: RequestInit) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        ...options?.headers,
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.status === 401) {
      // Handle token refresh or redirect to login
      this.handleUnauthorized();
    }
    
    return response.json();
  }
}
```

### Backend Route Protection

```python
from fastapi import Depends, APIRouter
from auth import get_current_user, require_owner, User

router = APIRouter()

@router.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    """Route requires any authenticated user"""
    return {"message": f"Hello {user.email}"}

@router.post("/admin-only")
async def admin_route(user: User = Depends(require_owner)):
    """Route requires owner role"""
    return {"message": "Admin access granted"}

@router.get("/optional-auth")
async def optional_auth(user: User = Depends(get_current_user_optional)):
    """Route with optional authentication"""
    if user:
        return {"message": f"Welcome back {user.email}"}
    else:
        return {"message": "Welcome guest"}
```

## Configuration

### Environment Variables

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Settings
MAX_LOGIN_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION_MINUTES=30

# Database
MONGO_URI=mongodb://localhost:27017/financial_agent

# Email (for future email verification)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@finagent.com
```

### Password Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character

### Security Settings

- **Account Lockout**: 5 failed attempts lock account for 30 minutes
- **Token Expiry**: Access tokens expire in 30 minutes, refresh tokens in 7 days
- **Password Hashing**: bcrypt with automatic salt generation
- **Audit Logging**: All authentication events logged with IP and user agent

## Error Handling

### Common Error Responses

```json
{
  "detail": "Email already registered"
}
```

```json
{
  "detail": "Invalid email or password"
}
```

```json
{
  "detail": "Account is locked due to too many failed login attempts"
}
```

```json
{
  "detail": "Token has expired"
}
```

```json
{
  "detail": "Operation requires owner role"
}
```

## Testing

The authentication system includes comprehensive test coverage:

- **Unit Tests**: Service layer functions and JWT operations
- **Integration Tests**: API endpoints and database operations
- **Security Tests**: Password validation, account lockout, token security

Run tests:
```bash
pytest test_auth_system.py -v --asyncio-mode=auto
```

## Security Considerations

1. **Production Deployment**:
   - Use strong JWT secret key (32+ characters)
   - Enable HTTPS only in production
   - Configure proper CORS origins
   - Use secure cookie settings

2. **Database Security**:
   - Use MongoDB Atlas or secure self-hosted instance
   - Enable authentication and authorization
   - Use connection encryption (TLS/SSL)

3. **Rate Limiting**:
   - Implement rate limiting on authentication endpoints
   - Use IP-based and user-based limits
   - Consider using Redis for distributed rate limiting

4. **Monitoring**:
   - Monitor failed login attempts
   - Set up alerts for suspicious activity
   - Regular security audit log reviews

## Future Enhancements

1. **Email Verification**: Implement email verification for new accounts
2. **Two-Factor Authentication**: Add TOTP-based 2FA
3. **OAuth Integration**: Support Google/Facebook login
4. **Password Reset**: Email-based password reset flow
5. **Session Management**: Server-side session tracking and revocation
6. **Advanced Security**: Device fingerprinting, IP geolocation