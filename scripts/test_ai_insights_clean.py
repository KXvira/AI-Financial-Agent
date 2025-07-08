#!/usr/bin/env python3
"""
Test script for AI Insights Service

This script tests the AI insights endpoints to ensure they're working correctly.
Run this after starting the backend server to validate the AI functionality.

Usage:
    python scripts/test_ai_insights_clean.py
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Configuration
BASE_URL = "http://localhost:8000"
AI_ENDPOINTS = {
    "health": f"{BASE_URL}/ai/health",
    "status": f"{BASE_URL}/ai/status", 
    "ask": f"{BASE_URL}/ai/ask",
    "ask_advanced": f"{BASE_URL}/ai/ask-advanced",
    "examples": f"{BASE_URL}/ai/examples"
}

def test_service_status():
    """Test the AI service status endpoint"""
    print("🔍 Testing AI service status...")
    
    try:
        response = requests.get(AI_ENDPOINTS["status"])
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Service Status: {data.get('status', 'unknown')}")
            print(f"   Version: {data.get('version', 'unknown')}")
            print(f"   AI Model: {data.get('ai_model', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Is it running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Status check error: {str(e)}")
        return False

def test_health_check():
    """Test the AI service health endpoint"""
    print("\n🏥 Testing AI service health...")
    
    try:
        response = requests.get(AI_ENDPOINTS["health"])
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Status: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Gemini API: {data.get('gemini_api', 'unknown')}")
            return True
        elif response.status_code == 503:
            data = response.json()
            print(f"⚠️  Service unhealthy: {data.get('error', 'unknown error')}")
            return False
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_example_queries():
    """Test getting example queries"""
    print("\n📋 Testing example queries endpoint...")
    
    try:
        response = requests.get(AI_ENDPOINTS["examples"])
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Retrieved example queries:")
            
            categories = data.get("categories", {})
            for category, examples in categories.items():
                print(f"   {category.replace('_', ' ').title()}:")
                for example in examples[:2]:  # Show first 2 examples
                    print(f"     - {example}")
            
            return True
        else:
            print(f"❌ Examples endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Examples endpoint error: {str(e)}")
        return False

def test_ai_query(question: str, expected_keywords: list = None):
    """Test a basic AI query"""
    print(f"\n🤖 Testing AI query: '{question}'")
    
    try:
        query_data = {
            "query": question,
            "user_id": "test_user"
        }
        
        response = requests.post(
            AI_ENDPOINTS["ask"],
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI query successful:")
            print(f"   Answer preview: {data.get('answer', 'N/A')[:100]}...")
            
            if expected_keywords:
                answer = data.get('answer', '').lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer]
                if found_keywords:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Expected keywords not found: {expected_keywords}")
            
            return True
        else:
            print(f"❌ AI query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ AI query error: {str(e)}")
        return False

def test_ai_advanced_query(question: str, expected_keywords: list = None):
    """Test an advanced AI query with detailed response"""
    print(f"\n🧠 Testing advanced AI query: '{question}'")
    
    try:
        query_data = {
            "question": question,
            "context": "test query",
            "date_range": {
                "start": (datetime.now() - timedelta(days=30)).isoformat(),
                "end": datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            AI_ENDPOINTS["ask_advanced"],
            json=query_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Advanced AI query successful:")
            print(f"   Question: {data.get('question', 'N/A')}")
            print(f"   Answer preview: {data.get('answer', 'N/A')[:100]}...")
            print(f"   Confidence: {data.get('confidence', 0):.2f}")
            print(f"   Data sources: {data.get('data_sources', [])}")
            
            if expected_keywords:
                answer = data.get('answer', '').lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in answer]
                if found_keywords:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Expected keywords not found: {expected_keywords}")
            
            return True
        else:
            print(f"❌ Advanced AI query failed: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Advanced AI query error: {str(e)}")
        return False

def main():
    """Run all AI insights tests"""
    print("🚀 AI Financial Insights Service Tests")
    print("=" * 50)
    
    # Test sequence
    tests = [
        ("Service Status", test_service_status),
        ("Health Check", test_health_check),
        ("Example Queries", test_example_queries),
    ]
    
    # AI query tests
    ai_queries = [
        ("What are my spending patterns?", ["spending", "patterns", "analysis"]),
        ("Show me my financial summary", ["financial", "summary", "total"]),
        ("How much revenue did I generate?", ["revenue", "generated", "income"]),
    ]
    
    # Run basic tests
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
    
    # Run AI query tests
    print("\n" + "=" * 50)
    print("🧠 Testing AI Query Functionality")
    print("=" * 50)

    ai_passed = 0
    for question, keywords in ai_queries:
        if test_ai_query(question, keywords):
            ai_passed += 1

    # Run advanced AI query tests
    print("\n🔬 Testing Advanced AI Query Functionality")
    print("-" * 50)

    advanced_ai_passed = 0
    for question, keywords in ai_queries:
        if test_ai_advanced_query(question, keywords):
            advanced_ai_passed += 1

    total_ai = len(ai_queries)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Basic Tests: {passed}/{total} passed")
    print(f"Basic AI Queries: {ai_passed}/{total_ai} passed")
    print(f"Advanced AI Queries: {advanced_ai_passed}/{total_ai} passed")

    overall_success = (passed == total) and (ai_passed > 0)

    if overall_success:
        print("🎉 AI Insights Service is working correctly!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the logs above.")
        if passed < total:
            print("   - Basic service endpoints may not be working")
        if ai_passed == 0:
            print("   - Basic AI query functionality is not working")
        if advanced_ai_passed == 0:
            print("   - Advanced AI query functionality is not working")
            print("   - Check your Gemini API key and database connection")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
