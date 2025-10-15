"""
Generate Receipt Data from Payments
This script creates receipt records based on existing payments in the database
"""
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import random
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def connect_to_database():
    """Connect to MongoDB"""
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        raise ValueError("MONGO_URI not found in environment variables")
    
    client = MongoClient(mongo_uri)
    db = client['financial_agent']
    return db

def generate_receipts(db):
    """
    Generate receipt records from payments
    - Payment receipts: Generated for completed payments
    - Invoice receipts: Generated for paid invoices
    """
    print("🧾 Starting Receipt Generation...\n")
    
    # Drop existing receipts collection
    if 'receipts' in db.list_collection_names():
        db.receipts.drop()
        print("🗑️  Cleared existing receipts\n")
    
    # Get all completed payments
    payments = list(db.payments.find({"status": "completed"}).sort("payment_date", -1))
    total_payments = len(payments)
    print(f"📊 Found {total_payments:,} completed payments")
    
    # Generate receipts for 80% of payments (realistic scenario)
    receipt_count = int(total_payments * 0.8)
    selected_payments = random.sample(payments, receipt_count)
    
    receipts = []
    payment_receipts = 0
    invoice_receipts = 0
    
    for payment in selected_payments:
        payment_id = payment['payment_id']
        invoice_id = payment.get('invoice_id')
        customer_id = payment.get('customer_id')
        amount = payment.get('amount', 0)
        payment_date = payment.get('payment_date')
        
        # Get customer info
        customer = db.customers.find_one({"customer_id": customer_id})
        customer_name = customer.get('name', 'Unknown') if customer else 'Unknown'
        customer_email = customer.get('email', '') if customer else ''
        customer_phone = customer.get('phone', '') if customer else ''
        
        # Parse payment date
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.utcnow()
        elif not isinstance(payment_date, datetime):
            payment_date = datetime.utcnow()
        
        # Determine receipt type (70% payment receipts, 30% invoice receipts)
        receipt_type = "payment" if random.random() < 0.7 else "invoice"
        
        if receipt_type == "payment":
            payment_receipts += 1
            receipt_number = f"RCT-PAY-{payment_date.strftime('%Y%m')}{str(payment_receipts).zfill(4)}"
            description = f"Payment received via {payment.get('payment_method', 'unknown').title()}"
        else:
            invoice_receipts += 1
            receipt_number = f"RCT-INV-{payment_date.strftime('%Y%m')}{str(invoice_receipts).zfill(4)}"
            
            # Get invoice info if available
            if invoice_id:
                invoice = db.invoices.find_one({"invoice_id": invoice_id})
                if invoice:
                    invoice_number = invoice.get('invoice_number', 'N/A')
                    description = f"Payment for Invoice {invoice_number}"
                else:
                    description = "Invoice payment received"
            else:
                description = "Invoice payment received"
        
        # Generate receipt metadata
        receipt = {
            'receipt_number': receipt_number,
            'receipt_type': receipt_type,
            'payment_id': payment_id,
            'invoice_id': invoice_id,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'amount': amount,
            'currency': 'KES',
            'payment_method': payment.get('payment_method', 'unknown'),
            'transaction_reference': payment.get('transaction_reference', ''),
            'description': description,
            'notes': f"Receipt generated for payment {payment.get('transaction_reference', '')}",
            'issued_date': payment_date,
            'status': 'issued',
            'generated_by': 'system',
            'pdf_generated': random.choice([True, False]),  # 50% have PDF
            'pdf_path': f"/receipts/{receipt_number}.pdf" if random.random() > 0.5 else None,
            'email_sent': random.choice([True, False]),  # 50% emailed
            'created_at': payment_date,
            'updated_at': payment_date
        }
        
        receipts.append(receipt)
    
    # Insert all receipts
    if receipts:
        db.receipts.insert_many(receipts)
        print(f"✅ Generated {len(receipts):,} receipts\n")
    
    # Calculate statistics
    total_amount = sum(r['amount'] for r in receipts)
    
    print("="*60)
    print("📈 RECEIPT GENERATION RESULTS")
    print("="*60)
    print(f"Total Receipts Generated:  {len(receipts):,}")
    print(f"  Payment Receipts:        {payment_receipts:,}")
    print(f"  Invoice Receipts:        {invoice_receipts:,}")
    print(f"\nTotal Amount:              KES {total_amount:,.2f}")
    print(f"\nPDF Generated:             {sum(1 for r in receipts if r['pdf_generated']):,}")
    print(f"Email Sent:                {sum(1 for r in receipts if r['email_sent']):,}")
    print("="*60)
    
    # Store summary statistics
    summary_stats = {
        'total_receipts': len(receipts),
        'payment_receipts': payment_receipts,
        'invoice_receipts': invoice_receipts,
        'total_amount': total_amount,
        'pdf_generated_count': sum(1 for r in receipts if r['pdf_generated']),
        'email_sent_count': sum(1 for r in receipts if r['email_sent']),
        'last_updated': datetime.utcnow()
    }
    
    db.receipt_summary.delete_many({})
    db.receipt_summary.insert_one(summary_stats)
    
    print(f"\n✅ Summary statistics stored in 'receipt_summary' collection")
    
    return summary_stats

def verify_results(db):
    """Verify the results are in the database"""
    print("\n🔍 Verifying Results...")
    
    # Check receipts collection
    total_receipts = db.receipts.count_documents({})
    payment_receipts = db.receipts.count_documents({'receipt_type': 'payment'})
    invoice_receipts = db.receipts.count_documents({'receipt_type': 'invoice'})
    
    print(f"  Total Receipts: {total_receipts:,}")
    print(f"  Payment Receipts: {payment_receipts:,}")
    print(f"  Invoice Receipts: {invoice_receipts:,}")
    
    # Check summary
    summary = db.receipt_summary.find_one({})
    if summary:
        print(f"\n  Summary Stats:")
        print(f"    Total Amount: KES {summary.get('total_amount', 0):,.2f}")
        print(f"    PDF Generated: {summary.get('pdf_generated_count', 0):,}")
        print(f"    Email Sent: {summary.get('email_sent_count', 0):,}")
    
    # Show sample receipts
    print("\n📋 Sample Receipts:")
    payment_receipt = db.receipts.find_one({'receipt_type': 'payment'})
    if payment_receipt:
        print(f"  Payment Receipt: {payment_receipt['receipt_number']}")
        print(f"    Customer: {payment_receipt['customer_name']}")
        print(f"    Amount: KES {payment_receipt['amount']:,.2f}")
    
    invoice_receipt = db.receipts.find_one({'receipt_type': 'invoice'})
    if invoice_receipt:
        print(f"  Invoice Receipt: {invoice_receipt['receipt_number']}")
        print(f"    Customer: {invoice_receipt['customer_name']}")
        print(f"    Amount: KES {invoice_receipt['amount']:,.2f}")
    
    print("\n✅ Verification complete!")

def main():
    """Main execution"""
    try:
        print("🚀 Receipt Generation from Payments\n")
        
        # Connect to database
        db = connect_to_database()
        print("✅ Connected to MongoDB: financial_agent\n")
        
        # Generate receipts
        results = generate_receipts(db)
        
        # Verify results
        verify_results(db)
        
        print("\n🎉 Receipt generation completed successfully!")
        print("\n💡 You can now:")
        print("   1. Refresh the Receipts page to see the generated receipts")
        print("   2. View payment and invoice receipts")
        print("   3. See receipt statistics")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
