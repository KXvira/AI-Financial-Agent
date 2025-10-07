"""
Simple test to debug the registration endpoint error
"""
import requests
import subprocess
import time
import os

def test_registration_debug():
    """Debug the registration endpoint"""
    print("🔍 DEBUGGING REGISTRATION ENDPOINT")
    print("=" * 50)
    
    # Start server
    print("🚀 Starting server...")
    os.chdir("/home/munga/Desktop/AI-Financial-Agent/backend")
    
    server_process = subprocess.Popen([
        "/home/munga/Desktop/AI-Financial-Agent/sprint7_env/bin/python",
        "-m", "uvicorn", "app:app", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Wait for server to start
    time.sleep(10)
    
    try:
        # Test registration
        print("📧 Testing registration...")
        response = requests.post(
            "http://localhost:8000/api/auth/register",
            json={
                "email": "debug_test@finagent.com",
                "password": "TestPassword123!",
                "confirm_password": "TestPassword123!", 
                "company_name": "Debug Test Company",
                "phone_number": "+254712345678",
                "role": "owner"
            },
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Get server logs
        print("\n📋 Server Output:")
        stdout, stderr = server_process.communicate(timeout=2)
        if stdout:
            print("STDOUT:", stdout[-1000:])  # Last 1000 chars
        if stderr:
            print("STDERR:", stderr[-1000:])
            
    except subprocess.TimeoutExpired:
        print("Server still running, getting partial output...")
        try:
            partial_output = server_process.stdout.read(1000)
            print("Partial output:", partial_output)
        except:
            print("Could not read server output")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Kill server
        server_process.terminate()
        server_process.wait()
        print("🛑 Server stopped")

if __name__ == "__main__":
    test_registration_debug()