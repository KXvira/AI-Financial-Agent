"""
Generate realistic financial data for a 5-year period
This script creates sample transactions, invoices, and M-Pesa payments
to demonstrate the AI insights functionality.
"""

import sys
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymongo import MongoClient

# Get MongoDB connection
def get_database():
    """Get MongoDB database connection"""
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.environ.get("MONGO_DB", "financial_agent")
    print(f"   Connecting to MongoDB: {mongo_uri[:50]}...")
    client = MongoClient(mongo_uri)
    return client[database_name]

# Sample data configurations
CUSTOMERS = [
    "Acme Corp Kenya Ltd",
    "Safari Traders",
    "Nairobi Tech Solutions",
    "East Africa Supplies",
    "Mombasa Imports Ltd",
    "Kisumu Distributors",
    "Highland Merchants",
    "Coastal Enterprises",
    "Valley View Trading",
    "Summit Business Group",
    "Lakeside Partners",
    "Metro Commerce Ltd",
    "Pioneer Ventures",
    "Horizon Trading Co",
    "Equity Suppliers"
]

PRODUCTS_SERVICES = [
    {"name": "Office Supplies", "price_range": (5000, 50000)},
    {"name": "IT Services", "price_range": (20000, 200000)},
    {"name": "Consulting Services", "price_range": (30000, 150000)},
    {"name": "Marketing Services", "price_range": (25000, 100000)},
    {"name": "Software Licenses", "price_range": (10000, 80000)},
    {"name": "Hardware Equipment", "price_range": (15000, 120000)},
    {"name": "Training Services", "price_range": (20000, 90000)},
    {"name": "Maintenance Contract", "price_range": (8000, 40000)},
    {"name": "Cloud Services", "price_range": (12000, 60000)},
    {"name": "Web Development", "price_range": (40000, 250000)},
]

EXPENSE_CATEGORIES = [
    {"name": "Salaries & Wages", "range": (200000, 400000)},
    {"name": "Rent", "range": (80000, 120000)},
    {"name": "Utilities", "range": (15000, 30000)},
    {"name": "Internet & Phone", "range": (8000, 15000)},
    {"name": "Office Supplies", "range": (5000, 20000)},
    {"name": "Marketing", "range": (20000, 80000)},
    {"name": "Transportation", "range": (10000, 30000)},
    {"name": "Insurance", "range": (15000, 25000)},
    {"name": "Software Subscriptions", "range": (10000, 30000)},
    {"name": "Professional Fees", "range": (15000, 50000)},
]

PHONE_PREFIXES = ["254712", "254722", "254733", "254745", "254756", "254768", "254790"]

def generate_phone_number():
    """Generate a random Kenyan phone number"""
    prefix = random.choice(PHONE_PREFIXES)
    suffix = ''.join([str(random.randint(0, 9)) for _ in range(6)])
    return prefix + suffix

def generate_mpesa_reference():
    """Generate a realistic M-Pesa reference code"""
    return f"QW{random.randint(10000000, 99999999)}XY"

def generate_invoice_number(year, month, sequence):
    """Generate invoice number in format INV-YYYY-MM-XXXX"""
    return f"INV-{year}-{month:02d}-{sequence:04d}"

