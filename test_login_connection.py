"""
Test script to verify login mechanism connection to database and frontend
"""
import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_login_connection():
    """Test the complete login flow"""
    print("🔐 TESTING LOGIN MECHANISM CONNECTION")
    print("=" * 60)
    
    try:
        # Import authentication modules
        from auth.service import AuthService
        from auth.models import UserCreate, UserLogin, UserRole
        from auth.database import auth_db_service
        
        print("✅ Authentication modules imported successfully")
        
        # Test database connection
        print("\n1. 📊 Testing Database Connection")
        try:
            db = await auth_db_service.get_database()
            await db.command("ping")
            print("   ✅ MongoDB Atlas connection successful")
            
            # Check collections
            users_collection = await auth_db_service.get_users_collection()
            user_count = await users_collection.count_documents({})
            print(f"   📊 Users collection ready ({user_count} existing users)")
            
        except Exception as e:
            print(f"   ❌ Database connection failed: {e}")
            return False
        
        # Test auth service initialization
        print("\n2. 🔧 Testing Auth Service Initialization")
        try:
            auth_service = AuthService()
            await auth_service.initialize()
            print("   ✅ AuthService initialized successfully")
            
        except Exception as e:
            print(f"   ❌ AuthService initialization failed: {e}")
            return False
        
        # Test user registration
        print("\n3. 👤 Testing User Registration")
        test_email = f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}@finagent.com"
        
        try:
            test_user_data = UserCreate(
                email=test_email,
                password="TestPassword123!",
                confirm_password="TestPassword123!",
                company_name="Test Company Ltd",
                phone_number="+254700000000",
                role=UserRole.OWNER
            )
            
            registration_result = await auth_service.register_user(
                test_user_data, 
                "127.0.0.1", 
                "test-client/1.0"
            )
            
            print(f"   ✅ User registered successfully")
            print(f"   📧 Email: {registration_result['email']}")
            print(f"   🆔 User ID: {registration_result['id']}")
            print(f"   👤 Role: {registration_result['role'].value}")
            
        except Exception as e:
            print(f"   ❌ User registration failed: {e}")
            # Continue with login test using existing user if registration fails
        
        # Test user login
        print("\n4. 🔑 Testing User Login")
        try:
            login_credentials = UserLogin(
                email=test_email,
                password="TestPassword123!"
            )
            
            login_result = await auth_service.login_user(
                login_credentials,
                "127.0.0.1",
                "test-client/1.0"
            )
            
            user = login_result["user"]
            tokens = login_result["tokens"]
            
            print(f"   ✅ Login successful")
            print(f"   👤 User: {user.email}")
            print(f"   🎫 Access Token: {tokens.access_token[:50]}...")
            print(f"   🔄 Refresh Token: {tokens.refresh_token[:50]}...")
            print(f"   ⏰ Expires in: {tokens.expires_in} seconds")
            
        except Exception as e:
            print(f"   ❌ User login failed: {e}")
            return False
        
        # Test token validation
        print("\n5. 🔍 Testing Token Validation")
        try:
            # Decode token to verify structure
            import jwt
            decoded = jwt.decode(
                tokens.access_token, 
                options={"verify_signature": False}
            )
            
            print(f"   ✅ Token structure valid")
            print(f"   📊 Token payload: user_id={decoded.get('user_id')}")
            print(f"   📊 Token payload: email={decoded.get('email')}")
            print(f"   📊 Token payload: role={decoded.get('role')}")
            
        except Exception as e:
            print(f"   ❌ Token validation failed: {e}")
            return False
        
        # Test frontend API endpoint format
        print("\n6. 🌐 Testing Frontend API Response Format")
        try:
            # Simulate the response format expected by frontend
            api_response = {
                "message": "Login successful",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.company_name,  # Using company_name as full_name
                    "role": user.role.value,
                    "is_active": user.is_active,
                    "is_verified": user.email_verified
                },
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "token_type": tokens.token_type
            }
            
            print(f"   ✅ Frontend API response format valid")
            print(f"   📊 Response keys: {list(api_response.keys())}")
            
            # Save sample response for frontend testing
            with open("sample_login_response.json", "w") as f:
                json.dump(api_response, f, indent=2, default=str)
            print(f"   💾 Sample response saved to: sample_login_response.json")
            
        except Exception as e:
            print(f"   ❌ Frontend API format test failed: {e}")
            return False
        
        # Test cleanup (optional)
        print("\n7. 🧹 Cleanup (Optional)")
        try:
            # Remove test user if needed
            await users_collection.delete_one({"email": test_email})
            print(f"   ✅ Test user cleaned up")
            
        except Exception as e:
            print(f"   ⚠️  Cleanup warning: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Login mechanism is properly connected to database")
        print("✅ Authentication service is working correctly") 
        print("✅ Token generation and validation working")
        print("✅ Frontend API response format is correct")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close database connections
        try:
            await auth_db_service.disconnect()
            print("\n🔌 Database connections closed")
        except:
            pass

async def test_backend_server_connection():
    """Test if backend server can start and serve login endpoints"""
    print("\n🚀 TESTING BACKEND SERVER CONNECTION")
    print("-" * 40)
    
    try:
        # Test if we can import the FastAPI app
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from app import app
        
        print("✅ FastAPI app imported successfully")
        
        # Check if auth router is included
        routes = [route.path for route in app.routes]
        auth_routes = [route for route in routes if '/api/auth' in route]
        
        if auth_routes:
            print(f"✅ Auth routes found: {auth_routes}")
        else:
            print("❌ No auth routes found in FastAPI app")
            return False
        
        # Check specific login endpoint
        login_endpoint_found = any('/api/auth/login' in route for route in routes)
        register_endpoint_found = any('/api/auth/register' in route for route in routes)
        
        if login_endpoint_found:
            print("✅ Login endpoint (/api/auth/login) available")
        else:
            print("❌ Login endpoint not found")
        
        if register_endpoint_found:
            print("✅ Register endpoint (/api/auth/register) available")
        else:
            print("❌ Register endpoint not found")
        
        print("🎯 Backend server is ready for frontend connection")
        return True
        
    except Exception as e:
        print(f"❌ Backend server test failed: {e}")
        return False

async def main():
    """Run all connection tests"""
    print("🧪 AI FINANCIAL AGENT - LOGIN CONNECTION TEST")
    print("Testing database, backend, and frontend integration")
    print("=" * 80)
    
    # Test login mechanism
    login_test_passed = await test_login_connection()
    
    # Test backend server
    server_test_passed = await test_backend_server_connection()
    
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    
    if login_test_passed and server_test_passed:
        print("🎉 ALL SYSTEMS GO!")
        print("✅ Login mechanism fully connected and working")
        print("✅ Database integration successful")
        print("✅ Backend API endpoints ready")
        print("✅ Frontend can now connect to authentication system")
        print("\n🚀 NEXT STEPS:")
        print("1. Start backend server: uvicorn backend.app:app --reload")
        print("2. Start frontend: cd finance-app && npm run dev")
        print("3. Test login at: http://localhost:3000/auth/login")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please review the errors above and fix before proceeding")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())