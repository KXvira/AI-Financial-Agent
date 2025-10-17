#!/usr/bin/env python3
"""Check M-Pesa payments in database"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.mongodb import Database

async def check_mpesa():
    db = Database.get_instance()
    
    print("=== CHECKING PAYMENTS COLLECTION ===\n")
    
    # Total payments
    total_payments = await db.payments.count_documents({})
    print(f"Total payments: {total_payments}")
    
    # Check payment_method field
    print("\nChecking payment_method values...")
    
    # Get sample payments
    sample_payments = await db.payments.find({}).limit(5).to_list(5)
    
    print("\nSample payments:")
    for i, p in enumerate(sample_payments, 1):
        print(f"\n{i}. Payment ID: {p.get('_id')}")
        print(f"   payment_method: {p.get('payment_method', 'FIELD NOT FOUND')}")
        print(f"   amount: {p.get('amount', 'N/A')}")
        print(f"   status: {p.get('status', 'N/A')}")
    
    # Count M-Pesa (case-insensitive)
    mpesa_count = await db.payments.count_documents({
        "payment_method": {"$regex": "mpesa", "$options": "i"}
    })
    print(f"\n✓ M-Pesa payments (case-insensitive): {mpesa_count}")
    
    # Get distinct payment methods
    print("\nAll payment method values in database:")
    payment_methods = await db.payments.distinct("payment_method")
    for method in payment_methods:
        count = await db.payments.count_documents({"payment_method": method})
        print(f"  - '{method}': {count}")

if __name__ == "__main__":
    asyncio.run(check_mpesa())
