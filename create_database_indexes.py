#!/usr/bin/env python3
"""
Create database indexes to optimize AR Aging performance
This script adds indexes to speed up lookups and joins
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database.mongodb import Database
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_indexes():
    """Create database indexes for performance optimization"""
    
    # Initialize database connection
    db = Database.get_instance()
    
    try:
        logger.info("Creating database indexes for performance optimization...")
        
        # 1. Index on invoice_items.invoice_id (for $lookup join)
        logger.info("Creating index on invoice_items.invoice_id...")
        try:
            await db.db["invoice_items"].create_index("invoice_id")
            logger.info("✅ Created index: invoice_items.invoice_id")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                logger.info("ℹ️  Index already exists: invoice_items.invoice_id")
            else:
                raise
        
        # 2. Index on customers.customer_id (for $lookup join)
        logger.info("Creating index on customers.customer_id...")
        try:
            await db.db["customers"].create_index("customer_id")
            logger.info("✅ Created index: customers.customer_id")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                logger.info("ℹ️  Index already exists: customers.customer_id")
            else:
                raise
        
        # 3. Compound index on invoices.status + issue_date (for filtering)
        logger.info("Creating compound index on invoices.status + issue_date...")
        try:
            await db.invoices.create_index([("status", 1), ("issue_date", 1)])
            logger.info("✅ Created index: invoices.status + issue_date")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                logger.info("ℹ️  Index already exists: invoices.status + issue_date")
            else:
                raise
        
        # 4. Index on invoices.invoice_id (for general lookups)
        logger.info("Creating index on invoices.invoice_id...")
        try:
            await db.invoices.create_index("invoice_id", unique=True)
            logger.info("✅ Created index: invoices.invoice_id (unique)")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e) or "duplicate key" in str(e).lower():
                logger.info("ℹ️  Index already exists: invoices.invoice_id")
            else:
                raise
        
        # 5. Index on payments.payment_date (for cash flow queries)
        logger.info("Creating index on payments.payment_date...")
        try:
            await db.payments.create_index("payment_date")
            logger.info("✅ Created index: payments.payment_date")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                logger.info("ℹ️  Index already exists: payments.payment_date")
            else:
                raise
        
        # 6. Index on receipts.created_at (for expense queries)
        logger.info("Creating index on receipts.created_at...")
        try:
            await db.db["receipts"].create_index("created_at")
            logger.info("✅ Created index: receipts.created_at")
        except Exception as e:
            if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                logger.info("ℹ️  Index already exists: receipts.created_at")
            else:
                raise
        
        # List all indexes
        logger.info("\n" + "="*60)
        logger.info("All indexes created successfully!")
        logger.info("="*60)
        
        # Show indexes for each collection
        collections = ["invoices", "invoice_items", "customers", "payments", "receipts"]
        for coll_name in collections:
            logger.info(f"\n{coll_name} indexes:")
            collection = db.db[coll_name]
            indexes = await collection.list_indexes().to_list(None)
            for idx in indexes:
                logger.info(f"  - {idx.get('name')}: {idx.get('key')}")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_indexes())
