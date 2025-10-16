"""
Test script to create sample expense receipts in the database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random

async def create_sample_expenses():
    # Connect to MongoDB
    client = AsyncIOMotorClient('mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/')
    db = client['financial_db']
    receipts = db['receipts']
    
    # Sample expense data
    categories = ['Office Supplies', 'Transport', 'Meals', 'Utilities', 'Fuel']
    vendors = ['Safaricom', 'Total Kenya', 'Naivas', 'Artcaffe', 'Uber', 'Kenya Power']
    
    print("Creating sample expense receipts...")
    
    created_count = 0
    for i in range(10):
        # Create expense receipt
        expense = {
            'receipt_type': 'expense',
            'status': 'processed',
            'receipt_number': f'EXP-2025-{1000 + i}',
            'created_at': datetime.utcnow() - timedelta(days=random.randint(1, 90)),
            'ocr_data': {
                'extracted_data': {
                    'total_amount': round(random.uniform(500, 50000), 2),
                    'merchant_name': random.choice(vendors),
                    'transaction_date': (datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat(),
                    'category': random.choice(categories)
                },
                'confidence': random.uniform(0.85, 0.99),
                'engine': 'test_data'
            },
            'payment_method': random.choice(['mpesa', 'cash', 'bank_transfer']),
            'currency': 'KES'
        }
        
        result = await receipts.insert_one(expense)
        created_count += 1
        print(f"Created expense {i+1}: {expense['ocr_data']['extracted_data']['merchant_name']} - KES {expense['ocr_data']['extracted_data']['total_amount']}")
    
    print(f"\n✅ Created {created_count} sample expense receipts")
    
    # Verify count
    total_expenses = await receipts.count_documents({'receipt_type': 'expense'})
    print(f"Total expense receipts in database: {total_expenses}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_sample_expenses())
