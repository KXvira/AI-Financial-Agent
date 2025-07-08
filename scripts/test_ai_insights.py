"""
Test script for AI Financial Insights Service
"""
import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.ai_insights.service import (
    QueryRequest,
    process_financial_query,
    validate_database_connection,
    validate_gemini_connection,
    retrieve_financial_context
)

async def test_ai_insights():
    """Test the AI insights service functionality"""
    
    print("🧪 Testing AI Financial Insights Service")
    print("=" * 50)
    
    # Test 1: Check connections
    print("\n1. Testing Database Connection:")
    db_connected = validate_database_connection()
    print(f"   Database Connected: {'✅' if db_connected else '❌'}")
    
    print("\n2. Testing Gemini API Connection:")
    gemini_connected = validate_gemini_connection()
    print(f"   Gemini API Connected: {'✅' if gemini_connected else '❌'}")
    
    # Test 2: Test data retrieval
    print("\n3. Testing Data Retrieval:")
    test_query = "What was my revenue for the last 3 months?"
    context = retrieve_financial_context(test_query)
    
    if context:
        print(f"   ✅ Retrieved context ({len(context)} characters)")
        print(f"   Preview: {context[:200]}...")
    else:
        print("   ❌ No context retrieved")
    
    # Test 3: Test full query processing (only if connections work)
    if db_connected and gemini_connected:
        print("\n4. Testing Full Query Processing:")
        
        test_queries = [
            "What was my revenue trend for the last 3 months?",
            "How many transactions did I process this month?",
            "What are my top expense categories?",
            "Show me my invoice payment status"
        ]
        
        for query in test_queries:
            print(f"\n   Query: {query}")
            try:
                request = QueryRequest(query=query)
                response = await process_financial_query(request)
                print(f"   ✅ Response received ({len(response.answer)} characters)")
                print(f"   Confidence: {response.confidence}")
                print(f"   Answer preview: {response.answer[:150]}...")
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    else:
        print("\n4. Skipping full query test due to connection issues")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    # Set up test environment variables if needed
    os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
    os.environ.setdefault("DATABASE_NAME", "kenya_fintech_suite")
    os.environ.setdefault("GEMINI_API_KEY", "your-test-api-key")
    
    asyncio.run(test_ai_insights())
