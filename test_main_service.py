#!/usr/bin/env python3
"""
Test script for the standalone main.py AI Financial Insights Service
"""

import requests
import json
from datetime import datetime

def test_ai_service():
    """Test the AI service functionality"""
    print("🚀 Testing AI-Powered Financial Insights Service")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Test health check
    print("\n1. 🏥 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📋 Status: {response.json()['status']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test sample queries
    test_queries = [
        {
            "query": "What is my current financial status?",
            "expected_keywords": ["revenue", "invoices", "transactions"]
        },
        {
            "query": "How are my payment collections performing?",
            "expected_keywords": ["overdue", "invoices", "payment"]
        },
        {
            "query": "What are my revenue trends?",
            "expected_keywords": ["June", "July", "KES"]
        },
        {
            "query": "Are there any overdue invoices?",
            "expected_keywords": ["INV-2025-071", "INV-2025-073", "overdue"]
        }
    ]
    
    print("\n2. 🤖 Testing AI Query Functionality...")
    success_count = 0
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n   Test {i}: {test_case['query']}")
        
        try:
            response = requests.post(
                f"{base_url}/ai/ask",
                json={
                    "query": test_case["query"],
                    "user_id": "test_user_123"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("answer", "")
                
                # Check if expected keywords are in the response
                keyword_found = any(keyword.lower() in answer.lower() 
                                  for keyword in test_case["expected_keywords"])
                
                if keyword_found and len(answer) > 50:
                    print(f"   ✅ Query successful")
                    print(f"   📝 Response: {answer[:100]}...")
                    success_count += 1
                else:
                    print(f"   ⚠️  Query returned but may not be comprehensive")
                    print(f"   📝 Response: {answer[:100]}...")
                    
            else:
                print(f"   ❌ Query failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Query error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"AI Queries: {success_count}/{len(test_queries)} successful")
    
    if success_count == len(test_queries):
        print("🎉 All tests passed! AI service is working correctly.")
        return True
    else:
        print("⚠️  Some tests had issues. Check the responses above.")
        return False

def demonstrate_rag_architecture():
    """Demonstrate how the RAG architecture works"""
    print("\n🔍 RAG Architecture Demonstration")
    print("=" * 60)
    
    print("\n📖 How the AI Financial Insights Service Works:")
    print("1. 🗂️  RETRIEVAL: Fetches financial data from multiple sources")
    print("   - Biggie's invoices collection")
    print("   - Muchamo's transactions collection") 
    print("   - Munga's analytics_cache collection")
    
    print("\n2. 🧠 GENERATION: Uses Gemini AI to analyze and respond")
    print("   - Processes the retrieved context")
    print("   - Generates intelligent insights")
    print("   - Provides actionable recommendations")
    
    print("\n3. 📊 RESULT: Delivers comprehensive financial analysis")
    print("   - Revenue trends and patterns")
    print("   - Outstanding invoice analysis")
    print("   - Payment health assessment")
    
    print("\n💡 Example Query Process:")
    print("   Query: 'What is my current financial status?'")
    print("   ↓")
    print("   Retrieval: Collects revenue data, overdue invoices, transaction stats")
    print("   ↓")
    print("   Generation: AI analyzes patterns and trends")
    print("   ↓")
    print("   Response: Comprehensive financial health assessment")

if __name__ == "__main__":
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run the tests
    success = test_ai_service()
    
    # Demonstrate RAG architecture
    demonstrate_rag_architecture()
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("\n🎯 Next Steps:")
        print("1. Visit http://localhost:8001/docs to explore the API")
        print("2. Integrate with your frontend application")
        print("3. Connect to real MongoDB data for production")
        print("4. Add more sophisticated retrieval logic")
        print("5. Implement caching for better performance")
    else:
        print("\n🔧 Troubleshooting:")
        print("1. Check if the server is running on port 8001")
        print("2. Verify your Gemini API key is configured")
        print("3. Check the server logs for error details")
