"""
Simple Test Data Creator using Backend API
Since direct MongoDB connection has DNS issues, we'll create data through the backend
which is already connected to the database
"""

import requests
import random
from datetime import datetime, timedelta
import json

BASE_URL = "http://localhost:8000"

# Summary
print("="*70)
print("🚀 SIMPLIFIED TEST DATA GENERATOR")
print("="*70)
print("\nThis script will create test data through the running backend API")
print("\nNote: Since the backend is already running with a working DB connection,")
print("we'll leverage that instead of creating a separate connection.")
print("\n" + "="*70)

# Check if backend is running
try:
    response = requests.get(f"{BASE_URL}/")
    print("\n✅ Backend is running!")
    print(f"   Status: {response.json()}")
except Exception as e:
    print(f"\n❌ Backend is not running or not accessible: {e}")
    print("   Please start the backend first with: python backend/app.py")
    exit(1)

print("\n" + "="*70)
print("📊 CURRENT DATABASE STATUS")
print("="*70)

# Check current data
try:
    # Check AR Aging for invoice count
    ar_response = requests.get(f"{BASE_URL}/reports/ar-aging")
    if ar_response.status_code == 200:
        ar_data = ar_response.json()
        print(f"\n📄 Existing Invoices: {ar_data.get('total_invoices', 0)}")
        print(f"   Outstanding Amount: KES {ar_data.get('total_outstanding', 0):,.2f}")
    
    # Check expenses
    expense_response = requests.get(f"{BASE_URL}/api/expenses/summary?days=365")
    if expense_response.status_code == 200:
        expense_data = expense_response.json()
        print(f"\n🧾 Existing Expenses: {expense_data.get('stats', {}).get('transaction_count', 0)}")
        print(f"   Total Amount: KES {expense_data.get('stats', {}).get('total_amount', 0):,.2f}")
    
    # Check dashboard
    dashboard_response = requests.get(f"{BASE_URL}/reports/dashboard-metrics")
    if dashboard_response.status_code == 200:
        dash_data = dashboard_response.json()
        print(f"\n💰 Dashboard Metrics:")
        print(f"   Total Revenue: KES {dash_data.get('total_revenue', 0):,.2f}")
        print(f"   Total Expenses: KES {dash_data.get('total_expenses', 0):,.2f}")
        print(f"   Net Income: KES {dash_data.get('net_income', 0):,.2f}")
        print(f"   Collection Rate: {dash_data.get('collection_rate', 0)}%")
        
except Exception as e:
    print(f"\n⚠️  Could not fetch current data: {e}")

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)

print("""
The system currently has:
  ✅ 413 invoices in the database
  ✅ 10 expense receipts
  ✅ AR Aging report working (KES 1.03B outstanding)
  ❌ Income Statement showing ZERO revenue
  
The income statement issue is because:
  - Invoices don't have proper 'issue_date' or 'date' fields
  - OR the date format/field name doesn't match what the code expects
  
SOLUTION: We need to either:
  1. Fix the income statement code to handle the existing invoice date format
  2. Update existing invoices to have proper date fields
  3. Create new test invoices with correct date structure

Since we have 413 existing invoices showing in AR aging, the best approach is to
FIX THE CODE to work with the existing data structure.
""")

print("\n" + "="*70)
print("📝 RECOMMENDATION")
print("="*70)
print("""
Instead of creating new data, let's fix the income statement service to:
1. Use the same date field logic as AR aging (which works)
2. Handle missing dates by using 'created_at' as fallback
3. Not filter out invoices with empty date strings

The AR aging report successfully finds and displays 413 invoices, so the data
EXISTS - we just need to access it correctly in the income statement.
""")

print("\n✅ Script complete - No new data created")
print("   Next step: Fix income statement service code")
print()
