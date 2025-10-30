#!/usr/bin/env python3
"""
Check invoice data structure for Tech Solutions Ltd
"""
import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient

async def main():
    # Connect to MongoDB
    uri = "mongodb+srv://alfredmunga254:mongodbkenya10@financialagent.ryjz7.mongodb.net/?retryWrites=true&w=majority&appName=FinancialAgent"
    client = AsyncIOMotorClient(uri)
    db = client['FinancialAgent']
    
    customer_id = "68ee94c0d2b4a41d555c0ae3"
    
    # Get customer first
    customer = await db.customers.find_one({"_id": customer_id})
    if not customer:
        print(f"Customer {customer_id} not found by _id")
        # Try UUID
        customer = await db.customers.find_one({"customer_id": customer_id})
        if customer:
            print(f"Found customer by customer_id UUID")
            actual_id = customer.get("customer_id")
        else:
            print("Customer not found!")
            return
    else:
        print(f"Found customer by _id: {customer.get('name')}")
        actual_id = customer.get("customer_id")
    
    print(f"Actual customer_id for queries: {actual_id}")
    print()
    
    # Get invoices
    invoices = await db.invoices.find({"customer_id": actual_id}).to_list(length=10)
    
    print(f"Found {len(invoices)} invoices for customer")
    print()
    
    for i, inv in enumerate(invoices[:5], 1):
        print(f"Invoice {i}:")
        print(f"  ID: {inv.get('invoice_id')}")
        print(f"  Date Issued: {inv.get('date_issued')}")
        print(f"  Status: {inv.get('status')}")
        print(f"  Total: {inv.get('total')} (field exists: {'total' in inv})")
        print(f"  Total Amount: {inv.get('total_amount')} (field exists: {'total_amount' in inv})")
        print(f"  Amount Paid: {inv.get('amount_paid')}")
        print(f"  Customer ID: {inv.get('customer_id')}")
        
        # Check invoice items
        items = await db.invoice_items.find({"invoice_id": inv.get('invoice_id')}).to_list(length=None)
        print(f"  Invoice Items: {len(items)}")
        
        if items:
            items_total = sum(item.get('total', 0) for item in items)
            print(f"  Items Total Sum: {items_total}")
            print(f"  First item: {items[0].get('description')} - Qty: {items[0].get('quantity')} - Price: {items[0].get('unit_price')} - Total: {items[0].get('total')}")
        
        print()
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
