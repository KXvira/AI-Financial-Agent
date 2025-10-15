#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database.mongodb import get_sync_database

db = get_sync_database()

print("="*70)
print("TESTING CUSTOMER STATEMENT DATA")
print("="*70)

# Get one invoice
invoice = db.db.invoices.find_one({})
if invoice:
    print("\n📄 Sample Invoice:")
    print(f"  invoice_id: {invoice.get('invoice_id')}")
    print(f"  customer_id: {invoice.get('customer_id')}")
    print(f"  total: KES {invoice.get('total'):,.2f}")
    print(f"  status: {invoice.get('status')}")
    print(f"  amount_paid: KES {invoice.get('amount_paid', 0):,.2f}")
    
    # Get customer
    customer_id = invoice.get('customer_id')
    customer = db.db.customers.find_one({"customer_id": customer_id})
    
    if customer:
        print(f"\n✅ Customer Found:")
        print(f"  name: {customer.get('name')}")
        print(f"  customer_id: {customer.get('customer_id')}")
    else:
        print(f"\n❌ No customer found with customer_id: {customer_id}")

# Test the query used by customer service
print("\n" + "="*70)
print("TESTING CUSTOMER SERVICE QUERY")
print("="*70)

sample_customer = db.db.customers.find_one({})
if sample_customer:
    customer_id = sample_customer.get('customer_id')
    print(f"\n👤 Testing with: {sample_customer.get('name')}")
    print(f"  customer_id: {customer_id}")
    
    # Try the query from customer_service.py
    invoice_match = {
        "$or": [
            {"customer_id": customer_id},
            {"customer.id": customer_id},
            {"customer.customer_id": customer_id}
        ],
        "status": {"$nin": ["paid", "cancelled", "refunded"]}
    }
    
    invoices = list(db.db.invoices.find(invoice_match))
    print(f"\n📊 Query Result:")
    print(f"  Invoices found: {len(invoices)}")
    
    if invoices:
        total_outstanding = sum(inv.get("total", 0) - inv.get("amount_paid", 0) for inv in invoices)
        print(f"  Outstanding: KES {total_outstanding:,.2f}")
        print(f"\n  Sample invoice:")
        print(f"    Invoice ID: {invoices[0].get('invoice_id')}")
        print(f"    Total: KES {invoices[0].get('total'):,.2f}")
        print(f"    Paid: KES {invoices[0].get('amount_paid', 0):,.2f}")
        print(f"    Status: {invoices[0].get('status')}")
    else:
        print("  ❌ No invoices found with this query!")
        
        # Try simpler query
        simple_match = {"customer_id": customer_id}
        simple_result = db.db.invoices.count_documents(simple_match)
        print(f"\n  Testing simple query: {{customer_id: '{customer_id}'}}")
        print(f"  Result: {simple_result} invoices")

print("\n" + "="*70)
print("OVERALL STATISTICS")
print("="*70)
print(f"Total customers: {db.db.customers.count_documents({})}")
print(f"Total invoices: {db.db.invoices.count_documents({})}")
print(f"Unpaid invoices: {db.db.invoices.count_documents({'status': {'$nin': ['paid', 'cancelled']}})}")
