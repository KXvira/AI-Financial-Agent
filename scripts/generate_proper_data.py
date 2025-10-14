"""
Generate realistic financial data matching exact database schemas
This script creates data compatible with dashboard queries and AI insights
"""

import sys
import os
from datetime import datetime, timedelta
import random
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
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.getenv("MONGO_DB", "financial_agent")
    print(f"   Connecting to: {mongo_uri[:50]}...")
    client = MongoClient(mongo_uri)
    return client[database_name]

# Sample data configurations
CUSTOMERS = [
    {"name": "Acme Corp Kenya Ltd", "email": "finance@acmecorp.co.ke", "city": "Nairobi"},
    {"name": "Safari Traders", "email": "accounts@safaritraders.com", "city": "Mombasa"},
    {"name": "Nairobi Tech Solutions", "email": "billing@nairobitch.ke", "city": "Nairobi"},
    {"name": "East Africa Supplies", "email": "payments@easupplies.com", "city": "Kampala"},
    {"name": "Mombasa Imports Ltd", "email": "finance@mombimports.co.ke", "city": "Mombasa"},
    {"name": "Kisumu Distributors", "email": "accounts@kisumudist.com", "city": "Kisumu"},
    {"name": "Highland Merchants", "email": "billing@highland.ke", "city": "Eldoret"},
    {"name": "Coastal Enterprises", "email": "finance@coastal.co.ke", "city": "Mombasa"},
    {"name": "Valley View Trading", "email": "accounts@valleyview.com", "city": "Nakuru"},
    {"name": "Summit Business Group", "email": "payments@summitbiz.ke", "city": "Nairobi"},
    {"name": "Lakeside Partners", "email": "finance@lakeside.co.ke", "city": "Kisumu"},
    {"name": "Metro Commerce Ltd", "email": "accounts@metrocommerce.ke", "city": "Nairobi"},
    {"name": "Pioneer Ventures", "email": "billing@pioneer.co.ke", "city": "Thika"},
    {"name": "Horizon Trading Co", "email": "finance@horizontrading.com", "city": "Nairobi"},
    {"name": "Equity Suppliers", "email": "payments@equitysuppliers.ke", "city": "Kisumu"}
]

