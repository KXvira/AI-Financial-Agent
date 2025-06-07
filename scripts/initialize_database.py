#!/usr/bin/env python3
"""
Initialize the MongoDB database with collections and indexes
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("db-init")

# Load environment variables
load_dotenv()

# MongoDB connection details
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("MONGO_DB", "financial_agent")

# Collection names
COLLECTIONS = {
    "transactions": "transactions",
    "invoices": "invoices",
    "customers": "customers",
    "reconciliation_logs": "reconciliation_logs", 
    "analytics": "analytics"
}

# Indexes configuration
INDEXES = {
    "transactions": [
        {
            "keys": [("status", 1)],
            "background": True,
        },
        {
            "keys": [("gateway_reference", 1)],
            "background": True,
            "sparse": True
        },
        {
            "keys": [("phone_number", 1)],
            "background": True
        },
        {
            "keys": [("reference", 1)],
            "background": True
        },
        {
            "keys": [("reconciliation_status", 1)],
            "background": True
        },
        {
            "keys": [("matched_invoice_id", 1)],
            "background": True,
            "sparse": True
        },
        {
            "keys": [("request_timestamp", -1)],
            "background": True
        },
        {
            "keys": [("metadata.checkout_request_id", 1)],
            "background": True,
            "sparse": True
        }
    ],
    "invoices": [
        {
            "keys": [("invoice_number", 1)],
            "background": True,
            "unique": True
        },
        {
            "keys": [("status", 1)],
            "background": True
        },
        {
            "keys": [("customer.id", 1)],
            "background": True,
            "sparse": True
        },
        {
            "keys": [("customer.phone_number", 1)],
            "background": True
        },
        {
            "keys": [("date_issued", -1)],
            "background": True
        },
        {
            "keys": [("due_date", 1)],
            "background": True,
            "sparse": True
        }
    ],
    "customers": [
        {
            "keys": [("name", 1)],
            "background": True
        },
        {
            "keys": [("phone_number", 1)],
            "background": True
        },
        {
            "keys": [("email", 1)],
            "background": True,
            "sparse": True
        }
    ],
    "reconciliation_logs": [
        {
            "keys": [("timestamp", -1)],
            "background": True
        },
        {
            "keys": [("payment_data.transaction_id", 1)],
            "background": True,
            "sparse": True
        },
        {
            "keys": [("payment_data.receipt_number", 1)],
            "background": True,
            "sparse": True
        }
    ],
    "analytics": [
        {
            "keys": [("date", -1)],
            "background": True
        },
        {
            "keys": [("type", 1)],
            "background": True
        }
    ]
}

async def create_collections_and_indexes():
    """Create collections and indexes in MongoDB"""
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DB_NAME]
        
        logger.info(f"Connected to MongoDB at {MONGO_URI}")
        
        # Create collections
        for name, collection in COLLECTIONS.items():
            logger.info(f"Creating collection {collection}")
            
            # Create the collection if it doesn't exist
            if collection not in await db.list_collection_names():
                await db.create_collection(collection)
            
            # Create indexes for the collection
            if name in INDEXES:
                for index_config in INDEXES[name]:
                    keys = index_config.pop("keys")
                    logger.info(f"Creating index on {collection}: {keys}")
                    await db[collection].create_index(keys, **index_config)
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
    finally:
        # Close the connection
        client.close()

# Run the initialization
if __name__ == "__main__":
    asyncio.run(create_collections_and_indexes())
