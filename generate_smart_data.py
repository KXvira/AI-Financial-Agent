"""
Smart Data Generator - Based on Actual API Field Requirements

This generator creates data by analyzing what the WORKING services actually expect.
All field names and structures match the exact queries used in:
- dashboard_metrics
- income_statement  
- vat_summary
- trend analysis

Author: AI Assistant
Date: 2025-10-17
"""

import asyncio
import random
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB connection
MONGO_URI = os.environ.get(
    "MONGO_URI", 
    "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
)
DATABASE_NAME = os.environ.get("MONGO_DATABASE", "financial_agent")

# Configuration
MONTHS_OF_DATA = 24
CUSTOMERS_COUNT = 50
INVOICES_PER_MONTH = (30, 50)

# Kenyan VAT rate
VAT_RATE = 0.16

# Sample data
KENYAN_COMPANIES = [
    "Safaricom Ltd", "Kenya Power", "Equity Bank", "KCB Bank",
    "Naivas Supermarket", "Java House", "Bamburi Cement",
    "Kenya Airways", "Britam", "CIC Insurance", "Twiga Foods",
    "Sendy Ltd", "MarketForce", "Jumia Kenya", "Glovo Kenya"
]

EXPENSE_CATEGORIES = [
    "Utilities", "Rent", "Salaries", "Marketing", "Transportation",
    "Equipment", "Software", "Insurance", "Professional Services",
    "Maintenance", "Travel", "Communication", "Bank Charges"
]

SERVICES = [
    "Consulting", "Development", "Cloud Services", "IT Support",
    "Training", "Analytics", "Maintenance", "Integration"
]


