#!/usr/bin/env python3
"""
Clear ALL Database Collections Script
⚠️ WARNING: This script deletes EVERYTHING from the database!
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseCleaner:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.client = None
        self.db = None
    
    async def connect(self):
        """Connect to MongoDB"""
        print(f"📡 Connecting to MongoDB: {self.mongo_uri[:50]}...")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client.financial_agent
        print("✅ Connected to MongoDB\n")
    
    async def show_current_state(self):
        """Show current state of all collections"""
        print("📊 Current Database State:")
        print("=" * 70)
        
        # Get all collection names
        collection_names = await self.db.list_collection_names()
        
        total_docs = 0
        for collection_name in sorted(collection_names):
            count = await self.db[collection_name].count_documents({})
            status = "📦" if count > 0 else "⚪"
            print(f"{status} {collection_name:30} {count:6} documents")
            total_docs += count
        
        print("=" * 70)
        print(f"Total: {len(collection_names)} collections, {total_docs} documents")
        print("=" * 70 + "\n")
    
    async def clear_all_collections(self):
        """Clear ALL collections in the database"""
        print("======================================================================")
        print("  CLEARING ALL COLLECTIONS")
        print("======================================================================\n")
        
        # Get all collection names
        collection_names = await self.db.list_collection_names()
        
        total_deleted = 0
        collections_cleared = 0
        
        for collection_name in sorted(collection_names):
            collection = self.db[collection_name]
            count_before = await collection.count_documents({})
            
            if count_before > 0:
                result = await collection.delete_many({})
                print(f"🗑️  {collection_name:30} Deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
                collections_cleared += 1
            else:
                print(f"   {collection_name:30} Already empty")
        
        print(f"\n======================================================================")
        print(f"✅ Cleared {collections_cleared} collections")
        print(f"✅ Total documents deleted: {total_deleted}")
        print(f"======================================================================\n")
    
    async def drop_all_collections(self):
        """Drop ALL collections (alternative to clearing)"""
        print("======================================================================")
        print("  DROPPING ALL COLLECTIONS")
        print("======================================================================\n")
        
        # Get all collection names
        collection_names = await self.db.list_collection_names()
        
        for collection_name in sorted(collection_names):
            await self.db[collection_name].drop()
            print(f"🗑️  Dropped collection: {collection_name}")
        
        print(f"\n======================================================================")
        print(f"✅ Dropped {len(collection_names)} collections")
        print(f"======================================================================\n")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

async def main():
    cleaner = DatabaseCleaner()
    
    try:
        await cleaner.connect()
        
        # Show state before clearing
        print("BEFORE CLEARING:")
        await cleaner.show_current_state()
        
        # Confirm action
        print("⚠️  ⚠️  ⚠️  CRITICAL WARNING ⚠️  ⚠️  ⚠️")
        print("=" * 70)
        print("This will DELETE ALL DATA from ALL collections in the database!")
        print("This action CANNOT be undone without a backup!")
        print("=" * 70)
        print("\nCollections that will be affected:")
        collection_names = await cleaner.db.list_collection_names()
        for name in sorted(collection_names):
            count = await cleaner.db[name].count_documents({})
            print(f"  - {name} ({count} documents)")
        print()
        
        confirm1 = input("Type 'DELETE ALL' to continue: ").strip()
        
        if confirm1 != 'DELETE ALL':
            print("❌ Operation cancelled")
            return
        
        confirm2 = input("Are you absolutely sure? Type 'yes' to confirm: ").strip().lower()
        
        if confirm2 != 'yes':
            print("❌ Operation cancelled")
            return
        
        # Ask for deletion method
        print("\nChoose deletion method:")
        print("1. Clear all documents (keeps collections and indexes)")
        print("2. Drop all collections (removes everything including indexes)")
        
        method = input("Enter choice (1 or 2): ").strip()
        
        if method == "1":
            await cleaner.clear_all_collections()
        elif method == "2":
            await cleaner.drop_all_collections()
        else:
            print("❌ Invalid choice. Operation cancelled")
            return
        
        # Show state after clearing
        print("AFTER CLEARING:")
        await cleaner.show_current_state()
        
        print("✅ Database has been completely cleared!")
        print("   The database is now empty and ready for fresh data.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cleaner.close()

if __name__ == "__main__":
    asyncio.run(main())
