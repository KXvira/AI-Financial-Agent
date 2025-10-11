"""
Add Recent Data to Database (Last 30 Days)
Generates more frequent recent transactions to see on dashboard
"""
import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "financial_agent")

# Get the user_id from existing data
USER_ID = "68ea89d7c2d973dca0591c34"  # From the previous script

# Customers
CUSTOMERS = [
    {"name": "ABC Corporation", "email": "accounts@abc-corp.com"},
    {"name": "XYZ Enterprises", "email": "finance@xyz-ent.com"},
    {"name": "Digital Marketing Co", "email": "billing@digitalmarketing.com"},
    {"name": "Retail Store Inc", "email": "payments@retailstore.com"},
    {"name": "Consulting Group", "email": "admin@consultinggroup.com"},
    {"name": "Software Startup", "email": "accounts@softwarestartup.io"},
]

# Recent services (more varied pricing)
SERVICES = [
    {"name": "Website Maintenance", "price_range": (8000, 15000)},
    {"name": "Mobile App Update", "price_range": (12000, 25000)},
    {"name": "IT Support Service", "price_range": (5000, 12000)},
    {"name": "Cloud Hosting", "price_range": (4000, 8000)},
    {"name": "API Integration", "price_range": (15000, 30000)},
    {"name": "Security Audit", "price_range": (10000, 20000)},
    {"name": "Performance Optimization", "price_range": (8000, 18000)},
]

# Recent expenses
RECENT_EXPENSES = [
    {"category": "Office Supplies", "amount_range": (1500, 4000)},
    {"category": "Internet & Utilities", "amount_range": (3500, 4500)},
    {"category": "Software Licenses", "amount_range": (9000, 11000)},
    {"category": "Marketing", "amount_range": (6000, 12000)},
    {"category": "Travel", "amount_range": (4000, 8000)},
    {"category": "Professional Services", "amount_range": (7000, 15000)},
    {"category": "Equipment Repair", "amount_range": (2000, 5000)},
]


def generate_mpesa_reference():
    """Generate realistic M-Pesa transaction reference"""
    prefixes = ["SH", "RI", "RK", "RC"]
    prefix = random.choice(prefixes)
    number = random.randint(1000000000, 9999999999)
    return f"{prefix}{number}"


def generate_phone_number():
    """Generate Kenyan phone number"""
    prefixes = ["254701", "254702", "254710", "254722", "254733"]
    return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"


