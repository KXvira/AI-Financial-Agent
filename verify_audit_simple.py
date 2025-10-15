#!/usr/bin/env python3
"""
Simplified Audit Verification Script (API-only)
Tests backend endpoints without direct database access
"""

import asyncio
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict
import httpx


class Colors:
    """ANSI color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class SimpleAuditVerifier:
    """API-only audit verification"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.results = defaultdict(list)
        self.stats = {"total": 0, "passed": 0, "warnings": 0, "failed": 0}
    
    def log_success(self, message: str):
        print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        self.results["passed"].append(message)
        self.stats["passed"] += 1
        self.stats["total"] += 1
    
    def log_warning(self, message: str):
        print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        self.results["warnings"].append(message)
        self.stats["warnings"] += 1
        self.stats["total"] += 1
    
    def log_error(self, message: str):
        print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        self.results["failed"].append(message)
        self.stats["failed"] += 1
        self.stats["total"] += 1
    
    def log_header(self, message: str):
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"  {message}")
        print(f"{'='*70}{Colors.ENDC}\n")
    
    async def test_authentication(self):
        """Test authentication endpoints"""
        self.log_header("Phase 1: Authentication Endpoints")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test login
            try:
                login_data = {"email": "admin@finagent.com", "password": "admin123"}
                response = await client.post(f"{self.base_url}/api/auth/login", json=login_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.token = data["access_token"]
                        self.log_success("POST /api/auth/login - Token obtained ✓")
                    else:
                        self.log_warning("POST /api/auth/login - No token in response")
                else:
                    self.log_error(f"POST /api/auth/login - Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"POST /api/auth/login failed: {str(e)[:80]}")
            
            # Test protected endpoint
            if self.token:
                try:
                    headers = {"Authorization": f"Bearer {self.token}"}
                    response = await client.get(f"{self.base_url}/api/auth/me", headers=headers)
                    
                    if response.status_code == 200:
                        self.log_success("GET /api/auth/me - Authentication verified ✓")
                    else:
                        self.log_warning(f"GET /api/auth/me - Status: {response.status_code}")
                except Exception as e:
                    self.log_error(f"GET /api/auth/me failed: {str(e)[:80]}")
    
    async def test_dashboard(self):
        """Test dashboard endpoints"""
        self.log_header("Phase 2: Dashboard & Metrics")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                start = time.time()
                response = await client.get(f"{self.base_url}/api/dashboard/stats", headers=headers)
                elapsed = (time.time() - start) * 1000
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_success(f"GET /api/dashboard/stats - {elapsed:.0f}ms ✓")
                    
                    # Verify data structure
                    if any(key in data for key in ['total_revenue', 'total_invoiced', 'total_expenses']):
                        self.log_success("Dashboard data structure - Valid ✓")
                    else:
                        self.log_warning("Dashboard data structure - Unexpected format")
                else:
                    self.log_error(f"GET /api/dashboard/stats - Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"GET /api/dashboard/stats failed: {str(e)[:80]}")
    
    async def test_reports(self):
        """Test reporting endpoints"""
        self.log_header("Phase 3: Reporting Endpoints")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        endpoints = [
            "/reports/types",
            "/reports/income-statement?start_date=2024-01-01&end_date=2024-12-31",
            "/reports/cash-flow?start_date=2024-01-01&end_date=2024-12-31",
            "/reports/ar-aging",
            "/reports/dashboard-metrics",
            "/reports/tax/vat-summary?start_date=2024-01-01&end_date=2024-12-31",
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data and len(str(data)) > 20:
                            self.log_success(f"GET {endpoint.split('?')[0]} - Working ✓")
                        else:
                            self.log_warning(f"GET {endpoint.split('?')[0]} - Empty response")
                    else:
                        self.log_warning(f"GET {endpoint.split('?')[0]} - Status: {response.status_code}")
                except Exception as e:
                    self.log_error(f"GET {endpoint.split('?')[0]} failed: {str(e)[:60]}")
    
    async def test_invoices(self):
        """Test invoice endpoints"""
        self.log_header("Phase 4: Invoice Management")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.base_url}/api/invoices?page=1&page_size=5", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) or "invoices" in data:
                        count = len(data) if isinstance(data, list) else len(data.get("invoices", []))
                        self.log_success(f"GET /api/invoices - {count} invoices retrieved ✓")
                    else:
                        self.log_warning("GET /api/invoices - Unexpected format")
                else:
                    self.log_warning(f"GET /api/invoices - Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"GET /api/invoices failed: {str(e)[:80]}")
    
    async def test_payments(self):
        """Test payment endpoints"""
        self.log_header("Phase 5: Payment Management")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                "/api/payments?page=1&page_size=5",
                "/api/payments/stats/summary",
            ]
            
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        self.log_success(f"GET {endpoint.split('?')[0]} - Working ✓")
                    else:
                        self.log_warning(f"GET {endpoint.split('?')[0]} - Status: {response.status_code}")
                except Exception as e:
                    self.log_error(f"GET {endpoint.split('?')[0]} failed: {str(e)[:60]}")
    
    async def test_receipts(self):
        """Test receipt/OCR endpoints"""
        self.log_header("Phase 6: OCR/Receipt Management")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            endpoints = [
                "/receipts/?page=1&page_size=5",
                "/receipts/statistics/summary",
                "/api/ocr/health",
            ]
            
            for endpoint in endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                    
                    if response.status_code == 200:
                        self.log_success(f"GET {endpoint.split('?')[0]} - Working ✓")
                    else:
                        self.log_warning(f"GET {endpoint.split('?')[0]} - Status: {response.status_code}")
                except Exception as e:
                    self.log_error(f"GET {endpoint.split('?')[0]} failed: {str(e)[:60]}")
    
    async def test_customers(self):
        """Test customer endpoints"""
        self.log_header("Phase 7: Customer Management")
        
        if not self.token:
            self.log_warning("Skipping - no auth token")
            return
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(f"{self.base_url}/reports/customers", headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    if "customers" in data:
                        count = len(data["customers"])
                        self.log_success(f"GET /reports/customers - {count} customers ✓")
                    else:
                        self.log_warning("GET /reports/customers - Unexpected format")
                else:
                    self.log_warning(f"GET /reports/customers - Status: {response.status_code}")
            except Exception as e:
                self.log_error(f"GET /reports/customers failed: {str(e)[:80]}")
    
    async def test_security(self):
        """Test security"""
        self.log_header("Phase 8: Security Verification")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test unauth access
            try:
                response = await client.get(f"{self.base_url}/api/dashboard/stats")
                
                if response.status_code == 401:
                    self.log_success("Protected endpoints require authentication ✓")
                else:
                    self.log_warning(f"Dashboard accessible without auth: {response.status_code}")
            except Exception as e:
                self.log_error(f"Security test failed: {str(e)[:80]}")
    
    def generate_report(self):
        """Generate final report"""
        self.log_header("Final Audit Report")
        
        print(f"\n{Colors.BOLD}Test Statistics:{Colors.ENDC}")
        print(f"  Total Tests: {self.stats['total']}")
        print(f"  {Colors.OKGREEN}✅ Passed: {self.stats['passed']}{Colors.ENDC}")
        print(f"  {Colors.WARNING}⚠️  Warnings: {self.stats['warnings']}{Colors.ENDC}")
        print(f"  {Colors.FAIL}❌ Failed: {self.stats['failed']}{Colors.ENDC}")
        
        if self.stats['total'] > 0:
            score = ((self.stats['passed'] + self.stats['warnings'] * 0.5) / self.stats['total']) * 100
            
            print(f"\n{Colors.BOLD}Overall Score: {score:.1f}/100{Colors.ENDC}")
            
            if score >= 90:
                print(f"{Colors.OKGREEN}{Colors.BOLD}Status: PRODUCTION READY ✅{Colors.ENDC}")
            elif score >= 75:
                print(f"{Colors.WARNING}{Colors.BOLD}Status: NEEDS MINOR FIXES ⚠️{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}{Colors.BOLD}Status: NEEDS ATTENTION ❌{Colors.ENDC}")
            
            # Save report
            report_file = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "statistics": self.stats,
                    "results": dict(self.results),
                    "score": score
                }, f, indent=2)
            
            print(f"\n{Colors.OKCYAN}Report saved to: {report_file}{Colors.ENDC}\n")
    
    async def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║     POST-MIGRATION AUDIT VERIFICATION (API-ONLY)                 ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.ENDC}")
        
        try:
            await self.test_authentication()
            await self.test_dashboard()
            await self.test_reports()
            await self.test_invoices()
            await self.test_payments()
            await self.test_receipts()
            await self.test_customers()
            await self.test_security()
            
            self.generate_report()
            
        except Exception as e:
            print(f"\n{Colors.FAIL}Fatal error: {e}{Colors.ENDC}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Verify audit findings via API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="Backend API base URL")
    
    args = parser.parse_args()
    
    verifier = SimpleAuditVerifier(base_url=args.base_url)
    await verifier.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
