#!/usr/bin/env python3
"""
Clear Normalized Collections Script
This script removes all data from normalized collections to prepare for fresh migration.
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CollectionCleaner:
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
    
    async def clear_collections(self):
        """Clear normalized collections"""
        print("======================================================================")
        print("  CLEARING NORMALIZED COLLECTIONS")
        print("======================================================================\n")
        
        collections_to_clear = [
            "customers",
            "invoice_items",
            "payments",
            "payment_gateway_data",
            "products",
            "user_sessions",
            "audit_logs"
        ]
        
        total_deleted = 0
        
        for collection_name in collections_to_clear:
            collection = self.db[collection_name]
            count_before = await collection.count_documents({})
            
            if count_before > 0:
                result = await collection.delete_many({})
                print(f"🗑️  {collection_name}: Deleted {result.deleted_count} documents")
                total_deleted += result.deleted_count
            else:
                print(f"   {collection_name}: Already empty")
        
        print(f"\n======================================================================")
        print(f"✅ Total documents deleted: {total_deleted}")
        print(f"======================================================================\n")
    
    async def show_current_state(self):
        """Show current state of all collections"""
        print("📊 Current Database State:")
        print("=" * 70)
        
        all_collections = [
            # Original collections
            "users",
            "invoices",
            "transactions",
            "mpesa_payments",
            "receipts",
            "ocr_results",
            # Normalized collections
            "customers",
            "invoice_items",
            "payments",
            "payment_gateway_data",
            "products",
            "user_sessions",
            "audit_logs"
        ]
        
        for collection_name in all_collections:
            count = await self.db[collection_name].count_documents({})
            status = "📦" if count > 0 else "⚪"
            print(f"{status} {collection_name:30} {count:6} documents")
        
        print("=" * 70 + "\n")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

async def main():
    cleaner = CollectionCleaner()
    
    try:
        await cleaner.connect()
        
        # Show state before clearing
        print("BEFORE CLEARING:")
        await cleaner.show_current_state()
        
        # Confirm action
        print("⚠️  WARNING: This will DELETE all data from normalized collections!")
        print("   The following collections will be cleared:")
        print("   - customers")
        print("   - invoice_items")
        print("   - payments")
        print("   - payment_gateway_data")
        print("   - products")
        print("   - user_sessions")
        print("   - audit_logs")
        print("\n   Original collections (invoices, transactions, etc.) will NOT be touched.\n")
        
        confirm = input("Type 'yes' to continue: ").strip().lower()
        
        if confirm != 'yes':
            print("❌ Operation cancelled")
            return
        
        # Clear collections
        await cleaner.clear_collections()
        
        # Show state after clearing
        print("AFTER CLEARING:")
        await cleaner.show_current_state()
        
        print("✅ Ready for fresh migration!")
        print("   Next step: python scripts/normalize_database.py --dry-run")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await cleaner.close()

if __name__ == "__main__":
    asyncio.run(main())
