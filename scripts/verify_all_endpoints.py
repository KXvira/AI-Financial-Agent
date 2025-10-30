#!/usr/bin/env python3
"""
Script to verify all API endpoints are working correctly
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def check_endpoint(name, endpoint, params=None):
    """Check if an endpoint is working"""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}")
            return True, data
        else:
            print(f"❌ {name} - Status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ {name} - Error: {str(e)}")
        return False, None

def main():
    print("=" * 60)
    print("API Endpoint Verification")
    print("=" * 60)
    print()
    
    # Dashboard endpoints
    print("DASHBOARD ENDPOINTS:")
    check_endpoint("Dashboard Health", "/api/dashboard/health")
    success, data = check_endpoint("Dashboard Stats", "/api/dashboard/stats")
    if success:
        print(f"  - Total Revenue: KES {data['total_revenue']:,.2f}")
        print(f"  - Total Payments: KES {data['total_payments']:,.2f}")
        print(f"  - Outstanding: KES {data['outstanding_amount']:,.2f}")
    
    check_endpoint("Dashboard Summary", "/api/dashboard/stats/summary")
    print()
    
    # Expense endpoints
    print("EXPENSE ENDPOINTS:")
    success, data = check_endpoint("Expense Summary", "/api/receipts/demo/summary")
    if success:
        print(f"  - Total Expenses: KES {data['totalExpenses']:,.2f}")
        print(f"  - Total Receipts: {data['totalReceipts']}")
        print(f"  - Monthly Total: KES {data['monthlyTotal']:,.2f}")
    print()
    
    # Invoice endpoints
    print("INVOICE ENDPOINTS:")
    success, data = check_endpoint("Invoice List", "/api/invoices", {"limit": 5})
    if success:
        print(f"  - Invoices returned: {len(data.get('invoices', []))}")
    
    success, data = check_endpoint("Invoice Stats", "/api/invoices/stats/summary")
    if success:
        print(f"  - Total Invoices: {data['totalInvoices']}")
        print(f"  - Paid Total: KES {data['paidTotal']:,.2f}")
        print(f"  - Pending Total: KES {data['pendingTotal']:,.2f}")
    print()
    
    # Payment endpoints
    print("PAYMENT ENDPOINTS:")
    success, data = check_endpoint("Payment List", "/api/payments", {"limit": 5})
    if success:
        print(f"  - Payments returned: {len(data.get('payments', []))}")
    
    success, data = check_endpoint("Payment Stats", "/api/payments/stats/summary")
    if success:
        print(f"  - Total Payments: {data['totalPayments']}")
        print(f"  - Completed Total: KES {data['completedTotal']:,.2f}")
        print(f"  - AI Accuracy: {data['aiAccuracy']:.1f}%")
        print(f"  - Matched: {data['matchedCount']}, Unmatched: {data['unmatchedCount']}")
    print()
    
    print("=" * 60)
    print("Verification Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
