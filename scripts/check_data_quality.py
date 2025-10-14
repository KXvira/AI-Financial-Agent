"""
Pre-Migration Data Quality Check Script

Identifies data quality issues that should be fixed before running
the normalization migration.

Usage:
    python scripts/check_data_quality.py
    python scripts/check_data_quality.py --fix  # Attempt auto-fixes
"""

import sys
import os
import asyncio
import argparse
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()


class DataQualityChecker:
    """Checks data quality before normalization"""
    
    def __init__(self, db, auto_fix=False):
        self.db = db
        self.auto_fix = auto_fix
        self.issues = []
        self.fixed = []
        self.warnings = []
    
    async def check_all(self):
        """Run all data quality checks"""
        print("\n" + "="*70)
        print("  PRE-MIGRATION DATA QUALITY CHECK")
        print("="*70 + "\n")
        
        if self.auto_fix:
            print("⚠️  AUTO-FIX MODE ENABLED\n")
        
        try:
            await self.check_duplicate_customers()
            await self.check_missing_customer_data()
            await self.check_invalid_invoice_totals()
            await self.check_orphaned_transactions()
            await self.check_missing_invoice_numbers()
            await self.check_date_consistency()
            await self.check_duplicate_emails()
            
            self.print_summary()
            
            return len(self.issues) == 0
            
        except Exception as e:
            print(f"\n❌ Check failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    async def check_duplicate_customers(self):
        """Find invoices with same email but different customer names"""
        print("🔍 Checking for duplicate customers...")
        
        pipeline = [
            {
                "$match": {
                    "customer.email": {"$exists": True, "$ne": ""}
                }
            },
            {
                "$group": {
                    "_id": "$customer.email",
                    "names": {"$addToSet": "$customer.name"},
                    "count": {"$sum": 1}
                }
            },
            {
                "$match": {
                    "$expr": {"$gt": [{"$size": "$names"}, 1]}
                }
            }
        ]
        
        duplicates = await self.db.invoices.aggregate(pipeline).to_list(None)
        
        if duplicates:
            for dup in duplicates:
                self.issues.append(
                    f"Email '{dup['_id']}' used by multiple customers: {dup['names']}"
                )
            
            print(f"   ⚠️  Found {len(duplicates)} duplicate customer emails")
            print("   💡 Manual review required to merge customers")
        else:
            print("   ✅ No duplicate customer emails found")
    
    async def check_missing_customer_data(self):
        """Check for invoices with incomplete customer data"""
        print("🔍 Checking for missing customer data...")
        
        missing_name = await self.db.invoices.count_documents({
            "$or": [
                {"customer.name": {"$exists": False}},
                {"customer.name": ""},
                {"customer.name": None}
            ]
        })
        
        missing_email = await self.db.invoices.count_documents({
            "$or": [
                {"customer.email": {"$exists": False}},
                {"customer.email": ""},
                {"customer.email": None}
            ]
        })
        
        missing_phone = await self.db.invoices.count_documents({
            "$or": [
                {"customer.phone_number": {"$exists": False}},
                {"customer.phone_number": ""},
                {"customer.phone": {"$exists": False}},
                {"customer.phone": ""}
            ]
        })
        
        if missing_name > 0:
            self.issues.append(f"{missing_name} invoices with missing customer name")
        
        if missing_email > 0:
            self.warnings.append(f"{missing_email} invoices with missing customer email")
            
            if self.auto_fix:
                # Generate emails based on name
                invoices = await self.db.invoices.find({
                    "$or": [
                        {"customer.email": {"$exists": False}},
                        {"customer.email": ""}
                    ]
                }).limit(100).to_list(100)
                
                for invoice in invoices:
                    name = invoice.get("customer", {}).get("name", "unknown")
                    email = f"{name.lower().replace(' ', '').replace('ltd', '')}@example.com"
                    
                    await self.db.invoices.update_one(
                        {"_id": invoice["_id"]},
                        {"$set": {"customer.email": email}}
                    )
                    self.fixed.append(f"Generated email for invoice {invoice.get('invoice_number')}")
        
        if missing_phone > 0:
            self.warnings.append(f"{missing_phone} invoices with missing customer phone")
        
        if missing_name == 0 and missing_email == 0:
            print("   ✅ All invoices have customer name and email")
        else:
            print(f"   ⚠️  Found invoices with missing customer data")
    
    async def check_invalid_invoice_totals(self):
        """Check for invoices where item totals don't match invoice total"""
        print("🔍 Checking invoice totals...")
        
        invoices = await self.db.invoices.find({
            "items": {"$exists": True, "$ne": []}
        }).limit(200).to_list(200)
        
        mismatches = []
        
        for invoice in invoices:
            invoice_total = invoice.get("total", 0)
            items = invoice.get("items", [])
            
            items_total = sum(item.get("amount", 0) for item in items)
            
            # Check if we need to add tax
            if invoice.get("tax", 0) > 0:
                items_total += invoice.get("tax", 0)
            elif invoice.get("tax_total", 0) > 0:
                items_total += invoice.get("tax_total", 0)
            
            # Allow small rounding differences
            if abs(invoice_total - items_total) > 0.02:
                mismatches.append({
                    "invoice_number": invoice.get("invoice_number"),
                    "invoice_total": invoice_total,
                    "items_total": items_total,
                    "difference": invoice_total - items_total
                })
        
        if mismatches:
            for mismatch in mismatches[:5]:  # Show first 5
                self.warnings.append(
                    f"Invoice {mismatch['invoice_number']}: "
                    f"total={mismatch['invoice_total']}, "
                    f"items={mismatch['items_total']}, "
                    f"diff={mismatch['difference']:.2f}"
                )
            
            print(f"   ⚠️  Found {len(mismatches)} invoices with total mismatches")
            
            if self.auto_fix:
                print("   🔧 Recalculating invoice totals...")
                for mismatch in mismatches:
                    invoice = await self.db.invoices.find_one({
                        "invoice_number": mismatch["invoice_number"]
                    })
                    
                    if invoice:
                        items = invoice.get("items", [])
                        correct_total = sum(item.get("amount", 0) for item in items)
                        
                        if invoice.get("tax", 0) > 0:
                            correct_total += invoice.get("tax", 0)
                        
                        await self.db.invoices.update_one(
                            {"_id": invoice["_id"]},
                            {"$set": {"total": correct_total}}
                        )
                        
                        self.fixed.append(
                            f"Fixed total for invoice {mismatch['invoice_number']}"
                        )
        else:
            print("   ✅ All invoice totals match item totals")
    
    async def check_orphaned_transactions(self):
        """Check for transactions without matching invoices"""
        print("🔍 Checking for orphaned transactions...")
        
        transactions = await self.db.transactions.find({
            "invoice_number": {"$exists": True, "$ne": None}
        }).limit(100).to_list(100)
        
        orphaned = []
        
        for txn in transactions:
            invoice_number = txn.get("invoice_number")
            invoice = await self.db.invoices.find_one({
                "invoice_number": invoice_number
            })
            
            if not invoice:
                orphaned.append(invoice_number)
        
        if orphaned:
            self.warnings.append(
                f"Found {len(orphaned)} transactions referencing non-existent invoices"
            )
            print(f"   ⚠️  Found {len(orphaned)} orphaned transactions")
        else:
            print("   ✅ All transactions reference valid invoices")
    
    async def check_missing_invoice_numbers(self):
        """Check for invoices without invoice numbers"""
        print("🔍 Checking for missing invoice numbers...")
        
        missing = await self.db.invoices.count_documents({
            "$or": [
                {"invoice_number": {"$exists": False}},
                {"invoice_number": ""},
                {"invoice_number": None}
            ]
        })
        
        if missing > 0:
            self.issues.append(f"{missing} invoices without invoice numbers")
            print(f"   ❌ Found {missing} invoices without invoice numbers")
            
            if self.auto_fix:
                print("   🔧 Generating invoice numbers...")
                
                invoices = await self.db.invoices.find({
                    "$or": [
                        {"invoice_number": {"$exists": False}},
                        {"invoice_number": ""}
                    ]
                }).to_list(None)
                
                for idx, invoice in enumerate(invoices, 1):
                    date = invoice.get("date_issued", datetime.now())
                    if isinstance(date, str):
                        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    
                    invoice_number = f"INV-{date.year}-{date.month:02d}-{idx:04d}"
                    
                    await self.db.invoices.update_one(
                        {"_id": invoice["_id"]},
                        {"$set": {"invoice_number": invoice_number}}
                    )
                    
                    self.fixed.append(f"Generated invoice number: {invoice_number}")
        else:
            print("   ✅ All invoices have invoice numbers")
    
    async def check_date_consistency(self):
        """Check for date inconsistencies"""
        print("🔍 Checking date consistency...")
        
        # Find invoices where due_date < date_issued
        pipeline = [
            {
                "$match": {
                    "date_issued": {"$exists": True},
                    "due_date": {"$exists": True}
                }
            },
            {
                "$project": {
                    "invoice_number": 1,
                    "date_issued": 1,
                    "due_date": 1,
                    "invalid": {
                        "$lt": ["$due_date", "$date_issued"]
                    }
                }
            },
            {
                "$match": {"invalid": True}
            }
        ]
        
        invalid_dates = await self.db.invoices.aggregate(pipeline).to_list(None)
        
        if invalid_dates:
            self.warnings.append(
                f"Found {len(invalid_dates)} invoices where due_date < date_issued"
            )
            print(f"   ⚠️  Found {len(invalid_dates)} invoices with invalid dates")
        else:
            print("   ✅ All invoice dates are consistent")
    
    async def check_duplicate_emails(self):
        """Check for duplicate customer emails across customers collection"""
        print("🔍 Checking for duplicate emails in customers...")
        
        customer_count = await self.db.customers.count_documents({})
        
        if customer_count == 0:
            print("   ℹ️  No customers collection found (will be created during migration)")
            return
        
        pipeline = [
            {
                "$group": {
                    "_id": "$email",
                    "count": {"$sum": 1},
                    "ids": {"$push": "$_id"}
                }
            },
            {
                "$match": {"count": {"$gt": 1}}
            }
        ]
        
        duplicates = await self.db.customers.aggregate(pipeline).to_list(None)
        
        if duplicates:
            for dup in duplicates:
                self.issues.append(
                    f"Email '{dup['_id']}' used by {dup['count']} customers"
                )
            
            print(f"   ❌ Found {len(duplicates)} duplicate emails in customers")
            print("   💡 Manual review required to merge customers")
        else:
            print("   ✅ No duplicate emails in customers collection")
    
    def print_summary(self):
        """Print summary of issues found"""
        print("\n" + "="*70)
        print("  DATA QUALITY CHECK SUMMARY")
        print("="*70)
        
        if not self.issues and not self.warnings:
            print("\n✅ No data quality issues found!")
            print("   Your database is ready for normalization.")
        else:
            if self.issues:
                print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
                for i, issue in enumerate(self.issues, 1):
                    print(f"   {i}. {issue}")
                print("\n   ⚠️  Fix these issues before running migration!")
            
            if self.warnings:
                print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
                for i, warning in enumerate(self.warnings, 1):
                    print(f"   {i}. {warning}")
                print("\n   ℹ️  These can be fixed during or after migration.")
            
            if self.fixed:
                print(f"\n✅ AUTO-FIXES APPLIED ({len(self.fixed)}):")
                for i, fix in enumerate(self.fixed, 1):
                    print(f"   {i}. {fix}")
        
        print("\n" + "="*70)
        
        if self.issues:
            print("\n💡 Recommended actions:")
            print("   1. Fix critical issues manually or with --fix flag")
            print("   2. Re-run this check to verify fixes")
            print("   3. Proceed with migration when all clear")
        else:
            print("\n✅ Ready for migration!")
            print("   Next step: python scripts/normalize_database.py --dry-run")


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Check data quality before normalization")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix issues where possible"
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
        print("✅ Connected to MongoDB\n")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return 1
    
    # Run checks
    checker = DataQualityChecker(db, auto_fix=args.fix)
    success = await checker.check_all()
    
    # Close connection
    client.close()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
