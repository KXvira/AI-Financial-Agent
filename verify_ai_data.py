#!/usr/bin/env python3
"""Verify AI Insights data accuracy"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.mongodb import Database

async def verify_data():
    """Verify the data shown in AI Insights page"""
    db = Database.get_instance()
    
    print("=== DATABASE VERIFICATION ===\n")
    
    # 1. Total transactions
    total_txns = await db.transactions.count_documents({})
    print(f"✓ Total Transactions: {total_txns}")
    
    # 2. Total invoices
    total_invoices = await db.invoices.count_documents({})
    print(f"✓ Total Invoices: {total_invoices}")
    
    # 3. M-Pesa transactions
    mpesa_count = await db.transactions.count_documents({"gateway": "mpesa"})
    print(f"✓ M-Pesa Transactions (gateway='mpesa'): {mpesa_count}")
    
    # Check if there are any transactions with mpesa in different cases
    mpesa_any = await db.transactions.count_documents({"gateway": {"$regex": "mpesa", "$options": "i"}})
    print(f"  - M-Pesa (case-insensitive): {mpesa_any}")
    
    # 4. Revenue from completed transactions
    revenue_pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]
    revenue_result = await db.transactions.aggregate(revenue_pipeline).to_list(1)
    total_revenue = revenue_result[0]["total"] if revenue_result else 0
    print(f"✓ Total Revenue (completed transactions): KES {total_revenue:,.2f}")
    
    # 5. Pending invoices
    pending_invoices = await db.invoices.count_documents({"status": "sent"})
    print(f"✓ Pending Invoices (status='sent'): {pending_invoices}")
    
    # 6. Pending amount
    pending_pipeline = [
        {"$match": {"status": {"$in": ["sent", "overdue"]}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    pending_result = await db.invoices.aggregate(pending_pipeline).to_list(1)
    pending_amount = pending_result[0]["total"] if pending_result else 0
    print(f"✓ Pending Amount (sent/overdue invoices): KES {pending_amount:,.2f}")
    
    # Additional checks
    print("\n=== ADDITIONAL ANALYSIS ===\n")
    
    # Check gateway values in transactions
    print("Transaction gateway values:")
    gateways = await db.transactions.distinct("gateway")
    for gw in gateways[:10]:  # Show first 10
        count = await db.transactions.count_documents({"gateway": gw})
        print(f"  - '{gw}': {count}")
    
    # Check transaction statuses
    print("\nTransaction status counts:")
    txn_statuses = await db.transactions.distinct("status")
    for status in txn_statuses:
        count = await db.transactions.count_documents({"status": status})
        print(f"  - '{status}': {count}")
    
    # Check invoice statuses
    print("\nInvoice status counts:")
    inv_statuses = await db.invoices.distinct("status")
    for status in inv_statuses:
        count = await db.invoices.count_documents({"status": status})
        print(f"  - '{status}': {count}")
    
    print("\n=== COMPARISON WITH UI ===\n")
    print("UI shows:")
    print("  - Total Transactions: 707")
    print("  - Total Invoices: 999")
    print("  - M-Pesa Transactions: 0")
    print("  - Total Revenue: KES 48,908,755.00")
    print()
    print("Database shows:")
    print(f"  - Total Transactions: {total_txns}")
    print(f"  - Total Invoices: {total_invoices}")
    print(f"  - M-Pesa Transactions: {mpesa_count}")
    print(f"  - Total Revenue: KES {total_revenue:,.2f}")
    print()
    
    if total_txns == 707 and total_invoices == 999 and total_revenue == 48908755.00:
        print("✅ ALL DATA MATCHES - Service is fetching correct data!")
    else:
        print("⚠️  Data mismatch detected!")

if __name__ == "__main__":
    asyncio.run(verify_data())
