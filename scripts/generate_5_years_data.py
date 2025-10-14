#!/usr/bin/env python3
"""
Generate 5 Years of Historical Financial Data
Creates realistic financial data from 5 years ago to present date
Following normalized database structure
"""

import asyncio
import os
from datetime import datetime, timedelta
from decimal import Decimal
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import uuid
from bson import ObjectId
import calendar

# Load environment variables
load_dotenv()

class HistoricalDataGenerator:
    def __init__(self, years=5):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.client = None
        self.db = None
        self.years = years
        
        # Date range
        self.end_date = datetime.now()
        self.start_date = self.end_date - timedelta(days=365 * years)
        
        # Storage for generated IDs
        self.user_ids = []
        self.customer_ids = []
        self.product_ids = []
        self.invoice_ids = []
        self.payment_ids = []
        
        # Statistics
        self.stats = {
            "users": 0,
            "customers": 0,
            "products": 0,
            "invoices": 0,
            "invoice_items": 0,
            "payments": 0,
            "total_revenue": 0,
            "total_payments": 0
        }
    
    async def connect(self):
        """Connect to MongoDB"""
        print(f"📡 Connecting to MongoDB...")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client.financial_agent
        print("✅ Connected to MongoDB\n")
    
    async def clear_existing_data(self):
        """Clear existing data (optional)"""
        print("🗑️  Checking for existing data...")
        
        collections = [
            "users", "customers", "products", "invoices",
            "invoice_items", "payments", "payment_gateway_data",
            "user_sessions", "audit_logs"
        ]
        
        existing_count = 0
        for coll in collections:
            count = await self.db[coll].count_documents({})
            existing_count += count
        
        if existing_count > 0:
            print(f"⚠️  Found {existing_count} existing documents")
            response = input("Clear existing data? (yes/no): ").strip().lower()
            if response == "yes":
                for coll in collections:
                    await self.db[coll].delete_many({})
                print("✅ Existing data cleared\n")
            else:
                print("⚠️  Continuing with existing data (may cause duplicates)\n")
        else:
            print("✅ No existing data found\n")
    
    async def create_indexes(self):
        """Create all necessary indexes"""
        print("📑 Creating indexes...")
        
        # Helper function to create index safely
        async def create_index_safe(collection, keys, **kwargs):
            try:
                await collection.create_index(keys, **kwargs)
            except Exception as e:
                if "already exists" in str(e) or "IndexKeySpecsConflict" in str(e):
                    pass
                else:
                    raise
        
        # Users
        await create_index_safe(self.db.users, [("email", 1)], unique=True)
        # Note: username field removed - using email as primary identifier
        
        # Customers
        await create_index_safe(self.db.customers, [("customer_id", 1)], unique=True)
        await create_index_safe(self.db.customers, [("email", 1)], unique=True)
        
        # Products
        await create_index_safe(self.db.products, [("product_id", 1)], unique=True)
        await create_index_safe(self.db.products, [("sku", 1)], unique=True)
        
        # Invoices
        await create_index_safe(self.db.invoices, [("invoice_id", 1)], unique=True)
        await create_index_safe(self.db.invoices, [("invoice_number", 1)], unique=True)
        await create_index_safe(self.db.invoices, [("customer_id", 1), ("date_issued", -1)])
        
        # Invoice Items
        await create_index_safe(self.db.invoice_items, [("item_id", 1)], unique=True)
        await create_index_safe(self.db.invoice_items, [("invoice_id", 1)])
        
        # Payments
        await create_index_safe(self.db.payments, [("payment_id", 1)], unique=True)
        await create_index_safe(self.db.payments, [("invoice_id", 1)])
        
        print("✅ Indexes created\n")
    
    async def generate_users(self):
        """Generate system users"""
        print("======================================================================")
        print("  GENERATING USERS")
        print("======================================================================\n")
        
        users_data = [
            {"email": "admin@finguard.com", "company_name": "FinGuard Admin", "phone": "+254712345678", "role": "admin"},
            {"email": "accountant1@finguard.com", "company_name": "FinGuard Accounting", "phone": "+254723456789", "role": "accountant"},
            {"email": "accountant2@finguard.com", "company_name": "FinGuard Finance", "phone": "+254734567890", "role": "accountant"},
            {"email": "manager@finguard.com", "company_name": "FinGuard Management", "phone": "+254745678901", "role": "manager"},
            {"email": "finance@finguard.com", "company_name": "FinGuard Operations", "phone": "+254756789012", "role": "accountant"},
            {"email": "sales1@finguard.com", "company_name": "FinGuard Sales Team", "phone": "+254767890123", "role": "owner"},
            {"email": "sales2@finguard.com", "company_name": "FinGuard Business Dev", "phone": "+254778901234", "role": "owner"},
            {"email": "support@finguard.com", "company_name": "FinGuard Support", "phone": "+254789012345", "role": "viewer"},
        ]
        
        users = []
        created_date = self.start_date
        
        for user_data in users_data:
            user = {
                "email": user_data["email"],
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU9uXMO",  # password123
                "company_name": user_data["company_name"],
                "phone_number": user_data["phone"],
                "role": user_data["role"],
                "is_active": True,
                "created_at": created_date,
                "updated_at": self.end_date,
                "last_login": self.end_date - timedelta(days=random.randint(0, 7)),
                "preferences": {
                    "theme": random.choice(["light", "dark"]),
                    "notifications": True,
                    "language": "en",
                    "currency": "KES"
                }
            }
            users.append(user)
            created_date += timedelta(days=random.randint(1, 30))
        
        result = await self.db.users.insert_many(users)
        self.user_ids = [str(id) for id in result.inserted_ids]
        self.stats["users"] = len(users)
        
        print(f"✅ Created {len(users)} users")
        print(f"   Roles: {len([u for u in users if u['role']=='admin'])} admin, "
              f"{len([u for u in users if u['role']=='accountant'])} accountant, "
              f"{len([u for u in users if u['role']=='manager'])} manager, "
              f"{len([u for u in users if u['role']=='owner'])} owner, "
              f"{len([u for u in users if u['role']=='viewer'])} viewer")
        print()
    
    async def generate_customers(self, count=100):
        """Generate customers over time"""
        print("======================================================================")
        print("  GENERATING CUSTOMERS")
        print("======================================================================\n")
        
        companies = [
            "Tech Solutions Ltd", "Digital Services Inc", "Cloud Innovations",
            "Data Systems Corp", "Mobile Apps Co", "Web Designers Ltd",
            "Enterprise Solutions", "Smart Business Ltd", "Global Trading Co",
            "Local Retail Chain", "Manufacturing Ltd", "Import Export Co",
            "Construction Group", "Real Estate Ltd", "Healthcare Services",
            "Education Center", "Hospitality Group", "Transport Services",
            "Agriculture Co", "Energy Solutions", "Security Services Ltd",
            "Media Company", "Advertising Agency", "Consulting Firm",
            "Law Firm", "Accounting Services", "Insurance Brokers",
            "Travel Agency", "Restaurant Chain", "Fashion Boutique"
        ]
        
        cities = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret", "Thika", "Malindi"]
        
        customers = []
        
        # Distribute customer creation over 5 years
        days_total = (self.end_date - self.start_date).days
        days_per_customer = days_total / count
        
        for i in range(count):
            customer_id = str(uuid.uuid4())
            self.customer_ids.append(customer_id)
            
            # Progressively create customers over time
            creation_date = self.start_date + timedelta(days=int(i * days_per_customer))
            
            # Use company names for first batch, then generic names
            if i < len(companies):
                company_name = companies[i]
                contact_name = f"{random.choice(['John', 'Jane', 'Peter', 'Mary', 'David', 'Sarah'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])}"
            else:
                company_name = f"Business {i+1}"
                contact_name = f"Contact Person {i+1}"
            
            customer = {
                "customer_id": customer_id,
                "name": company_name,
                "contact_person": contact_name,
                "email": f"{company_name.lower().replace(' ', '')}@example.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "status": "active" if random.random() > 0.1 else "inactive",
                "address": {
                    "street": f"{random.randint(1, 999)} {random.choice(['Main', 'Market', 'Industrial', 'Business', 'Commerce'])} Street",
                    "city": random.choice(cities),
                    "postal_code": f"{random.randint(10000, 99999)}",
                    "country": "Kenya"
                },
                "tax_info": {
                    "tax_id": f"P{random.randint(100000000, 999999999)}",
                    "tax_rate": 0.16
                },
                "payment_terms": random.choice([15, 30, 45, 60]),
                "credit_limit": round(random.uniform(50000, 500000), 2),
                "created_at": creation_date,
                "updated_at": creation_date + timedelta(days=random.randint(0, 365)),
                "notes": f"Customer since {creation_date.year}"
            }
            customers.append(customer)
        
        await self.db.customers.insert_many(customers)
        self.stats["customers"] = len(customers)
        
        print(f"✅ Created {len(customers)} customers")
        print(f"   Date range: {self.start_date.date()} to {self.end_date.date()}")
        print(f"   Cities: {', '.join(set(c['address']['city'] for c in customers[:10]))}")
        print(f"   Active: {len([c for c in customers if c['status']=='active'])}")
        print()
    
    async def generate_products(self):
        """Generate product catalog"""
        print("======================================================================")
        print("  GENERATING PRODUCTS")
        print("======================================================================\n")
        
        products_data = [
            # Software Services
            {"name": "Website Development", "category": "Software Development", "base_price": 150000, "variation": 0.3},
            {"name": "Mobile App Development", "category": "Software Development", "base_price": 250000, "variation": 0.4},
            {"name": "E-commerce Platform", "category": "Software Development", "base_price": 300000, "variation": 0.35},
            {"name": "Custom Software Solution", "category": "Software Development", "base_price": 500000, "variation": 0.5},
            {"name": "API Integration", "category": "Software Development", "base_price": 80000, "variation": 0.3},
            
            # Consulting Services
            {"name": "IT Consulting (Per Hour)", "category": "Consulting", "base_price": 5000, "variation": 0.2},
            {"name": "Business Analysis", "category": "Consulting", "base_price": 75000, "variation": 0.25},
            {"name": "Project Management", "category": "Consulting", "base_price": 100000, "variation": 0.3},
            {"name": "Technical Audit", "category": "Consulting", "base_price": 120000, "variation": 0.3},
            
            # Cloud & Hosting
            {"name": "Cloud Hosting (Monthly)", "category": "Cloud Services", "base_price": 15000, "variation": 0.2},
            {"name": "Dedicated Server (Monthly)", "category": "Cloud Services", "base_price": 45000, "variation": 0.2},
            {"name": "VPS Hosting (Monthly)", "category": "Cloud Services", "base_price": 8000, "variation": 0.15},
            {"name": "Domain Registration (Annual)", "category": "Cloud Services", "base_price": 1500, "variation": 0.1},
            {"name": "SSL Certificate (Annual)", "category": "Cloud Services", "base_price": 8000, "variation": 0.15},
            
            # Support & Maintenance
            {"name": "Technical Support (Monthly)", "category": "Support", "base_price": 25000, "variation": 0.2},
            {"name": "Software Maintenance (Annual)", "category": "Support", "base_price": 120000, "variation": 0.25},
            {"name": "Emergency Support (Per Incident)", "category": "Support", "base_price": 15000, "variation": 0.3},
            
            # Design Services
            {"name": "UI/UX Design", "category": "Design", "base_price": 80000, "variation": 0.3},
            {"name": "Graphic Design", "category": "Design", "base_price": 35000, "variation": 0.25},
            {"name": "Brand Identity Package", "category": "Design", "base_price": 150000, "variation": 0.3},
            
            # Data Services
            {"name": "Database Design", "category": "Data Services", "base_price": 90000, "variation": 0.3},
            {"name": "Data Migration", "category": "Data Services", "base_price": 120000, "variation": 0.35},
            {"name": "Database Optimization", "category": "Data Services", "base_price": 65000, "variation": 0.25},
            {"name": "Backup Solutions (Monthly)", "category": "Data Services", "base_price": 12000, "variation": 0.2},
            
            # Training
            {"name": "Software Training (Per Day)", "category": "Training", "base_price": 45000, "variation": 0.2},
            {"name": "Team Workshop", "category": "Training", "base_price": 80000, "variation": 0.25},
            
            # Security
            {"name": "Security Audit", "category": "Security", "base_price": 150000, "variation": 0.3},
            {"name": "Penetration Testing", "category": "Security", "base_price": 200000, "variation": 0.35},
            {"name": "Security Monitoring (Monthly)", "category": "Security", "base_price": 35000, "variation": 0.2},
            
            # License & Software
            {"name": "Software License (Annual)", "category": "Licensing", "base_price": 60000, "variation": 0.2},
            {"name": "Enterprise License", "category": "Licensing", "base_price": 180000, "variation": 0.3},
        ]
        
        products = []
        
        for i, prod_data in enumerate(products_data):
            product_id = str(uuid.uuid4())
            self.product_ids.append(product_id)
            
            # Create product early in the timeline
            creation_date = self.start_date + timedelta(days=random.randint(0, 180))
            
            # Calculate price with variation
            base = prod_data["base_price"]
            variation = prod_data["variation"]
            price = round(base * random.uniform(1 - variation, 1 + variation), 2)
            
            product = {
                "product_id": product_id,
                "sku": f"PRD-{1000 + i}",
                "name": prod_data["name"],
                "description": f"Professional {prod_data['name'].lower()} service",
                "category": prod_data["category"],
                "unit_price": price,
                "cost_price": round(price * 0.6, 2),  # 40% margin
                "currency": "KES",
                "status": "active",
                "unit": "service" if "Monthly" not in prod_data["name"] else "month",
                "tax_rate": 0.16,
                "created_at": creation_date,
                "updated_at": creation_date,
                "price_history": [
                    {
                        "price": price,
                        "effective_date": creation_date,
                        "reason": "Initial price"
                    }
                ]
            }
            products.append(product)
        
        await self.db.products.insert_many(products)
        self.stats["products"] = len(products)
        
        print(f"✅ Created {len(products)} products")
        categories = {}
        for p in products:
            categories[p["category"]] = categories.get(p["category"], 0) + 1
        print(f"   Categories: {dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))}")
        print()
    
    async def generate_invoices_and_items(self):
        """Generate invoices with items over 5 years"""
        print("======================================================================")
        print("  GENERATING INVOICES (5 YEARS)")
        print("======================================================================\n")
        
        print("📊 This will take a few minutes...")
        print("   Generating invoices from {} to {}".format(
            self.start_date.date(), self.end_date.date()
        ))
        print()
        
        # Calculate invoices per month (increasing over time)
        months_total = self.years * 12
        invoices_per_month = list(range(10, 10 + months_total))  # Growing business
        
        invoices = []
        invoice_items_batch = []
        invoice_counter = 1
        
        # Generate month by month
        current_date = self.start_date
        
        for month_idx in range(months_total):
            month_start = current_date
            month_end = month_start + timedelta(days=calendar.monthrange(month_start.year, month_start.month)[1])
            
            num_invoices = invoices_per_month[month_idx]
            
            print(f"   {month_start.strftime('%B %Y')}: Generating {num_invoices} invoices...", end='\r')
            
            for _ in range(num_invoices):
                invoice_id = str(uuid.uuid4())
                self.invoice_ids.append(invoice_id)
                
                # Random date within the month
                days_in_month = (month_end - month_start).days
                invoice_date = month_start + timedelta(
                    days=random.randint(0, days_in_month - 1),
                    hours=random.randint(8, 17)
                )
                
                # Select active customer (prefer older customers)
                active_customers = [c for c in self.customer_ids if c]
                # Weight toward customers created before this invoice date
                customer_id = random.choice(active_customers)
                
                due_date = invoice_date + timedelta(days=random.choice([15, 30, 45, 60]))
                
                # Determine status based on due date vs current date
                if due_date < self.end_date:
                    if random.random() < 0.85:  # 85% payment rate
                        status = "paid"
                    elif invoice_date < self.end_date - timedelta(days=60):
                        status = "overdue"
                    else:
                        status = "pending"
                else:
                    status = "pending"
                
                invoice = {
                    "invoice_id": invoice_id,
                    "invoice_number": f"INV-{self.start_date.year + month_idx // 12}{invoice_counter:05d}",
                    "customer_id": customer_id,
                    "date_issued": invoice_date,
                    "due_date": due_date,
                    "status": status,
                    "subtotal": 0,
                    "tax_rate": 0.16,
                    "tax_amount": 0,
                    "total_amount": 0,
                    "currency": "KES",
                    "payment_terms": random.choice([15, 30, 45, 60]),
                    "notes": f"Invoice for services - {invoice_date.strftime('%B %Y')}",
                    "created_at": invoice_date,
                    "updated_at": invoice_date if status == "pending" else invoice_date + timedelta(days=random.randint(1, 30))
                }
                
                # Create 1-8 invoice items
                num_items = random.choices([1, 2, 3, 4, 5, 6, 7, 8], weights=[5, 15, 25, 25, 15, 8, 5, 2])[0]
                invoice_subtotal = 0
                
                selected_products = random.sample(self.product_ids, min(num_items, len(self.product_ids)))
                
                for product_id in selected_products:
                    # Get product (in real scenario, fetch from DB)
                    quantity = random.choices(
                        [1, 2, 3, 4, 5, 10, 12, 20],
                        weights=[30, 20, 15, 10, 8, 7, 5, 5]
                    )[0]
                    
                    # Simulate product price
                    unit_price = round(random.uniform(5000, 300000), 2)
                    line_total = round(quantity * unit_price, 2)
                    invoice_subtotal += line_total
                    
                    item = {
                        "item_id": str(uuid.uuid4()),
                        "invoice_id": invoice_id,
                        "product_id": product_id,
                        "description": f"Service/Product",
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total,
                        "currency": "KES",
                        "tax_rate": 0.16,
                        "product_snapshot": {
                            "sku": f"PRD-{random.randint(1000, 1030)}",
                            "name": "Product Name"
                        }
                    }
                    invoice_items_batch.append(item)
                
                # Calculate totals
                invoice["subtotal"] = round(invoice_subtotal, 2)
                invoice["tax_amount"] = round(invoice_subtotal * 0.16, 2)
                invoice["total_amount"] = round(invoice_subtotal * 1.16, 2)
                
                invoices.append(invoice)
                invoice_counter += 1
            
            # Move to next month
            current_date = month_end
        
        print()  # Clear the progress line
        
        # Insert in batches for performance
        print("💾 Saving to database...")
        batch_size = 1000
        
        for i in range(0, len(invoices), batch_size):
            await self.db.invoices.insert_many(invoices[i:i+batch_size])
        
        for i in range(0, len(invoice_items_batch), batch_size):
            await self.db.invoice_items.insert_many(invoice_items_batch[i:i+batch_size])
        
        self.stats["invoices"] = len(invoices)
        self.stats["invoice_items"] = len(invoice_items_batch)
        self.stats["total_revenue"] = sum(inv["total_amount"] for inv in invoices)
        
        print(f"\n✅ Created {len(invoices):,} invoices")
        print(f"✅ Created {len(invoice_items_batch):,} invoice items")
        print(f"   Total revenue: KES {self.stats['total_revenue']:,.2f}")
        print(f"   Average invoice: KES {self.stats['total_revenue']/len(invoices):,.2f}")
        print(f"   Items per invoice: {len(invoice_items_batch)/len(invoices):.1f}")
        
        # Status breakdown
        status_counts = {}
        for inv in invoices:
            status_counts[inv["status"]] = status_counts.get(inv["status"], 0) + 1
        print(f"   Status breakdown: {status_counts}")
        print()
    
    async def generate_payments(self):
        """Generate payments for paid invoices"""
        print("======================================================================")
        print("  GENERATING PAYMENTS")
        print("======================================================================\n")
        
        print("💾 Fetching paid invoices...")
        paid_invoices = await self.db.invoices.find({"status": "paid"}).to_list(None)
        
        print(f"📊 Processing {len(paid_invoices):,} paid invoices...")
        
        payment_methods = ["mpesa", "bank_transfer", "card", "cash", "cheque"]
        payment_weights = [40, 30, 15, 10, 5]  # M-Pesa is most popular
        
        payments = []
        gateway_data_batch = []
        
        for idx, invoice in enumerate(paid_invoices):
            if idx % 1000 == 0 and idx > 0:
                print(f"   Processed {idx:,} payments...", end='\r')
            
            payment_id = str(uuid.uuid4())
            self.payment_ids.append(payment_id)
            
            payment_method = random.choices(payment_methods, weights=payment_weights)[0]
            
            # Payment made between invoice date and a bit after due date
            days_to_pay = random.randint(1, 45)
            payment_date = invoice["date_issued"] + timedelta(days=days_to_pay)
            
            # Ensure payment date is not in the future
            if payment_date > self.end_date:
                payment_date = self.end_date - timedelta(days=random.randint(1, 30))
            
            payment = {
                "payment_id": payment_id,
                "invoice_id": invoice["invoice_id"],
                "customer_id": invoice["customer_id"],
                "amount": invoice["total_amount"],
                "currency": "KES",
                "payment_method": payment_method,
                "payment_date": payment_date,
                "status": "completed",
                "transaction_reference": f"TXN{payment_date.year}{random.randint(100000, 999999)}",
                "notes": f"Payment via {payment_method}",
                "created_at": payment_date,
                "updated_at": payment_date
            }
            payments.append(payment)
            
            # Create gateway-specific data
            if payment_method == "mpesa":
                gateway_data = {
                    "payment_id": payment_id,
                    "gateway": "mpesa",
                    "gateway_transaction_id": f"MPM{random.randint(10000000, 99999999)}",
                    "gateway_data": {
                        "phone": f"+254{random.randint(700000000, 799999999)}",
                        "mpesa_receipt": f"QGN{random.randint(1000000, 9999999)}",
                        "account_reference": invoice["invoice_number"],
                        "result_code": "0",
                        "result_desc": "The service request is processed successfully",
                        "transaction_date": payment_date.isoformat()
                    },
                    "created_at": payment_date
                }
                gateway_data_batch.append(gateway_data)
            elif payment_method == "bank_transfer":
                gateway_data = {
                    "payment_id": payment_id,
                    "gateway": "bank",
                    "gateway_transaction_id": f"BNK{random.randint(100000000, 999999999)}",
                    "gateway_data": {
                        "bank_name": random.choice(["KCB", "Equity", "Cooperative", "NCBA", "Absa"]),
                        "account_number": f"ACC{random.randint(1000000, 9999999)}",
                        "reference": invoice["invoice_number"],
                        "transfer_date": payment_date.isoformat()
                    },
                    "created_at": payment_date
                }
                gateway_data_batch.append(gateway_data)
        
        print()
        
        # Insert in batches
        print("💾 Saving payments to database...")
        batch_size = 1000
        
        if payments:
            for i in range(0, len(payments), batch_size):
                await self.db.payments.insert_many(payments[i:i+batch_size])
        
        if gateway_data_batch:
            for i in range(0, len(gateway_data_batch), batch_size):
                await self.db.payment_gateway_data.insert_many(gateway_data_batch[i:i+batch_size])
        
        self.stats["payments"] = len(payments)
        self.stats["total_payments"] = sum(p["amount"] for p in payments)
        
        print(f"\n✅ Created {len(payments):,} payments")
        print(f"✅ Created {len(gateway_data_batch):,} gateway data records")
        print(f"   Total amount paid: KES {self.stats['total_payments']:,.2f}")
        print(f"   Payment rate: {len(payments)/self.stats['invoices']*100:.1f}%")
        
        # Payment method breakdown
        method_counts = {}
        for p in payments:
            method_counts[p["payment_method"]] = method_counts.get(p["payment_method"], 0) + 1
        print(f"   Methods: {method_counts}")
        print()
    
    async def create_audit_log(self):
        """Create initial audit log"""
        print("📝 Creating audit log entry...")
        
        audit_entry = {
            "user_id": self.user_ids[0] if self.user_ids else None,
            "action": "database.bulk_generate",
            "resource_type": "database",
            "resource_id": "financial_agent",
            "timestamp": self.end_date,
            "details": {
                "operation": "5_year_historical_data_generation",
                "date_range": {
                    "start": self.start_date.isoformat(),
                    "end": self.end_date.isoformat()
                },
                "statistics": self.stats
            },
            "ip_address": "127.0.0.1",
            "user_agent": "Data Generation Script"
        }
        
        await self.db.audit_logs.insert_one(audit_entry)
        print("✅ Audit log created\n")
    
    async def generate_summary_stats(self):
        """Generate and display summary statistics"""
        print("======================================================================")
        print("  GENERATING SUMMARY STATISTICS")
        print("======================================================================\n")
        
        # Yearly breakdown
        print("📊 Yearly Breakdown:")
        print("-" * 70)
        
        for year in range(self.start_date.year, self.end_date.year + 1):
            year_start = datetime(year, 1, 1)
            year_end = datetime(year, 12, 31, 23, 59, 59)
            
            year_invoices = await self.db.invoices.count_documents({
                "date_issued": {"$gte": year_start, "$lte": year_end}
            })
            
            year_pipeline = [
                {"$match": {"date_issued": {"$gte": year_start, "$lte": year_end}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            year_revenue_result = await self.db.invoices.aggregate(year_pipeline).to_list(1)
            year_revenue = year_revenue_result[0]["total"] if year_revenue_result else 0
            
            year_payments = await self.db.payments.count_documents({
                "payment_date": {"$gte": year_start, "$lte": year_end}
            })
            
            year_payment_pipeline = [
                {"$match": {"payment_date": {"$gte": year_start, "$lte": year_end}}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            year_paid_result = await self.db.payments.aggregate(year_payment_pipeline).to_list(1)
            year_paid = year_paid_result[0]["total"] if year_paid_result else 0
            
            print(f"{year}: {year_invoices:4} invoices, KES {year_revenue:15,.2f} revenue, "
                  f"{year_payments:4} payments, KES {year_paid:15,.2f} collected")
        
        print("-" * 70)
        print()
        
        # Top customers
        print("👥 Top 10 Customers by Revenue:")
        print("-" * 70)
        
        top_customers_pipeline = [
            {
                "$group": {
                    "_id": "$customer_id",
                    "total_revenue": {"$sum": "$total_amount"},
                    "invoice_count": {"$sum": 1}
                }
            },
            {"$sort": {"total_revenue": -1}},
            {"$limit": 10}
        ]
        
        top_customers = await self.db.invoices.aggregate(top_customers_pipeline).to_list(10)
        
        for idx, cust in enumerate(top_customers, 1):
            customer_doc = await self.db.customers.find_one({"customer_id": cust["_id"]})
            customer_name = customer_doc["name"] if customer_doc else "Unknown"
            print(f"{idx:2}. {customer_name[:30]:30} KES {cust['total_revenue']:12,.2f} ({cust['invoice_count']:3} invoices)")
        
        print("-" * 70)
        print()
        
        # Monthly trend (last 12 months)
        print("📈 Last 12 Months Trend:")
        print("-" * 70)
        
        for month_offset in range(11, -1, -1):
            month_date = self.end_date - timedelta(days=30 * month_offset)
            month_start = datetime(month_date.year, month_date.month, 1)
            
            if month_date.month == 12:
                month_end = datetime(month_date.year + 1, 1, 1) - timedelta(seconds=1)
            else:
                month_end = datetime(month_date.year, month_date.month + 1, 1) - timedelta(seconds=1)
            
            month_invoices = await self.db.invoices.count_documents({
                "date_issued": {"$gte": month_start, "$lte": month_end}
            })
            
            month_pipeline = [
                {"$match": {"date_issued": {"$gte": month_start, "$lte": month_end}}},
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            month_revenue_result = await self.db.invoices.aggregate(month_pipeline).to_list(1)
            month_revenue = month_revenue_result[0]["total"] if month_revenue_result else 0
            
            bar_length = int(month_invoices / 10) if month_invoices > 0 else 0
            bar = "█" * bar_length
            
            print(f"{month_start.strftime('%b %Y')}: {month_invoices:3} inv {bar:20} KES {month_revenue:12,.2f}")
        
        print("-" * 70)
        print()
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

async def main():
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║         5 YEARS HISTORICAL DATA GENERATOR                            ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    years = 5
    generator = HistoricalDataGenerator(years=years)
    
    try:
        await generator.connect()
        
        print(f"📅 Date Range: {generator.start_date.date()} to {generator.end_date.date()}")
        print(f"📊 Duration: {years} years ({(generator.end_date - generator.start_date).days} days)\n")
        
        # Optional: Clear existing data
        # await generator.clear_existing_data()
        
        # Create indexes
        await generator.create_indexes()
        
        # Generate data
        await generator.generate_users()
        await generator.generate_customers(count=100)
        await generator.generate_products()
        await generator.generate_invoices_and_items()
        await generator.generate_payments()
        await generator.create_audit_log()
        
        # Summary statistics
        await generator.generate_summary_stats()
        
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║              ✅ DATA GENERATION COMPLETE!                            ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝\n")
        
        print("📊 Final Statistics:")
        print(f"   Users: {generator.stats['users']}")
        print(f"   Customers: {generator.stats['customers']}")
        print(f"   Products: {generator.stats['products']}")
        print(f"   Invoices: {generator.stats['invoices']:,}")
        print(f"   Invoice Items: {generator.stats['invoice_items']:,}")
        print(f"   Payments: {generator.stats['payments']:,}")
        print(f"   Total Revenue: KES {generator.stats['total_revenue']:,.2f}")
        print(f"   Total Collected: KES {generator.stats['total_payments']:,.2f}")
        print(f"   Collection Rate: {generator.stats['total_payments']/generator.stats['total_revenue']*100:.1f}%")
        print()
        
        print("🎉 Your database now contains 5 years of financial history!")
        print("   Ready for reporting, analytics, and forecasting.\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await generator.close()

if __name__ == "__main__":
    asyncio.run(main())
