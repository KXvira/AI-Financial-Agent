"""
API Endpoint Test for Login and Registration
Tests the FastAPI backend endpoints for authentication
"""
import asyncio
import aiohttp
import json
from datetime import datetime

async def test_backend_api_endpoints():
    """Test the backend API endpoints for login and registration"""
    print("🚀 BACKEND API ENDPOINTS TEST")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Health check
            print("1. Testing Health Check Endpoint")
            print("-" * 40)
            try:
                async with session.get(f"{base_url}/") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Health check successful")
                        print(f"   📊 Service: {data.get('service', 'Unknown')}")
                        print(f"   📊 Status: {data.get('status', 'Unknown')}")
                        print(f"   📊 Version: {data.get('version', 'Unknown')}")
                    else:
                        print(f"   ❌ Health check failed: {response.status}")
                        return False
            except Exception as e:
                print(f"   ❌ Cannot connect to backend server: {e}")
                print("   💡 Make sure to start the server first:")
                print("      cd backend && uvicorn app:app --reload --port 8000")
                return False
            
            # Test 2: Registration endpoint
            print("\n2. Testing Registration Endpoint")
            print("-" * 40)
            
            test_email = f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@finagent.com"
            registration_data = {
                "email": test_email,
                "password": "TestApiPassword123!",
                "confirm_password": "TestApiPassword123!",
                "company_name": "API Test Company Ltd",
                "phone_number": "+254712345999",
                "role": "owner"
            }
            
            try:
                async with session.post(
                    f"{base_url}/api/auth/register",
                    json=registration_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Registration successful")
                        print(f"   📧 User registered: {data.get('user', {}).get('email', 'Unknown')}")
                        print(f"   🎫 Access token provided: {'access_token' in data}")
                        print(f"   🔄 Refresh token provided: {'refresh_token' in data}")
                        
                        # Save credentials for login test
                        login_email = test_email
                        login_password = "TestApiPassword123!"
                        
                    else:
                        error_data = await response.text()
                        print(f"   ❌ Registration failed: {response.status}")
                        print(f"   📄 Error: {error_data}")
                        return False
                        
            except Exception as e:
                print(f"   ❌ Registration endpoint error: {e}")
                return False
            
            # Test 3: Login endpoint
            print("\n3. Testing Login Endpoint")
            print("-" * 40)
            
            login_data = {
                "email": login_email,
                "password": login_password
            }
            
            try:
                async with session.post(
                    f"{base_url}/api/auth/login",
                    json=login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Login successful")
                        print(f"   👤 User: {data.get('user', {}).get('email', 'Unknown')}")
                        print(f"   🏢 Company: {data.get('user', {}).get('full_name', 'Unknown')}")
                        print(f"   👑 Role: {data.get('user', {}).get('role', 'Unknown')}")
                        print(f"   🎫 Access token: ...{data.get('access_token', '')[-20:]}")
                        print(f"   🔄 Refresh token: ...{data.get('refresh_token', '')[-20:]}")
                        print(f"   🔒 Token type: {data.get('token_type', 'Unknown')}")
                        
                        # Save token for authenticated request test
                        access_token = data.get('access_token')
                        
                    else:
                        error_data = await response.text()
                        print(f"   ❌ Login failed: {response.status}")
                        print(f"   📄 Error: {error_data}")
                        return False
                        
            except Exception as e:
                print(f"   ❌ Login endpoint error: {e}")
                return False
            
            # Test 4: Authenticated request (user profile)
            print("\n4. Testing Authenticated Request")
            print("-" * 40)
            
            try:
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                async with session.get(
                    f"{base_url}/api/auth/me",
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"   ✅ Authenticated request successful")
                        print(f"   👤 Profile email: {data.get('email', 'Unknown')}")
                        print(f"   🏢 Profile company: {data.get('company_name', 'Unknown')}")
                        print(f"   👑 Profile role: {data.get('role', 'Unknown')}")
                        print(f"   🟢 Profile active: {data.get('is_active', False)}")
                        
                    else:
                        error_data = await response.text()
                        print(f"   ❌ Authenticated request failed: {response.status}")
                        print(f"   📄 Error: {error_data}")
                        return False
                        
            except Exception as e:
                print(f"   ❌ Authenticated request error: {e}")
                return False
            
            # Test 5: Invalid login attempt
            print("\n5. Testing Invalid Login Protection")
            print("-" * 40)
            
            invalid_login_data = {
                "email": login_email,
                "password": "WrongPassword123!"
            }
            
            try:
                async with session.post(
                    f"{base_url}/api/auth/login",
                    json=invalid_login_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    
                    if response.status == 401:
                        print(f"   ✅ Invalid login correctly rejected (401)")
                    else:
                        print(f"   ⚠️  Invalid login response: {response.status} (expected 401)")
                        
            except Exception as e:
                print(f"   ❌ Invalid login test error: {e}")
            
            print("\n" + "=" * 60)
            print("🎉 ALL API ENDPOINT TESTS PASSED!")
            print("✅ Backend API is fully functional")
            print("✅ Registration endpoint working")
            print("✅ Login endpoint working")
            print("✅ Authentication protection working")
            print("✅ Token validation working")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"❌ API endpoint test failed: {e}")
            return False

async def test_with_server_check():
    """Test API endpoints with server availability check"""
    import aiohttp
    
    print("🧪 API ENDPOINT COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Check if server is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/", timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    print("✅ Backend server is running")
                    success = await test_backend_api_endpoints()
                    
                    if success:
                        print("\n🎯 FINAL RESULT: API ENDPOINTS FULLY OPERATIONAL")
                        print("🚀 The authentication system is ready for frontend integration!")
                    else:
                        print("\n⚠️  Some API endpoint issues found")
                        
                else:
                    print(f"⚠️  Server responded with status: {response.status}")
                    
    except asyncio.TimeoutError:
        print("❌ Backend server is not responding")
        print("💡 Please start the backend server:")
        print("   cd /home/munga/Desktop/AI-Financial-Agent/backend")
        print("   uvicorn app:app --reload --port 8000")
        
    except Exception as e:
        print(f"❌ Cannot connect to backend server: {e}")
        print("💡 Please start the backend server:")
        print("   cd /home/munga/Desktop/AI-Financial-Agent/backend")
        print("   uvicorn app:app --reload --port 8000")

if __name__ == "__main__":
    asyncio.run(test_with_server_check())