async def add_recent_data():
    """Add recent data for the last 30 days"""
    
    print("=" * 60)
    print("ADDING RECENT DATA (LAST 30 DAYS)")
    print("=" * 60)
    print(f"User ID: {USER_ID}")
    print()
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB]
    
    print("✓ Connected to MongoDB")
    
    # Collections
    invoices_col = db.invoices
    transactions_col = db.transactions
    receipts_col = db.receipts
    
    # Get the last invoice number
    last_invoice = await invoices_col.find_one(
        {"user_id": USER_ID}, 
        sort=[("invoice_number", -1)]
    )
    invoice_counter = 2000 if not last_invoice else int(last_invoice["invoice_number"].split("-")[1]) + 1
    
    # Get the last receipt number
    last_receipt = await receipts_col.find_one(
        {"user_id": USER_ID}, 
        sort=[("receipt_number", -1)]
    )
    receipt_counter = 6000 if not last_receipt else int(last_receipt["receipt_number"].split("-")[1]) + 1
    
    # Start date: 30 days ago
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    invoices = []
    transactions = []
    receipts = []
    
    print("\n💰 Generating recent invoices and payments...")
    
    # Generate more frequent recent transactions (1-3 per day)
    current_date = start_date
    while current_date <= end_date:
        # Generate 1-3 invoices per day for recent data
        num_invoices = random.randint(1, 3)
        
        for _ in range(num_invoices):
            customer = random.choice(CUSTOMERS)
            service = random.choice(SERVICES)
            
            invoice_amount = random.uniform(service["price_range"][0], service["price_range"][1])
            invoice_amount = round(invoice_amount, 2)
            
            # Random time during the day
            invoice_datetime = current_date + timedelta(
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59)
            )
            
            due_date = invoice_datetime + timedelta(days=random.choice([7, 14, 30]))
            
            invoice_id = ObjectId()
            invoice_number = f"INV-{invoice_counter}"
            invoice_counter += 1
            
            # Higher chance of being paid for recent invoices
            is_paid = random.random() > 0.2  # 80% paid
            
            invoice = {
                "_id": invoice_id,
                "user_id": USER_ID,
                "invoice_number": invoice_number,
                "customer_name": customer["name"],
                "customer_email": customer["email"],
                "amount": invoice_amount,
                "currency": "KES",
                "status": "paid" if is_paid else "pending",
                "issue_date": invoice_datetime,
                "due_date": due_date,
                "description": service["name"],
                "created_at": invoice_datetime,
                "updated_at": invoice_datetime,
            }
            
            invoices.append(invoice)
            
            # Generate payment for paid invoices
            if is_paid:
                # Most payments happen within a few days
                payment_delay = random.randint(0, 5)
                payment_datetime = invoice_datetime + timedelta(
                    days=payment_delay,
                    hours=random.randint(9, 16),
                    minutes=random.randint(0, 59)
                )
                
                if payment_datetime > end_date:
                    payment_datetime = end_date
                
                # Create transaction record
                transaction_id = ObjectId()
                mpesa_ref = generate_mpesa_reference()
                phone = generate_phone_number()
                
                transaction = {
                    "_id": transaction_id,
                    "user_id": USER_ID,
                    "invoice_id": str(invoice_id),
                    "invoice_number": invoice_number,
                    "type": "payment",
                    "amount": invoice_amount,
                    "currency": "KES",
                    "status": "completed",
                    "mpesa_reference": mpesa_ref,
                    "phone_number": phone,
                    "customer_name": customer["name"],
                    "description": f"Payment for {invoice_number} - {service['name']}",
                    "payment_method": "mpesa",
                    "created_at": payment_datetime,
                    "updated_at": payment_datetime,
                }
                
                transactions.append(transaction)
        
        current_date += timedelta(days=1)
    
    print(f"✓ Generated {len(invoices)} recent invoices")
    print(f"✓ Generated {len(transactions)} payment transactions")
    
    # Generate recent expenses (more frequent)
    print("\n🧾 Generating recent expenses...")
    
    current_date = start_date
    while current_date <= end_date:
        # Random chance of expense each day (40% chance)
        if random.random() < 0.4:
            expense = random.choice(RECENT_EXPENSES)
            amount = random.uniform(expense["amount_range"][0], expense["amount_range"][1])
            amount = round(amount, 2)
            
            expense_datetime = current_date + timedelta(
                hours=random.randint(9, 17),
                minutes=random.randint(0, 59)
            )
            
            receipt_id = ObjectId()
            receipt_number = f"RCP-{receipt_counter}"
            receipt_counter += 1
            
            receipt = {
                "_id": receipt_id,
                "user_id": USER_ID,
                "receipt_number": receipt_number,
                "category": expense["category"],
                "amount": amount,
                "currency": "KES",
                "status": "processed",
                "created_at": expense_datetime,
                "updated_at": expense_datetime,
                "ocr_data": {
                    "extracted_data": {
                        "vendor_name": f"{expense['category']} Provider",
                        "total_amount": amount,
                        "date": expense_datetime.strftime("%Y-%m-%d"),
                        "category": expense["category"],
                    },
                    "confidence": random.uniform(0.88, 0.98),
                }
            }
            
            receipts.append(receipt)
            
            # Create expense transaction
            transaction = {
                "_id": ObjectId(),
                "user_id": USER_ID,
                "receipt_id": str(receipt_id),
                "type": "expense",
                "amount": amount,
                "currency": "KES",
                "status": "completed",
                "description": f"{expense['category']} - {expense_datetime.strftime('%d %b %Y')}",
                "category": expense["category"],
                "created_at": expense_datetime,
                "updated_at": expense_datetime,
            }
            
            transactions.append(transaction)
        
        current_date += timedelta(days=1)
    
    print(f"✓ Generated {len(receipts)} expense receipts")
    print(f"✓ Total recent transactions: {len(transactions)}")
    
    # Add some transactions for TODAY
    print("\n📅 Adding transactions for TODAY...")
    
    today = datetime.now()
    today_transactions = 0
    
    # Add 3-5 transactions today
    for i in range(random.randint(3, 5)):
        if i % 2 == 0:  # Payment
            customer = random.choice(CUSTOMERS)
            service = random.choice(SERVICES)
            amount = random.uniform(8000, 20000)
            amount = round(amount, 2)
            
            transaction_time = datetime(
                today.year, today.month, today.day,
                random.randint(9, 17),
                random.randint(0, 59)
            )
            
            invoice_id = ObjectId()
            invoice_number = f"INV-{invoice_counter}"
            invoice_counter += 1
            
            # Create invoice
            invoice = {
                "_id": invoice_id,
                "user_id": USER_ID,
                "invoice_number": invoice_number,
                "customer_name": customer["name"],
                "customer_email": customer["email"],
                "amount": amount,
                "currency": "KES",
                "status": "paid",
                "issue_date": transaction_time,
                "due_date": transaction_time + timedelta(days=14),
                "description": service["name"],
                "created_at": transaction_time,
                "updated_at": transaction_time,
            }
            invoices.append(invoice)
            
            # Create payment
            transaction = {
                "_id": ObjectId(),
                "user_id": USER_ID,
                "invoice_id": str(invoice_id),
                "invoice_number": invoice_number,
                "type": "payment",
                "amount": amount,
                "currency": "KES",
                "status": "completed",
                "mpesa_reference": generate_mpesa_reference(),
                "phone_number": generate_phone_number(),
                "customer_name": customer["name"],
                "description": f"Payment for {invoice_number} - {service['name']}",
                "payment_method": "mpesa",
                "created_at": transaction_time,
                "updated_at": transaction_time,
            }
            transactions.append(transaction)
            today_transactions += 1
            
        else:  # Expense
            expense = random.choice(RECENT_EXPENSES)
            amount = random.uniform(expense["amount_range"][0], expense["amount_range"][1])
            amount = round(amount, 2)
            
            transaction_time = datetime(
                today.year, today.month, today.day,
                random.randint(10, 16),
                random.randint(0, 59)
            )
            
            receipt_id = ObjectId()
            receipt_number = f"RCP-{receipt_counter}"
            receipt_counter += 1
            
            receipt = {
                "_id": receipt_id,
                "user_id": USER_ID,
                "receipt_number": receipt_number,
                "category": expense["category"],
                "amount": amount,
                "currency": "KES",
                "status": "processed",
                "created_at": transaction_time,
                "updated_at": transaction_time,
                "ocr_data": {
                    "extracted_data": {
                        "vendor_name": f"{expense['category']} Provider",
                        "total_amount": amount,
                        "date": transaction_time.strftime("%Y-%m-%d"),
                        "category": expense["category"],
                    },
                    "confidence": random.uniform(0.90, 0.98),
                }
            }
            receipts.append(receipt)
            
            transaction = {
                "_id": ObjectId(),
                "user_id": USER_ID,
                "receipt_id": str(receipt_id),
                "type": "expense",
                "amount": amount,
                "currency": "KES",
                "status": "completed",
                "description": f"{expense['category']} - Today",
                "category": expense["category"],
                "created_at": transaction_time,
                "updated_at": transaction_time,
            }
            transactions.append(transaction)
            today_transactions += 1
    
    print(f"✓ Added {today_transactions} transactions for today")
    
    # Insert into database
    print("\n💾 Inserting data into database...")
    
    if invoices:
        await invoices_col.insert_many(invoices)
        print(f"✓ Inserted {len(invoices)} invoices")
    
    if transactions:
        await transactions_col.insert_many(transactions)
        print(f"✓ Inserted {len(transactions)} transactions")
    
    if receipts:
        await receipts_col.insert_many(receipts)
        print(f"✓ Inserted {len(receipts)} receipts")
    
    # Calculate summary for last 30 days
    print("\n" + "=" * 60)
    print("LAST 30 DAYS SUMMARY")
    print("=" * 60)
    
    total_invoiced = sum(inv["amount"] for inv in invoices)
    paid_invoices = [inv for inv in invoices if inv["status"] == "paid"]
    total_paid = sum(inv["amount"] for inv in paid_invoices)
    payment_transactions = [t for t in transactions if t["type"] == "payment"]
    expense_transactions = [t for t in transactions if t["type"] == "expense"]
    total_expenses = sum(t["amount"] for t in expense_transactions)
    net_profit = sum(t["amount"] for t in payment_transactions) - total_expenses
    
    print(f"Total Invoiced: KES {total_invoiced:,.2f}")
    print(f"Total Paid: KES {total_paid:,.2f}")
    print(f"Payment Rate: {len(paid_invoices)/len(invoices)*100:.1f}%")
    print(f"Total Expenses: KES {total_expenses:,.2f}")
    print(f"Net Profit: KES {net_profit:,.2f}")
    
    # Today's summary
    today_payments = [t for t in payment_transactions if t["created_at"].date() == today.date()]
    today_expenses = [t for t in expense_transactions if t["created_at"].date() == today.date()]
    
    print(f"\nToday's Activity:")
    print(f"Payments Received: KES {sum(t['amount'] for t in today_payments):,.2f}")
    print(f"Expenses: KES {sum(t['amount'] for t in today_expenses):,.2f}")
    print(f"Transactions: {len(today_payments) + len(today_expenses)}")
    
    print("\n" + "=" * 60)
    print("✅ RECENT DATA ADDED SUCCESSFULLY!")
    print("=" * 60)
    print("\nRefresh your dashboard to see the updated data.")
    print("You should now see recent transactions including today's activity!")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(add_recent_data())
