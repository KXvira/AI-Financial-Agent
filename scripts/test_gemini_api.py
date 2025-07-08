#!/usr/bin/env python3
"""
Test script to verify Gemini API key functionality

This script tests if the Gemini API key is working correctly.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

import google.generativeai as genai

def test_gemini_api():
    """Test the Gemini API key"""
    print("🔍 Testing Gemini API Key...")
    print("=" * 50)
    
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key or api_key == "your-api-key":
        print("❌ No valid API key found in environment")
        print("   Please set GEMINI_API_KEY in your .env file")
        return False
    
    print(f"📋 API Key found: {api_key[:20]}...")
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Get model
        model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro")
        print(f"🤖 Using model: {model_name}")
        
        model = genai.GenerativeModel(model_name)
        
        # Test simple query
        print("\n🧪 Testing simple query...")
        test_prompt = "Hello! Can you respond with 'API test successful' if you're working?"
        
        response = model.generate_content(test_prompt)
        
        print("✅ API Response received:")
        print(f"   Response: {response.text}")
        
        # Test financial query
        print("\n💰 Testing financial query...")
        financial_prompt = """
        You are a financial assistant. Based on this data:
        - Revenue: 100,000 KES
        - Expenses: 75,000 KES
        
        What's the profit margin?
        """
        
        financial_response = model.generate_content(financial_prompt)
        print("✅ Financial query response:")
        print(f"   Response: {financial_response.text[:200]}...")
        
        print("\n🎉 Gemini API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        if "API key not valid" in str(e):
            print("   The API key appears to be invalid or expired")
            print("   Please check your Gemini API key in the .env file")
        elif "quota" in str(e).lower():
            print("   API quota exceeded - you may need to upgrade your plan")
        elif "permission" in str(e).lower():
            print("   Permission denied - check API key permissions")
        else:
            print("   Unknown API error - check your internet connection and API key")
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    sys.exit(0 if success else 1)
