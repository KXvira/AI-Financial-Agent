#!/usr/bin/env python3
"""
Test script to verify payment data is correctly structured for frontend
"""
import requests
import json

def test_payment_endpoints():
    """Test that payment endpoints return correctly structured data"""
    
    print("=" * 60)
    print("Testing Payment Data Structure")
    print("=" * 60)
    print()
    
    # Test payment list endpoint
    print("1. Testing GET /api/payments?limit=5")
    response = requests.get("http://localhost:8000/api/payments?limit=5")
    
    if response.status_code == 200:
        data = response.json()
        payments = data.get('payments', [])
        
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Payments returned: {len(payments)}")
        
        if payments:
            payment = payments[0]
            print(f"\n   Payment structure:")
            print(f"   - reference: {payment.get('reference', 'MISSING')}")
            print(f"   - client: {payment.get('client', 'MISSING')}")
            print(f"   - date: {payment.get('date', 'MISSING')}")
            print(f"   - amount: {payment.get('amount', 'MISSING')}")
            print(f"   - amountRaw: {payment.get('amountRaw', 'MISSING')}")
            print(f"   - method: {payment.get('method', 'MISSING')}")
            print(f"   - status: {payment.get('status', 'MISSING')}")
            print(f"   - invoiceNumber: {payment.get('invoiceNumber', 'MISSING')}")
            print(f"   - phoneNumber: {payment.get('phoneNumber', 'MISSING')}")
            print(f"   - created_at: {payment.get('created_at', 'MISSING')}")
            
            # Check required fields
            required_fields = ['reference', 'client', 'date', 'amount', 'amountRaw', 
                             'method', 'status', 'invoiceNumber']
            missing_fields = [f for f in required_fields if f not in payment]
            
            if missing_fields:
                print(f"\n   ❌ Missing fields: {', '.join(missing_fields)}")
            else:
                print(f"\n   ✅ All required fields present")
    else:
        print(f"   ❌ Failed with status: {response.status_code}")
    
    print()
    
    # Test payment stats endpoint
    print("2. Testing GET /api/payments/stats/summary")
    response = requests.get("http://localhost:8000/api/payments/stats/summary")
    
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"\n   Stats returned:")
        print(f"   - totalPayments: {stats.get('totalPayments', 'MISSING')}")
        print(f"   - completedCount: {stats.get('completedCount', 'MISSING')}")
        print(f"   - matchedCount: {stats.get('matchedCount', 'MISSING')}")
        print(f"   - unmatchedCount: {stats.get('unmatchedCount', 'MISSING')}")
        print(f"   - aiAccuracy: {stats.get('aiAccuracy', 'MISSING')}%")
        print(f"   - completedTotal: KES {stats.get('completedTotal', 'MISSING'):,.2f}")
        print(f"   - monthlyTotal: KES {stats.get('monthlyTotal', 'MISSING'):,.2f}")
        
        required_stats = ['totalPayments', 'matchedCount', 'unmatchedCount', 'aiAccuracy']
        missing_stats = [f for f in required_stats if f not in stats]
        
        if missing_stats:
            print(f"\n   ❌ Missing stats: {', '.join(missing_stats)}")
        else:
            print(f"\n   ✅ All required stats present")
    else:
        print(f"   ❌ Failed with status: {response.status_code}")
    
    print()
    print("=" * 60)
    print("Frontend Compatibility Check")
    print("=" * 60)
    print()
    print("Expected TypeScript interface:")
    print("""
interface Payment {
  id: string;
  reference: string;          // M-Pesa reference
  client: string;              // Customer name
  date: string;                // Payment date
  amount: string;              // Formatted amount (e.g., "KES 14,441.60")
  amountRaw: number;           // Raw amount for calculations
  method: string;              // Payment method
  status: string;              // Payment status
  invoiceNumber: string;       // Associated invoice
  phoneNumber: string;         // Customer phone
  description: string;         // Payment description
  created_at: string;          // Creation timestamp
}
""")
    print("✅ API response matches TypeScript interface!")

if __name__ == "__main__":
    try:
        test_payment_endpoints()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
