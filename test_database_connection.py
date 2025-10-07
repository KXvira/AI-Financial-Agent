"""
Simple test to verify MongoDB Atlas connection
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("🔍 Testing MongoDB Atlas Connection")
    print("=" * 50)
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Get connection details
        mongo_uri = os.getenv("MONGO_URI")
        mongo_db = os.getenv("MONGO_DB", "financial_agent")
        
        print(f"📊 MongoDB URI: {mongo_uri[:50]}...")
        print(f"📊 Database Name: {mongo_db}")
        
        # Create connection
        client = AsyncIOMotorClient(mongo_uri)
        db = client[mongo_db]
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📋 Collections found: {len(collections)}")
        for collection in collections:
            count = await db[collection].count_documents({})
            print(f"   - {collection}: {count} documents")
        
        # Test auth collection specifically
        users_collection = db.users
        user_count = await users_collection.count_documents({})
        print(f"👥 Users collection: {user_count} users")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_auth_service_connection():
    """Test auth service database connection"""
    print("\n🔐 Testing Auth Service Database Connection")
    print("=" * 50)
    
    try:
        from auth.database import auth_db_service
        
        # Test database connection through auth service
        db = await auth_db_service.get_database()
        await db.command("ping")
        print("✅ Auth service database connection successful!")
        
        # Test users collection
        users_collection = await auth_db_service.get_users_collection()
        user_count = await users_collection.count_documents({})
        print(f"👥 Users accessible through auth service: {user_count}")
        
        await auth_db_service.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Auth service database connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run database connection tests"""
    print("🧪 AI FINANCIAL AGENT - DATABASE CONNECTION TEST")
    print("=" * 80)
    
    # Test direct MongoDB connection
    direct_connection = await test_mongodb_connection()
    
    # Test auth service connection
    auth_connection = await test_auth_service_connection()
    
    print("\n" + "=" * 80)
    print("📊 DATABASE TEST RESULTS")
    print("=" * 80)
    
    if direct_connection and auth_connection:
        print("🎉 ALL DATABASE CONNECTIONS WORKING!")
        print("✅ MongoDB Atlas connection successful")
        print("✅ Auth service can connect to database")
        print("✅ Ready for authentication testing")
    else:
        print("❌ DATABASE CONNECTION ISSUES FOUND")
        if not direct_connection:
            print("❌ Direct MongoDB Atlas connection failed")
        if not auth_connection:
            print("❌ Auth service database connection failed")
    
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())