"""
Check MongoDB data for predictive analytics
"""
from pymongo import MongoClient
import os
from datetime import datetime, timedelta

# Connect to MongoDB
mongo_uri = "mongodb+srv://alfred:test@mongodbtutorial.f71m5.mongodb.net/?retryWrites=true&w=majority&appName=MongoDBtutorial"
client = MongoClient(mongo_uri)
db = client['financial_agent']

print("=" * 70)
print("Checking Invoice Data for Revenue Forecast")
print("=" * 70)

# Check date range
end_date = datetime.now()
start_date = end_date - timedelta(days=365)
start_str = start_date.strftime("%Y-%m-%d")
end_str = end_date.strftime("%Y-%m-%d")

print(f"\nDate Range for Query:")
print(f"  Start: {start_str}")
print(f"  End: {end_str}")

# Check total invoices
total_invoices = db.invoices.count_documents({})
print(f"\nTotal Invoices: {total_invoices}")

# Check invoices with issue_date field
with_issue_date = db.invoices.count_documents({"issue_date": {"$exists": True}})
print(f"Invoices with issue_date: {with_issue_date}")

# Check paid/sent/overdue invoices
paid_invoices = db.invoices.count_documents({"status": {"$in": ["paid", "sent", "overdue"]}})
print(f"Paid/Sent/Overdue Invoices: {paid_invoices}")

# Try the actual query
print(f"\nTrying actual predictive query...")
query = {
    "issue_date": {"$gte": start_str, "$lte": end_str},
    "status": {"$in": ["paid", "sent", "overdue"]}
}
matching = db.invoices.count_documents(query)
print(f"Matching Invoices: {matching}")

# Get a sample
sample = db.invoices.find_one({"status": "paid"})
if sample:
    print(f"\nSample Invoice:")
    print(f"  issue_date: {sample.get('issue_date')}")
    print(f"  status: {sample.get('status')}")
    print(f"  total_amount: {sample.get('total_amount')}")

# Check if string comparison works
if matching > 0:
    print(f"\n✅ Query works! Should be able to forecast.")
    # Get one matching invoice
    one = db.invoices.find_one(query)
    print(f"  Sample match: {one['invoice_id']} - {one['issue_date']}")
else:
    print(f"\n❌ No matching invoices! Need to investigate.")
    # Check date format
    samples = list(db.invoices.find({"status": "paid"}).limit(3))
    print(f"\nSample issue_dates:")
    for s in samples:
        print(f"  {s.get('invoice_id')}: '{s.get('issue_date')}' (type: {type(s.get('issue_date'))})")

print("\n" + "=" * 70)
print("Checking Transaction Data for Expense Forecast")
print("=" * 70)

# Check transactions
total_txns = db.transactions.count_documents({})
print(f"\nTotal Transactions: {total_txns}")

expense_txns = db.transactions.count_documents({"type": "expense"})
print(f"Expense Transactions: {expense_txns}")

# Try the actual query
query = {
    "transaction_date": {"$gte": start_str, "$lte": end_str},
    "type": "expense",
    "status": "completed"
}
matching = db.transactions.count_documents(query)
print(f"Matching Expenses: {matching}")

if matching > 0:
    print(f"✅ Expense query works!")
else:
    print(f"❌ No matching expenses!")

print("\n" + "=" * 70)
