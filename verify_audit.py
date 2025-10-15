#!/usr/bin/env python3
"""
Comprehensive Post-Migration Audit Verification Script
Tests all backend endpoints, database schema, and integration points
"""

import asyncio
import sys
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict

import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AuditVerifier:
    """Main audit verification class"""
    
    def __init__(self, base_url: str = "http://localhost:8000", mongo_uri: str = None):
        self.base_url = base_url
        self.mongo_uri = mongo_uri or "mongodb+srv://alfredmunga254:mongodbkenya10@financialagent.ryjz7.mongodb.net/?retryWrites=true&w=majority&appName=FinancialAgent"
        self.client = None
        self.db = None
        self.token = None
        self.results = defaultdict(list)
        self.stats = {
            "total": 0,
            "passed": 0,
            "warnings": 0,
            "failed": 0
        }
    
    async def setup(self):
        """Initialize database connection and test user"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client['FinancialAgent']
            await self.db.command('ping')
            self.log_success("Database connection established")
        except Exception as e:
            self.log_error(f"Database connection failed: {e}")
            raise
    
    async def cleanup(self):
        """Close connections"""
        if self.client:
            self.client.close()
    
    def log_success(self, message: str):
        """Log success message"""
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        self.results["passed"].append(message)
        self.stats["passed"] += 1
        self.stats["total"] += 1
    
    def log_warning(self, message: str):
        """Log warning message"""
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        self.results["warnings"].append(message)
        self.stats["warnings"] += 1
        self.stats["total"] += 1
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        self.results["failed"].append(message)
        self.stats["failed"] += 1
        self.stats["total"] += 1
    
    def log_info(self, message: str):
        """Log info message"""
        print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")
    
    def log_header(self, message: str):
        """Log section header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"  {message}")
        print(f"{'='*70}{Colors.ENDC}\n")
    
    async def test_database_collections(self):
        """Test all MongoDB collections exist and have correct structure"""
        self.log_header("Phase 1: Database Schema Verification")
        
        expected_collections = {
            "users": 8,
            "customers": 100,
            "products": 31,
            "invoices": 2370,
            "invoice_items": 9231,
            "payments": 1957,
            "payment_gateway_data": 1369,
            "receipts": 1565,
            "transactions": 383,
            "ai_matching_results": 1957,
            "audit_logs": None  # Variable count
        }
        
        for collection_name, expected_count in expected_collections.items():
            try:
                collection = self.db[collection_name]
                actual_count = await collection.count_documents({})
                
                if expected_count is None:
                    self.log_success(f"Collection '{collection_name}' exists with {actual_count} documents")
                elif actual_count >= expected_count * 0.9:  # Allow 10% variance
                    self.log_success(f"Collection '{collection_name}' has {actual_count} documents (expected ~{expected_count})")
                else:
                    self.log_warning(f"Collection '{collection_name}' has {actual_count} documents (expected {expected_count})")
                
            except Exception as e:
                self.log_error(f"Collection '{collection_name}' check failed: {e}")
    
    async def test_database_indexes(self):
        """Verify database indexes are properly created"""
        self.log_header("Phase 2: Database Index Verification")
        
        index_checks = {
            "invoices": ["customer_id_1", "invoice_id_1"],
            "invoice_items": ["invoice_id_1", "item_id_1"],
            "payments": ["invoice_id_1", "payment_id_1"],
            "customers": ["customer_id_1", "email_1"],
            "users": ["email_1"]
        }
        
        for collection_name, expected_indexes in index_checks.items():
            try:
                collection = self.db[collection_name]
                indexes = await collection.index_information()
                index_names = list(indexes.keys())
                
                missing = []
                for expected in expected_indexes:
                    if not any(expected in idx_name for idx_name in index_names):
                        missing.append(expected)
                
                if not missing:
                    self.log_success(f"Collection '{collection_name}' has all required indexes")
                else:
                    self.log_warning(f"Collection '{collection_name}' missing indexes: {missing}")
                    
            except Exception as e:
                self.log_error(f"Index check for '{collection_name}' failed: {e}")
    
    async def test_normalized_schema(self):
        """Test normalized schema relationships"""
        self.log_header("Phase 3: Normalized Schema Relationships")
        
        # Test invoice -> invoice_items relationship
        try:
            sample_invoice = await self.db.invoices.find_one({})
            if sample_invoice:
                invoice_id = sample_invoice.get("invoice_id")
                items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
                
                if items:
                    total = sum(item.get("line_total", 0) for item in items)
                    self.log_success(f"Invoice-Items relationship working: {len(items)} items, total: KES {total:,.2f}")
                else:
                    self.log_warning(f"No items found for invoice {invoice_id}")
            else:
                self.log_warning("No sample invoice found")
        except Exception as e:
            self.log_error(f"Invoice-Items relationship test failed: {e}")
        
        # Test invoice -> customer relationship
        try:
            sample_invoice = await self.db.invoices.find_one({})
            if sample_invoice:
                customer_id = sample_invoice.get("customer_id")
                customer = await self.db.customers.find_one({"customer_id": customer_id})
                
                if customer:
                    self.log_success(f"Invoice-Customer relationship working: {customer.get('name')}")
                else:
                    self.log_warning(f"Customer {customer_id} not found for invoice")
        except Exception as e:
            self.log_error(f"Invoice-Customer relationship test failed: {e}")
        
        # Test payment -> invoice relationship
        try:
            sample_payment = await self.db.payments.find_one({"invoice_id": {"$exists": True}})
            if sample_payment:
                invoice_id = sample_payment.get("invoice_id")
                invoice = await self.db.invoices.find_one({"invoice_id": invoice_id})
                
                if invoice:
                    self.log_success(f"Payment-Invoice relationship working")
                else:
                    self.log_warning(f"Invoice {invoice_id} not found for payment")
        except Exception as e:
            self.log_error(f"Payment-Invoice relationship test failed: {e}")
    
    async def test_authentication_endpoints(self):
        """Test authentication endpoints"""
        self.log_header("Phase 4: Authentication Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test registration (use unique email)
            try:
                timestamp = int(time.time())
                register_data = {
                    "email": f"audit_test_{timestamp}@example.com",
                    "password": "SecurePass123!",
                    "full_name": "Audit Test User"
                }
                
                response = await client.post(f"{self.base_url}/api/auth/register", json=register_data)
                
                if response.status_code in [200, 201, 409]:  # 409 if user exists
                    self.log_success("POST /api/auth/register - Working")
                else:
                    self.log_warning(f"POST /api/auth/register - Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"POST /api/auth/register failed: {e}")
            
            # Test login with existing user
            try:
                login_data = {
                    "email": "admin@finagent.com",
                    "password": "admin123"
                }
                
                response = await client.post(f"{self.base_url}/api/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.token = data["access_token"]
                        self.log_success("POST /api/auth/login - Working (token obtained)")
                    else:
                        self.log_warning("POST /api/auth/login - No token in response")
                else:
                    self.log_warning(f"POST /api/auth/login - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"POST /api/auth/login failed: {e}")
            
            # Test protected endpoint
            if self.token:
                try:
                    headers = {"Authorization": f"Bearer {self.token}"}
                    response = await client.get(f"{self.base_url}/api/auth/me", headers=headers)
                    
                    if response.status_code == 200:
                        self.log_success("GET /api/auth/me - Working (authentication verified)")
                    else:
                        self.log_warning(f"GET /api/auth/me - Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"GET /api/auth/me failed: {e}")
    
    async def test_dashboard_endpoints(self):
        """Test dashboard and reporting endpoints"""
        self.log_header("Phase 5: Dashboard & Reports Endpoints")
        
        if not self.token:
            self.log_warning("Skipping dashboard tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                ("GET", "/api/dashboard/stats", "Dashboard Statistics"),
                ("GET", "/reports/types", "Report Types"),
                ("GET", "/reports/income-statement?start_date=2024-01-01&end_date=2024-12-31", "Income Statement"),
                ("GET", "/reports/cash-flow?start_date=2024-01-01&end_date=2024-12-31", "Cash Flow"),
                ("GET", "/reports/ar-aging", "AR Aging"),
                ("GET", "/reports/dashboard-metrics", "Dashboard Metrics"),
                ("GET", "/reports/tax/vat-summary?start_date=2024-01-01&end_date=2024-12-31", "VAT Summary"),
            ]
            
            for method, endpoint, name in endpoints:
                try:
                    response = await client.request(method, f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Verify response has data
                        if data and len(str(data)) > 10:
                            self.log_success(f"{method} {endpoint} - Working ({len(str(data))} bytes)")
                        else:
                            self.log_warning(f"{method} {endpoint} - Empty response")
                    elif response.status_code == 401:
                        self.log_warning(f"{method} {endpoint} - Authentication failed")
                    else:
                        self.log_warning(f"{method} {endpoint} - Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"{method} {endpoint} failed: {e}")
    
    async def test_invoice_endpoints(self):
        """Test invoice-related endpoints"""
        self.log_header("Phase 6: Invoice Management Endpoints")
        
        if not self.token:
            self.log_warning("Skipping invoice tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test list invoices
            try:
                response = await client.get(
                    f"{self.base_url}/api/invoices?page=1&page_size=10",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "invoices" in data or isinstance(data, list):
                        self.log_success("GET /api/invoices - Working (list retrieved)")
                    else:
                        self.log_warning("GET /api/invoices - Unexpected response format")
                else:
                    self.log_warning(f"GET /api/invoices - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"GET /api/invoices failed: {e}")
            
            # Test get single invoice
            try:
                # Get a sample invoice ID from database
                sample_invoice = await self.db.invoices.find_one({})
                if sample_invoice:
                    invoice_id = str(sample_invoice.get("_id"))
                    response = await client.get(
                        f"{self.base_url}/api/invoices/{invoice_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        self.log_success(f"GET /api/invoices/{{id}} - Working")
                    elif response.status_code == 404:
                        self.log_warning(f"GET /api/invoices/{{id}} - Invoice not found")
                    else:
                        self.log_warning(f"GET /api/invoices/{{id}} - Status: {response.status_code}")
                        
            except Exception as e:
                self.log_error(f"GET /api/invoices/{{id}} failed: {e}")
    
    async def test_payment_endpoints(self):
        """Test payment-related endpoints"""
        self.log_header("Phase 7: Payment Management Endpoints")
        
        if not self.token:
            self.log_warning("Skipping payment tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                ("GET", "/api/payments?page=1&page_size=10", "Payment List"),
                ("GET", "/api/payments/stats/summary", "Payment Statistics"),
            ]
            
            for method, endpoint, name in endpoints:
                try:
                    response = await client.request(method, f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            self.log_success(f"{method} {endpoint} - Working")
                        else:
                            self.log_warning(f"{method} {endpoint} - Empty response")
                    else:
                        self.log_warning(f"{method} {endpoint} - Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"{method} {endpoint} failed: {e}")
    
    async def test_receipt_endpoints(self):
        """Test OCR/receipt endpoints"""
        self.log_header("Phase 8: OCR/Receipt Endpoints")
        
        if not self.token:
            self.log_warning("Skipping receipt tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                ("GET", "/receipts/?page=1&page_size=10", "Receipt List"),
                ("GET", "/receipts/statistics/summary", "Receipt Statistics"),
                ("GET", "/api/ocr/health", "OCR Health Check"),
            ]
            
            for method, endpoint, name in endpoints:
                try:
                    response = await client.request(method, f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        self.log_success(f"{method} {endpoint} - Working")
                    else:
                        self.log_warning(f"{method} {endpoint} - Status: {response.status_code}")
                        
                except Exception as e:
                    self.log_error(f"{method} {endpoint} failed: {e}")
    
    async def test_customer_endpoints(self):
        """Test customer management endpoints"""
        self.log_header("Phase 9: Customer Management Endpoints")
        
        if not self.token:
            self.log_warning("Skipping customer tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test customer list
            try:
                response = await client.get(f"{self.base_url}/reports/customers", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "customers" in data:
                        count = len(data["customers"])
                        self.log_success(f"GET /reports/customers - Working ({count} customers)")
                    else:
                        self.log_warning("GET /reports/customers - Unexpected format")
                else:
                    self.log_warning(f"GET /reports/customers - Status: {response.status_code}")
                    
            except Exception as e:
                self.log_error(f"GET /reports/customers failed: {e}")
            
            # Test customer statement
            try:
                # Get a sample customer ID
                sample_customer = await self.db.customers.find_one({})
                if sample_customer:
                    customer_id = str(sample_customer.get("_id"))
                    start_date = "2024-01-01"
                    end_date = "2024-12-31"
                    
                    response = await client.get(
                        f"{self.base_url}/reports/customer-statement/{customer_id}?start_date={start_date}&end_date={end_date}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "customer" in data and "transactions" in data:
                            txn_count = len(data["transactions"])
                            self.log_success(f"GET /reports/customer-statement/{{id}} - Working ({txn_count} transactions)")
                        else:
                            self.log_warning("GET /reports/customer-statement/{{id}} - Incomplete data")
                    else:
                        self.log_warning(f"GET /reports/customer-statement/{{id}} - Status: {response.status_code}")
                        
            except Exception as e:
                self.log_error(f"GET /reports/customer-statement/{{id}} failed: {e}")
    
    async def test_data_integrity(self):
        """Test data integrity and calculations"""
        self.log_header("Phase 10: Data Integrity & Calculations")
        
        # Test invoice total calculation from invoice_items
        try:
            sample_invoice = await self.db.invoices.find_one({})
            if sample_invoice:
                invoice_id = sample_invoice.get("invoice_id")
                items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
                
                if items:
                    calculated_total = sum(item.get("line_total", 0) for item in items)
                    stored_total = sample_invoice.get("total_amount", 0)
                    
                    if abs(calculated_total - stored_total) < 0.01:
                        self.log_success(f"Invoice totals match: Calculated={calculated_total:.2f}, Stored={stored_total:.2f}")
                    else:
                        self.log_warning(f"Invoice total mismatch: Calculated={calculated_total:.2f}, Stored={stored_total:.2f}")
                else:
                    self.log_warning(f"No items found for invoice {invoice_id}")
        except Exception as e:
            self.log_error(f"Invoice total verification failed: {e}")
        
        # Test payment matching accuracy
        try:
            matched_payments = await self.db.payments.count_documents({"invoice_id": {"$exists": True, "$ne": None}})
            total_payments = await self.db.payments.count_documents({})
            
            if total_payments > 0:
                accuracy = (matched_payments / total_payments) * 100
                if accuracy >= 90:
                    self.log_success(f"Payment matching accuracy: {accuracy:.1f}% ({matched_payments}/{total_payments})")
                else:
                    self.log_warning(f"Payment matching accuracy: {accuracy:.1f}% ({matched_payments}/{total_payments})")
        except Exception as e:
            self.log_error(f"Payment matching verification failed: {e}")
    
    async def test_performance(self):
        """Test API performance"""
        self.log_header("Phase 11: Performance Testing")
        
        if not self.token:
            self.log_warning("Skipping performance tests - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test dashboard load time
            try:
                start = time.time()
                response = await client.get(f"{self.base_url}/api/dashboard/stats", headers=headers)
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    if elapsed < 1000:
                        self.log_success(f"Dashboard load time: {elapsed:.0f}ms (excellent)")
                    elif elapsed < 2000:
                        self.log_success(f"Dashboard load time: {elapsed:.0f}ms (good)")
                    else:
                        self.log_warning(f"Dashboard load time: {elapsed:.0f}ms (slow)")
            except Exception as e:
                self.log_error(f"Dashboard performance test failed: {e}")
            
            # Test report generation time
            try:
                start = time.time()
                response = await client.get(
                    f"{self.base_url}/reports/income-statement?start_date=2024-01-01&end_date=2024-12-31",
                    headers=headers
                )
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    if elapsed < 3000:
                        self.log_success(f"Report generation time: {elapsed:.0f}ms (acceptable)")
                    else:
                        self.log_warning(f"Report generation time: {elapsed:.0f}ms (slow)")
            except Exception as e:
                self.log_error(f"Report performance test failed: {e}")
    
    async def test_security(self):
        """Test security features"""
        self.log_header("Phase 12: Security Verification")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test authentication requirement
            try:
                response = await client.get(f"{self.base_url}/api/dashboard/stats")
                
                if response.status_code == 401:
                    self.log_success("Authentication required for protected endpoints")
                else:
                    self.log_warning(f"Protected endpoint accessible without auth: {response.status_code}")
            except Exception as e:
                self.log_error(f"Security test failed: {e}")
            
            # Test CORS headers
            try:
                response = await client.options(f"{self.base_url}/api/auth/login")
                headers = response.headers
                
                if "access-control-allow-origin" in headers:
                    origin = headers["access-control-allow-origin"]
                    if origin == "*":
                        self.log_warning("CORS allows all origins (not recommended for production)")
                    else:
                        self.log_success(f"CORS configured: {origin}")
                else:
                    self.log_warning("CORS headers not found")
            except Exception as e:
                self.log_error(f"CORS test failed: {e}")
    
    def generate_report(self):
        """Generate final audit report"""
        self.log_header("Final Audit Report")
        
        print(f"\n{Colors.BOLD}Test Statistics:{Colors.ENDC}")
        print(f"  Total Tests: {self.stats['total']}")
        print(f"  {Colors.OKGREEN}✅ Passed: {self.stats['passed']}{Colors.ENDC}")
        print(f"  {Colors.WARNING}⚠️  Warnings: {self.stats['warnings']}{Colors.ENDC}")
        print(f"  {Colors.FAIL}❌ Failed: {self.stats['failed']}{Colors.ENDC}")
        
        # Calculate score
        if self.stats['total'] > 0:
            score = ((self.stats['passed'] + self.stats['warnings'] * 0.5) / self.stats['total']) * 100
            
            print(f"\n{Colors.BOLD}Overall Score: {score:.1f}/100{Colors.ENDC}")
            
            if score >= 90:
                print(f"{Colors.OKGREEN}{Colors.BOLD}Status: PRODUCTION READY ✅{Colors.ENDC}")
            elif score >= 75:
                print(f"{Colors.WARNING}{Colors.BOLD}Status: NEEDS MINOR FIXES ⚠️{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}{Colors.BOLD}Status: NEEDS ATTENTION ❌{Colors.ENDC}")
        
        # Save report to file
        report_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "statistics": self.stats,
                "results": dict(self.results),
                "score": score if self.stats['total'] > 0 else 0
            }, f, indent=2)
        
        print(f"\n{Colors.OKCYAN}Report saved to: {report_file}{Colors.ENDC}")
    
    async def run_all_tests(self):
        """Run all verification tests"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║     POST-MIGRATION AUDIT VERIFICATION SCRIPT                     ║")
        print("║     Testing Backend Endpoints, Database Schema & Integration    ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        try:
            await self.setup()
            
            # Run all test phases
            await self.test_database_collections()
            await self.test_database_indexes()
            await self.test_normalized_schema()
            await self.test_authentication_endpoints()
            await self.test_dashboard_endpoints()
            await self.test_invoice_endpoints()
            await self.test_payment_endpoints()
            await self.test_receipt_endpoints()
            await self.test_customer_endpoints()
            await self.test_data_integrity()
            await self.test_performance()
            await self.test_security()
            
            # Generate final report
            self.generate_report()
            
        except Exception as e:
            print(f"\n{Colors.FAIL}Fatal error during audit: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()
        finally:
            await self.cleanup()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify post-migration audit findings")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend API base URL")
    parser.add_argument("--mongo-uri", help="MongoDB connection URI")
    
    args = parser.parse_args()
    
    verifier = AuditVerifier(base_url=args.base_url, mongo_uri=args.mongo_uri)
    await verifier.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
