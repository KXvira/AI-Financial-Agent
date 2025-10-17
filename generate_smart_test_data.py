"""
Smart Test Data Generator - Based on Actual Working API Queries

Analyzes the working dashboard metrics service and creates data
that exactly matches the expected structure and fields.

Key Findings from Analysis:
1. Invoices:
   - Must have: status (lowercase: "paid", "pending", "sent", "unpaid", "overdue")
   - Must have: total_amount (primary field used in all queries)
   - Optional: amount (fallback field)
   - Date fields: issue_date (string YYYY-MM-DD), created_at (datetime), due_date
   - Customer: customer_id (ObjectId reference)
   
2. Customers:
   - Queried by customer_id from invoices
   - Must exist to count active customers
   
3. Expenses (from receipts collection):
   - receipt_type: "expense" or "refund"
   - ocr_data.extracted_data.total_amount
   - ocr_data.extracted_data.merchant_name (for category)
   - created_at: datetime (for date filtering)
   
4. Transactions:
   - Optional collection for transaction tracking
   - Fields: reconciled (boolean), transaction_date
"""

import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB Configuration
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
)
DATABASE_NAME = os.environ.get("MONGO_DATABASE", "financial_agent")

# Data Generation Settings
MONTHS_OF_DATA = 18  # 1.5 years of data
CUSTOMERS_COUNT = 40
INVOICES_PER_MONTH = (25, 45)
EXPENSES_PER_MONTH = (15, 30)

# Kenyan Context
COMPANIES = [
    "Safaricom PLC", "Kenya Power", "Equity Bank", "KCB Group",
    "Co-operative Bank", "Naivas Ltd", "Java House", "Bamburi Cement",
    "East African Breweries", "Kenya Airways", "Britam", "CIC Insurance",
    "Twiga Foods", "Sendy Ltd", "iPay Africa", "PesaPal", "Cellulant",
    "Jumia Kenya", "Glovo Kenya", "Little Cab", "Nairobi Hospital"
]

SERVICES = [
    "IT Support & Maintenance", "Software Development", "Cloud Hosting",
    "Digital Marketing", "Consulting Services", "Training Programs",
    "Security Services", "Data Analytics", "API Integration",
    "Website Development", "Mobile Apps", "System Administration"
]

EXPENSE_MERCHANTS = [
    "Naivas", "Carrefour", "Uber", "Kenya Power", "Safaricom",
    "Quickmart", "Chandarana", "Nairobi Java House", "ArtCaffe",
    "Shell Petrol", "Total Energies", "Gilani's Supermarket"
]


class SmartDataGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.customers = []
        self.start_date = datetime.now() - timedelta(days=MONTHS_OF_DATA * 30)
        
    async def connect(self):
        """Connect to MongoDB"""
        print(f"\n🔌 Connecting to {DATABASE_NAME}...")
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        await self.client.admin.command('ping')
        print("✅ Connected successfully\n")
        
    async def analyze_existing_schema(self):
        """Analyze existing collections to understand schema"""
        print("🔍 Analyzing existing data schema...")
        
        # Check invoices
        sample_invoice = await self.db.invoices.find_one()
        if sample_invoice:
            print(f"\n📄 Sample Invoice Fields:")
            for key in sample_invoice.keys():
                print(f"  - {key}: {type(sample_invoice[key]).__name__}")
        
        # Check customers
        sample_customer = await self.db.customers.find_one()
        if sample_customer:
            print(f"\n👤 Sample Customer Fields:")
            for key in sample_customer.keys():
                print(f"  - {key}: {type(sample_customer[key]).__name__}")
        
        # Check receipts
        sample_receipt = await self.db.receipts.find_one()
        if sample_receipt:
            print(f"\n🧾 Sample Receipt Fields:")
            for key in sample_receipt.keys():
                print(f"  - {key}: {type(sample_receipt[key]).__name__}")
        
        print("\n" + "="*60)
        
    async def clear_data(self):
        """Clear test data collections"""
        print("🗑️  Clearing old test data...")
        
        # Only clear if user confirms
        print(f"  Current counts:")
        print(f"    Customers: {await self.db.customers.count_documents({})}")
        print(f"    Invoices: {await self.db.invoices.count_documents({})}")
        print(f"    Receipts: {await self.db.receipts.count_documents({})}")
        
        response = input("\n  Clear existing data? (yes/no): ")
        if response.lower() in ['yes', 'y']:
            await self.db.customers.delete_many({"customer_id": {"$regex": "^TEST-"}})
            await self.db.invoices.delete_many({"invoice_number": {"$regex": "^TEST-"}})
            await self.db.receipts.delete_many({"receipt_id": {"$regex": "^TEST-"}})
            print("✅ Cleared test data\n")
        else:
            print("⏭️  Keeping existing data\n")
        
    async def generate_customers(self):
        """Generate customers matching the schema"""
        print(f"👥 Generating {CUSTOMERS_COUNT} customers...")
        
        customers_data = []
        for i in range(CUSTOMERS_COUNT):
            customer_id = f"TEST-CUST-{1000+i}"
            customer = {
                "_id": ObjectId(),
                "customer_id": customer_id,
                "name": random.choice(COMPANIES),
                "email": f"{customer_id.lower().replace('-', '_')}@example.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "address": f"{random.randint(1, 999)} Enterprise Road, Nairobi",
                "status": random.choice(["active"] * 9 + ["inactive"]),
                "payment_terms": random.choice([7, 14, 30, 45]),
                "created_at": self.start_date + timedelta(days=random.randint(0, 30)),
                "updated_at": datetime.now()
            }
            customers_data.append(customer)
        
        if customers_data:
            await self.db.customers.insert_many(customers_data)
            self.customers = customers_data
            print(f"✅ Created {len(customers_data)} customers\n")
        
    async def generate_invoices(self):
        """Generate invoices matching the exact working query structure"""
        print(f"📄 Generating invoices for {MONTHS_OF_DATA} months...")
        
        invoices_data = []
        invoice_num = 1
        
        for month_offset in range(MONTHS_OF_DATA):
            month_date = self.start_date + timedelta(days=month_offset * 30)
            month_start = month_date.replace(day=1)
            
            num_invoices = random.randint(*INVOICES_PER_MONTH)
            
            for _ in range(num_invoices):
                customer = random.choice(self.customers)
                
                # Issue date within the month
                issue_day = random.randint(1, 28)
                issue_date = month_start + timedelta(days=issue_day)
                due_date = issue_date + timedelta(days=customer["payment_terms"])
                
                # Calculate amounts
                subtotal = random.choice([50000, 100000, 250000, 500000, 750000, 1000000])
                tax_rate = 0.16
                tax_amount = subtotal * tax_rate
                total_amount = subtotal + tax_amount
                
                # Determine status based on age
                days_old = (datetime.now() - issue_date).days
                days_overdue = (datetime.now() - due_date).days
                
                if days_overdue > 30:
                    status = random.choice(["paid"] * 7 + ["overdue"] * 3)
                elif days_overdue > 0:
                    status = random.choice(["paid"] * 5 + ["overdue"] * 3 + ["pending"] * 2)
                elif days_old > 5:
                    status = random.choice(["paid"] * 6 + ["pending", "sent"] * 2)
                else:
                    status = random.choice(["paid"] * 3 + ["pending", "sent", "unpaid"] * 7)
                
                # Payment date for paid invoices
                if status == "paid":
                    payment_days = random.randint(0, min(customer["payment_terms"] + 10, days_old))
                    payment_date = issue_date + timedelta(days=payment_days)
                else:
                    payment_date = None
                
                invoice = {
                    "_id": ObjectId(),
                    "invoice_id": f"TEST{invoice_num:06d}",  # For unique index
                    "invoice_number": f"TEST-INV-{invoice_num:06d}",
                    "customer_id": customer["_id"],  # ObjectId reference
                    "customer_name": customer["name"],
                    
                    # Date fields (CRITICAL - exactly as working query expects)
                    "issue_date": issue_date.strftime("%Y-%m-%d"),  # String format
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "payment_date": payment_date.strftime("%Y-%m-%d") if payment_date else None,
                    "created_at": issue_date,  # Datetime object
                    "updated_at": payment_date if payment_date else issue_date,
                    
                    # Status (CRITICAL - lowercase as working query expects)
                    "status": status,
                    
                    # Amounts (CRITICAL - total_amount is primary field)
                    "total_amount": total_amount,  # PRIMARY field used in queries
                    "amount": total_amount,  # Fallback field
                    "subtotal": subtotal,
                    "tax_amount": tax_amount,
                    "tax_rate": tax_rate,
                    
                    # Additional fields
                    "items": [{
                        "description": random.choice(SERVICES),
                        "quantity": random.randint(1, 5),
                        "unit_price": subtotal / random.randint(1, 5),
                        "total": subtotal
                    }],
                    "currency": "KES",
                    "notes": f"Net {customer['payment_terms']} days"
                }
                
                invoices_data.append(invoice)
                invoice_num += 1
        
        # Insert in batches
        batch_size = 500
        total_inserted = 0
        for i in range(0, len(invoices_data), batch_size):
            batch = invoices_data[i:i + batch_size]
            await self.db.invoices.insert_many(batch)
            total_inserted += len(batch)
            print(f"  📊 {total_inserted}/{len(invoices_data)} invoices...")
        
        print(f"✅ Created {len(invoices_data)} invoices\n")
        
        # Show status breakdown
        statuses = {}
        for inv in invoices_data:
            statuses[inv["status"]] = statuses.get(inv["status"], 0) + 1
        print("  Status breakdown:")
        for status, count in sorted(statuses.items()):
            print(f"    {status}: {count}")
        print()
        
    async def generate_expenses(self):
        """Generate expenses in receipts collection (as working query expects)"""
        print(f"💰 Generating expenses for {MONTHS_OF_DATA} months...")
        
        receipts_data = []
        receipt_num = 1
        
        for month_offset in range(MONTHS_OF_DATA):
            month_date = self.start_date + timedelta(days=month_offset * 30)
            month_start = month_date.replace(day=1)
            
            num_expenses = random.randint(*EXPENSES_PER_MONTH)
            
            for _ in range(num_expenses):
                expense_day = random.randint(1, 28)
                expense_date = month_start + timedelta(days=expense_day)
                
                merchant = random.choice(EXPENSE_MERCHANTS)
                amount = random.choice([5000, 10000, 15000, 25000, 50000, 75000, 100000])
                
                receipt = {
                    "_id": ObjectId(),
                    "receipt_id": f"TEST-RCP-{receipt_num:06d}",
                    
                    # CRITICAL - receipt_type triggers expense matching
                    "receipt_type": "expense",
                    
                    # CRITICAL - created_at used for date filtering
                    "created_at": expense_date,
                    "updated_at": expense_date,
                    
                    # CRITICAL - OCR data structure as working query expects
                    "ocr_data": {
                        "extracted_data": {
                            "total_amount": amount,  # PRIMARY field for amount
                            "merchant_name": merchant,  # Used for category
                            "date": expense_date.strftime("%Y-%m-%d"),
                            "currency": "KES"
                        },
                        "confidence": 0.95
                    },
                    
                    # Additional fields
                    "status": "processed",
                    "image_url": f"/uploads/receipts/test_{receipt_num}.jpg",
                    "user_id": "test_user"
                }
                
                receipts_data.append(receipt)
                receipt_num += 1
        
        # Insert in batches
        batch_size = 500
        total_inserted = 0
        for i in range(0, len(receipts_data), batch_size):
            batch = receipts_data[i:i + batch_size]
            await self.db.receipts.insert_many(batch)
            total_inserted += len(batch)
            print(f"  📊 {total_inserted}/{len(receipts_data)} expenses...")
        
        print(f"✅ Created {len(receipts_data)} expense receipts\n")
        
    async def verify_data(self):
        """Verify data matches working query expectations"""
        print("🔍 Verifying data structure...")
        
        # Test invoice query (exact same as dashboard metrics)
        paid_revenue_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        result = await self.db.invoices.aggregate(paid_revenue_pipeline).to_list(None)
        revenue = result[0]["total"] if result else 0
        
        # Test expense query (exact same as dashboard metrics)
        expense_match = {
            "$or": [
                {"receipt_type": "expense"},
                {"receipt_type": "refund"},
                {"ocr_data.extracted_data.total_amount": {"$exists": True}}
            ]
        }
        expense_receipts = await self.db.receipts.find(expense_match).to_list(None)
        total_expenses = sum(
            r.get("ocr_data", {}).get("extracted_data", {}).get("total_amount", 0)
            for r in expense_receipts
        )
        
        # Status counts
        statuses = {
            "paid": await self.db.invoices.count_documents({"status": "paid"}),
            "pending": await self.db.invoices.count_documents({"status": {"$in": ["pending", "sent", "unpaid"]}}),
            "overdue": await self.db.invoices.count_documents({"status": "overdue"})
        }
        
        print(f"\n{'='*60}")
        print(f"📊 DATA VERIFICATION SUMMARY")
        print(f"{'='*60}")
        print(f"\n💰 Financial Metrics:")
        print(f"  Total Revenue (Paid): KES {revenue:,.2f}")
        print(f"  Total Expenses:       KES {total_expenses:,.2f}")
        print(f"  Net Income:           KES {(revenue - total_expenses):,.2f}")
        
        print(f"\n📄 Invoice Breakdown:")
        print(f"  Paid:    {statuses['paid']:,}")
        print(f"  Pending: {statuses['pending']:,}")
        print(f"  Overdue: {statuses['overdue']:,}")
        print(f"  Total:   {sum(statuses.values()):,}")
        
        print(f"\n👥 Customers: {await self.db.customers.count_documents({})}")
        print(f"💸 Expense Receipts: {len(expense_receipts)}")
        
        print(f"\n{'='*60}")
        print(f"✅ All data generated successfully!")
        print(f"{'='*60}\n")
        
    async def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
            
    async def run(self):
        """Run the generation process"""
        try:
            await self.connect()
            await self.analyze_existing_schema()
            await self.clear_data()
            await self.generate_customers()
            await self.generate_invoices()
            await self.generate_expenses()
            await self.verify_data()
            
            print("\n🎉 You can now test all reporting features!")
            print("  • Dashboard metrics")
            print("  • Income statements")
            print("  • Revenue trends")
            print("  • Expense analysis\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 SMART TEST DATA GENERATOR")
    print("="*60)
    print("\nGenerat data based on working API query analysis")
    print(f"Database: {DATABASE_NAME}\n")
    
    asyncio.run(SmartDataGenerator().run())