def generate_data_for_period(start_date, end_date):
    """Generate financial data for a specific period"""
    db = get_database()
    
    # Collections
    transactions = db['transactions']
    invoices = db['invoices']
    mpesa_payments = db['mpesa_payments']
    
    print(f"\n🔄 Generating data from {start_date.date()} to {end_date.date()}...")
    
    # Clear existing data
    print("   Clearing existing data...")
    transactions.delete_many({})
    invoices.delete_many({})
    mpesa_payments.delete_many({})
    
    current_date = start_date
    invoice_sequence = 1
    transaction_count = 0
    invoice_count = 0
    mpesa_count = 0
    
    while current_date <= end_date:
        # Generate 2-5 transactions per day
        daily_transactions = random.randint(2, 5)
        
        for _ in range(daily_transactions):
            transaction_type = random.choice(['income', 'income', 'income', 'expense'])  # More income than expenses
            
            if transaction_type == 'income':
                # Generate income transaction
                customer = random.choice(CUSTOMERS)
                product = random.choice(PRODUCTS_SERVICES)
                amount = round(random.uniform(*product['price_range']), 2)
                
                # Create invoice
                invoice_number = generate_invoice_number(current_date.year, current_date.month, invoice_sequence)
                invoice_due_date = current_date + timedelta(days=30)
                
                # Random payment status
                payment_status = random.choice(['paid', 'paid', 'paid', 'pending', 'overdue'])
                paid_amount = amount if payment_status == 'paid' else (amount * random.uniform(0, 0.8) if payment_status == 'partial' else 0)
                
                total_with_tax = round(amount * 1.16, 2)
                
                invoice_doc = {
                    'invoice_number': invoice_number,
                    'customer_name': customer,
                    'customer_email': f"{customer.lower().replace(' ', '').replace('ltd', '').replace('.', '')}@example.com",
                    'customer_phone': generate_phone_number(),
                    'issue_date': current_date,
                    'due_date': invoice_due_date,
                    'items': [
                        {
                            'description': product['name'],
                            'quantity': random.randint(1, 5),
                            'unit_price': amount / random.randint(1, 5),
                            'amount': amount
                        }
                    ],
                    'subtotal': amount,
                    'tax': round(amount * 0.16, 2),  # 16% VAT in Kenya
                    'total': total_with_tax,
                    'amount': total_with_tax,  # Add 'amount' field for dashboard queries
                    'paid_amount': round(paid_amount * 1.16 if payment_status == 'paid' else 0, 2),
                    'status': payment_status,
                    'payment_method': 'M-Pesa' if payment_status == 'paid' else None,
                    'notes': f"Invoice for {product['name']} services",
                    'created_at': current_date,
                    'updated_at': current_date
                }
                
                invoices.insert_one(invoice_doc)
                invoice_sequence += 1
                invoice_count += 1
                
                # Create corresponding transaction if paid
                if payment_status == 'paid':
                    transaction_amount = round(amount * 1.16, 2)
                    transaction_doc = {
                        'transaction_id': f"TXN-{current_date.year}{current_date.month:02d}{current_date.day:02d}-{random.randint(1000, 9999)}",
                        'type': 'payment',  # Changed from 'income' to 'payment' for dashboard compatibility
                        'category': 'Sales Revenue',
                        'amount': transaction_amount,
                        'description': f"Payment received for {invoice_number} - {product['name']}",
                        'customer': customer,
                        'invoice_number': invoice_number,
                        'date': current_date,
                        'payment_method': 'M-Pesa',
                        'reference': generate_mpesa_reference(),
                        'status': 'completed',
                        'created_at': current_date,
                        'updated_at': current_date
                    }
                    
                    transactions.insert_one(transaction_doc)
                    transaction_count += 1
                    
                    # Create M-Pesa payment record
                    mpesa_doc = {
                        'TransactionType': 'CustomerPayBillOnline',
                        'TransID': generate_mpesa_reference(),
                        'TransTime': current_date.strftime('%Y%m%d%H%M%S'),
                        'TransAmount': round(amount * 1.16, 2),
                        'BusinessShortCode': '174379',
                        'BillRefNumber': invoice_number,
                        'InvoiceNumber': invoice_number,
                        'OrgAccountBalance': round(random.uniform(500000, 2000000), 2),
                        'ThirdPartyTransID': '',
                        'MSISDN': generate_phone_number(),
                        'FirstName': customer.split()[0],
                        'MiddleName': '',
                        'LastName': customer.split()[-1] if len(customer.split()) > 1 else '',
                        'processed': True,
                        'created_at': current_date,
                        'updated_at': current_date
                    }
                    
                    mpesa_payments.insert_one(mpesa_doc)
                    mpesa_count += 1
            
            else:
                # Generate expense transaction
                expense = random.choice(EXPENSE_CATEGORIES)
                amount = round(random.uniform(*expense['range']), 2)
                
                transaction_doc = {
                    'transaction_id': f"TXN-{current_date.year}{current_date.month:02d}{current_date.day:02d}-{random.randint(1000, 9999)}",
                    'type': 'expense',
                    'category': expense['name'],
                    'amount': amount,
                    'description': f"{expense['name']} - {current_date.strftime('%B %Y')}",
                    'vendor': f"{expense['name']} Provider",
                    'date': current_date,
                    'payment_method': random.choice(['Bank Transfer', 'M-Pesa', 'Cash', 'Check']),
                    'reference': generate_mpesa_reference() if random.random() > 0.5 else None,
                    'status': 'completed',
                    'created_at': current_date,
                    'updated_at': current_date
                }
                
                transactions.insert_one(transaction_doc)
                transaction_count += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    print(f"   ✅ Created {transaction_count} transactions")
    print(f"   ✅ Created {invoice_count} invoices")
    print(f"   ✅ Created {mpesa_count} M-Pesa payments")
    
    return transaction_count, invoice_count, mpesa_count

