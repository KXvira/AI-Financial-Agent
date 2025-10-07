"""
Frontend Integration Test - Test actual HTTP endpoints
"""
import requests
import json
import time
import asyncio
import subprocess
import os
import signal
from typing import Optional

class BackendServerTest:
    """Test the backend server HTTP endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.server_process: Optional[subprocess.Popen] = None
    
    def start_server(self) -> bool:
        """Start the backend server"""
        try:
            print("🚀 Starting Backend Server...")
            
            # Change to the backend directory for proper imports
            os.chdir("/home/munga/Desktop/AI-Financial-Agent/backend")
            
            # Start server process from backend directory
            self.server_process = subprocess.Popen([
                "/home/munga/Desktop/AI-Financial-Agent/sprint7_env/bin/python",
                "-m", "uvicorn", "app:app", "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for server to start
            print("   ⏳ Waiting for server to start...")
            time.sleep(8)
            
            # Test if server is responding
            try:
                response = requests.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    print("   ✅ Server started successfully")
                    return True
                else:
                    print(f"   ❌ Server returned status {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Server not responding: {e}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to start server: {e}")
            return False
    
    def stop_server(self):
        """Stop the backend server"""
        if self.server_process:
            print("🛑 Stopping Backend Server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("   ✅ Server stopped")
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint"""
        try:
            print("\n1. 🌐 Testing Root Endpoint")
            response = requests.get(f"{self.base_url}/", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Root endpoint working")
                print(f"   📊 Status: {data.get('status')}")
                print(f"   📊 Service: {data.get('service')}")
                print(f"   📊 Version: {data.get('version')}")
                return True
            else:
                print(f"   ❌ Root endpoint failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Root endpoint error: {e}")
            return False
    
    def test_auth_registration(self) -> tuple[bool, dict]:
        """Test user registration endpoint"""
        try:
            print("\n2. 👤 Testing User Registration")
            
            # Create test user data
            user_data = {
                "email": f"frontend_test_{int(time.time())}@finagent.com",
                "password": "FrontendTest123!",
                "confirm_password": "FrontendTest123!",
                "company_name": "Frontend Test Company",
                "phone_number": "+254712345678",
                "role": "owner"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json=user_data,
                timeout=15
            )
            
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Registration successful")
                print(f"   📧 Email: {data.get('user', {}).get('email')}")
                print(f"   🆔 User ID: {data.get('user', {}).get('id')}")
                return True, data
            else:
                print(f"   ❌ Registration failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False, {}
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Registration error: {e}")
            return False, {}
    
    def test_auth_login(self, user_data: dict) -> tuple[bool, dict]:
        """Test user login endpoint"""
        try:
            print("\n3. 🔑 Testing User Login")
            
            login_data = {
                "email": user_data.get("user", {}).get("email"),
                "password": "FrontendTest123!"
            }
            
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json=login_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Login successful")
                print(f"   👤 User: {data.get('user', {}).get('email')}")
                print(f"   🎫 Access Token: ...{data.get('access_token', '')[-20:]}")
                print(f"   🔄 Token Type: {data.get('token_type')}")
                return True, data
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False, {}
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Login error: {e}")
            return False, {}
    
    def test_protected_endpoint(self, login_data: dict) -> bool:
        """Test accessing a protected endpoint with the token"""
        try:
            print("\n4. 🔒 Testing Protected Endpoint")
            
            headers = {
                "Authorization": f"Bearer {login_data.get('access_token')}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/api/auth/me",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Protected endpoint accessible")
                print(f"   👤 Current user: {data.get('email')}")
                print(f"   🏢 Company: {data.get('company_name')}")
                return True
            else:
                print(f"   ❌ Protected endpoint failed: {response.status_code}")
                print(f"   📄 Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Protected endpoint error: {e}")
            return False
    
    def run_full_test(self) -> bool:
        """Run the complete frontend integration test"""
        print("🧪 FRONTEND INTEGRATION TEST")
        print("Testing HTTP endpoints for frontend connection")
        print("=" * 80)
        
        try:
            # Start server
            if not self.start_server():
                return False
            
            # Test root endpoint
            if not self.test_root_endpoint():
                return False
            
            # Test registration
            reg_success, reg_data = self.test_auth_registration()
            if not reg_success:
                return False
            
            # Test login
            login_success, login_data = self.test_auth_login(reg_data)
            if not login_success:
                return False
            
            # Test protected endpoint
            if not self.test_protected_endpoint(login_data):
                return False
            
            print("\n" + "=" * 80)
            print("🎉 FRONTEND INTEGRATION TEST SUCCESSFUL!")
            print("=" * 80)
            print("✅ Backend server is running and accessible")
            print("✅ User registration endpoint working")
            print("✅ User login endpoint working")
            print("✅ JWT token authentication working")
            print("✅ Protected endpoints accessible with token")
            print("\n🔗 FRONTEND CONNECTION READY!")
            print("📋 Frontend can now connect to:")
            print(f"   • Registration: POST {self.base_url}/api/auth/register")
            print(f"   • Login: POST {self.base_url}/api/auth/login")
            print(f"   • Profile: GET {self.base_url}/api/auth/me")
            print("=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ FRONTEND INTEGRATION TEST FAILED: {e}")
            return False
        
        finally:
            # Always stop the server
            self.stop_server()

def main():
    """Run the frontend integration test"""
    tester = BackendServerTest()
    success = tester.run_full_test()
    
    if success:
        print("\n🎯 RESULT: LOGIN MECHANISM SUCCESSFULLY CONNECTED!")
        print("✅ Database ↔ Backend ↔ Frontend integration is complete")
        print("🚀 Ready for frontend development!")
    else:
        print("\n⚠️  RESULT: INTEGRATION TEST FAILED")
        print("❌ Please check the errors above and fix before proceeding")

if __name__ == "__main__":
    main()