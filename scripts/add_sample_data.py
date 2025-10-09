#!/usr/bin/env python3
"""
Add sample data to the MongoDB database for testing
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime, timedelta
from backend.database.mongodb import Database
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("sample-data")

async def add_sample_data():
    """Add sample transactions and invoices to the database"""
    try:
        # Get database instance
        db = Database.get_instance()
        
        # Sample transactions
        sample_transactions = [
            {
                "transaction_id": "TXN001",
                "reference": "PAY001",
                "phone_number": "254712345678",
                "amount": 1500.00,
                "status": "completed",
                "gateway": "mpesa",
                "gateway_reference": "QAB7C8D9E1",
                "request_timestamp": datetime.now() - timedelta(days=5),
                "reconciliation_status": "matched",
                "metadata": {
                    "checkout_request_id": "ws_CO_123456789"
                }
            },
            {
                "transaction_id": "TXN002", 
                "reference": "PAY002",
                "phone_number": "254787654321",
                "amount": 2500.50,
                "status": "completed",
                "gateway": "mpesa",
                "gateway_reference": "QBC8D9E1F2",
                "request_timestamp": datetime.now() - timedelta(days=3),
                "reconciliation_status": "matched",
                "metadata": {
                    "checkout_request_id": "ws_CO_987654321"
                }
            },
            {
                "transaction_id": "TXN003",
                "reference": "PAY003", 
                "phone_number": "254798765432",
                "amount": 750.75,
                "status": "completed",
                "gateway": "mpesa",
                "gateway_reference": "QCD9E1F2G3",
                "request_timestamp": datetime.now() - timedelta(days=1),
                "reconciliation_status": "matched",
                "metadata": {
                    "checkout_request_id": "ws_CO_192837465"
                }
            },
            {
                "transaction_id": "TXN004",
                "reference": "PAY004",
                "phone_number": "254756789123", 
                "amount": 3200.25,
                "status": "pending",
                "gateway": "mpesa",
                "gateway_reference": "QDE1F2G3H4",
                "request_timestamp": datetime.now() - timedelta(hours=2),
                "reconciliation_status": "pending",
                "metadata": {
                    "checkout_request_id": "ws_CO_564738291"
                }
            }
        ]
        
        # Sample invoices
        sample_invoices = [
            {
                "invoice_number": "INV-001",
                "customer": {
                    "id": "CUST001",
                    "name": "John Doe",
                    "phone_number": "254712345678",
                    "email": "john@example.com"
                },
                "items": [
                    {
                        "description": "Product A",
                        "quantity": 2,
                        "unit_price": 750.00,
                        "amount": 1500.00
                    }
                ],
                "total_amount": 1500.00,
                "status": "paid",
                "date_issued": datetime.now() - timedelta(days=5),
                "due_date": datetime.now() - timedelta(days=1)
            },
            {
                "invoice_number": "INV-002",
                "customer": {
                    "id": "CUST002", 
                    "name": "Jane Smith",
                    "phone_number": "254787654321",
                    "email": "jane@example.com"
                },
                "items": [
                    {
                        "description": "Service B",
                        "quantity": 1,
                        "unit_price": 2500.50,
                        "amount": 2500.50
                    }
                ],
                "total_amount": 2500.50,
                "status": "paid",
                "date_issued": datetime.now() - timedelta(days=3),
                "due_date": datetime.now() + timedelta(days=7)
            },
            {
                "invoice_number": "INV-003",
                "customer": {
                    "id": "CUST003",
                    "name": "Alice Johnson", 
                    "phone_number": "254798765432",
                    "email": "alice@example.com"
                },
                "items": [
                    {
                        "description": "Product C",
                        "quantity": 3,
                        "unit_price": 250.25,
                        "amount": 750.75
                    }
                ],
                "total_amount": 750.75,
                "status": "paid",
                "date_issued": datetime.now() - timedelta(days=1),
                "due_date": datetime.now() + timedelta(days=14)
            },
            {
                "invoice_number": "INV-004",
                "customer": {
                    "id": "CUST004",
                    "name": "Bob Wilson",
                    "phone_number": "254756789123",
                    "email": "bob@example.com"
                },
                "items": [
                    {
                        "description": "Service D",
                        "quantity": 2,
                        "unit_price": 1600.125,
                        "amount": 3200.25
                    }
                ],
                "total_amount": 3200.25,
                "status": "sent",
                "date_issued": datetime.now() - timedelta(hours=2),
                "due_date": datetime.now() + timedelta(days=30)
            },
            {
                "invoice_number": "INV-005",
                "customer": {
                    "id": "CUST005",
                    "name": "Carol Brown",
                    "phone_number": "254723456789",
                    "email": "carol@example.com"
                },
                "items": [
                    {
                        "description": "Product E",
                        "quantity": 1,
                        "unit_price": 5000.00,
                        "amount": 5000.00
                    }
                ],
                "total_amount": 5000.00,
                "status": "overdue",
                "date_issued": datetime.now() - timedelta(days=45),
                "due_date": datetime.now() - timedelta(days=15)
            }
        ]
        
        # Insert sample transactions
        if await db.transactions.count_documents({}) == 0:
            logger.info("Inserting sample transactions...")
            await db.transactions.insert_many(sample_transactions)
            logger.info(f"Inserted {len(sample_transactions)} sample transactions")
        else:
            logger.info("Transactions already exist, skipping insertion")
            
        # Insert sample invoices
        if await db.invoices.count_documents({}) == 0:
            logger.info("Inserting sample invoices...")
            await db.invoices.insert_many(sample_invoices)
            logger.info(f"Inserted {len(sample_invoices)} sample invoices")
        else:
            logger.info("Invoices already exist, skipping insertion")
            
        logger.info("Sample data insertion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error adding sample data: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(add_sample_data())