def main():
    """Generate 5 years of financial data"""
    print("\n" + "="*60)
    print("   FINANCIAL DATA GENERATOR - 5 YEAR PERIOD")
    print("="*60)
    
    # Define 5-year period
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*5)
    
    print(f"\n📅 Period: {start_date.date()} to {end_date.date()}")
    print(f"   Duration: 5 years ({(end_date - start_date).days} days)")
    
    try:
        # Generate data
        total_transactions, total_invoices, total_mpesa = generate_data_for_period(start_date, end_date)
        
        # Calculate totals
        db = get_database()
        
        # Calculate revenue (from payments)
        income_pipeline = [
            {'$match': {'type': 'payment'}},  # Changed from 'income' to 'payment'
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        income_result = list(db['transactions'].aggregate(income_pipeline))
        total_revenue = income_result[0]['total'] if income_result else 0
        
        # Calculate expenses
        expense_pipeline = [
            {'$match': {'type': 'expense'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        expense_result = list(db['transactions'].aggregate(expense_pipeline))
        total_expenses = expense_result[0]['total'] if expense_result else 0
        
        # Calculate invoice metrics
        paid_invoices = db['invoices'].count_documents({'status': 'paid'})
        pending_invoices = db['invoices'].count_documents({'status': 'pending'})
        overdue_invoices = db['invoices'].count_documents({'status': 'overdue'})
        
        print("\n" + "="*60)
        print("   GENERATION SUMMARY")
        print("="*60)
        print(f"\n📊 Data Created:")
        print(f"   • Transactions: {total_transactions:,}")
        print(f"   • Invoices: {total_invoices:,}")
        print(f"   • M-Pesa Payments: {total_mpesa:,}")
        
        print(f"\n💰 Financial Summary:")
        print(f"   • Total Revenue: KES {total_revenue:,.2f}")
        print(f"   • Total Expenses: KES {total_expenses:,.2f}")
        print(f"   • Net Profit: KES {(total_revenue - total_expenses):,.2f}")
        if total_revenue > 0:
            print(f"   • Profit Margin: {((total_revenue - total_expenses) / total_revenue * 100):.2f}%")
        else:
            print(f"   • Profit Margin: N/A (no revenue)")
        
        print(f"\n📄 Invoice Status:")
        print(f"   • Paid: {paid_invoices:,} ({paid_invoices/total_invoices*100:.1f}%)")
        print(f"   • Pending: {pending_invoices:,} ({pending_invoices/total_invoices*100:.1f}%)")
        print(f"   • Overdue: {overdue_invoices:,} ({overdue_invoices/total_invoices*100:.1f}%)")
        
        print("\n✅ Data generation completed successfully!")
        print("\n💡 You can now test the AI Insights with rich financial data!")
        print("   Navigate to: http://localhost:3000/ai-insights")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating data: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
