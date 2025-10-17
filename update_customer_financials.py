#!/usr/bin/env python3
"""
Update all customers' financial data (outstanding_balance, total_billed, etc.)
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.mongodb import Database
from customers.service import CustomerService

async def update_all_customers():
    """Update financial data for all customers"""
    db = Database.get_instance().db
    service = CustomerService(db)
    
    # Get all customers
    customers = await db.customers.find({}).to_list(length=None)
    
    print(f"Found {len(customers)} customers")
    print("Updating financial data...")
    print()
    
    updated = 0
    failed = 0
    
    for customer in customers:
        customer_id = customer.get("customer_id")
        if not customer_id:
            print(f"⚠️  Skipping customer with no customer_id: {customer.get('name', 'Unknown')}")
            failed += 1
            continue
        
        try:
            success = await service.update_customer_financials(customer_id)
            if success:
                updated += 1
                # Get updated data
                updated_customer = await db.customers.find_one({"customer_id": customer_id})
                outstanding = updated_customer.get("outstanding_balance", 0)
                print(f"✓ {customer.get('name', 'Unknown')[:30]:30} | Balance: KES {outstanding:,.2f}")
            else:
                failed += 1
                print(f"✗ {customer.get('name', 'Unknown')[:30]:30} | Failed to update")
        except Exception as e:
            failed += 1
            print(f"✗ {customer.get('name', 'Unknown')[:30]:30} | Error: {str(e)}")
    
    print()
    print("="*60)
    print(f"✅ Successfully updated: {updated}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total processed: {len(customers)}")
    
    # Calculate total outstanding
    all_customers = await db.customers.find({}).to_list(length=None)
    total_outstanding = sum(c.get("outstanding_balance", 0) for c in all_customers)
    customers_with_balance = sum(1 for c in all_customers if c.get("outstanding_balance", 0) > 0)
    
    print()
    print("="*60)
    print("SUMMARY:")
    print(f"Total Outstanding Balance: KES {total_outstanding:,.2f}")
    print(f"Customers with Outstanding Balance: {customers_with_balance}")
    print("="*60)

if __name__ == "__main__":
    print("="*60)
    print("UPDATING CUSTOMER FINANCIAL DATA")
    print("="*60)
    print()
    asyncio.run(update_all_customers())
