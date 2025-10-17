"""
Complete Test Data Generator for Financial System
Generates realistic data for:
- Customers
- Invoices (with proper dates and amounts)
- Payments
- Expense Receipts
- Invoice Items
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import random
from decimal import Decimal
import uuid

# MongoDB Connection
MONGO_URI = "mongodb+srv://alfredmunga31:Munga8820@cluster0.xkuqb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "financial_agent"

# Configuration
NUM_CUSTOMERS = 50
NUM_INVOICES = 200
NUM_PAYMENTS = 150
NUM_EXPENSES = 30

# Data generators
CUSTOMER_TYPES = ["Corporate", "SME", "Individual", "Enterprise"]
INDUSTRIES = ["Technology", "Manufacturing", "Retail", "Services", "Healthcare", "Education", "Transport"]
COMPANY_NAMES = [
    "Acme Corp", "TechVentures Ltd", "Global Solutions", "Prime Industries",
    "Swift Logistics", "Diamond Enterprises", "Summit Trading", "Nexus Systems",
    "Horizon Ventures", "Pioneer Group", "Elite Services", "Quantum Corp",
    "Zenith Holdings", "Apex Innovations", "Stellar Enterprises"
]

EXPENSE_CATEGORIES = [
    {"name": "Kenya Power", "range": (5000, 50000)},
    {"name": "Safaricom", "range": (2000, 20000)},
    {"name": "Naivas", "range": (3000, 30000)},
    {"name": "Uber", "range": (500, 5000)},
    {"name": "Artcaffe", "range": (1000, 10000)},
    {"name": "Office Supplies", "range": (2000, 15000)},
    {"name": "Fuel Station", "range": (3000, 25000)},
    {"name": "Internet Service", "range": (5000, 15000)},
]

INVOICE_STATUSES = ["paid", "pending", "overdue", "sent"]
PAYMENT_METHODS = ["mpesa", "bank_transfer", "cash", "cheque"]

class DataGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.customers = []
        self.invoices = []
        
    async def connect(self):
        """Connect to MongoDB"""
        print("🔌 Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        print("✅ Connected successfully!")
        
    async def cleanup_existing_data(self):
        """Optional: Clean up existing test data"""
        print("\n🧹 Cleaning up existing test data...")
        
        # Delete existing test data (optional - comment out if you want to keep existing data)
        # await self.db.customers.delete_many({"test_data": True})
        # await self.db.invoices.delete_many({"test_data": True})
        # await self.db.payments.delete_many({"test_data": True})
        # await self.db.receipts.delete_many({"test_data": True})
        # await self.db.invoice_items.delete_many({"test_data": True})
        
        print("✅ Cleanup complete!")
        
    async def generate_customers(self):
        """Generate customer records"""
        print(f"\n👥 Generating {NUM_CUSTOMERS} customers...")
        
        for i in range(NUM_CUSTOMERS):
            customer_id = str(uuid.uuid4())
            company_name = f"{random.choice(COMPANY_NAMES)} {i+1}"
            
            customer = {
                "customer_id": customer_id,
                "name": company_name,
                "company_name": company_name,
                "customer_type": random.choice(CUSTOMER_TYPES),
                "industry": random.choice(INDUSTRIES),
                "email": f"contact{i+1}@{company_name.lower().replace(' ', '')}.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "address": f"{random.randint(1, 999)} Business Avenue, Nairobi",
                "tax_id": f"KRA{random.randint(100000, 999999)}",
                "credit_limit": round(random.uniform(100000, 5000000), 2),
                "payment_terms": random.choice([30, 60, 90]),
                "status": "active",
                "created_at": datetime.now() - timedelta(days=random.randint(365, 730)),
                "test_data": True
            }
            
            result = await self.db.customers.insert_one(customer)
            customer["_id"] = result.inserted_id
            self.customers.append(customer)
            
        print(f"✅ Created {len(self.customers)} customers")
        
    async def generate_invoices(self):
        """Generate invoice records with proper dates"""
        print(f"\n📄 Generating {NUM_INVOICES} invoices...")
        
        # Generate invoices across the last 12 months
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        for i in range(NUM_INVOICES):
            customer = random.choice(self.customers)
            invoice_id = str(uuid.uuid4())
            invoice_number = f"INV-{2024}{str(i+1000).zfill(4)}"
            
            # Random date within last 12 months
            days_ago = random.randint(0, 365)
            issue_date = end_date - timedelta(days=days_ago)
            due_date = issue_date + timedelta(days=customer.get("payment_terms", 30))
            
            # Generate line items
            num_items = random.randint(1, 5)
            line_items = []
            subtotal = 0
            
            for j in range(num_items):
                quantity = random.randint(1, 10)
                unit_price = round(random.uniform(1000, 50000), 2)
                line_total = round(quantity * unit_price, 2)
                subtotal += line_total
                
                line_items.append({
                    "description": f"Service/Product {j+1}",
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total
                })
            
            # Calculate tax and total
            tax_rate = 0.16  # 16% VAT
            tax_amount = round(subtotal * tax_rate, 2)
            total_amount = round(subtotal + tax_amount, 2)
            
            # Determine status based on age
            if days_ago < 30:
                status_weights = [0.4, 0.3, 0.2, 0.1]  # More likely to be pending/sent
            elif days_ago < 90:
                status_weights = [0.6, 0.2, 0.1, 0.1]  # More likely to be paid
            else:
                status_weights = [0.8, 0.1, 0.05, 0.05]  # Most likely paid
                
            status = random.choices(INVOICE_STATUSES, weights=status_weights)[0]
            
            invoice = {
                "invoice_id": invoice_id,
                "invoice_number": invoice_number,
                "customer_id": customer["customer_id"],
                "customer_name": customer["name"],
                "issue_date": issue_date,
                "due_date": due_date,
                "status": status,
                "subtotal": subtotal,
                "tax_amount": tax_amount,
                "total_amount": total_amount,
                "amount": total_amount,  # Legacy field
                "currency": "KES",
                "line_items": line_items,
                "notes": f"Invoice for services rendered in {issue_date.strftime('%B %Y')}",
                "created_at": issue_date,
                "updated_at": datetime.now(),
                "test_data": True
            }
            
            result = await self.db.invoices.insert_one(invoice)
            invoice["_id"] = result.inserted_id
            self.invoices.append(invoice)
            
            # Create invoice items in separate collection
            for idx, item in enumerate(line_items):
                invoice_item = {
                    "invoice_id": invoice_id,
                    "item_id": str(uuid.uuid4()),
                    "line_number": idx + 1,
                    "description": item["description"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "line_total": item["line_total"],
                    "total": item["line_total"],  # Legacy field
                    "created_at": issue_date,
                    "test_data": True
                }
                await self.db.invoice_items.insert_one(invoice_item)
        
        print(f"✅ Created {len(self.invoices)} invoices with line items")
        
    async def generate_payments(self):
        """Generate payment records for paid invoices"""
        print(f"\n💰 Generating payments for paid invoices...")
        
        paid_invoices = [inv for inv in self.invoices if inv["status"] == "paid"]
        payment_count = 0
        
        for invoice in paid_invoices[:NUM_PAYMENTS]:
            # Payment date is after invoice date
            payment_date = invoice["issue_date"] + timedelta(days=random.randint(1, 60))
            
            payment = {
                "payment_id": str(uuid.uuid4()),
                "invoice_id": invoice["invoice_id"],
                "invoice_number": invoice["invoice_number"],
                "customer_id": invoice["customer_id"],
                "amount": invoice["total_amount"],
                "payment_method": random.choice(PAYMENT_METHODS),
                "payment_date": payment_date,
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "status": "completed",
                "currency": "KES",
                "notes": f"Payment received via {random.choice(PAYMENT_METHODS)}",
                "created_at": payment_date,
                "test_data": True
            }
            
            await self.db.payments.insert_one(payment)
            payment_count += 1
            
        print(f"✅ Created {payment_count} payments")
        
    async def generate_expenses(self):
        """Generate expense receipts with OCR data"""
        print(f"\n🧾 Generating {NUM_EXPENSES} expense receipts...")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        for i in range(NUM_EXPENSES):
            category = random.choice(EXPENSE_CATEGORIES)
            amount = round(random.uniform(category["range"][0], category["range"][1]), 2)
            
            # Random date within last 12 months
            receipt_date = start_date + timedelta(days=random.randint(0, 365))
            
            receipt = {
                "receipt_id": str(uuid.uuid4()),
                "receipt_number": f"EXP-{receipt_date.strftime('%Y%m%d')}-{str(i+1).zfill(4)}",
                "receipt_type": "expense",
                "status": "processed",
                "file_path": f"/receipts/expense_{i+1}.pdf",
                "created_at": receipt_date,
                "processed_at": receipt_date + timedelta(hours=1),
                "ocr_data": {
                    "extracted_data": {
                        "total_amount": amount,
                        "merchant_name": category["name"],
                        "transaction_date": receipt_date.isoformat(),
                        "category": category["name"],
                        "payment_method": random.choice(["card", "cash", "mpesa"]),
                        "receipt_number": f"R{random.randint(10000, 99999)}"
                    },
                    "ai_analysis": {
                        "category": category["name"],
                        "confidence": round(random.uniform(0.85, 0.99), 2),
                        "is_business_expense": True,
                        "tax_deductible": True
                    }
                },
                "currency": "KES",
                "notes": f"Business expense - {category['name']}",
                "test_data": True
            }
            
            await self.db.receipts.insert_one(receipt)
            
        print(f"✅ Created {NUM_EXPENSES} expense receipts")
        
    async def generate_summary(self):
        """Print summary of generated data"""
        print("\n" + "="*60)
        print("📊 DATA GENERATION SUMMARY")
        print("="*60)
        
        # Customers
        customer_count = await self.db.customers.count_documents({"test_data": True})
        print(f"\n👥 Customers: {customer_count}")
        
        # Invoices by status
        print(f"\n📄 Invoices:")
        for status in INVOICE_STATUSES:
            count = await self.db.invoices.count_documents({"test_data": True, "status": status})
            total = await self.db.invoices.aggregate([
                {"$match": {"test_data": True, "status": status}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]).to_list(1)
            total_amount = total[0]["total"] if total else 0
            print(f"  - {status.capitalize()}: {count} invoices (KES {total_amount:,.2f})")
        
        # Total invoice value
        total_invoices = await self.db.invoices.aggregate([
            {"$match": {"test_data": True}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]).to_list(1)
        total_invoice_value = total_invoices[0]["total"] if total_invoices else 0
        print(f"  - TOTAL: {await self.db.invoices.count_documents({'test_data': True})} invoices (KES {total_invoice_value:,.2f})")
        
        # Payments
        payment_count = await self.db.payments.count_documents({"test_data": True})
        total_payments = await self.db.payments.aggregate([
            {"$match": {"test_data": True}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        total_payment_value = total_payments[0]["total"] if total_payments else 0
        print(f"\n💰 Payments: {payment_count} (KES {total_payment_value:,.2f})")
        
        # Expenses
        expense_count = await self.db.receipts.count_documents({"test_data": True, "receipt_type": "expense"})
        total_expenses = await self.db.receipts.aggregate([
            {"$match": {"test_data": True, "receipt_type": "expense"}},
            {"$group": {"_id": None, "total": {"$sum": "$ocr_data.extracted_data.total_amount"}}}
        ]).to_list(1)
        total_expense_value = total_expenses[0]["total"] if total_expenses else 0
        print(f"\n🧾 Expenses: {expense_count} receipts (KES {total_expense_value:,.2f})")
        
        # Date ranges
        print(f"\n📅 Date Ranges:")
        oldest_invoice = await self.db.invoices.find_one(
            {"test_data": True},
            sort=[("issue_date", 1)]
        )
        newest_invoice = await self.db.invoices.find_one(
            {"test_data": True},
            sort=[("issue_date", -1)]
        )
        if oldest_invoice and newest_invoice:
            print(f"  - Invoices: {oldest_invoice['issue_date'].strftime('%Y-%m-%d')} to {newest_invoice['issue_date'].strftime('%Y-%m-%d')}")
        
        oldest_expense = await self.db.receipts.find_one(
            {"test_data": True, "receipt_type": "expense"},
            sort=[("created_at", 1)]
        )
        newest_expense = await self.db.receipts.find_one(
            {"test_data": True, "receipt_type": "expense"},
            sort=[("created_at", -1)]
        )
        if oldest_expense and newest_expense:
            print(f"  - Expenses: {oldest_expense['created_at'].strftime('%Y-%m-%d')} to {newest_expense['created_at'].strftime('%Y-%m-%d')}")
        
        print("\n" + "="*60)
        print("✅ DATA GENERATION COMPLETE!")
        print("="*60)
        print("\nYou can now:")
        print("  1. View reports in the dashboard")
        print("  2. Run income statement: http://localhost:8000/reports/income-statement")
        print("  3. Run cash flow: http://localhost:8000/reports/cash-flow")
        print("  4. View AR aging: http://localhost:8000/reports/ar-aging")
        print("  5. Check expenses: http://localhost:8000/api/expenses/summary")
        print()
        
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("\n👋 Database connection closed")

async def main():
    """Main execution flow"""
    generator = DataGenerator()
    
    try:
        await generator.connect()
        await generator.cleanup_existing_data()
        await generator.generate_customers()
        await generator.generate_invoices()
        await generator.generate_payments()
        await generator.generate_expenses()
        await generator.generate_summary()
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        await generator.close()

if __name__ == "__main__":
    print("="*60)
    print("🚀 COMPLETE TEST DATA GENERATOR")
    print("="*60)
    print("\nThis script will generate:")
    print(f"  - {NUM_CUSTOMERS} customers")
    print(f"  - {NUM_INVOICES} invoices (with proper dates and line items)")
    print(f"  - {NUM_PAYMENTS} payments")
    print(f"  - {NUM_EXPENSES} expense receipts")
    print("\nAll data will be marked with 'test_data: True' for easy cleanup")
    print("\nStarting in 3 seconds...")
    print("="*60)
    
    import time
    time.sleep(3)
    
    asyncio.run(main())
