"""
Populate Database with Dummy Data for Small Business
Generates one year of realistic financial data
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

# Small business profile
BUSINESS_NAME = "Tech Solutions Ltd"
BUSINESS_EMAIL = "21407alfredmunga@gmail.com"
USER_ID = str(ObjectId())

# Customer pool for the small business
CUSTOMERS = [
    {"name": "ABC Corporation", "email": "accounts@abc-corp.com"},
    {"name": "XYZ Enterprises", "email": "finance@xyz-ent.com"},
    {"name": "Digital Marketing Co", "email": "billing@digitalmarketing.com"},
    {"name": "Retail Store Inc", "email": "payments@retailstore.com"},
    {"name": "Consulting Group", "email": "admin@consultinggroup.com"},
    {"name": "Software Startup", "email": "accounts@softwarestartup.io"},
    {"name": "Manufacturing Ltd", "email": "finance@manufacturing.com"},
    {"name": "Education Center", "email": "billing@educationcenter.com"},
]

# Service offerings
SERVICES = [
    {"name": "Web Development", "price_range": (15000, 50000)},
    {"name": "Mobile App Development", "price_range": (25000, 80000)},
    {"name": "IT Consulting", "price_range": (5000, 20000)},
    {"name": "Cloud Services", "price_range": (3000, 15000)},
    {"name": "Database Management", "price_range": (8000, 25000)},
    {"name": "Technical Support", "price_range": (2000, 10000)},
    {"name": "Software Maintenance", "price_range": (5000, 18000)},
    {"name": "System Integration", "price_range": (10000, 35000)},
]

# Expense categories
EXPENSE_CATEGORIES = [
    {"category": "Office Rent", "amount_range": (20000, 20000), "frequency": "monthly"},
    {"category": "Internet & Utilities", "amount_range": (3000, 5000), "frequency": "monthly"},
    {"category": "Software Licenses", "amount_range": (8000, 12000), "frequency": "monthly"},
    {"category": "Employee Salaries", "amount_range": (150000, 150000), "frequency": "monthly"},
    {"category": "Office Supplies", "amount_range": (2000, 5000), "frequency": "monthly"},
    {"category": "Marketing", "amount_range": (5000, 15000), "frequency": "monthly"},
    {"category": "Equipment", "amount_range": (10000, 50000), "frequency": "quarterly"},
    {"category": "Professional Services", "amount_range": (5000, 20000), "frequency": "quarterly"},
    {"category": "Travel", "amount_range": (3000, 10000), "frequency": "occasional"},
    {"category": "Training", "amount_range": (5000, 15000), "frequency": "occasional"},
]

# M-Pesa transaction references
MPESA_PREFIXES = ["SH", "RI", "RK", "RC"]


def generate_mpesa_reference():
    """Generate realistic M-Pesa transaction reference"""
    prefix = random.choice(MPESA_PREFIXES)
    number = random.randint(1000000000, 9999999999)
    return f"{prefix}{number}"


def generate_phone_number():
    """Generate Kenyan phone number"""
    prefixes = ["254701", "254702", "254703", "254710", "254711", "254712", "254722", "254733"]
    return f"{random.choice(prefixes)}{random.randint(100000, 999999)}"


async def populate_data():
    """Main function to populate database with dummy data"""
    
    print("=" * 60)
    print("POPULATING DATABASE WITH DUMMY DATA")
    print("=" * 60)
    print(f"Business: {BUSINESS_NAME}")
    print(f"Period: One year from today")
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
    
    # Clear existing data (optional - comment out if you want to keep existing data)
    print("\n📋 Clearing existing data...")
    await invoices_col.delete_many({})
    await transactions_col.delete_many({})
    await receipts_col.delete_many({})
    print("✓ Existing data cleared")
    
    # Start date: one year ago
    start_date = datetime.now() - timedelta(days=365)
    end_date = datetime.now()
    
    invoices = []
    transactions = []
    receipts = []
    
    invoice_counter = 1000
    receipt_counter = 5000
    
    print("\n💰 Generating invoices and payments...")
    
    # Generate invoices throughout the year (2-5 per week)
    current_date = start_date
    while current_date <= end_date:
        # Generate 2-5 invoices per week
        num_invoices = random.randint(2, 5)
        
        for _ in range(num_invoices):
            customer = random.choice(CUSTOMERS)
            service = random.choice(SERVICES)
            
            invoice_amount = random.uniform(service["price_range"][0], service["price_range"][1])
            invoice_amount = round(invoice_amount, 2)
            
            invoice_date = current_date + timedelta(days=random.randint(0, 6))
            due_date = invoice_date + timedelta(days=random.choice([7, 14, 30]))
            
            invoice_id = ObjectId()
            invoice_number = f"INV-{invoice_counter}"
            invoice_counter += 1
            
            invoice = {
                "_id": invoice_id,
                "user_id": USER_ID,
                "invoice_number": invoice_number,
                "customer_name": customer["name"],
                "customer_email": customer["email"],
                "amount": invoice_amount,
                "currency": "KES",
                "status": "paid" if random.random() > 0.15 else "pending",
                "issue_date": invoice_date,
                "due_date": due_date,
                "description": service["name"],
                "created_at": invoice_date,
                "updated_at": invoice_date,
            }
            
            invoices.append(invoice)
            
            # Generate payment for paid invoices (80-85% paid on time, rest paid late or unpaid)
            if invoice["status"] == "paid":
                payment_delay = random.randint(-2, 10)  # Some pay early, most on time or slightly late
                payment_date = due_date + timedelta(days=payment_delay)
                
                if payment_date > end_date:
                    payment_date = end_date
                
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
                    "created_at": payment_date,
                    "updated_at": payment_date,
                }
                
                transactions.append(transaction)
        
        # Move to next week
        current_date += timedelta(days=7)
    
    print(f"✓ Generated {len(invoices)} invoices")
    print(f"✓ Generated {len(transactions)} payment transactions")
    
    # Generate expenses/receipts
    print("\n🧾 Generating expenses and receipts...")
    
    current_date = start_date
    while current_date <= end_date:
        # Monthly expenses
        if current_date.day == 1 or (current_date == start_date):
            for expense in EXPENSE_CATEGORIES:
                if expense["frequency"] == "monthly":
                    amount = random.uniform(expense["amount_range"][0], expense["amount_range"][1])
                    amount = round(amount, 2)
                    
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
                        "created_at": current_date,
                        "updated_at": current_date,
                        "ocr_data": {
                            "extracted_data": {
                                "vendor_name": f"{expense['category']} Provider",
                                "total_amount": amount,
                                "date": current_date.strftime("%Y-%m-%d"),
                                "category": expense["category"],
                            },
                            "confidence": random.uniform(0.85, 0.98),
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
                        "description": f"{expense['category']} - {current_date.strftime('%B %Y')}",
                        "category": expense["category"],
                        "created_at": current_date,
                        "updated_at": current_date,
                    }
                    
                    transactions.append(transaction)
        
        # Quarterly expenses
        if current_date.day == 1 and current_date.month in [1, 4, 7, 10]:
            for expense in EXPENSE_CATEGORIES:
                if expense["frequency"] == "quarterly":
                    amount = random.uniform(expense["amount_range"][0], expense["amount_range"][1])
                    amount = round(amount, 2)
                    
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
                        "created_at": current_date,
                        "updated_at": current_date,
                        "ocr_data": {
                            "extracted_data": {
                                "vendor_name": f"{expense['category']} Provider",
                                "total_amount": amount,
                                "date": current_date.strftime("%Y-%m-%d"),
                                "category": expense["category"],
                            },
                            "confidence": random.uniform(0.85, 0.98),
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
                        "description": f"{expense['category']} - Q{(current_date.month-1)//3 + 1} {current_date.year}",
                        "category": expense["category"],
                        "created_at": current_date,
                        "updated_at": current_date,
                    }
                    
                    transactions.append(transaction)
        
        # Occasional expenses (randomly throughout the year)
        if random.random() > 0.85:  # 15% chance each day
            for expense in EXPENSE_CATEGORIES:
                if expense["frequency"] == "occasional" and random.random() > 0.5:
                    amount = random.uniform(expense["amount_range"][0], expense["amount_range"][1])
                    amount = round(amount, 2)
                    
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
                        "created_at": current_date,
                        "updated_at": current_date,
                        "ocr_data": {
                            "extracted_data": {
                                "vendor_name": f"{expense['category']} Provider",
                                "total_amount": amount,
                                "date": current_date.strftime("%Y-%m-%d"),
                                "category": expense["category"],
                            },
                            "confidence": random.uniform(0.85, 0.98),
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
                        "description": f"{expense['category']} - {current_date.strftime('%d %b %Y')}",
                        "category": expense["category"],
                        "created_at": current_date,
                        "updated_at": current_date,
                    }
                    
                    transactions.append(transaction)
        
        current_date += timedelta(days=1)
    
    print(f"✓ Generated {len(receipts)} expense receipts")
    print(f"✓ Total transactions: {len(transactions)}")
    
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
    
    # Calculate and display summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    
    total_invoiced = sum(inv["amount"] for inv in invoices)
    paid_invoices = [inv for inv in invoices if inv["status"] == "paid"]
    total_paid = sum(inv["amount"] for inv in paid_invoices)
    total_expenses = sum(rec["amount"] for rec in receipts)
    net_profit = total_paid - total_expenses
    
    print(f"Total Invoiced: KES {total_invoiced:,.2f}")
    print(f"Total Paid: KES {total_paid:,.2f}")
    print(f"Payment Rate: {len(paid_invoices)/len(invoices)*100:.1f}%")
    print(f"Total Expenses: KES {total_expenses:,.2f}")
    print(f"Net Profit: KES {net_profit:,.2f}")
    print(f"Profit Margin: {(net_profit/total_paid*100):.1f}%")
    
    print("\nMonthly Averages:")
    print(f"Revenue: KES {total_paid/12:,.2f}")
    print(f"Expenses: KES {total_expenses/12:,.2f}")
    print(f"Profit: KES {net_profit/12:,.2f}")
    
    print("\n" + "=" * 60)
    print("✅ DATABASE POPULATION COMPLETE!")
    print("=" * 60)
    print("\nYou can now refresh your dashboard to see the data.")
    
    # Close connection
    client.close()


if __name__ == "__main__":
    asyncio.run(populate_data())
