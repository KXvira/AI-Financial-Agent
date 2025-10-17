"""Debug script to test income statement data retrieval"""
import asyncio
from backend.database.mongodb import Database
from datetime import datetime
from dateutil import parser as date_parser

async def debug_income_statement():
    # Initialize database
    from motor.motor_asyncio import AsyncIOMotorClient
    MONGODB_URL = "mongodb+srv://alfredmunga31:Munga8820@cluster0.xkuqb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME = "financial_agent"
    
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    
    print("=" * 60)
    print("INCOME STATEMENT DEBUG")
    print("=" * 60)
    
    # Test 1: Count all invoices
    total_count = await db["invoices"].count_documents({})
    print(f"\n1. Total invoices in database: {total_count}")
    
    # Test 2: Get sample invoice
    sample = await db["invoices"].find_one({})
    if sample:
        print(f"\n2. Sample invoice fields:")
        for key in sample.keys():
            print(f"   - {key}: {sample[key]} (type: {type(sample[key]).__name__})")
    
    # Test 3: Get all invoices
    all_invoices = await db["invoices"].find({}).to_list(None)
    print(f"\n3. Fetched {len(all_invoices)} invoices")
    
    # Test 4: Check date formats
    start_dt = datetime(2024, 1, 1)
    end_dt = datetime(2025, 12, 31)
    
    print(f"\n4. Filtering by date range: {start_dt.date()} to {end_dt.date()}")
    
    filtered = []
    date_samples = []
    for i, invoice in enumerate(all_invoices[:10]):  # Check first 10
        issue_date_str = invoice.get("issue_date", invoice.get("date", ""))
        if issue_date_str:
            try:
                if isinstance(issue_date_str, datetime):
                    invoice_date = issue_date_str
                else:
                    invoice_date = date_parser.parse(str(issue_date_str))
                
                date_samples.append({
                    'invoice_num': invoice.get('invoice_number', 'N/A'),
                    'date_str': str(issue_date_str),
                    'parsed': invoice_date,
                    'in_range': start_dt <= invoice_date <= end_dt
                })
                
                if start_dt <= invoice_date <= end_dt:
                    filtered.append(invoice)
            except Exception as e:
                print(f"   Error parsing date for invoice {i}: {e}")
    
    print(f"\n   Date parsing samples (first 10):")
    for sample in date_samples[:5]:
        print(f"     - {sample['invoice_num']}: {sample['date_str']} -> {sample['parsed']} (in_range: {sample['in_range']})")
    
    print(f"\n   Invoices matching date range: {len(filtered)} out of {len(all_invoices)}")
    
    # Test 5: Check paid invoices
    paid_count = sum(1 for inv in all_invoices if inv.get('status') == 'paid')
    print(f"\n5. Paid invoices: {paid_count}")
    
    # Test 6: Calculate totals
    paid_invoices = [inv for inv in filtered if inv.get('status') == 'paid']
    total_paid = sum(inv.get("total_amount", inv.get("amount", 0)) for inv in paid_invoices)
    print(f"\n6. Total paid amount in date range: KES {total_paid:,.2f}")
    print(f"   From {len(paid_invoices)} paid invoices")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(debug_income_statement())