class SmartDataGenerator:
    def __init__(self):
        self.client = None
        self.db = None
        self.customers = []
        self.start_date = datetime.now() - timedelta(days=MONTHS_OF_DATA * 30)
        
    async def connect(self):
        """Connect to MongoDB"""
        print(f"🔌 Connecting to {DATABASE_NAME}...")
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DATABASE_NAME]
        await self.client.admin.command('ping')
        print("✅ Connected successfully\n")
    
    async def clear_existing_data(self):
        """Delete all existing data"""
        print("🗑️  Clearing existing data...")
        
        await self.db.customers.delete_many({})
        await self.db.invoices.delete_many({})
        await self.db.transactions.delete_many({})
        await self.db.payments.delete_many({})
        await self.db.ai_matching_summary.delete_many({})
        
        print("✅ Existing data cleared\n")
        
    async def generate_customers(self):
        """Generate customers with EXACT fields from dashboard query"""
        print(f"👥 Generating {CUSTOMERS_COUNT} customers...")
        
        customers = []
        for i in range(CUSTOMERS_COUNT):
            cust_id = f"CUST-{1001+i:06d}"
            
            # Create a good distribution:
            # - 85% active customers (will get most invoices)
            # - 15% inactive customers (will get fewer/no recent invoices)
            is_active = i < int(CUSTOMERS_COUNT * 0.85)
            
            customer = {
                "_id": ObjectId(),
                "customer_id": cust_id,  # Required by unique index
                "name": f"{random.choice(KENYAN_COMPANIES)} - {random.choice(['Ltd', 'Co', 'Group'])}",
                "email": f"billing{i+1}@company{i+1}.co.ke",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "status": "active" if is_active else "inactive",
                "payment_terms": random.choice([7, 14, 30, 45, 60]),
                "created_at": self.start_date,
                "updated_at": datetime.now()
            }
            customers.append(customer)
        
        if customers:
            await self.db.customers.insert_many(customers)
            self.customers = customers
            print(f"✅ Created {len(customers)} customers\n")
        
        return customers
    
    async def generate_invoices(self):
        """
        Generate invoices with ALL required fields based on ACTUAL queries:
        - status: "paid", "pending", "sent", "unpaid", "overdue" (used by dashboard)
        - total_amount: main amount field (used by dashboard aggregation)
        - issue_date: string YYYY-MM-DD format (for trend filtering)
        - invoice_date: string YYYY-MM-DD (for VAT reports)
        - tax_amount, tax_rate, subtotal: for VAT calculations
        - invoice_id: unique identifier (has unique index)
        """
        print(f"📄 Generating invoices for {MONTHS_OF_DATA} months...")
        
        invoices = []
        invoice_num = 10001
        
        for month_offset in range(MONTHS_OF_DATA):
            month_date = self.start_date + timedelta(days=month_offset * 30)
            num_invoices = random.randint(*INVOICES_PER_MONTH)
            
            for _ in range(num_invoices):
                # Active customers get more invoices than inactive ones
                active_customers = [c for c in self.customers if c["status"] == "active"]
                inactive_customers = [c for c in self.customers if c["status"] == "inactive"]
                
                # 90% of invoices go to active customers, 10% to inactive
                if random.random() < 0.9 and active_customers:
                    customer = random.choice(active_customers)
                elif inactive_customers:
                    customer = random.choice(inactive_customers)
                else:
                    customer = random.choice(self.customers)
                
                # Issue date within the month
                issue_day = random.randint(1, 28)
                issue_date = month_date + timedelta(days=issue_day)
                due_date = issue_date + timedelta(days=customer["payment_terms"])
                
                # Calculate amounts
                subtotal = random.choice([50000, 100000, 250000, 500000, 1000000, 2500000])
                tax_amount = subtotal * VAT_RATE
                total_amount = subtotal + tax_amount
                
                # Determine status based on customer status and age
                days_old = (datetime.now() - issue_date).days
                days_overdue = (datetime.now() - due_date).days
                
                # Inactive customers are more likely to have unpaid invoices
                if customer["status"] == "inactive":
                    if days_overdue > 60:
                        status = random.choice(["overdue"] * 7 + ["paid"] * 3)
                    elif days_overdue > 30:
                        status = random.choice(["overdue"] * 6 + ["unpaid"] * 3 + ["paid"])
                    else:
                        status = random.choice(["unpaid"] * 5 + ["pending"] * 3 + ["overdue"] * 2)
                else:
                    # Active customers - mostly paid
                    if days_overdue > 30:
                        status = random.choice(["paid"] * 7 + ["overdue"] * 3)
                    elif days_overdue > 0:
                        status = random.choice(["paid"] * 6 + ["overdue"] * 4)
                    else:
                        status = random.choice(["paid"] * 7 + ["pending", "sent", "unpaid"] * 3)
                
                # Payment details for paid invoices
                if status == "paid":
                    payment_days = random.randint(0, min(days_old, 45))
                    payment_date = issue_date + timedelta(days=payment_days)
                    amount_paid = total_amount
                else:
                    payment_date = None
                    amount_paid = 0
                
                invoice = {
                    "_id": ObjectId(),
                    "invoice_id": f"INV{invoice_num}",  # Unique index requirement
                    "invoice_number": f"INV-{invoice_num:06d}",
                    "customer_id": customer["customer_id"],  # Link to customer
                    "customer_name": customer["name"],
                    
                    # Date fields - CRITICAL for all reports
                    "issue_date": issue_date.strftime("%Y-%m-%d"),  # For trends
                    "invoice_date": issue_date.strftime("%Y-%m-%d"),  # For VAT
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "payment_date": payment_date.strftime("%Y-%m-%d") if payment_date else None,
                    
                    # Status - used by dashboard queries
                    "status": status,  # MUST be lowercase!
                    
                    # Amount fields - CRITICAL for aggregations
                    "subtotal": subtotal,
                    "tax_rate": VAT_RATE,
                    "tax_amount": tax_amount,
                    "vat_amount": tax_amount,  # Alternative field name
                    "total_amount": total_amount,  # PRIMARY field for revenue
                    "amount": total_amount,  # Duplicate for compatibility
                    "amount_paid": amount_paid,
                    "balance": total_amount - amount_paid,
                    
                    # VAT fields for tax reports
                    "vat_rate": VAT_RATE,
                    "taxable_amount": subtotal,
                    "vat_applicable": True,
                    
                    # Additional fields
                    "currency": "KES",
                    "items": [{
                        "description": random.choice(SERVICES),
                        "quantity": random.randint(1, 10),
                        "unit_price": subtotal / random.randint(1, 5),
                        "total": subtotal
                    }],
                    "notes": f"Payment terms: Net {customer['payment_terms']} days",
                    "created_at": issue_date,
                    "updated_at": payment_date if payment_date else issue_date
                }
                
                invoices.append(invoice)
                invoice_num += 1
        
        # Batch insert
        batch_size = 500
        for i in range(0, len(invoices), batch_size):
            batch = invoices[i:i + batch_size]
            await self.db.invoices.insert_many(batch)
            print(f"  📊 Inserted {min(i + batch_size, len(invoices))}/{len(invoices)} invoices...")
        
        print(f"✅ Created {len(invoices)} invoices\n")
        return invoices
    
    async def generate_expenses(self):
        """
        Generate expenses with fields expected by:
        - Expense aggregation queries
        - VAT input calculations
        """
        print(f"💰 Generating expenses for {MONTHS_OF_DATA} months...")
        
        expenses = []
        
        for month_offset in range(MONTHS_OF_DATA):
            month_date = self.start_date + timedelta(days=month_offset * 30)
            num_expenses = random.randint(20, 40)
            
            for _ in range(num_expenses):
                trans_day = random.randint(1, 28)
                trans_date = month_date + timedelta(days=trans_day)
                
                category = random.choice(EXPENSE_CATEGORIES)
                
                # Amount based on category
                if category in ["Rent", "Salaries"]:
                    amount = random.randint(100000, 500000)
                elif category == "Utilities":
                    amount = random.randint(20000, 100000)
                else:
                    amount = random.randint(5000, 50000)
                
                # Some expenses include VAT (input VAT)
                has_vat = random.choice([True, False])
                if has_vat:
                    taxable_amount = amount / (1 + VAT_RATE)
                    vat_amount = amount - taxable_amount
                else:
                    taxable_amount = amount
                    vat_amount = 0
                
                expense = {
                    "_id": ObjectId(),
                    "type": "expense",  # CRITICAL for filtering
                    "category": category,
                    "amount": amount,
                    "description": f"{category} - {trans_date.strftime('%B %Y')}",
                    
                    # Date fields for filtering
                    "transaction_date": trans_date.strftime("%Y-%m-%d"),  # For expense trends
                    "date": trans_date.strftime("%Y-%m-%d"),  # For VAT reports
                    
                    # VAT fields for input VAT
                    "vat_applicable": has_vat,
                    "vat_rate": VAT_RATE if has_vat else 0,
                    "vat_amount": vat_amount,
                    "taxable_amount": taxable_amount,
                    
                    # Additional fields
                    "payment_method": random.choice(["M-Pesa", "Bank Transfer", "Cash"]),
                    "vendor": random.choice(KENYAN_COMPANIES),
                    "reference": f"EXP-{random.randint(10000, 99999)}",
                    "status": "completed",
                    "created_at": trans_date,
                    "updated_at": trans_date
                }
                
                expenses.append(expense)
        
        # Batch insert
        batch_size = 500
        for i in range(0, len(expenses), batch_size):
            batch = expenses[i:i + batch_size]
            await self.db.transactions.insert_many(batch)
            print(f"  📊 Inserted {min(i + batch_size, len(expenses))}/{len(expenses)} expenses...")
        
        print(f"✅ Created {len(expenses)} expense transactions\n")
    
    async def generate_payments(self, invoices_data):
        """Generate payment records from paid invoices"""
        print("💰 Generating payments for paid invoices...")
        
        payments = []
        payment_methods = ["M-Pesa", "Bank Transfer", "Cash", "Card"]
        
        # Generate payments for all paid invoices
        for invoice in invoices_data:
            if invoice["status"] == "paid" and invoice.get("payment_date"):
                # Parse payment date
                payment_date = datetime.strptime(invoice["payment_date"], "%Y-%m-%d")
                
                # Generate M-Pesa style reference
                payment_method = random.choice(payment_methods)
                if payment_method == "M-Pesa":
                    reference = f"QGH{random.randint(1000000000, 9999999999)}"
                else:
                    reference = f"PAY{random.randint(100000, 999999)}"
                
                # Generate unique payment ID
                payment_id = f"PAY{len(payments) + 10001:06d}"
                
                payment = {
                    "_id": ObjectId(),
                    "payment_id": payment_id,  # Unique identifier
                    "transaction_reference": reference,
                    "invoice_id": invoice["invoice_id"],
                    "customer_id": invoice["customer_id"],
                    "amount": invoice["total_amount"],
                    "payment_date": invoice["payment_date"],  # String format YYYY-MM-DD
                    "payment_method": payment_method,
                    "status": "completed",
                    "notes": f"Payment for {invoice['invoice_number']}",
                    
                    # AI matching fields
                    "ai_matched": True,
                    "match_status": "correct",
                    "match_confidence": round(random.uniform(0.85, 0.99), 2),
                    
                    # Timestamps
                    "created_at": payment_date,
                    "updated_at": payment_date
                }
                
                payments.append(payment)
        
        # Add some unmatched payments (pending reconciliation)
        num_unmatched = int(len(payments) * 0.05)  # 5% unmatched
        for _ in range(num_unmatched):
            # Random date in last 6 months
            days_ago = random.randint(0, 180)
            payment_date = datetime.now() - timedelta(days=days_ago)
            
            # Generate unique payment ID for unmatched payments
            payment_id = f"PAY{len(payments) + 10001:06d}"
            
            payment = {
                "_id": ObjectId(),
                "payment_id": payment_id,  # Unique identifier
                "transaction_reference": f"QGH{random.randint(1000000000, 9999999999)}",
                "invoice_id": None,  # Unmatched
                "customer_id": None,
                "amount": random.choice([50000, 100000, 250000, 500000]),
                "payment_date": payment_date.strftime("%Y-%m-%d"),
                "payment_method": "M-Pesa",
                "status": "pending",  # Pending matching
                "notes": "Unmatched payment - requires reconciliation",
                
                # AI matching fields
                "ai_matched": False,
                "match_status": "unmatched",
                "match_confidence": 0.0,
                
                # Timestamps
                "created_at": payment_date,
                "updated_at": payment_date
            }
            
            payments.append(payment)
        
        # Batch insert
        batch_size = 500
        for i in range(0, len(payments), batch_size):
            batch = payments[i:i + batch_size]
            await self.db.payments.insert_many(batch)
            print(f"  📊 Inserted {min(i + batch_size, len(payments))}/{len(payments)} payments...")
        
        # Update AI matching summary
        matched_count = sum(1 for p in payments if p["ai_matched"] and p["match_status"] == "correct")
        unmatched_count = sum(1 for p in payments if not p["ai_matched"])
        total_matched = sum(1 for p in payments if p["ai_matched"])
        ai_accuracy = round((matched_count / total_matched * 100), 2) if total_matched > 0 else 0
        
        await self.db.ai_matching_summary.delete_many({})
        await self.db.ai_matching_summary.insert_one({
            "correct_matches": matched_count,
            "unmatched_count": unmatched_count,
            "ai_accuracy": ai_accuracy,
            "last_updated": datetime.now()
        })
        
        print(f"✅ Created {len(payments)} payments")
        print(f"   - Matched: {matched_count}")
        print(f"   - Unmatched: {unmatched_count}")
        print(f"   - AI Accuracy: {ai_accuracy}%\n")
        
        return payments
    
    async def create_indexes(self):
        """Create indexes for performance - skip if they already exist"""
        print("🔍 Creating database indexes...")
        
        try:
            # Customer indexes
            try:
                await self.db.customers.create_index("customer_id", unique=True)
            except:
                pass  # Index already exists
            
            # Invoice indexes  
            try:
                await self.db.invoices.create_index("invoice_id", unique=True)
            except:
                pass
                
            try:
                await self.db.invoices.create_index("invoice_number", unique=True)
            except:
                pass
            
            await self.db.invoices.create_index("status", background=True)
            await self.db.invoices.create_index("issue_date", background=True)
            await self.db.invoices.create_index("invoice_date", background=True)
            await self.db.invoices.create_index("customer_id", background=True)
            
            # Transaction indexes
            await self.db.transactions.create_index("type", background=True)
            await self.db.transactions.create_index("transaction_date", background=True)
            await self.db.transactions.create_index("date", background=True)
            await self.db.transactions.create_index("category", background=True)
            
            # Payment indexes
            await self.db.payments.create_index("transaction_reference", background=True)
            await self.db.payments.create_index("invoice_id", background=True)
            await self.db.payments.create_index("customer_id", background=True)
            await self.db.payments.create_index("payment_date", background=True)
            await self.db.payments.create_index("status", background=True)
            await self.db.payments.create_index("ai_matched", background=True)
            
            print("✅ Indexes created\n")
        except Exception as e:
            print(f"⚠️  Some indexes already exist (this is OK): {e}\n")
    
    async def show_summary(self):
        """Display summary statistics"""
        print("="*70)
        print("📊 DATA GENERATION SUMMARY")
        print("="*70)
        
        # Counts
        customer_count = await self.db.customers.count_documents({})
        active_customers = await self.db.customers.count_documents({"status": "active"})
        inactive_customers = await self.db.customers.count_documents({"status": "inactive"})
        
        invoice_count = await self.db.invoices.count_documents({})
        paid_count = await self.db.invoices.count_documents({"status": "paid"})
        unpaid_count = await self.db.invoices.count_documents({"status": {"$in": ["pending", "unpaid", "overdue"]}})
        
        expense_count = await self.db.transactions.count_documents({"type": "expense"})
        payment_count = await self.db.payments.count_documents({})
        
        # Revenue
        revenue_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        revenue_result = await self.db.invoices.aggregate(revenue_pipeline).to_list(None)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Expenses
        expense_pipeline = [
            {"$match": {"type": "expense"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        expense_result = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
        total_expenses = expense_result[0]["total"] if expense_result else 0
        
        # VAT
        vat_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$vat_amount"}}}
        ]
        vat_result = await self.db.invoices.aggregate(vat_pipeline).to_list(None)
        total_vat = vat_result[0]["total"] if vat_result else 0
        
        print(f"\n👥 Customers:              {customer_count:,}")
        print(f"  ✅ Active:               {active_customers:,}")
        print(f"  ⏸️  Inactive:             {inactive_customers:,}")
        
        print(f"\n📄 Total Invoices:         {invoice_count:,}")
        print(f"  ✅ Paid:                 {paid_count:,}")
        print(f"  ⏳ Unpaid/Pending:       {unpaid_count:,}")
        
        print(f"\n💳 Total Payments:         {payment_count:,}")
        
        # Get payment statistics
        ai_summary = await self.db.ai_matching_summary.find_one({})
        if ai_summary:
            print(f"  ✅ Matched:              {ai_summary.get('correct_matches', 0):,}")
            print(f"  ❌ Unmatched:            {ai_summary.get('unmatched_count', 0):,}")
            print(f"  🤖 AI Accuracy:          {ai_summary.get('ai_accuracy', 0)}%")
        
        print(f"\n💰 Total Revenue:          KES {total_revenue:,.2f}")
        print(f"💸 Total Expenses:         KES {total_expenses:,.2f}")
        print(f"📊 Total VAT Collected:    KES {total_vat:,.2f}")
        print(f"📈 Net Income:             KES {(total_revenue - total_expenses):,.2f}")
        print(f"\n📆 Date Range:             {self.start_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}")
        print(f"📅 Months of Data:         {MONTHS_OF_DATA}")
        
        print("\n" + "="*70)
        print("✅ ALL DATA GENERATED SUCCESSFULLY!")
        print("="*70)
        print("\nAll reporting features should now work:")
        print("  ✓ Dashboard Metrics")
        print("  ✓ Revenue Trends")
        print("  ✓ Expense Trends")
        print("  ✓ Month-over-Month Comparisons")
        print("  ✓ Year-over-Year Comparisons")
        print("  ✓ VAT Reports")
        print("  ✓ Income Statements")
        print("  ✓ AR Aging Reports")
        print("  ✓ Payments Overview")
        print("  ✓ Predictive Analytics\n")
    
    async def close(self):
        """Close connection"""
        if self.client:
            self.client.close()
    
    async def run(self):
        """Run the complete generation process"""
        try:
            await self.connect()
            await self.clear_existing_data()
            customers = await self.generate_customers()
            invoices = await self.generate_invoices()
            await self.generate_expenses()
            await self.generate_payments(invoices)  # Generate payments from invoices
            await self.create_indexes()
            await self.show_summary()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()


async def main():
    print("\n" + "="*70)
    print("🚀 SMART DATA GENERATOR")
    print("="*70)
    print(f"\nDatabase: {DATABASE_NAME}")
    print(f"Will generate {MONTHS_OF_DATA} months of financial data\n")
    
    response = input("Proceed? (yes/no): ")
    if response.lower() in ['yes', 'y']:
        generator = SmartDataGenerator()
        await generator.run()
    else:
        print("\n❌ Cancelled")


if __name__ == "__main__":
    asyncio.run(main())
