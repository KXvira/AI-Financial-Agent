#!/usr/bin/env python3
"""
Comprehensive test script for the Full-Stack AI Financial Insights Service
"""

import requests
import json
import time
from datetime import datetime
import webbrowser
import subprocess
import os

def test_fullstack_service():
    """Test the full-stack AI service functionality"""
    print("🚀 Testing Full-Stack AI Financial Insights Service")
    print("=" * 70)
    
    base_url = "http://localhost:8002"
    
    # Test 1: Health Check
    print("\n1. 🏥 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/ai/health")
        if response.status_code == 200:
            health_data = response.json()
            print("   ✅ Health check passed")
            print(f"   📋 Status: {health_data.get('status', 'unknown')}")
            print(f"   💾 Database: {health_data.get('database', 'unknown')}")
            print(f"   🤖 Gemini API: {health_data.get('gemini_api', 'unknown')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Financial Stats API
    print("\n2. 📊 Testing Financial Stats API...")
    try:
        response = requests.get(f"{base_url}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Stats API working")
            print(f"   💰 Revenue: {stats.get('revenue', 'N/A')}")
            print(f"   📄 Overdue: {stats.get('overdue_invoices', 'N/A')}")
            print(f"   ✅ Success Rate: {stats.get('payment_success_rate', 'N/A')}")
        else:
            print(f"   ❌ Stats API failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats API error: {e}")
    
    # Test 3: Frontend Accessibility
    print("\n3. 🌐 Testing Frontend Accessibility...")
    try:
        response = requests.get(base_url)
        if response.status_code == 200:
            print("   ✅ Frontend is accessible")
            print(f"   📄 Content length: {len(response.content)} bytes")
            if "AI Financial Insights" in response.text:
                print("   ✅ Frontend content verified")
            else:
                print("   ⚠️  Frontend content may be incomplete")
        else:
            print(f"   ❌ Frontend not accessible: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    # Test 4: AI Query Functionality
    print("\n4. 🤖 Testing AI Query Functionality...")
    
    test_queries = [
        {
            "query": "What is my current financial status?",
            "expected_keywords": ["revenue", "invoices", "transactions", "KES"]
        },
        {
            "query": "Are there any overdue invoices I should be concerned about?",
            "expected_keywords": ["INV-2025-071", "INV-2025-073", "overdue", "KES"]
        },
        {
            "query": "How is my payment collection performance?",
            "expected_keywords": ["payment", "successful", "98%", "transactions"]
        },
        {
            "query": "What are my revenue trends over the last two months?",
            "expected_keywords": ["June", "July", "2025", "revenue", "decline"]
        }
    ]
    
    success_count = 0
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n   Test 4.{i}: {test_case['query'][:50]}...")
        
        try:
            response = requests.post(
                f"{base_url}/ai/ask",
                json={
                    "query": test_case["query"],
                    "user_id": f"test_user_{i}"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")
                
                # Check if expected keywords are in the response
                keyword_found = any(keyword.lower() in answer.lower() 
                                  for keyword in test_case["expected_keywords"])
                
                if keyword_found and len(answer) > 50:
                    print(f"   ✅ AI query successful")
                    print(f"   📝 Response preview: {answer[:120]}...")
                    success_count += 1
                else:
                    print(f"   ⚠️  Query returned but may lack expected content")
                    print(f"   📝 Response preview: {answer[:120]}...")
                    
            else:
                print(f"   ❌ AI query failed: {response.status_code}")
                if response.content:
                    print(f"   📝 Error: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"   ❌ AI query error: {e}")
    
    # Test 5: API Documentation
    print("\n5. 📚 Testing API Documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("   ✅ API documentation accessible")
            print(f"   📋 Documentation URL: {base_url}/docs")
        else:
            print(f"   ❌ API documentation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API documentation error: {e}")
    
    # Summary
    total_ai_tests = len(test_queries)
    print("\n" + "=" * 70)
    print("📊 Full-Stack Test Summary")
    print("=" * 70)
    print(f"AI Queries: {success_count}/{total_ai_tests} successful")
    
    if success_count == total_ai_tests:
        print("🎉 All AI tests passed! Full-stack service is working correctly.")
        return True
    else:
        print("⚠️  Some tests had issues. Check the responses above.")
        return False

def demonstrate_fullstack_features():
    """Demonstrate the full-stack features"""
    print("\n🔍 Full-Stack Features Demonstration")
    print("=" * 70)
    
    print("\n📖 Full-Stack Architecture Overview:")
    print("1. 🖥️  FRONTEND: Interactive web interface with Tailwind CSS")
    print("   - Chat-based AI interaction")
    print("   - Financial dashboard with real-time stats")
    print("   - Quick question buttons")
    print("   - Responsive design")
    
    print("\n2. 🚀 BACKEND: FastAPI server with AI integration")
    print("   - RAG architecture for intelligent responses")
    print("   - MongoDB integration (with fallback to mock data)")
    print("   - Google Gemini AI for natural language processing")
    print("   - RESTful API endpoints")
    
    print("\n3. 🔗 INTEGRATION: Seamless frontend-backend communication")
    print("   - CORS middleware for cross-origin requests")
    print("   - Static file serving for frontend assets")
    print("   - Real-time chat interface")
    print("   - Error handling and loading states")
    
    print("\n4. 📊 FEATURES:")
    print("   - Conversational AI for financial queries")
    print("   - Real-time financial dashboard")
    print("   - Invoice and payment analysis")
    print("   - Revenue trend analysis")
    print("   - Interactive web interface")

def open_browser_demo():
    """Open the browser to demonstrate the interface"""
    base_url = "http://localhost:8002"
    print(f"\n🌐 Opening browser demo at {base_url}")
    
    try:
        webbrowser.open(base_url)
        print("✅ Browser opened successfully")
        print("\n💡 Try these demo queries in the web interface:")
        print("   • 'What is my current financial status?'")
        print("   • 'Are there any overdue invoices?'")
        print("   • 'How are my payment collections performing?'")
        print("   • 'What are my revenue trends?'")
    except Exception as e:
        print(f"❌ Could not open browser: {e}")
        print(f"   Please manually open: {base_url}")

def check_server_status():
    """Check if the server is running"""
    try:
        response = requests.get("http://localhost:8002/ai/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print(f"🕐 Full-Stack Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    if check_server_status():
        print("✅ Server is running on port 8002")
        
        # Run comprehensive tests
        success = test_fullstack_service()
        
        # Demonstrate features
        demonstrate_fullstack_features()
        
        # Open browser demo if tests passed
        if success:
            print("\n🎯 Next Steps:")
            print("1. Open http://localhost:8002 to use the web interface")
            print("2. Test the chat functionality with financial queries")
            print("3. Explore the API documentation at http://localhost:8002/docs")
            print("4. Integrate with Diana's frontend components")
            print("5. Connect to real MongoDB data for production")
            
            # Ask if user wants to open browser
            try:
                user_input = input("\n🌐 Would you like to open the web interface now? (y/n): ")
                if user_input.lower() in ['y', 'yes']:
                    open_browser_demo()
            except KeyboardInterrupt:
                print("\n👋 Test completed")
        else:
            print("\n🔧 Troubleshooting:")
            print("1. Ensure the server is running: python fullstack_main.py")
            print("2. Check your Gemini API key configuration")
            print("3. Verify port 8002 is not blocked")
            print("4. Check the server logs for detailed errors")
    else:
        print("❌ Server is not running on port 8002")
        print("🚀 Start the server with: python fullstack_main.py")
        print("   Then run this test again")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