PRODUCTS_SERVICES = [
    {"name": "Office Supplies", "price_range": (5000, 50000), "category": "Products"},
    {"name": "IT Services", "price_range": (20000, 200000), "category": "Services"},
    {"name": "Consulting Services", "price_range": (30000, 150000), "category": "Services"},
    {"name": "Marketing Services", "price_range": (25000, 100000), "category": "Services"},
    {"name": "Software Licenses", "price_range": (10000, 80000), "category": "Products"},
    {"name": "Hardware Equipment", "price_range": (15000, 120000), "category": "Products"},
    {"name": "Training Services", "price_range": (20000, 90000), "category": "Services"},
    {"name": "Maintenance Contract", "price_range": (8000, 40000), "category": "Services"},
    {"name": "Cloud Services", "price_range": (12000, 60000), "category": "Services"},
    {"name": "Web Development", "price_range": (40000, 250000), "category": "Services"},
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
    """Generate financial data for a specific period with proper schema"""
    db = get_database()
    
    # Collections
    invoices = db['invoices']
    transactions = db['transactions']
    mpesa_payments = db['mpesa_payments']
    customers_collection = db['customers']
    
    print(f"\n🔄 Generating data from {start_date.date()} to {end_date.date()}...")
    
    # Clear existing data
    print("   Clearing existing data...")
    invoices.delete_many({})
    transactions.delete_many({})
    mpesa_payments.delete_many({})
    customers_collection.delete_many({})
    
    # Create customer records first
    print("   Creating customer records...")
    customer_records = {}
    for idx, customer in enumerate(CUSTOMERS):
        customer_id = f"CUST-{idx+1:04d}"
        customer_phone = generate_phone_number()
        customer_doc = {
            'customer_id': customer_id,
            'name': customer['name'],
            'email': customer['email'],
            'phone_number': customer_phone,
            'city': customer['city'],
            'country': 'Kenya',
            'address': f"{random.randint(1, 999)} {random.choice(['Main', 'Industrial', 'Commercial', 'Business'])} Street",
            'total_invoices': 0,
            'total_revenue': 0,
            'outstanding_balance': 0,
            'status': 'active',
            'metadata': {},
            'created_at': start_date,
            'updated_at': start_date
        }
        result = customers_collection.insert_one(customer_doc)
        customer_records[customer['name']] = {
            '_id': result.inserted_id,
            'customer_id': customer_id,
            'phone': customer_phone,
            **customer
        }
    print(f"   ✅ Created {len(customer_records)} customer records")
    
    current_date = start_date
    invoice_sequence = 1
    transaction_count = 0
    invoice_count = 0
    mpesa_count = 0
    
    while current_date <= end_date:
        # Generate 2-5 transactions per day
        daily_transactions = random.randint(2, 5)
        
        for _ in range(daily_transactions):
            transaction_type = random.choice(['income', 'income', 'income', 'expense'])  # 75% income
            
            if transaction_type == 'income':
                # Generate income transaction (invoice + payment)
                customer_name = random.choice(list(customer_records.keys()))
                customer = customer_records[customer_name]
                product = random.choice(PRODUCTS_SERVICES)
                quantity = random.randint(1, 5)
                unit_price = round(random.uniform(*product['price_range']) / quantity, 2)
                subtotal = round(unit_price * quantity, 2)
                tax_amount = round(subtotal * 0.16, 2)  # 16% VAT
                total = round(subtotal + tax_amount, 2)
                
                # Determine payment status
                payment_status = random.choice([
                    'paid', 'paid', 'paid', 'paid', 'paid',  # 62.5% paid
                    'partially_paid',  # 12.5% partial
                    'overdue', 'overdue'  # 25% overdue/pending
                ])
                
                # Calculate amounts
                if payment_status == 'paid':
                    amount_paid = total
                    balance = 0
                elif payment_status == 'partially_paid':
                    amount_paid = round(total * random.uniform(0.3, 0.7), 2)
                    balance = round(total - amount_paid, 2)
                else:
                    amount_paid = 0
                    balance = total
                
                # Create invoice document (matching InvoiceSchema)
                invoice_number = generate_invoice_number(current_date.year, current_date.month, invoice_sequence)
                due_date = current_date + timedelta(days=30)
                
                invoice_doc = {
                    'invoice_number': invoice_number,
                    # Link to customer
                    'customer_id': customer['customer_id'],
                    # Nested customer object (for proper schema)
                    'customer': {
                        'id': customer['customer_id'],
                        'name': customer_name,
                        'phone_number': customer['phone'],
                        'email': customer['email'],
                        'city': customer['city'],
                        'country': 'Kenya',
                        'metadata': {}
                    },
                    # Flat fields for backward compatibility with invoice router
                    'customer_name': customer_name,
                    'customer_email': customer['email'],
                    'customer_phone': customer['phone'],
                    'items': [{
                        'description': product['name'],
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'amount': subtotal,
                        'tax_rate': 0.16,
                        'tax_amount': tax_amount,
                        'metadata': {'category': product['category']}
                    }],
                    'issue_date': current_date,  # datetime object (for backend compatibility)
                    'date_issued': current_date,  # datetime object (for schema)
                    'due_date': due_date,  # datetime object
                    'subtotal': subtotal,
                    'tax_total': tax_amount,
                    'discount_total': 0,
                    'total': total,
                    'amount': total,  # For dashboard aggregation
                    'amount_paid': amount_paid,
                    'balance': balance,
                    'status': payment_status,
                    'payment_reference': generate_mpesa_reference() if payment_status == 'paid' else None,
                    'payment_gateway': 'mpesa' if payment_status == 'paid' else None,
                    'payment_transactions': [],
                    'notes': f"Invoice for {product['name']}",
                    'description': f"{product['name']} for {customer['name']}",
                    'currency': 'KES',
                    'metadata': {'product_category': product['category']},
                    'created_at': current_date,  # datetime object
                    'updated_at': current_date  # datetime object
                }
                
                invoices.insert_one(invoice_doc)
                invoice_sequence += 1
                invoice_count += 1
                
                # Create payment transaction if paid
                if amount_paid > 0:
                    mpesa_ref = generate_mpesa_reference()
                    
                    transaction_doc = {
                        'type': 'payment',  # Dashboard looks for this
                        'reference': invoice_number,
                        'customer_id': customer['customer_id'],
                        'amount': amount_paid,
                        'customer_name': customer_name,
                        'description': f"Payment for {invoice_number} - {product['name']}",
                        'invoice_number': invoice_number,
                        'payment_method': 'mpesa',
                        'mpesa_reference': mpesa_ref,
                        'status': 'completed',  # Dashboard looks for this
                        'gateway': 'mpesa',
                        'phone_number': customer['phone'],
                        'currency': 'KES',
                        'metadata': {'customer_city': customer['city'], 'customer_id': customer['customer_id']},
                        'created_at': current_date,  # datetime object
                        'updated_at': current_date  # datetime object
                    }
                    
                    transactions.insert_one(transaction_doc)
                    transaction_count += 1
                    
                    # Create M-Pesa payment record
                    mpesa_doc = {
                        'TransactionType': 'CustomerPayBillOnline',
                        'TransID': mpesa_ref,
                        'TransTime': current_date.strftime('%Y%m%d%H%M%S'),
                        'TransAmount': amount_paid,
                        'BusinessShortCode': '174379',
                        'BillRefNumber': invoice_number,
                        'InvoiceNumber': invoice_number,
                        'CustomerID': customer['customer_id'],
                        'CustomerName': customer_name,
                        'OrgAccountBalance': round(random.uniform(500000, 2000000), 2),
                        'ThirdPartyTransID': '',
                        'MSISDN': customer['phone'],
                        'FirstName': customer_name.split()[0],
                        'MiddleName': '',
                        'LastName': customer_name.split()[-1] if len(customer_name.split()) > 1 else '',
                        'processed': True,
                        'created_at': current_date,  # datetime object
                        'updated_at': current_date  # datetime object
                    }
                    
                    mpesa_payments.insert_one(mpesa_doc)
                    mpesa_count += 1
                
                # Update customer totals
                customer_updates = customers_collection.find_one({'customer_id': customer['customer_id']})
                if customer_updates:
                    customers_collection.update_one(
                        {'customer_id': customer['customer_id']},
                        {
                            '$inc': {
                                'total_invoices': 1,
                                'total_revenue': amount_paid,
                                'outstanding_balance': balance
                            },
                            '$set': {'updated_at': current_date}
                        }
                    )
            
            else:
                # Generate expense transaction
                expense = random.choice(EXPENSE_CATEGORIES)
                amount = round(random.uniform(*expense['range']), 2)
                
                transaction_doc = {
                    'type': 'expense',
                    'reference': f"EXP-{current_date.year}{current_date.month:02d}{current_date.day:02d}-{random.randint(1000, 9999)}",
                    'amount': amount,
                    'customer_name': f"{expense['name']} Vendor",
                    'description': f"{expense['name']} - {current_date.strftime('%B %Y')}",
                    'payment_method': random.choice(['bank', 'mpesa', 'cash']),
                    'status': 'completed',
                    'currency': 'KES',
                    'category': expense['name'],
                    'metadata': {},
                    'created_at': current_date,  # datetime object
                    'updated_at': current_date  # datetime object
                }
                
                transactions.insert_one(transaction_doc)
                transaction_count += 1
        
        # Move to next day
        current_date += timedelta(days=1)
    
    print(f"   ✅ Created {transaction_count:,} transactions")
    print(f"   ✅ Created {invoice_count:,} invoices")
    print(f"   ✅ Created {mpesa_count:,} M-Pesa payments")
    
    return transaction_count, invoice_count, mpesa_count

def main():
    """Generate 5 years of financial data"""
    print("\n" + "="*70)
    print("   FINANCIAL DATA GENERATOR - PROPER SCHEMA ALIGNMENT")
    print("="*70)
    
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
        
        # Calculate revenue from payments
        payment_pipeline = [
            {'$match': {'type': 'payment', 'status': 'completed'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        payment_result = list(db['transactions'].aggregate(payment_pipeline))
        total_revenue = payment_result[0]['total'] if payment_result else 0
        
        # Calculate expenses
        expense_pipeline = [
            {'$match': {'type': 'expense'}},
            {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
        ]
        expense_result = list(db['transactions'].aggregate(expense_pipeline))
        total_expenses = expense_result[0]['total'] if expense_result else 0
        
        # Calculate invoice totals
        invoice_pipeline = [
            {'$group': {'_id': None, 'total': {'$sum': '$total'}}}
        ]
        invoice_result = list(db['invoices'].aggregate(invoice_pipeline))
        total_invoiced = invoice_result[0]['total'] if invoice_result else 0
        
        # Calculate invoice metrics
        paid_invoices = db['invoices'].count_documents({'status': 'paid'})
        partial_invoices = db['invoices'].count_documents({'status': 'partially_paid'})
        overdue_invoices = db['invoices'].count_documents({'status': 'overdue'})
        
        # Calculate outstanding balance
        outstanding = total_invoiced - total_revenue
        
        print("\n" + "="*70)
        print("   GENERATION SUMMARY")
        print("="*70)
        print(f"\n📊 Data Created:")
        print(f"   • Transactions: {total_transactions:,}")
        print(f"   • Invoices: {total_invoices:,}")
        print(f"   • M-Pesa Payments: {total_mpesa:,}")
        
        print(f"\n💰 Financial Summary:")
        print(f"   • Total Invoiced: KES {total_invoiced:,.2f}")
        print(f"   • Payments Received: KES {total_revenue:,.2f}")
        print(f"   • Total Expenses: KES {total_expenses:,.2f}")
        print(f"   • Outstanding Balance: KES {outstanding:,.2f}")
        print(f"   • Net Profit: KES {(total_revenue - total_expenses):,.2f}")
        if total_revenue > 0:
            print(f"   • Profit Margin: {((total_revenue - total_expenses) / total_revenue * 100):.2f}%")
            print(f"   • Collection Rate: {(total_revenue / total_invoiced * 100):.2f}%")
        
        print(f"\n📄 Invoice Status:")
        print(f"   • Paid: {paid_invoices:,} ({paid_invoices/total_invoices*100:.1f}%)")
        print(f"   • Partially Paid: {partial_invoices:,} ({partial_invoices/total_invoices*100:.1f}%)")
        print(f"   • Overdue: {overdue_invoices:,} ({overdue_invoices/total_invoices*100:.1f}%)")
        
        # Customer statistics
        total_customers = db['customers'].count_documents({})
        active_customers_pipeline = [
            {'$match': {'total_invoices': {'$gt': 0}}},
            {'$group': {'_id': None, 'count': {'$sum': 1}}}
        ]
        active_result = list(db['customers'].aggregate(active_customers_pipeline))
        active_customers = active_result[0]['count'] if active_result else 0
        
        print(f"\n👥 Customer Statistics:")
        print(f"   • Total Customers: {total_customers:,}")
        print(f"   • Active Customers: {active_customers:,}")
        print(f"   • Avg Invoices per Customer: {total_invoices/total_customers:.1f}")
        print(f"   • Avg Revenue per Customer: KES {total_revenue/total_customers:,.2f}")
        
        print("\n✅ Data generation completed successfully!")
        print("\n💡 Dashboard should now show:")
        print(f"   • Total Invoices: KES {total_invoiced:,.2f}")
        print(f"   • Payments Received: KES {total_revenue:,.2f}")
        print(f"   • Outstanding Balance: KES {outstanding:,.2f}")
        print(f"   • Daily Cash Flow: KES {(total_revenue - total_expenses) / ((end_date - start_date).days):,.2f}")
        
        print("\n🔄 Next Steps:")
        print("   1. Refresh the dashboard: http://localhost:3000")
        print("   2. Test AI Insights: http://localhost:3000/ai-insights")
        print("   3. Check invoice list: http://localhost:3000/invoices")
        print("\n" + "="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error generating data: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
