"""
Check Database Data
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
sys.path.append('/home/munga/Desktop/AI-Financial-Agent')
from dotenv import load_dotenv

load_dotenv()

async def check_data():
    MONGO_URI = os.getenv("MONGO_URI")
    MONGO_DB = os.getenv("MONGO_DB", "financial_agent")
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    print("=" * 60)
    print("DATABASE DATA CHECK")
    print("=" * 60)
    
    # Count transactions
    total_transactions = await db.transactions.count_documents({})
    payment_transactions = await db.transactions.count_documents({"type": "payment"})
    expense_transactions = await db.transactions.count_documents({"type": "expense"})
    
    print(f"\nTransactions:")
    print(f"  Total: {total_transactions}")
    print(f"  Payments: {payment_transactions}")
    print(f"  Expenses: {expense_transactions}")
    
    # Check for payment transactions with completed status
    completed_payments = await db.transactions.count_documents({
        "type": "payment",
        "status": {"$in": ["completed", "success"]}
    })
    print(f"  Completed payments: {completed_payments}")
    
    # Get recent payment transactions
    print("\n" + "=" * 60)
    print("RECENT PAYMENT TRANSACTIONS (Last 5)")
    print("=" * 60)
    cursor = db.transactions.find({
        "type": "payment",
        "status": {"$in": ["completed", "success"]}
    }).sort("created_at", -1).limit(5)
    
    count = 0
    async for doc in cursor:
        count += 1
        print(f"\n{count}. Transaction ID: {doc.get('_id')}")
        print(f"   Date: {doc.get('created_at')}")
        print(f"   Customer: {doc.get('customer_name')}")
        print(f"   Amount: KES {doc.get('amount'):,.2f}")
        print(f"   Reference: {doc.get('mpesa_reference')}")
        print(f"   Status: {doc.get('status')}")
    
    if count == 0:
        print("No payment transactions found!")
    
    client.close()

asyncio.run(check_data())
