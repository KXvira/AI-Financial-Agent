#!/usr/bin/env python3
"""
Setup Normalized Database from Scratch
Creates all collections, indexes, and sample data following normalization best practices.
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

# Load environment variables
load_dotenv()

class NormalizedDatabaseSetup:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.client = None
        self.db = None
        
        # Sample data storage
        self.user_ids = []
        self.customer_ids = []
        self.product_ids = []
        self.invoice_ids = []
        self.payment_ids = []
    
    async def connect(self):
        """Connect to MongoDB"""
        print(f"📡 Connecting to MongoDB: {self.mongo_uri[:50]}...")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        self.db = self.client.financial_agent
        print("✅ Connected to MongoDB\n")
    
    async def create_indexes(self):
        """Create all necessary indexes for normalized collections"""
        print("======================================================================")
        print("  STEP 1: CREATING INDEXES")
        print("======================================================================\n")
        
        # Users collection indexes
        print("📑 Creating indexes for users...")
        await self.db.users.create_index([("email", 1)], unique=True)
        await self.db.users.create_index([("username", 1)], unique=True)
        await self.db.users.create_index([("role", 1)])
        await self.db.users.create_index([("status", 1)])
        print("   ✅ Users indexes created")
        
        # Customers collection indexes
        print("📑 Creating indexes for customers...")
        await self.db.customers.create_index([("customer_id", 1)], unique=True)
        await self.db.customers.create_index([("email", 1)], unique=True)
        await self.db.customers.create_index([("phone", 1)])
        await self.db.customers.create_index([("status", 1)])
        await self.db.customers.create_index([("created_at", -1)])
        print("   ✅ Customers indexes created")
        
        # Products collection indexes
        print("📑 Creating indexes for products...")
        await self.db.products.create_index([("product_id", 1)], unique=True)
        await self.db.products.create_index([("sku", 1)], unique=True)
        await self.db.products.create_index([("name", 1)])
        await self.db.products.create_index([("category", 1)])
        await self.db.products.create_index([("status", 1)])
        print("   ✅ Products indexes created")
        
        # Invoices collection indexes
        print("📑 Creating indexes for invoices...")
        await self.db.invoices.create_index([("invoice_id", 1)], unique=True)
        await self.db.invoices.create_index([("invoice_number", 1)], unique=True)
        await self.db.invoices.create_index([("customer_id", 1)])
        await self.db.invoices.create_index([("status", 1)])
        await self.db.invoices.create_index([("date_issued", -1)])
        await self.db.invoices.create_index([("due_date", 1)])
        await self.db.invoices.create_index([("customer_id", 1), ("date_issued", -1)])
        print("   ✅ Invoices indexes created")
        
        # Invoice Items collection indexes
        print("📑 Creating indexes for invoice_items...")
        await self.db.invoice_items.create_index([("item_id", 1)], unique=True)
        await self.db.invoice_items.create_index([("invoice_id", 1)])
        await self.db.invoice_items.create_index([("product_id", 1)])
        await self.db.invoice_items.create_index([("invoice_id", 1), ("product_id", 1)])
        print("   ✅ Invoice Items indexes created")
        
        # Payments collection indexes
        print("📑 Creating indexes for payments...")
        await self.db.payments.create_index([("payment_id", 1)], unique=True)
        await self.db.payments.create_index([("invoice_id", 1)])
        await self.db.payments.create_index([("customer_id", 1)])
        await self.db.payments.create_index([("status", 1)])
        await self.db.payments.create_index([("payment_date", -1)])
        await self.db.payments.create_index([("payment_method", 1)])
        print("   ✅ Payments indexes created")
        
        # Payment Gateway Data collection indexes
        print("📑 Creating indexes for payment_gateway_data...")
        await self.db.payment_gateway_data.create_index([("payment_id", 1)])
        await self.db.payment_gateway_data.create_index([("gateway", 1)])
        await self.db.payment_gateway_data.create_index([("gateway_transaction_id", 1)])
        print("   ✅ Payment Gateway Data indexes created")
        
        # User Sessions collection indexes
        print("📑 Creating indexes for user_sessions...")
        await self.db.user_sessions.create_index([("user_id", 1)])
        await self.db.user_sessions.create_index([("token", 1)], unique=True)
        await self.db.user_sessions.create_index([("expires_at", 1)])
        await self.db.user_sessions.create_index([("is_active", 1)])
        print("   ✅ User Sessions indexes created")
        
        # Audit Logs collection indexes
        print("📑 Creating indexes for audit_logs...")
        await self.db.audit_logs.create_index([("timestamp", -1)])
        await self.db.audit_logs.create_index([("user_id", 1)])
        await self.db.audit_logs.create_index([("action", 1)])
        await self.db.audit_logs.create_index([("resource_type", 1)])
        await self.db.audit_logs.create_index([("resource_id", 1)])
        print("   ✅ Audit Logs indexes created")
        
        print("\n✅ All indexes created successfully!\n")
    
    async def create_users(self, count=5):
        """Create sample users"""
        print("======================================================================")
        print("  STEP 2: CREATING USERS")
        print("======================================================================\n")
        
        users = []
        roles = ["admin", "accountant", "manager", "user"]
        
        for i in range(count):
            user = {
                "username": f"user{i+1}",
                "email": f"user{i+1}@finguard.com",
                "password_hash": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIeWU9uXMO",  # hashed "password123"
                "full_name": f"User {i+1}",
                "role": roles[i % len(roles)],
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "last_login": None,
                "preferences": {
                    "theme": "light",
                    "notifications": True,
                    "language": "en"
                }
            }
            users.append(user)
        
        result = await self.db.users.insert_many(users)
        self.user_ids = [str(id) for id in result.inserted_ids]
        
        print(f"✅ Created {len(users)} users")
        for user in users:
            print(f"   - {user['email']} ({user['role']})")
        print()
        
        return self.user_ids
    
    async def create_customers(self, count=20):
        """Create sample customers"""
        print("======================================================================")
        print("  STEP 3: CREATING CUSTOMERS")
        print("======================================================================\n")
        
        customers = []
        
        for i in range(count):
            customer_id = str(uuid.uuid4())
            self.customer_ids.append(customer_id)
            
            customer = {
                "customer_id": customer_id,
                "name": f"Customer {i+1}",
                "email": f"customer{i+1}@example.com",
                "phone": f"+254{random.randint(700000000, 799999999)}",
                "status": "active",
                "address": {
                    "street": f"{random.randint(1, 999)} Main Street",
                    "city": random.choice(["Nairobi", "Mombasa", "Kisumu", "Nakuru"]),
                    "country": "Kenya"
                },
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
                "updated_at": datetime.utcnow(),
                "notes": f"Sample customer {i+1}"
            }
            customers.append(customer)
        
        await self.db.customers.insert_many(customers)
        
        print(f"✅ Created {len(customers)} customers")
        print(f"   Sample: {customers[0]['name']} ({customers[0]['email']})")
        print()
        
        return self.customer_ids
    
    async def create_products(self, count=15):
        """Create sample products"""
        print("======================================================================")
        print("  STEP 4: CREATING PRODUCTS")
        print("======================================================================\n")
        
        products = []
        categories = ["Software", "Hardware", "Services", "Consulting", "Training"]
        
        product_names = [
            "Web Development Service",
            "Mobile App Development",
            "Cloud Hosting (Monthly)",
            "Database Management",
            "API Integration",
            "UI/UX Design",
            "Technical Support",
            "Software License",
            "Server Setup",
            "Security Audit",
            "Performance Optimization",
            "Data Migration",
            "Custom Development",
            "Maintenance Package",
            "Training Session"
        ]
        
        for i in range(count):
            product_id = str(uuid.uuid4())
            self.product_ids.append(product_id)
            
            product = {
                "product_id": product_id,
                "sku": f"PRD-{1000 + i}",
                "name": product_names[i],
                "description": f"Professional {product_names[i].lower()} service",
                "category": categories[i % len(categories)],
                "unit_price": round(random.uniform(5000, 50000), 2),
                "currency": "KES",
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                "updated_at": datetime.utcnow()
            }
            products.append(product)
        
        await self.db.products.insert_many(products)
        
        print(f"✅ Created {len(products)} products")
        for i, prod in enumerate(products[:5]):
            print(f"   - {prod['name']} (KES {prod['unit_price']:,.2f})")
        print(f"   ... and {len(products) - 5} more")
        print()
        
        return self.product_ids
    
    async def create_invoices(self, count=50):
        """Create sample invoices with items"""
        print("======================================================================")
        print("  STEP 5: CREATING INVOICES AND INVOICE ITEMS")
        print("======================================================================\n")
        
        invoices = []
        invoice_items_batch = []
        
        for i in range(count):
            invoice_id = str(uuid.uuid4())
            self.invoice_ids.append(invoice_id)
            
            customer_id = random.choice(self.customer_ids)
            date_issued = datetime.utcnow() - timedelta(days=random.randint(1, 180))
            due_date = date_issued + timedelta(days=30)
            
            # Create invoice
            invoice = {
                "invoice_id": invoice_id,
                "invoice_number": f"INV-{2024000 + i}",
                "customer_id": customer_id,
                "date_issued": date_issued,
                "due_date": due_date,
                "status": random.choice(["paid", "pending", "overdue", "cancelled"]),
                "subtotal": 0,  # Will calculate
                "tax_rate": 0.16,  # 16% VAT
                "tax_amount": 0,  # Will calculate
                "total_amount": 0,  # Will calculate
                "currency": "KES",
                "notes": f"Invoice for services rendered",
                "created_at": date_issued,
                "updated_at": datetime.utcnow()
            }
            
            # Create 1-5 invoice items for this invoice
            num_items = random.randint(1, 5)
            invoice_subtotal = 0
            
            for j in range(num_items):
                product = random.choice(self.product_ids)
                quantity = random.randint(1, 10)
                
                # Get product details (simulated)
                unit_price = round(random.uniform(5000, 50000), 2)
                line_total = round(quantity * unit_price, 2)
                invoice_subtotal += line_total
                
                item = {
                    "item_id": str(uuid.uuid4()),
                    "invoice_id": invoice_id,
                    "product_id": product,
                    "description": f"Product/Service item {j+1}",
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "line_total": line_total,
                    "currency": "KES",
                    # Product snapshot for historical accuracy
                    "product_snapshot": {
                        "name": f"Product {j+1}",
                        "sku": f"PRD-{1000 + random.randint(0, 14)}"
                    }
                }
                invoice_items_batch.append(item)
            
            # Calculate invoice totals
            invoice["subtotal"] = round(invoice_subtotal, 2)
            invoice["tax_amount"] = round(invoice_subtotal * 0.16, 2)
            invoice["total_amount"] = round(invoice_subtotal * 1.16, 2)
            
            invoices.append(invoice)
        
        # Insert invoices and items
        await self.db.invoices.insert_many(invoices)
        await self.db.invoice_items.insert_many(invoice_items_batch)
        
        print(f"✅ Created {len(invoices)} invoices")
        print(f"✅ Created {len(invoice_items_batch)} invoice items")
        
        # Calculate statistics
        total_value = sum(inv["total_amount"] for inv in invoices)
        avg_items_per_invoice = len(invoice_items_batch) / len(invoices)
        
        print(f"   Total invoice value: KES {total_value:,.2f}")
        print(f"   Average items per invoice: {avg_items_per_invoice:.1f}")
        print()
        
        return self.invoice_ids
    
    async def create_payments(self):
        """Create sample payments for invoices"""
        print("======================================================================")
        print("  STEP 6: CREATING PAYMENTS")
        print("======================================================================\n")
        
        payments = []
        gateway_data_batch = []
        
        # Get all paid invoices
        paid_invoices = await self.db.invoices.find({"status": "paid"}).to_list(None)
        
        payment_methods = ["mpesa", "bank_transfer", "card", "cash"]
        
        for invoice in paid_invoices:
            payment_id = str(uuid.uuid4())
            self.payment_ids.append(payment_id)
            
            payment_method = random.choice(payment_methods)
            payment_date = invoice["date_issued"] + timedelta(days=random.randint(1, 15))
            
            payment = {
                "payment_id": payment_id,
                "invoice_id": invoice["invoice_id"],
                "customer_id": invoice["customer_id"],
                "amount": invoice["total_amount"],
                "currency": "KES",
                "payment_method": payment_method,
                "payment_date": payment_date,
                "status": "completed",
                "transaction_reference": f"TXN-{random.randint(100000, 999999)}",
                "notes": f"Payment via {payment_method}",
                "created_at": payment_date,
                "updated_at": datetime.utcnow()
            }
            payments.append(payment)
            
            # Create gateway-specific data for M-Pesa payments
            if payment_method == "mpesa":
                gateway_data = {
                    "payment_id": payment_id,
                    "gateway": "mpesa",
                    "gateway_transaction_id": f"MPM{random.randint(10000000, 99999999)}",
                    "gateway_data": {
                        "phone": f"+254{random.randint(700000000, 799999999)}",
                        "mpesa_receipt": f"QGN{random.randint(1000000, 9999999)}",
                        "result_code": "0",
                        "result_desc": "The service request is processed successfully"
                    },
                    "created_at": payment_date
                }
                gateway_data_batch.append(gateway_data)
        
        if payments:
            await self.db.payments.insert_many(payments)
        
        if gateway_data_batch:
            await self.db.payment_gateway_data.insert_many(gateway_data_batch)
        
        print(f"✅ Created {len(payments)} payments")
        print(f"✅ Created {len(gateway_data_batch)} gateway data records")
        
        # Calculate statistics
        if payments:
            total_paid = sum(p["amount"] for p in payments)
            print(f"   Total amount paid: KES {total_paid:,.2f}")
            print(f"   Payment methods: {', '.join(set(p['payment_method'] for p in payments))}")
        print()
        
        return self.payment_ids
    
    async def create_audit_log(self):
        """Create initial audit log entry"""
        print("======================================================================")
        print("  STEP 7: CREATING AUDIT LOG")
        print("======================================================================\n")
        
        audit_entry = {
            "user_id": self.user_ids[0] if self.user_ids else None,
            "action": "database.setup",
            "resource_type": "database",
            "resource_id": "financial_agent",
            "timestamp": datetime.utcnow(),
            "details": {
                "operation": "normalized_database_setup",
                "collections_created": [
                    "users", "customers", "products", "invoices",
                    "invoice_items", "payments", "payment_gateway_data",
                    "user_sessions", "audit_logs"
                ],
                "records_created": {
                    "users": len(self.user_ids),
                    "customers": len(self.customer_ids),
                    "products": len(self.product_ids),
                    "invoices": len(self.invoice_ids),
                    "payments": len(self.payment_ids)
                }
            },
            "ip_address": "127.0.0.1",
            "user_agent": "Database Setup Script"
        }
        
        await self.db.audit_logs.insert_one(audit_entry)
        
        print("✅ Created audit log entry")
        print()
    
    async def verify_setup(self):
        """Verify the database setup"""
        print("======================================================================")
        print("  STEP 8: VERIFYING DATABASE SETUP")
        print("======================================================================\n")
        
        collections = [
            "users", "customers", "products", "invoices",
            "invoice_items", "payments", "payment_gateway_data",
            "user_sessions", "audit_logs"
        ]
        
        print("📊 Collection Statistics:")
        print("-" * 70)
        
        total_docs = 0
        for collection_name in collections:
            count = await self.db[collection_name].count_documents({})
            indexes = await self.db[collection_name].index_information()
            status = "✅" if count > 0 or collection_name in ["user_sessions"] else "⚠️"
            print(f"{status} {collection_name:30} {count:6} docs, {len(indexes):2} indexes")
            total_docs += count
        
        print("-" * 70)
        print(f"Total: {total_docs} documents across {len(collections)} collections")
        print()
        
        # Verify relationships
        print("🔗 Verifying Relationships:")
        print("-" * 70)
        
        # Check invoice -> customer references
        sample_invoice = await self.db.invoices.find_one()
        if sample_invoice:
            customer = await self.db.customers.find_one({"customer_id": sample_invoice["customer_id"]})
            print(f"✅ Invoice -> Customer reference: Valid" if customer else "❌ Invoice -> Customer reference: Broken")
        
        # Check invoice_items -> invoice references
        sample_item = await self.db.invoice_items.find_one()
        if sample_item:
            invoice = await self.db.invoices.find_one({"invoice_id": sample_item["invoice_id"]})
            print(f"✅ Invoice Item -> Invoice reference: Valid" if invoice else "❌ Invoice Item -> Invoice reference: Broken")
        
        # Check payment -> invoice references
        sample_payment = await self.db.payments.find_one()
        if sample_payment:
            invoice = await self.db.invoices.find_one({"invoice_id": sample_payment["invoice_id"]})
            print(f"✅ Payment -> Invoice reference: Valid" if invoice else "❌ Payment -> Invoice reference: Broken")
        
        print("-" * 70)
        print()
    
    async def show_sample_queries(self):
        """Show sample queries demonstrating the normalized structure"""
        print("======================================================================")
        print("  SAMPLE QUERIES (Demonstrating Normalized Structure)")
        print("======================================================================\n")
        
        # Query 1: Get invoice with customer details
        print("📝 Query 1: Get invoice with customer details")
        pipeline = [
            {"$limit": 1},
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "customer_id",
                    "foreignField": "customer_id",
                    "as": "customer"
                }
            },
            {"$unwind": "$customer"}
        ]
        result = await self.db.invoices.aggregate(pipeline).to_list(1)
        if result:
            inv = result[0]
            print(f"   Invoice: {inv['invoice_number']}")
            print(f"   Customer: {inv['customer']['name']} ({inv['customer']['email']})")
            print(f"   Amount: KES {inv['total_amount']:,.2f}")
        print()
        
        # Query 2: Get invoice with all items
        print("📝 Query 2: Get invoice with all items")
        pipeline = [
            {"$limit": 1},
            {
                "$lookup": {
                    "from": "invoice_items",
                    "localField": "invoice_id",
                    "foreignField": "invoice_id",
                    "as": "items"
                }
            }
        ]
        result = await self.db.invoices.aggregate(pipeline).to_list(1)
        if result:
            inv = result[0]
            print(f"   Invoice: {inv['invoice_number']}")
            print(f"   Items: {len(inv['items'])} items")
            for item in inv['items'][:3]:
                print(f"      - {item['description']}: {item['quantity']} x KES {item['unit_price']:,.2f}")
        print()
        
        # Query 3: Customer payment history
        print("📝 Query 3: Customer payment history")
        customer = await self.db.customers.find_one()
        if customer:
            payments = await self.db.payments.find(
                {"customer_id": customer["customer_id"]}
            ).sort("payment_date", -1).to_list(5)
            
            print(f"   Customer: {customer['name']}")
            print(f"   Total Payments: {len(payments)}")
            if payments:
                total = sum(p["amount"] for p in payments)
                print(f"   Total Amount: KES {total:,.2f}")
        print()
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

async def main():
    setup = NormalizedDatabaseSetup()
    
    try:
        await setup.connect()
        
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║         NORMALIZED DATABASE SETUP FROM SCRATCH                       ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝\n")
        
        # Execute setup steps
        await setup.create_indexes()
        await setup.create_users(count=5)
        await setup.create_customers(count=20)
        await setup.create_products(count=15)
        await setup.create_invoices(count=50)
        await setup.create_payments()
        await setup.create_audit_log()
        
        # Verify and show results
        await setup.verify_setup()
        await setup.show_sample_queries()
        
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║                  ✅ DATABASE SETUP COMPLETE!                         ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝\n")
        
        print("🎉 Your normalized database is ready!")
        print("   - All collections created with proper indexes")
        print("   - Sample data generated following normalization best practices")
        print("   - Referential integrity maintained")
        print("   - Ready for your application to use\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await setup.close()

if __name__ == "__main__":
    asyncio.run(main())
