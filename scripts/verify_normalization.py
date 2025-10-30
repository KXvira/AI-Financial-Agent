"""
Database Normalization Verification Script

Verifies the integrity and correctness of the normalized database schema
after running the migration script.

Usage:
    python scripts/verify_normalization.py
"""

import sys
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from bson import ObjectId

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment
load_dotenv()


class NormalizationVerifier:
    """Verifies normalized database structure"""
    
    def __init__(self, db):
        self.db = db
        self.issues = []
        self.warnings = []
        self.stats = {}
    
    async def verify_all(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("  DATABASE NORMALIZATION VERIFICATION")
        print("="*70 + "\n")
        
        try:
            # Collect statistics
            await self.collect_statistics()
            
            # Check 1: Verify all invoices have customer references
            await self.verify_invoice_customer_references()
            
            # Check 2: Verify no orphaned invoice items
            await self.verify_invoice_items()
            
            # Check 3: Verify payment references
            await self.verify_payment_references()
            
            # Check 4: Check for remaining embedded data
            await self.check_embedded_data()
            
            # Check 5: Verify indexes
            await self.verify_indexes()
            
            # Check 6: Data consistency checks
            await self.verify_data_consistency()
            
            # Print results
            self.print_results()
            
            return len(self.issues) == 0
            
        except Exception as e:
            print(f"\n❌ Verification failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def collect_statistics(self):
        """Collect collection statistics"""
        print("📊 Collecting statistics...\n")
        
        self.stats = {
            "users": await self.db.users.count_documents({}),
            "customers": await self.db.customers.count_documents({}),
            "invoices": await self.db.invoices.count_documents({}),
            "invoice_items": await self.db.invoice_items.count_documents({}),
            "payments": await self.db.payments.count_documents({}),
            "payment_gateway_data": await self.db.payment_gateway_data.count_documents({}),
            "transactions": await self.db.transactions.count_documents({}),
            "mpesa_payments": await self.db.mpesa_payments.count_documents({}),
            "receipts": await self.db.receipts.count_documents({}),
            "ocr_results": await self.db.ocr_results.count_documents({}),
            "audit_logs": await self.db.audit_logs.count_documents({})
        }
        
        print("Collection counts:")
        for collection, count in self.stats.items():
            print(f"   {collection:30s}: {count:,}")
        print()
    
    async def verify_invoice_customer_references(self):
        """Check that all invoices have valid customer references"""
        print("✓ Checking invoice-customer references...")
        
        # Check for invoices without customer_id
        invoices_no_ref = await self.db.invoices.count_documents({
            "customer_id": {"$exists": False}
        })
        
        if invoices_no_ref > 0:
            self.issues.append(
                f"Found {invoices_no_ref} invoices without customer_id reference"
            )
        
        # Check for invoices with embedded customer data (not migrated)
        invoices_with_embedded = await self.db.invoices.count_documents({
            "customer": {"$exists": True}
        })
        
        if invoices_with_embedded > 0:
            self.issues.append(
                f"Found {invoices_with_embedded} invoices still with embedded customer data"
            )
        
        # Check for invalid customer references
        pipeline = [
            {
                "$match": {
                    "customer_id": {"$exists": True}
                }
            },
            {
                "$lookup": {
                    "from": "customers",
                    "localField": "customer_id",
                    "foreignField": "_id",
                    "as": "customer"
                }
            },
            {
                "$match": {
                    "customer": {"$size": 0}
                }
            },
            {
                "$count": "orphaned"
            }
        ]
        
        result = await self.db.invoices.aggregate(pipeline).to_list(1)
        orphaned_count = result[0]["orphaned"] if result else 0
        
        if orphaned_count > 0:
            self.issues.append(
                f"Found {orphaned_count} invoices with invalid customer_id references"
            )
        else:
            print("   ✅ All invoices have valid customer references")
    
    async def verify_invoice_items(self):
        """Check invoice items integrity"""
        print("✓ Checking invoice items...")
        
        # Check for orphaned invoice items
        pipeline = [
            {
                "$lookup": {
                    "from": "invoices",
                    "localField": "invoice_id",
                    "foreignField": "_id",
                    "as": "invoice"
                }
            },
            {
                "$match": {
                    "invoice": {"$size": 0}
                }
            },
            {
                "$count": "orphaned"
            }
        ]
        
        result = await self.db.invoice_items.aggregate(pipeline).to_list(1)
        orphaned_count = result[0]["orphaned"] if result else 0
        
        if orphaned_count > 0:
            self.issues.append(
                f"Found {orphaned_count} orphaned invoice items (no matching invoice)"
            )
        
        # Check for invoices still with embedded items
        invoices_with_items = await self.db.invoices.count_documents({
            "items": {"$exists": True}
        })
        
        if invoices_with_items > 0:
            self.warnings.append(
                f"Found {invoices_with_items} invoices still with embedded items array"
            )
        
        # Check invoice item totals match invoice totals
        sample_invoices = await self.db.invoices.find({}).limit(100).to_list(100)
        
        mismatches = 0
        for invoice in sample_invoices:
            invoice_total = invoice.get("total", 0)
            
            # Sum invoice items
            items = await self.db.invoice_items.find({
                "invoice_id": invoice["_id"]
            }).to_list(None)
            
            items_total = sum(item.get("total", 0) for item in items)
            
            # Allow small rounding differences
            if abs(invoice_total - items_total) > 0.01:
                mismatches += 1
        
        if mismatches > 0:
            self.warnings.append(
                f"Found {mismatches} invoices with total mismatch (out of 100 sampled)"
            )
        else:
            print("   ✅ Invoice items correctly normalized")
    
    async def verify_payment_references(self):
        """Check payment references"""
        print("✓ Checking payment references...")
        
        # Check for payments with invalid invoice references
        pipeline = [
            {
                "$match": {
                    "invoice_id": {"$exists": True, "$ne": None}
                }
            },
            {
                "$lookup": {
                    "from": "invoices",
                    "localField": "invoice_id",
                    "foreignField": "_id",
                    "as": "invoice"
                }
            },
            {
                "$match": {
                    "invoice": {"$size": 0}
                }
            },
            {
                "$count": "invalid"
            }
        ]
        
        result = await self.db.payments.aggregate(pipeline).to_list(1)
        invalid_count = result[0]["invalid"] if result else 0
        
        if invalid_count > 0:
            self.issues.append(
                f"Found {invalid_count} payments with invalid invoice_id references"
            )
        
        # Check for payments with invalid customer references
        pipeline[0]["$match"] = {"customer_id": {"$exists": True, "$ne": None}}
        pipeline[1]["$lookup"]["from"] = "customers"
        pipeline[1]["$lookup"]["localField"] = "customer_id"
        
        result = await self.db.payments.aggregate(pipeline).to_list(1)
        invalid_customer_count = result[0]["invalid"] if result else 0
        
        if invalid_customer_count > 0:
            self.issues.append(
                f"Found {invalid_customer_count} payments with invalid customer_id references"
            )
        else:
            print("   ✅ Payment references are valid")
    
    async def check_embedded_data(self):
        """Check for remaining embedded/denormalized data"""
        print("✓ Checking for embedded data...")
        
        checks = [
            ("invoices", "customer", "embedded customer data"),
            ("invoices", "items", "embedded items array"),
            ("transactions", "gateway_data", "embedded gateway data"),
        ]
        
        remaining = []
        for collection, field, description in checks:
            count = await self.db[collection].count_documents({
                field: {"$exists": True}
            })
            if count > 0:
                remaining.append(f"{count} {collection} with {description}")
        
        if remaining:
            self.warnings.append(
                "Remaining denormalized data:\n      " + "\n      ".join(remaining)
            )
        else:
            print("   ✅ No embedded data found")
    
    async def verify_indexes(self):
        """Verify required indexes exist"""
        print("✓ Checking indexes...")
        
        required_indexes = {
            "customers": ["customer_id", "email"],
            "invoices": ["invoice_number", "customer_id"],
            "invoice_items": ["invoice_id"],
            "payments": ["payment_id", "invoice_id", "customer_id"]
        }
        
        missing_indexes = []
        
        for collection, index_fields in required_indexes.items():
            indexes = await self.db[collection].index_information()
            index_keys = []
            
            for index_info in indexes.values():
                keys = index_info.get("key", [])
                for key, _ in keys:
                    index_keys.append(key)
            
            for field in index_fields:
                if field not in index_keys:
                    missing_indexes.append(f"{collection}.{field}")
        
        if missing_indexes:
            self.warnings.append(
                f"Missing indexes: {', '.join(missing_indexes)}"
            )
        else:
            print("   ✅ All required indexes exist")
    
    async def verify_data_consistency(self):
        """Verify data consistency between collections"""
        print("✓ Checking data consistency...")
        
        # Check customer invoice counts
        customers = await self.db.customers.find({}).limit(50).to_list(50)
        
        for customer in customers:
            # Count invoices
            invoice_count = await self.db.invoices.count_documents({
                "customer_id": customer["_id"]
            })
            
            # Calculate totals
            pipeline = [
                {"$match": {"customer_id": customer["_id"]}},
                {
                    "$group": {
                        "_id": None,
                        "total_billed": {"$sum": "$total"},
                        "total_paid": {"$sum": "$amount_paid"},
                        "outstanding": {"$sum": "$balance"}
                    }
                }
            ]
            
            result = await self.db.invoices.aggregate(pipeline).to_list(1)
            
            if result:
                stats = result[0]
                # Check if customer has denormalized fields that don't match
                if customer.get("total_invoices") and customer["total_invoices"] != invoice_count:
                    self.warnings.append(
                        f"Customer {customer['customer_id']} has mismatched invoice count"
                    )
        
        print("   ✅ Data consistency check complete")
    
    def print_results(self):
        """Print verification results"""
        print("\n" + "="*70)
        print("  VERIFICATION RESULTS")
        print("="*70)
        
        if not self.issues and not self.warnings:
            print("\n✅ All checks passed! Database normalization is successful.")
        else:
            if self.issues:
                print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
                for i, issue in enumerate(self.issues, 1):
                    print(f"   {i}. {issue}")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
        
        print("\n" + "="*70)
        
        if self.issues:
            print("\n⚠️  Please review and fix critical issues before proceeding.")
        else:
            print("\n✅ Database normalization verified successfully!")


async def main():
    """Main verification function"""
    
    # Connect to MongoDB
    mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    database_name = os.environ.get("MONGO_DB", "financial_agent")
    
    print(f"\n📡 Connecting to MongoDB: {mongo_uri[:50]}...")
    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]
    
    # Test connection
    try:
        await db.command("ping")
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return 1
    
    # Run verification
    verifier = NormalizationVerifier(db)
    success = await verifier.verify_all()
    
    # Close connection
    client.close()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
