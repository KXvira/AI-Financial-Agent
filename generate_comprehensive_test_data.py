"""
Comprehensive Test Data Generator for FinGuard Financial System

This script generates realistic financial data with proper date fields
and relationships to support all reporting features including:
- Revenue trends
- Expense trends
- Month-over-Month comparisons
- Year-over-Year comparisons
- Customer analytics
- AR Aging reports

Author: AI Assistant
Date: 2025-10-17
"""

import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB connection - Update these values for your environment
MONGO_URI = os.environ.get(
    "MONGO_URI", 
    "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
)
DATABASE_NAME = os.environ.get("MONGO_DATABASE", "financial_agent")

print(f"📝 Using database: {DATABASE_NAME}")

# Configuration
MONTHS_OF_DATA = 24  # Generate 2 years of historical data
CUSTOMERS_COUNT = 50
INVOICES_PER_MONTH_RANGE = (30, 50)
EXPENSES_PER_MONTH_RANGE = (20, 40)
TRANSACTIONS_PER_MONTH_RANGE = (50, 100)

# Kenyan business context
KENYAN_COMPANIES = [
    "Safaricom Ltd", "Kenya Power & Lighting Co.", "Equity Bank Kenya",
    "KCB Bank Kenya", "Co-operative Bank", "Naivas Supermarket",
    "Nakumatt Holdings", "Uchumi Supermarkets", "Java House Group",
    "ArtCaffe Limited", "Bamburi Cement", "East African Breweries",
    "Kenya Airways", "Standard Chartered Kenya", "Barclays Bank Kenya",
    "I&M Bank", "Diamond Trust Bank", "Family Bank", "Sidian Bank",
    "Stanbic Bank Kenya", "Standard Group", "Nation Media Group",
    "Britam Holdings", "CIC Insurance", "Jubilee Insurance",
    "UAP Insurance", "Metropolitan Cannon", "Airtel Kenya",
    "Telkom Kenya", "Finserve Africa", "iPay Limited",
    "PesaPal Limited", "Cellulant Corporation", "Twiga Foods",
    "Sendy Limited", "MarketForce", "Copia Global", "Jumia Kenya",
    "Glovo Kenya", "Uber Kenya", "Bolt Kenya", "Little Cab",
    "Nairobi Hospital", "Aga Khan Hospital", "MP Shah Hospital",
    "Gertrude's Children Hospital", "Kenyatta National Hospital",
    "Mater Hospital", "Avenue Healthcare", "Bliss Healthcare"
]

EXPENSE_CATEGORIES = [
    "Office Supplies", "Utilities", "Rent", "Salaries", "Marketing",
    "Transportation", "Equipment", "Software & Technology", "Insurance",
    "Professional Services", "Maintenance", "Training", "Travel",
    "Communication", "Bank Charges", "Taxes", "Entertainment",
    "Security", "Cleaning Services", "Internet & Hosting"
]

PRODUCT_SERVICES = [
    "Financial Consulting", "Software Development", "Cloud Services",
    "Marketing Services", "IT Support", "Training Services",
    "Business Analytics", "Data Management", "Security Services",
    "Web Development", "Mobile App Development", "API Integration",
    "System Maintenance", "Database Management", "Network Setup",
    "Hardware Sales", "Software Licenses", "Project Management",
    "Quality Assurance", "DevOps Services"
]


class ComprehensiveDataGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.customers = []
        self.invoices = []
        self.start_date = datetime.now() - timedelta(days=MONTHS_OF_DATA * 30)
        
    async def connect(self):
        """Connect to MongoDB"""
        print("🔌 Connecting to MongoDB Atlas...")
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        
        # Test connection
        await self.client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
        
    async def clear_existing_data(self):
        """Clear existing test data (optional)"""
        print("\n🗑️  Clearing existing test data...")
        
        # Comment out this section if you want to keep existing data
        # await self.db.customers.delete_many({})
        # await self.db.invoices.delete_many({})
        # await self.db.transactions.delete_many({})
        # await self.db.payments.delete_many({})
        
        print("✅ Existing data cleared")
        
    async def generate_customers(self):
        """Generate customer records"""
        print(f"\n👥 Generating {CUSTOMERS_COUNT} customers...")
        
        customers_data = []
        for i in range(CUSTOMERS_COUNT):
            customer = {
                "_id": ObjectId(),
                "customer_id": f"CUST-{1001+i:06d}",  # Unique customer ID
                "name": random.choice(KENYAN_COMPANIES),
                "email": f"contact{i+1}@{random.choice(['gmail', 'yahoo', 'company'])}.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "address": f"{random.randint(1, 999)} {random.choice(['Kenyatta', 'Moi', 'Uhuru', 'Kimathi'])} Avenue, Nairobi",
                "status": random.choice(["active"] * 8 + ["inactive"] * 2),  # 80% active
                "credit_limit": random.choice([500000, 1000000, 2000000, 5000000]),
                "payment_terms": random.choice([7, 14, 30, 45, 60]),
                "created_at": self.start_date + timedelta(days=random.randint(0, 60)),
                "updated_at": datetime.now(),
                "total_invoiced": 0,  # Will be updated as we create invoices
                "total_paid": 0,
                "outstanding_balance": 0
            }
            customers_data.append(customer)
            
        # Insert customers
        if customers_data:
            result = await self.db.customers.insert_many(customers_data)
            self.customers = customers_data
            print(f"✅ Created {len(result.inserted_ids)} customers")
            
    async def generate_invoices(self):
        """Generate invoice records with proper date fields"""
        print(f"\n📄 Generating invoices for {MONTHS_OF_DATA} months...")
        
        invoices_data = []
        invoice_number = 10001
        
        for month_offset in range(MONTHS_OF_DATA):
            # Calculate month start/end dates
            month_date = self.start_date + timedelta(days=month_offset * 30)
            month_start = month_date.replace(day=1)
            
            # Determine number of invoices for this month
            invoices_this_month = random.randint(*INVOICES_PER_MONTH_RANGE)
            
            for _ in range(invoices_this_month):
                customer = random.choice(self.customers)
                
                # Random issue date within the month
                issue_day = random.randint(1, 28)
                issue_date = month_start + timedelta(days=issue_day)
                
                # Due date based on payment terms
                due_date = issue_date + timedelta(days=customer["payment_terms"])
                
                # Generate invoice items
                items = []
                subtotal = 0
                num_items = random.randint(1, 5)
                
                for item_num in range(num_items):
                    quantity = random.randint(1, 10)
                    unit_price = random.choice([5000, 10000, 25000, 50000, 100000, 250000])
                    item_total = quantity * unit_price
                    
                    items.append({
                        "description": random.choice(PRODUCT_SERVICES),
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "total": item_total
                    })
                    subtotal += item_total
                
                # Calculate tax and total
                tax_rate = 0.16  # 16% VAT in Kenya
                tax_amount = subtotal * tax_rate
                total_amount = subtotal + tax_amount
                
                # Determine invoice status based on date
                days_since_issue = (datetime.now() - issue_date).days
                days_since_due = (datetime.now() - due_date).days
                
                if days_since_issue < 0:  # Future invoice (shouldn't happen)
                    status = "draft"
                    payment_date = None
                elif days_since_due > 30:  # Very old invoice
                    status = random.choice(["paid"] * 7 + ["overdue"] * 3)
                elif days_since_due > 0:  # Past due
                    status = random.choice(["paid"] * 5 + ["overdue"] * 5)
                elif days_since_issue > 3:  # Issued but not due
                    status = random.choice(["paid"] * 6 + ["pending", "sent"] * 4)
                else:  # Recently issued
                    status = random.choice(["paid"] * 3 + ["pending", "sent"] * 7)
                
                # Set payment date for paid invoices
                if status == "paid":
                    # Payment within 0-45 days after issue
                    payment_days = random.randint(0, min(45, days_since_issue))
                    payment_date = issue_date + timedelta(days=payment_days)
                    paid_amount = total_amount
                else:
                    payment_date = None
                    paid_amount = 0
                
                invoice = {
                    "_id": ObjectId(),
                    "invoice_id": f"INV{invoice_number}",  # Unique invoice ID
                    "invoice_number": f"INV-{invoice_number:06d}",
                    "customer_id": customer["_id"],
                    "customer_name": customer["name"],
                    "issue_date": issue_date.strftime("%Y-%m-%d"),
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "payment_date": payment_date.strftime("%Y-%m-%d") if payment_date else None,
                    "status": status,
                    "items": items,
                    "subtotal": subtotal,
                    "tax_rate": tax_rate,
                    "tax_amount": tax_amount,
                    "total_amount": total_amount,
                    "amount": total_amount,  # Duplicate field for compatibility
                    "paid_amount": paid_amount,
                    "balance": total_amount - paid_amount,
                    "currency": "KES",
                    "notes": f"Thank you for your business. Payment terms: Net {customer['payment_terms']} days",
                    "created_at": issue_date,
                    "updated_at": payment_date if payment_date else issue_date
                }
                
                invoices_data.append(invoice)
                invoice_number += 1
                
                # Update customer totals
                customer["total_invoiced"] += total_amount
                customer["total_paid"] += paid_amount
                customer["outstanding_balance"] += (total_amount - paid_amount)
        
        # Insert invoices in batches
        batch_size = 500
        total_inserted = 0
        
        for i in range(0, len(invoices_data), batch_size):
            batch = invoices_data[i:i + batch_size]
            result = await self.db.invoices.insert_many(batch)
            total_inserted += len(result.inserted_ids)
            print(f"  📊 Inserted {total_inserted}/{len(invoices_data)} invoices...")
        
        self.invoices = invoices_data
        print(f"✅ Created {len(invoices_data)} invoices")
        
        # Update customer totals
        print("  📊 Updating customer totals...")
        for customer in self.customers:
            await self.db.customers.update_one(
                {"_id": customer["_id"]},
                {"$set": {
                    "total_invoiced": customer["total_invoiced"],
                    "total_paid": customer["total_paid"],
                    "outstanding_balance": customer["outstanding_balance"]
                }}
            )
        
    async def generate_expenses(self):
        """Generate expense transactions"""
        print(f"\n💰 Generating expenses for {MONTHS_OF_DATA} months...")
        
        expenses_data = []
        
        for month_offset in range(MONTHS_OF_DATA):
            month_date = self.start_date + timedelta(days=month_offset * 30)
            month_start = month_date.replace(day=1)
            
            expenses_this_month = random.randint(*EXPENSES_PER_MONTH_RANGE)
            
            for _ in range(expenses_this_month):
                transaction_day = random.randint(1, 28)
                transaction_date = month_start + timedelta(days=transaction_day)
                
                category = random.choice(EXPENSE_CATEGORIES)
                
                # Amount based on category
                if category in ["Rent", "Salaries"]:
                    amount = random.randint(100000, 500000)
                elif category in ["Utilities", "Insurance", "Marketing"]:
                    amount = random.randint(20000, 100000)
                else:
                    amount = random.randint(5000, 50000)
                
                expense = {
                    "_id": ObjectId(),
                    "type": "expense",
                    "category": category,
                    "amount": amount,
                    "description": f"{category} - {transaction_date.strftime('%B %Y')}",
                    "transaction_date": transaction_date.strftime("%Y-%m-%d"),
                    "payment_method": random.choice(["M-Pesa", "Bank Transfer", "Cash", "Card"]),
                    "vendor": random.choice(KENYAN_COMPANIES[:20]),
                    "reference": f"EXP-{random.randint(10000, 99999)}",
                    "status": "completed",
                    "created_at": transaction_date,
                    "updated_at": transaction_date
                }
                
                expenses_data.append(expense)
        
        # Insert expenses in batches
        if expenses_data:
            batch_size = 500
            total_inserted = 0
            
            for i in range(0, len(expenses_data), batch_size):
                batch = expenses_data[i:i + batch_size]
                result = await self.db.transactions.insert_many(batch)
                total_inserted += len(result.inserted_ids)
                print(f"  📊 Inserted {total_inserted}/{len(expenses_data)} expenses...")
            
            print(f"✅ Created {len(expenses_data)} expense transactions")
            
    async def generate_payments(self):
        """Generate payment records for paid invoices"""
        print("\n💳 Generating payment records...")
        
        payments_data = []
        
        # Get all paid invoices
        paid_invoices = [inv for inv in self.invoices if inv["status"] == "paid" and inv["payment_date"]]
        
        for invoice in paid_invoices:
            payment_date_obj = datetime.strptime(invoice["payment_date"], "%Y-%m-%d")
            
            payment = {
                "_id": ObjectId(),
                "invoice_id": invoice["_id"],
                "invoice_number": invoice["invoice_number"],
                "customer_id": invoice["customer_id"],
                "customer_name": invoice["customer_name"],
                "amount": invoice["paid_amount"],
                "payment_date": invoice["payment_date"],
                "payment_method": random.choice(["M-Pesa", "Bank Transfer", "Cheque", "Cash"]),
                "reference": f"PAY-{random.randint(100000, 999999)}",
                "status": "completed",
                "notes": f"Payment for {invoice['invoice_number']}",
                "created_at": payment_date_obj,
                "updated_at": payment_date_obj
            }
            
            payments_data.append(payment)
        
        # Insert payments in batches
        if payments_data:
            batch_size = 500
            total_inserted = 0
            
            for i in range(0, len(payments_data), batch_size):
                batch = payments_data[i:i + batch_size]
                result = await self.db.payments.insert_many(batch)
                total_inserted += len(result.inserted_ids)
                print(f"  📊 Inserted {total_inserted}/{len(payments_data)} payments...")
            
            print(f"✅ Created {len(payments_data)} payment records")
            
    async def create_indexes(self):
        """Create database indexes for better performance"""
        print("\n🔍 Creating database indexes...")
        
        # Customer indexes
        await self.db.customers.create_index("email")
        await self.db.customers.create_index("status")
        
        # Invoice indexes
        await self.db.invoices.create_index("invoice_number", unique=True)
        await self.db.invoices.create_index("customer_id")
        await self.db.invoices.create_index("status")
        await self.db.invoices.create_index("issue_date")
        await self.db.invoices.create_index("due_date")
        await self.db.invoices.create_index("payment_date")
        await self.db.invoices.create_index([("status", 1), ("issue_date", -1)])
        
        # Transaction indexes
        await self.db.transactions.create_index("type")
        await self.db.transactions.create_index("transaction_date")
        await self.db.transactions.create_index("category")
        await self.db.transactions.create_index([("type", 1), ("transaction_date", -1)])
        
        # Payment indexes
        await self.db.payments.create_index("invoice_id")
        await self.db.payments.create_index("payment_date")
        await self.db.payments.create_index("status")
        
        print("✅ Database indexes created")
        
    async def generate_summary(self):
        """Generate and display summary statistics"""
        print("\n" + "="*60)
        print("📊 DATA GENERATION SUMMARY")
        print("="*60)
        
        # Count documents
        customer_count = await self.db.customers.count_documents({})
        invoice_count = await self.db.invoices.count_documents({})
        paid_invoice_count = await self.db.invoices.count_documents({"status": "paid"})
        pending_invoice_count = await self.db.invoices.count_documents({"status": {"$in": ["pending", "sent"]}})
        overdue_invoice_count = await self.db.invoices.count_documents({"status": "overdue"})
        expense_count = await self.db.transactions.count_documents({"type": "expense"})
        payment_count = await self.db.payments.count_documents({})
        
        # Calculate totals
        pipeline_revenue = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        revenue_result = await self.db.invoices.aggregate(pipeline_revenue).to_list(None)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        pipeline_expenses = [
            {"$match": {"type": "expense"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        expense_result = await self.db.transactions.aggregate(pipeline_expenses).to_list(None)
        total_expenses = expense_result[0]["total"] if expense_result else 0
        
        print(f"\n👥 Customers:           {customer_count:,}")
        print(f"📄 Total Invoices:      {invoice_count:,}")
        print(f"  ✅ Paid:              {paid_invoice_count:,}")
        print(f"  ⏳ Pending:           {pending_invoice_count:,}")
        print(f"  ⚠️  Overdue:           {overdue_invoice_count:,}")
        print(f"\n💰 Total Revenue:       KES {total_revenue:,.2f}")
        print(f"💸 Total Expenses:      KES {total_expenses:,.2f}")
        print(f"📈 Net Income:          KES {(total_revenue - total_expenses):,.2f}")
        print(f"\n💳 Payment Records:     {payment_count:,}")
        print(f"📊 Expense Records:     {expense_count:,}")
        
        print(f"\n📅 Date Range:          {self.start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        print(f"📆 Months of Data:      {MONTHS_OF_DATA}")
        
        print("\n" + "="*60)
        print("✅ DATA GENERATION COMPLETE!")
        print("="*60)
        print("\nYou can now use all reporting features:")
        print("  • Revenue Trends")
        print("  • Expense Trends")
        print("  • Month-over-Month Comparisons")
        print("  • Year-over-Year Comparisons")
        print("  • AR Aging Reports")
        print("  • Dashboard Analytics")
        print("\n")
        
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed")
            
    async def run(self):
        """Run the complete data generation process"""
        try:
            await self.connect()
            await self.clear_existing_data()
            await self.generate_customers()
            await self.generate_invoices()
            await self.generate_expenses()
            await self.generate_payments()
            await self.create_indexes()
            await self.generate_summary()
            
        except Exception as e:
            print(f"\n❌ Error during data generation: {str(e)}")
            import traceback
            traceback.print_exc()
            
        finally:
            await self.close()


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🚀 COMPREHENSIVE TEST DATA GENERATOR")
    print("="*60)
    print(f"\nThis will generate {MONTHS_OF_DATA} months of test data")
    print(f"including customers, invoices, payments, and expenses.\n")
    
    response = input("Do you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        generator = ComprehensiveDataGenerator()
        await generator.run()
    else:
        print("\n❌ Data generation cancelled")


if __name__ == "__main__":
    asyncio.run(main())
