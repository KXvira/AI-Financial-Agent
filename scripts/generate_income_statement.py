#!/usr/bin/env python3
"""
Generate Income Statement from existing data
Demonstrates what financial reports can be created
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from collections import defaultdict

# MongoDB connection
MONGO_URI = "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
DB_NAME = "financial_agent"

async def generate_income_statement():
    """Generate a simple income statement from existing data"""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("\n" + "=" * 70)
    print("                         INCOME STATEMENT")
    print("                    AI Financial Agent System")
    print("                        All Time Period")
    print("=" * 70)
    
    # ========== REVENUE SECTION ==========
    print("\n📊 REVENUE")
    print("-" * 70)
    
    # Get all invoices
    invoices = await db.invoices.find().to_list(None)
    print(f"   Analyzing {len(invoices)} invoices...")
    
    # Calculate revenue by status
    paid_invoices = [inv for inv in invoices if inv.get("status") == "paid"]
    pending_invoices = [inv for inv in invoices if inv.get("status") in ["sent", "pending"]]
    
    total_paid = sum(inv.get("amount", 0) for inv in paid_invoices)
    total_pending = sum(inv.get("amount", 0) for inv in pending_invoices)
    total_invoiced = sum(inv.get("amount", 0) for inv in invoices)
    
    print(f"\n   Total Invoiced (All Time)      KES {total_invoiced:>15,.2f}")
    print(f"   └─ Paid Invoices              KES {total_paid:>15,.2f}")
    print(f"   └─ Pending/Unpaid             KES {total_pending:>15,.2f}")
    
    # Use paid invoices as recognized revenue
    total_revenue = total_paid
    
    # ========== EXPENSES SECTION ==========
    print("\n\n💸 OPERATING EXPENSES")
    print("-" * 70)
    
    # Get all expense transactions
    transactions = await db.transactions.find({"type": "expense"}).to_list(None)
    print(f"   Analyzing {len(transactions)} expense transactions...")
    
    # Group by category
    expenses_by_category = defaultdict(float)
    for txn in transactions:
        category = txn.get("category", "Uncategorized")
        amount = txn.get("amount", 0)
        expenses_by_category[category] += amount
    
    # Sort by amount (descending)
    sorted_expenses = sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)
    
    print()
    for category, amount in sorted_expenses:
        print(f"   {category:<30} KES {amount:>15,.2f}")
    
    total_expenses = sum(expenses_by_category.values())
    print(f"\n   {'Total Operating Expenses':<30} KES {total_expenses:>15,.2f}")
    
    # ========== NET INCOME CALCULATION ==========
    print("\n\n" + "=" * 70)
    gross_profit = total_revenue
    net_income = gross_profit - total_expenses
    net_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
    
    print(f"   Gross Profit                   KES {gross_profit:>15,.2f}")
    print(f"   Operating Expenses            (KES {total_expenses:>14,.2f})")
    print(f"   {'─' * 50}")
    print(f"   NET INCOME                     KES {net_income:>15,.2f}")
    print(f"\n   Net Profit Margin              {net_margin:>15,.1f}%")
    print("=" * 70)
    
    # ========== KEY METRICS ==========
    print("\n\n📈 KEY METRICS")
    print("-" * 70)
    
    avg_invoice = total_revenue / len(paid_invoices) if paid_invoices else 0
    print(f"   Total Invoices Generated       {len(invoices):>15,}")
    print(f"   Paid Invoices                  {len(paid_invoices):>15,}")
    print(f"   Average Invoice Value          KES {avg_invoice:>15,.2f}")
    
    # Get customer count
    customers = await db.customers.find().to_list(None)
    print(f"   Active Customers               {len(customers):>15,}")
    
    if customers:
        revenue_per_customer = total_revenue / len(customers)
        print(f"   Revenue per Customer           KES {revenue_per_customer:>15,.2f}")
    
    print()
    
    # ========== EXPENSE BREAKDOWN ==========
    if sorted_expenses:
        print("\n📊 EXPENSE BREAKDOWN")
        print("-" * 70)
        print("\n   Category Analysis:")
        print()
        for category, amount in sorted_expenses[:5]:  # Top 5
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            print(f"   {category:<25} {percentage:>6.1f}%  KES {amount:>12,.2f}")
    
    # ========== CASH FLOW SNAPSHOT ==========
    print("\n\n💰 CASH FLOW SNAPSHOT")
    print("-" * 70)
    
    # Get all payment transactions
    payments = await db.transactions.find({"type": "payment"}).to_list(None)
    total_payments_received = sum(p.get("amount", 0) for p in payments)
    
    print(f"   Total Payments Received        KES {total_payments_received:>15,.2f}")
    print(f"   Total Expenses Paid           (KES {total_expenses:>14,.2f})")
    print(f"   {'─' * 50}")
    net_cash_flow = total_payments_received - total_expenses
    print(f"   Net Cash Flow                  KES {net_cash_flow:>15,.2f}")
    
    # ========== ACCOUNTS RECEIVABLE ==========
    print("\n\n📄 ACCOUNTS RECEIVABLE")
    print("-" * 70)
    
    outstanding_count = len(pending_invoices)
    print(f"   Outstanding Invoices           {outstanding_count:>15,}")
    print(f"   Outstanding Amount             KES {total_pending:>15,.2f}")
    
    if total_invoiced > 0:
        collection_rate = (total_paid / total_invoiced * 100)
        print(f"   Collection Rate                {collection_rate:>15,.1f}%")
    
    print("\n" + "=" * 70)
    print("   Report Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70 + "\n")
    
    client.close()

async def generate_summary_dashboard():
    """Generate a quick financial dashboard"""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("\n" + "=" * 70)
    print("                    FINANCIAL DASHBOARD SUMMARY")
    print("=" * 70)
    
    # Get counts
    invoice_count = await db.invoices.count_documents({})
    customer_count = await db.customers.count_documents({})
    transaction_count = await db.transactions.count_documents({})
    
    # Get totals
    invoices = await db.invoices.find().to_list(None)
    total_billed = sum(inv.get("amount", 0) for inv in invoices)
    
    paid_invoices = [inv for inv in invoices if inv.get("status") == "paid"]
    total_paid = sum(inv.get("amount", 0) for inv in paid_invoices)
    
    pending_invoices = [inv for inv in invoices if inv.get("status") in ["sent", "pending"]]
    total_outstanding = sum(inv.get("amount", 0) for inv in pending_invoices)
    
    print(f"\n   📊 Database Records")
    print(f"      Invoices:        {invoice_count:>10,}")
    print(f"      Customers:       {customer_count:>10,}")
    print(f"      Transactions:    {transaction_count:>10,}")
    
    print(f"\n   💰 Financial Overview")
    print(f"      Total Billed:    KES {total_billed:>15,.2f}")
    print(f"      Total Paid:      KES {total_paid:>15,.2f}")
    print(f"      Outstanding:     KES {total_outstanding:>15,.2f}")
    
    collection_rate = (total_paid / total_billed * 100) if total_billed > 0 else 0
    print(f"\n   📈 Collection Rate:  {collection_rate:.1f}%")
    
    print("\n" + "=" * 70 + "\n")
    
    client.close()

async def main():
    """Main function to generate reports"""
    
    print("\n🚀 AI Financial Agent - Report Generator")
    print("\nGenerating financial statements from your existing data...\n")
    
    try:
        # Generate summary first
        await generate_summary_dashboard()
        
        # Generate detailed income statement
        await generate_income_statement()
        
        print("\n✅ Reports generated successfully!")
        print("\n💡 Next Steps:")
        print("   1. Review the reports above")
        print("   2. Check /docs/FINANCIAL_STATEMENTS_GUIDE.md for more options")
        print("   3. Implement API endpoints for automated report generation")
        print("   4. Create frontend UI for interactive reports")
        
    except Exception as e:
        print(f"\n❌ Error generating reports: {e}")
        print("   Make sure MongoDB connection is working")

if __name__ == "__main__":
    asyncio.run(main())
