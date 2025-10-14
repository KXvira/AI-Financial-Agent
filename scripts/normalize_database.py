"""
MongoDB Database Normalization Migration Script

This script migrates the existing denormalized schema to a normalized structure
following the design in docs/MONGODB_NORMALIZATION_ANALYSIS.md

IMPORTANT: 
- Backup your database before running this script!
- Test in a development environment first!
- Run with --dry-run flag to see changes without committing

Usage:
    python scripts/normalize_database.py --dry-run  # Preview changes
    python scripts/normalize_database.py            # Execute migration
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional
from bson import ObjectId
from pymongo.errors import DuplicateKeyError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

class DatabaseNormalizer:
    """Handles database normalization migration"""
    
    def __init__(self, db, dry_run=False):
        self.db = db
        self.dry_run = dry_run
        self.stats = {
            "customers_created": 0,
            "customers_skipped": 0,
            "invoices_updated": 0,
            "invoice_items_created": 0,
            "payments_unified": 0,
            "gateway_data_created": 0,
            "errors": []
        }
        
    async def migrate_all(self):
        """Run all migration steps"""
        print("\n" + "="*70)
        print("  DATABASE NORMALIZATION MIGRATION")
        print("="*70)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes will be committed\n")
        else:
            print("\n🚀 LIVE MODE - Database will be modified\n")
            response = input("Type 'yes' to continue: ")
            if response.lower() != 'yes':
                print("Migration cancelled.")
                return False
        
        try:
            # Step 1: Create indexes for new collections
            await self.create_indexes()
            
            # Step 2: Extract and normalize customers
            await self.normalize_customers()
            
            # Step 3: Extract invoice items into separate collection
            await self.normalize_invoice_items()
            
            # Step 4: Unify payments (transactions + mpesa_payments)
            await self.normalize_payments()
            
            # Step 5: Create audit logs for existing data
            await self.create_initial_audit_logs()
            
            # Print summary
            self.print_summary()
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def create_indexes(self):
        """Create indexes for normalized collections"""
        print("\n📊 Step 1: Creating indexes...")
        
        if self.dry_run:
            print("   [DRY RUN] Would create indexes")
            return
        
        # Helper function to create index safely
        async def create_index_safe(collection, keys, **kwargs):
            try:
                await collection.create_index(keys, **kwargs)
            except Exception as e:
                if "IndexKeySpecsConflict" in str(e) or "already exists" in str(e):
                    print(f"   ℹ️  Index already exists: {keys}")
                else:
                    raise
        
        # Customer indexes
        await create_index_safe(self.db.customers, [("customer_id", 1)], unique=True)
        await create_index_safe(self.db.customers, [("email", 1)], unique=True)
        await create_index_safe(self.db.customers, [("phone", 1)])
        await create_index_safe(self.db.customers, [("status", 1)])
        
        # Invoice indexes
        await self.db.invoices.create_index([("invoice_number", 1)], unique=True)
        await self.db.invoices.create_index([("customer_id", 1), ("date_issued", -1)])
        await self.db.invoices.create_index([("status", 1), ("due_date", 1)])
        
        # Invoice items indexes
        await self.db.invoice_items.create_index([("invoice_id", 1)])
        await self.db.invoice_items.create_index([("invoice_id", 1), ("line_number", 1)])
        await self.db.invoice_items.create_index([("product_id", 1)])
        
        # Payment indexes
        await self.db.payments.create_index([("payment_id", 1)], unique=True)
        await self.db.payments.create_index([("invoice_id", 1), ("payment_date", -1)])
        await self.db.payments.create_index([("customer_id", 1), ("payment_date", -1)])
        await self.db.payments.create_index([("gateway_reference", 1), ("gateway", 1)])
        
        # Gateway data indexes
        await self.db.payment_gateway_data.create_index([("payment_id", 1)])
        
        # Audit log indexes
        await self.db.audit_logs.create_index([("user_id", 1), ("timestamp", -1)])
        await self.db.audit_logs.create_index([("resource_type", 1), ("resource_id", 1)])
        
        print("   ✅ Indexes created")
    
    async def normalize_customers(self):
        """Extract customers from invoices and create customer collection"""
        print("\n👥 Step 2: Normalizing customers...")
        
        # Track unique customers by email
        customer_map: Dict[str, ObjectId] = {}
        
        # Get all invoices with embedded customer data
        invoices = await self.db.invoices.find({"customer": {"$exists": True}}).to_list(None)
        
        print(f"   Found {len(invoices)} invoices with embedded customer data")
        
        for invoice in invoices:
            customer_data = invoice.get("customer", {})
            
            if not customer_data:
                continue
            
            email = customer_data.get("email")
            if not email:
                # Try to get email from other fields
                name = customer_data.get("name", "Unknown")
                email = f"{name.lower().replace(' ', '')}@example.com"
            
            # Check if we've already processed this customer
            if email in customer_map:
                customer_id = customer_map[email]
                self.stats["customers_skipped"] += 1
            else:
                # Check if customer already exists in database
                existing = await self.db.customers.find_one({"email": email})
                
                if existing:
                    customer_id = existing["_id"]
                    customer_map[email] = customer_id
                    self.stats["customers_skipped"] += 1
                else:
                    # Create new customer
                    customer_doc = await self._create_customer_from_invoice(customer_data, invoice)
                    
                    if not self.dry_run:
                        try:
                            result = await self.db.customers.insert_one(customer_doc)
                            customer_id = result.inserted_id
                            customer_map[email] = customer_id
                            self.stats["customers_created"] += 1
                        except DuplicateKeyError:
                            # Race condition - customer was created by another process
                            existing = await self.db.customers.find_one({"email": email})
                            customer_id = existing["_id"]
                            customer_map[email] = customer_id
                            self.stats["customers_skipped"] += 1
                    else:
                        # Dry run - use fake ObjectId
                        customer_id = ObjectId()
                        customer_map[email] = customer_id
                        self.stats["customers_created"] += 1
            
            # Update invoice with customer reference
            if not self.dry_run:
                await self.db.invoices.update_one(
                    {"_id": invoice["_id"]},
                    {
                        "$set": {"customer_id": customer_id},
                        "$unset": {"customer": ""}
                    }
                )
            
            self.stats["invoices_updated"] += 1
        
        print(f"   ✅ Created {self.stats['customers_created']} customers")
        print(f"   ✅ Updated {self.stats['invoices_updated']} invoices")
        print(f"   ℹ️  Skipped {self.stats['customers_skipped']} duplicate customers")
    
    async def _create_customer_from_invoice(self, customer_data: Dict, invoice: Dict) -> Dict:
        """Create customer document from invoice customer data"""
        
        # Generate customer_id
        last_customer = await self.db.customers.find_one(
            {},
            sort=[("customer_id", -1)]
        )
        
        if last_customer:
            last_id = int(last_customer["customer_id"].split("-")[1])
            customer_id = f"CUST-{last_id + 1:04d}"
        else:
            customer_id = "CUST-0001"
        
        # Extract address
        address = {
            "street": customer_data.get("address", ""),
            "city": customer_data.get("city", "Nairobi"),
            "postal_code": "00100",
            "country": customer_data.get("country", "Kenya")
        }
        
        return {
            "customer_id": customer_id,
            "name": customer_data.get("name", "Unknown"),
            "email": customer_data.get("email"),
            "phone": customer_data.get("phone_number", customer_data.get("phone", "")),
            "address": address,
            "business_type": "general",
            "preferred_payment_method": "mpesa",
            "payment_terms": "net_30",
            "auto_send_invoices": False,
            "send_reminders": True,
            "ai_preferences": {
                "invoice_template": "professional",
                "language": "english",
                "include_tax": True,
                "default_currency": "KES"
            },
            "status": "active",
            "notes": f"Migrated from invoice data on {datetime.now().strftime('%Y-%m-%d')}",
            "tags": [],
            "created_at": invoice.get("created_at", datetime.now()),
            "updated_at": datetime.now()
        }
    
    async def normalize_invoice_items(self):
        """Extract invoice items into separate collection"""
        print("\n🧾 Step 3: Normalizing invoice items...")
        
        # Get all invoices with embedded items
        invoices = await self.db.invoices.find({"items": {"$exists": True}}).to_list(None)
        
        print(f"   Found {len(invoices)} invoices with embedded items")
        
        for invoice in invoices:
            items = invoice.get("items", [])
            
            if not items:
                continue
            
            for idx, item in enumerate(items):
                item_doc = {
                    "invoice_id": invoice["_id"],
                    "line_number": idx + 1,
                    "description": item.get("description", ""),
                    "quantity": item.get("quantity", 1),
                    "unit_price": item.get("unit_price", 0),
                    "subtotal": item.get("amount", 0),
                    "discount_rate": item.get("discount_rate", 0),
                    "discount_amount": item.get("discount_amount", 0),
                    "tax_rate": item.get("tax_rate", 0.16),
                    "tax_amount": item.get("tax_amount", 0),
                    "total": item.get("amount", 0) + item.get("tax_amount", 0),
                    "product_snapshot": None,  # No product catalog yet
                    "created_at": invoice.get("created_at", datetime.now())
                }
                
                if not self.dry_run:
                    await self.db.invoice_items.insert_one(item_doc)
                
                self.stats["invoice_items_created"] += 1
            
            # Remove items array from invoice
            if not self.dry_run:
                await self.db.invoices.update_one(
                    {"_id": invoice["_id"]},
                    {"$unset": {"items": ""}}
                )
        
        print(f"   ✅ Created {self.stats['invoice_items_created']} invoice items")
    
    async def normalize_payments(self):
        """Unify transactions and mpesa_payments into payments collection"""
        print("\n💰 Step 4: Normalizing payments...")
        
        # Process transactions (type: payment)
        transactions = await self.db.transactions.find({"type": "payment"}).to_list(None)
        print(f"   Found {len(transactions)} payment transactions")
        
        for txn in transactions:
            payment_doc = await self._convert_transaction_to_payment(txn)
            
            if not self.dry_run:
                await self.db.payments.insert_one(payment_doc)
            
            self.stats["payments_unified"] += 1
            
            # Check for corresponding M-Pesa payment record
            mpesa_data = await self.db.mpesa_payments.find_one({
                "TransID": txn.get("reference")
            })
            
            if mpesa_data and not self.dry_run:
                # Create gateway data record
                gateway_doc = {
                    "payment_id": payment_doc["_id"],
                    "gateway": "mpesa",
                    "gateway_data": mpesa_data,
                    "raw_request": mpesa_data,
                    "created_at": mpesa_data.get("created_at", datetime.now())
                }
                await self.db.payment_gateway_data.insert_one(gateway_doc)
                self.stats["gateway_data_created"] += 1
        
        print(f"   ✅ Created {self.stats['payments_unified']} unified payment records")
        print(f"   ✅ Created {self.stats['gateway_data_created']} gateway data records")
    
    async def _convert_transaction_to_payment(self, txn: Dict) -> Dict:
        """Convert transaction record to payment record"""
        
        # Generate payment_id
        last_payment = await self.db.payments.find_one(
            {},
            sort=[("payment_id", -1)]
        )
        
        if last_payment and last_payment.get("payment_id"):
            last_id = int(last_payment["payment_id"].split("-")[-1])
            payment_id = f"PAY-{datetime.now().strftime('%Y-%m')}-{last_id + 1:04d}"
        else:
            payment_id = f"PAY-{datetime.now().strftime('%Y-%m')}-0001"
        
        # Find associated invoice
        invoice_id = None
        invoice_number = txn.get("invoice_number")
        if invoice_number:
            invoice = await self.db.invoices.find_one({"invoice_number": invoice_number})
            if invoice:
                invoice_id = invoice["_id"]
        
        # Find customer
        customer_id = None
        customer_name = txn.get("customer")
        if customer_name:
            customer = await self.db.customers.find_one({"name": customer_name})
            if customer:
                customer_id = customer["_id"]
        
        return {
            "payment_id": payment_id,
            "amount": txn.get("amount", 0),
            "currency": "KES",
            "payment_date": txn.get("date", datetime.now()),
            "gateway": txn.get("payment_method", "mpesa").lower(),
            "gateway_reference": txn.get("reference", ""),
            "customer_id": customer_id,
            "payer_name": customer_name,
            "payer_phone": txn.get("phone_number", ""),
            "payer_email": None,
            "invoice_id": invoice_id,
            "allocated_amount": txn.get("amount", 0),
            "status": txn.get("status", "completed"),
            "reconciliation_status": "matched" if invoice_id else "unmatched",
            "reconciliation_date": datetime.now() if invoice_id else None,
            "reconciliation_confidence": 0.9 if invoice_id else None,
            "reconciliation_method": "automatic" if invoice_id else None,
            "created_at": txn.get("created_at", datetime.now()),
            "updated_at": datetime.now()
        }
    
    async def create_initial_audit_logs(self):
        """Create audit logs for migration"""
        print("\n📝 Step 5: Creating migration audit logs...")
        
        if self.dry_run:
            print("   [DRY RUN] Would create audit log")
            return
        
        audit_doc = {
            "user_id": None,  # System action
            "action": "database.migration",
            "resource_type": "database",
            "resource_id": None,
            "changes": {
                "migration": "normalization",
                "stats": self.stats
            },
            "ip_address": "127.0.0.1",
            "user_agent": "Migration Script",
            "timestamp": datetime.now(),
            "success": True
        }
        
        await self.db.audit_logs.insert_one(audit_doc)
        print("   ✅ Audit log created")
    
    def print_summary(self):
        """Print migration summary"""
        print("\n" + "="*70)
        print("  MIGRATION SUMMARY")
        print("="*70)
        print(f"\n✅ Customers created: {self.stats['customers_created']}")
        print(f"ℹ️  Customers skipped (duplicates): {self.stats['customers_skipped']}")
        print(f"✅ Invoices updated: {self.stats['invoices_updated']}")
        print(f"✅ Invoice items created: {self.stats['invoice_items_created']}")
        print(f"✅ Payments unified: {self.stats['payments_unified']}")
        print(f"✅ Gateway data records: {self.stats['gateway_data_created']}")
        
        if self.stats['errors']:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:10]:  # Show first 10
                print(f"   - {error}")
        
        print("\n" + "="*70)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN COMPLETE - No changes were made to the database")
        else:
            print("\n✅ MIGRATION COMPLETE!")
            print("\n💡 Next steps:")
            print("   1. Verify data integrity with scripts/verify_normalization.py")
            print("   2. Update application code to use new schema")
            print("   3. Test thoroughly in development environment")
            print("   4. Consider removing old denormalized fields after verification")


async def main():
    """Main migration function"""
    parser = argparse.ArgumentParser(description="Normalize MongoDB database schema")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying database"
    )
    args = parser.parse_args()
    
    # Connect to MongoDB
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.environ.get("MONGO_DB", "financial_agent")
    
    print(f"\n📡 Connecting to MongoDB: {mongo_uri[:50]}...")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]
    
    # Test connection
    try:
        await db.command("ping")
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return 1
    
    # Run migration
    normalizer = DatabaseNormalizer(db, dry_run=args.dry_run)
    success = await normalizer.migrate_all()
    
    # Close connection
    client.close()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
