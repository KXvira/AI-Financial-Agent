#!/usr/bin/env python3
"""Check for overdue invoices directly from MongoDB"""
import asyncio
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.mongodb import Database

async def check_overdue():
    """Check for overdue invoices"""
    db = Database.get_instance()
    
    print("=== CHECKING INVOICES IN DATABASE ===\n")
    
    # Get all invoices
    all_invoices = await db.invoices.count_documents({})
    print(f"Total Invoices in Database: {all_invoices}")
    
    # Count by status
    print("\n=== INVOICE STATUS BREAKDOWN ===")
    statuses = await db.invoices.distinct("status")
    for status in statuses:
        count = await db.invoices.count_documents({"status": status})
        
        # Get total amount for this status
        pipeline = [
            {"$match": {"status": status}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        result = await db.invoices.aggregate(pipeline).to_list(1)
        amount = result[0]["total"] if result else 0
        
        print(f"  {status.upper()}: {count} invoices (KES {amount:,.2f})")
    
    # Check for overdue invoices
    print("\n=== OVERDUE INVOICES ===")
    overdue_count = await db.invoices.count_documents({"status": "overdue"})
    print(f"Overdue Invoices: {overdue_count}")
    
    if overdue_count > 0:
        # Get overdue invoices with customer info
        overdue_invoices = await db.invoices.find({"status": "overdue"}).to_list(length=100)
        
        # Group by customer
        by_customer = {}
        total_overdue_amount = 0
        
        for inv in overdue_invoices:
            customer_id = inv.get("customer_id")
            amount = inv.get("total_amount", 0)
            invoice_number = inv.get("invoice_number", "N/A")
            due_date = inv.get("due_date", "N/A")
            
            # Get customer info
            if customer_id:
                customer = await db.customers.find_one({"_id": customer_id})
                customer_name = customer.get("name", "Unknown") if customer else "Unknown"
            else:
                customer_name = "No Customer"
            
            if customer_name not in by_customer:
                by_customer[customer_name] = {
                    "invoices": [],
                    "total_amount": 0
                }
            
            by_customer[customer_name]["invoices"].append({
                "invoice_number": invoice_number,
                "amount": amount,
                "due_date": due_date
            })
            by_customer[customer_name]["total_amount"] += amount
            total_overdue_amount += amount
        
        # Sort by amount
        sorted_customers = sorted(by_customer.items(), key=lambda x: x[1]["total_amount"], reverse=True)
        
        print(f"\nCustomers with Overdue Invoices: {len(sorted_customers)}")
        print(f"Total Overdue Amount: KES {total_overdue_amount:,.2f}\n")
        print("=" * 80)
        
        for customer_name, data in sorted_customers:
            print(f"\n📌 {customer_name}")
            print(f"   Total Overdue: KES {data['total_amount']:,.2f}")
            print(f"   Number of Overdue Invoices: {len(data['invoices'])}")
            print(f"   Invoices:")
            for inv in data["invoices"][:5]:
                print(f"      • #{inv['invoice_number']} - KES {inv['amount']:,.2f} (Due: {inv['due_date']})")
            if len(data["invoices"]) > 5:
                print(f"      ... and {len(data['invoices']) - 5} more")
    else:
        print("\n✅ No overdue invoices!")
    
    # Check for sent/pending invoices
    print("\n=== UNPAID INVOICES (Status: sent) ===")
    sent_count = await db.invoices.count_documents({"status": "sent"})
    print(f"Sent/Unpaid Invoices: {sent_count}")
    
    if sent_count > 0:
        sent_invoices = await db.invoices.find({"status": "sent"}).to_list(length=100)
        
        # Group by customer
        by_customer = {}
        total_sent_amount = 0
        
        for inv in sent_invoices:
            customer_id = inv.get("customer_id")
            amount = inv.get("total_amount", 0)
            invoice_number = inv.get("invoice_number", "N/A")
            due_date = inv.get("due_date", "N/A")
            issue_date = inv.get("issue_date", "N/A")
            
            # Get customer info
            if customer_id:
                customer = await db.customers.find_one({"_id": customer_id})
                customer_name = customer.get("name", "Unknown") if customer else "Unknown"
            else:
                customer_name = "No Customer"
            
            if customer_name not in by_customer:
                by_customer[customer_name] = {
                    "invoices": [],
                    "total_amount": 0
                }
            
            by_customer[customer_name]["invoices"].append({
                "invoice_number": invoice_number,
                "amount": amount,
                "due_date": due_date,
                "issue_date": issue_date
            })
            by_customer[customer_name]["total_amount"] += amount
            total_sent_amount += amount
        
        sorted_customers = sorted(by_customer.items(), key=lambda x: x[1]["total_amount"], reverse=True)
        
        print(f"\nCustomers with Unpaid Invoices: {len(sorted_customers)}")
        print(f"Total Unpaid Amount: KES {total_sent_amount:,.2f}\n")
        print("=" * 80)
        
        for customer_name, data in sorted_customers[:15]:
            print(f"\n📋 {customer_name}")
            print(f"   Total Unpaid: KES {data['total_amount']:,.2f}")
            print(f"   Number of Invoices: {len(data['invoices'])}")
            for inv in data["invoices"][:3]:
                print(f"      • #{inv['invoice_number']} - KES {inv['amount']:,.2f}")
                print(f"        Issued: {inv['issue_date']}, Due: {inv['due_date']}")
            if len(data["invoices"]) > 3:
                print(f"      ... and {len(data['invoices']) - 3} more")
    else:
        print("\n✅ No unpaid invoices with 'sent' status!")

if __name__ == "__main__":
    asyncio.run(check_overdue())
