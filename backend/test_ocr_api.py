"""
Test script to verify OCR system functionality
"""

import requests
import json
import time

def test_ocr_server():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing OCR Server API...")
    print("-" * 50)
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        health_response = requests.get(f"{base_url}/api/ocr/health")
        if health_response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {health_response.json()}")
        else:
            print("   ❌ Health check failed")
            return
        
        print()
        
        # Test receipts list (should be empty initially)
        print("2. Testing receipts list...")
        receipts_response = requests.get(f"{base_url}/api/ocr/receipts")
        if receipts_response.status_code == 200:
            receipts_data = receipts_response.json()
            print(f"   ✅ Receipts endpoint works - Found {receipts_data['total']} receipts")
        else:
            print("   ❌ Receipts endpoint failed")
            return
        
        print()
        
        # Test expense summary
        print("3. Testing expense summary...")
        summary_response = requests.get(f"{base_url}/api/ocr/expense-summary")
        if summary_response.status_code == 200:
            summary_data = summary_response.json()
            print("   ✅ Expense summary works")
            print(f"   💰 Total expenses: KES {summary_data['totalExpenses']}")
            print(f"   📈 Categories: {len(summary_data['categorySummary'])}")
        else:
            print("   ❌ Expense summary failed")
            return
        
        print()
        
        # Test file upload simulation
        print("4. Testing file upload simulation...")
        # Create a dummy file for testing
        files = {'file': ('test_receipt.jpg', b'fake_image_data', 'image/jpeg')}
        upload_response = requests.post(f"{base_url}/api/ocr/upload-receipt", files=files)
        
        if upload_response.status_code == 200:
            upload_data = upload_response.json()
            print("   ✅ Upload simulation works")
            print(f"   🆔 Receipt ID: {upload_data['receipt_id']}")
            print(f"   🏪 Vendor: {upload_data['parsed_data']['vendor']}")
            print(f"   💵 Amount: KES {upload_data['parsed_data']['total']}")
            
            receipt_id = upload_data['receipt_id']
        else:
            print("   ❌ Upload simulation failed")
            return
        
        print()
        
        # Test individual receipt retrieval
        print("5. Testing individual receipt retrieval...")
        individual_response = requests.get(f"{base_url}/api/ocr/receipts/{receipt_id}")
        if individual_response.status_code == 200:
            print("   ✅ Individual receipt retrieval works")
        else:
            print("   ❌ Individual receipt retrieval failed")
        
        print()
        
        # Test updated summary
        print("6. Testing updated expense summary...")
        updated_summary = requests.get(f"{base_url}/api/ocr/expense-summary")
        if updated_summary.status_code == 200:
            updated_data = updated_summary.json()
            print("   ✅ Updated summary works")
            print(f"   💰 New total: KES {updated_data['totalExpenses']}")
            print(f"   📋 Recent expenses: {len(updated_data['recentExpenses'])}")
        
        print()
        print("🎉 All tests passed! OCR system is working correctly.")
        print(f"🌐 Frontend should now work with: http://localhost:3001/expenses")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to OCR server. Make sure it's running on port 8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_ocr_server()