"""
Check payment-related collections
"""
from pymongo import MongoClient
import os

# Connect to MongoDB
mongo_uri = "mongodb+srv://alfred:test@mongodbtutorial.f71m5.mongodb.net/?retryWrites=true&w=majority&appName=MongoDBtutorial"
client = MongoClient(mongo_uri)
db = client['financial_agent']

print("=" * 70)
print("PAYMENT DATA ANALYSIS")
print("=" * 70)

# Check payments collection
payments_count = db.payments.count_documents({})
print(f"\n📦 Payments Collection: {payments_count} documents")

if payments_count > 0:
    sample = db.payments.find_one()
    print(f"\nSample payment fields:")
    for key in sorted(sample.keys()):
        print(f"  - {key}")
else:
    print("  ❌ No payments found in collection")

# Check ai_matching_summary
ai_summary = db.ai_matching_summary.find_one({})
if ai_summary:
    print(f"\n🤖 AI Matching Summary:")
    print(f"  - Correct Matches: {ai_summary.get('correct_matches', 0)}")
    print(f"  - Unmatched Count: {ai_summary.get('unmatched_count', 0)}")
    print(f"  - AI Accuracy: {ai_summary.get('ai_accuracy', 0)}%")
else:
    print(f"\n❌ No AI matching summary found")

# Check if we need to generate payment data from invoices
invoices_with_payment = db.invoices.count_documents({"status": "paid", "payment_date": {"$exists": True}})
print(f"\n📄 Invoices with payment info: {invoices_with_payment}")

if invoices_with_payment > 0:
    print(f"\n💡 Solution: Generate payment records from paid invoices")
    sample_invoice = db.invoices.find_one({"status": "paid", "payment_date": {"$exists": True}})
    if sample_invoice:
        print(f"\nSample invoice payment fields:")
        print(f"  - invoice_id: {sample_invoice.get('invoice_id')}")
        print(f"  - payment_date: {sample_invoice.get('payment_date')}")
        print(f"  - total_amount: {sample_invoice.get('total_amount')}")
        print(f"  - customer_name: {sample_invoice.get('customer_name')}")

print("\n" + "=" * 70)
