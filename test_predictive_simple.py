#!/usr/bin/env python3
"""
Simple test for predictive analytics API
"""
import requests
import json
import time

print("\n" + "="*70)
print("PREDICTIVE ANALYTICS API TEST")
print("="*70)

# Wait for server
time.sleep(2)

# Test Revenue Forecast
print("\n1. Testing Revenue Forecast API...")
try:
    url = "http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=3&include_confidence=false"
    print(f"   URL: {url}")
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            print(f"   ❌ API Error: {data['error']}")
        else:
            print(f"   ✅ SUCCESS!")
            print(f"   Response keys: {list(data.keys())}")
            if "forecast" in data:
                print(f"   Forecast items: {len(data['forecast'])}")
                if data['forecast']:
                    print(f"   First item keys: {list(data['forecast'][0].keys())}")
                    print(f"   Sample: {json.dumps(data['forecast'][0], indent=6)}")
    else:
        print(f"   ❌ HTTP {response.status_code}: {response.text[:200]}")
except requests.Timeout:
    print(f"   ❌ Request timed out after 30 seconds")
except Exception as e:
    print(f"   ❌ Exception: {e}")

# Test Expense Forecast  
print("\n2. Testing Expense Forecast API...")
try:
    url = "http://localhost:8000/reports/predictive/expense-forecast?months_ahead=3&include_confidence=false"
    print(f"   URL: {url}")
    response = requests.get(url, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            print(f"   ❌ API Error: {data['error']}")
        else:
            print(f"   ✅ SUCCESS!")
            print(f"   Response keys: {list(data.keys())}")
            if "forecast" in data:
                print(f"   Forecast items: {len(data['forecast'])}")
    else:
        print(f"   ❌ HTTP {response.status_code}")
except requests.Timeout:
    print(f"   ❌ Request timed out after 30 seconds")
except Exception as e:
    print(f"   ❌ Exception: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print("="*70 + "\n")
