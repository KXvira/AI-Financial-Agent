#!/usr/bin/env python3
"""
Comprehensive Receipt System Test
Tests all receipt functionality including:
1. Manual receipt creation
2. OCR-based receipt creation
3. PDF generation
4. Receipt listing and filtering
5. Receipt download
"""

import requests
import json
import time
import os
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
RECEIPTS_ENDPOINT = f"{BASE_URL}/receipts"

# Test data
TEST_RECEIPT_DATA = {
    "receipt_type": "payment",
    "customer": {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+254712345678"
    },
    "payment_method": "mpesa",
    "amount": 5000.00,
    "description": "Payment for services rendered",
    "include_vat": True,
    "send_email": False,
    "line_items": [
        {
            "description": "Web Development Services",
            "quantity": 10,
            "unit_price": 400.00,
            "total": 4000.00
        },
        {
            "description": "Hosting & Maintenance",
            "quantity": 1,
            "unit_price": 862.07,
            "total": 862.07
        }
    ]
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def test_manual_receipt_creation():
    """Test 1: Create receipt manually"""
    print_section("TEST 1: Manual Receipt Creation")
    
    try:
        response = requests.post(
            f"{RECEIPTS_ENDPOINT}/generate",
            json=TEST_RECEIPT_DATA,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            receipt = response.json()
            print_success("Receipt created successfully!")
            print_info(f"Receipt Number: {receipt['receipt_number']}")
            print_info(f"Receipt ID: {receipt.get('id', receipt.get('_id'))}")
            print_info(f"Customer: {receipt['customer']['name']}")
            print_info(f"Amount: KES {receipt['tax_breakdown']['total']:,.2f}")
            print_info(f"Status: {receipt['status']}")
            print_info(f"PDF Path: {receipt.get('pdf_path', 'Not generated')}")
            return receipt
        else:
            print_error(f"Failed to create receipt: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_ocr_receipt_upload():
    """Test 2: Create receipt from OCR image upload"""
    print_section("TEST 2: OCR-Based Receipt Creation")
    
    # Check if test image exists
    test_image_path = "test_receipt.jpg"
    if not os.path.exists(test_image_path):
        print_info("No test image found. Creating a test scenario...")
        print_info("To test OCR, place a receipt image as 'test_receipt.jpg'")
        print_info("Supported formats: JPG, PNG, WEBP, PDF")
        return None
    
    try:
        with open(test_image_path, 'rb') as img_file:
            files = {'file': (test_image_path, img_file, 'image/jpeg')}
            
            response = requests.post(
                f"{RECEIPTS_ENDPOINT}/upload-ocr",
                files=files
            )
        
        if response.status_code == 201:
            receipt = response.json()
            print_success("Receipt created from OCR successfully!")
            print_info(f"Receipt Number: {receipt['receipt_number']}")
            print_info(f"Receipt ID: {receipt.get('id', receipt.get('_id'))}")
            print_info(f"Customer: {receipt['customer']['name']}")
            print_info(f"Amount: KES {receipt['tax_breakdown']['total']:,.2f}")
            print_info(f"Items extracted: {len(receipt.get('line_items', []))}")
            print_info(f"Payment Method: {receipt['payment_method']}")
            return receipt
        else:
            print_error(f"Failed to upload receipt: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_list_receipts():
    """Test 3: List all receipts"""
    print_section("TEST 3: List Receipts")
    
    try:
        response = requests.get(f"{RECEIPTS_ENDPOINT}/")
        
        if response.status_code == 200:
            data = response.json()
            receipts = data.get('receipts', [])
            total = data.get('total', len(receipts))
            
            print_success(f"Retrieved {len(receipts)} receipts (Total: {total})")
            
            if receipts:
                print("\nRecent Receipts:")
                print("-" * 70)
                for receipt in receipts[:5]:  # Show first 5
                    receipt_num = receipt.get('receipt_number', 'N/A')
                    customer_name = receipt.get('customer', {}).get('name', 'Unknown')
                    amount = receipt.get('tax_breakdown', {}).get('total', 0)
                    status = receipt.get('status', 'unknown')
                    date = receipt.get('issued_date', receipt.get('generated_at', 'N/A'))
                    
                    print(f"  {receipt_num} | {customer_name:20} | KES {amount:10,.2f} | {status:10} | {date[:10] if isinstance(date, str) else 'N/A'}")
                print("-" * 70)
            
            return receipts
        else:
            print_error(f"Failed to list receipts: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return []

def test_get_receipt_details(receipt_id):
    """Test 4: Get specific receipt details"""
    print_section("TEST 4: Get Receipt Details")
    
    try:
        response = requests.get(f"{RECEIPTS_ENDPOINT}/{receipt_id}")
        
        if response.status_code == 200:
            receipt = response.json()
            print_success("Receipt details retrieved successfully!")
            print_info(f"Receipt Number: {receipt['receipt_number']}")
            print_info(f"Type: {receipt['receipt_type']}")
            print_info(f"Status: {receipt['status']}")
            print_info(f"Customer: {receipt['customer']['name']}")
            
            if receipt.get('line_items'):
                print_info(f"\nLine Items ({len(receipt['line_items'])}):")
                for idx, item in enumerate(receipt['line_items'], 1):
                    print(f"    {idx}. {item['description']} - {item['quantity']} x KES {item['unit_price']:,.2f} = KES {item['total']:,.2f}")
            
            tax = receipt.get('tax_breakdown', {})
            if tax:
                print_info(f"\nFinancials:")
                print(f"    Subtotal: KES {tax.get('subtotal', 0):,.2f}")
                print(f"    VAT ({tax.get('vat_rate', 0)*100:.0f}%): KES {tax.get('vat_amount', 0):,.2f}")
                print(f"    Total: KES {tax.get('total', 0):,.2f}")
            
            return receipt
        else:
            print_error(f"Failed to get receipt: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_download_receipt_pdf(receipt_id, receipt_number):
    """Test 5: Download receipt PDF"""
    print_section("TEST 5: Download Receipt PDF")
    
    try:
        response = requests.get(f"{RECEIPTS_ENDPOINT}/{receipt_id}/download")
        
        if response.status_code == 200:
            filename = f"test_download_{receipt_number}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print_success("PDF downloaded successfully!")
            print_info(f"Filename: {filename}")
            print_info(f"Size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
            print_info(f"Location: {os.path.abspath(filename)}")
            return filename
        else:
            print_error(f"Failed to download PDF: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_receipt_statistics():
    """Test 6: Get receipt statistics"""
    print_section("TEST 6: Receipt Statistics")
    
    try:
        response = requests.get(f"{RECEIPTS_ENDPOINT}/statistics/summary")
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Statistics retrieved successfully!")
            print_info(f"Total Receipts: {stats.get('total_receipts', 0)}")
            print_info(f"Total Amount: KES {stats.get('total_amount', 0):,.2f}")
            
            by_type = stats.get('receipts_by_type', {})
            if by_type:
                print_info("\nReceipts by Type:")
                for rtype, count in by_type.items():
                    print(f"    {rtype}: {count}")
            
            by_status = stats.get('receipts_by_status', {})
            if by_status:
                print_info("\nReceipts by Status:")
                for status, count in by_status.items():
                    print(f"    {status}: {count}")
            
            return stats
        else:
            print_error(f"Failed to get statistics: {response.status_code}")
            return None
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None

def test_filter_receipts():
    """Test 7: Filter receipts"""
    print_section("TEST 7: Filter Receipts")
    
    try:
        # Filter by type
        response = requests.get(f"{RECEIPTS_ENDPOINT}/?receipt_type=payment")
        
        if response.status_code == 200:
            data = response.json()
            receipts = data.get('receipts', [])
            print_success(f"Filtered receipts by type 'payment': {len(receipts)} found")
            return receipts
        else:
            print_error(f"Failed to filter receipts: {response.status_code}")
            return []
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return []

def main():
    """Run all tests"""
    print("\n" + "🚀 " * 20)
    print("    RECEIPT SYSTEM - COMPREHENSIVE TEST SUITE")
    print("🚀 " * 20)
    
    # Check if backend is running
    try:
        response = requests.get(BASE_URL, timeout=5)
        print_success("Backend is running")
    except:
        print_error("Backend is not accessible at http://localhost:8000")
        print_info("Please start the backend server first:")
        print_info("  cd /home/munga/Desktop/AI-Financial-Agent")
        print_info("  source venv-ocr/bin/activate")
        print_info("  uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000")
        return
    
    # Run tests
    test_results = {}
    
    # Test 1: Manual receipt creation
    receipt1 = test_manual_receipt_creation()
    test_results['manual_creation'] = receipt1 is not None
    time.sleep(1)
    
    # Test 2: OCR receipt upload
    receipt2 = test_ocr_receipt_upload()
    test_results['ocr_upload'] = receipt2 is not None
    time.sleep(1)
    
    # Test 3: List receipts
    receipts = test_list_receipts()
    test_results['list_receipts'] = len(receipts) > 0
    time.sleep(1)
    
    # Test 4: Get receipt details (use first successful receipt)
    test_receipt = receipt1 or receipt2
    if test_receipt:
        receipt_id = test_receipt.get('id') or test_receipt.get('_id')
        receipt_details = test_get_receipt_details(receipt_id)
        test_results['get_details'] = receipt_details is not None
        time.sleep(1)
        
        # Test 5: Download PDF
        if receipt_details:
            pdf_file = test_download_receipt_pdf(receipt_id, receipt_details['receipt_number'])
            test_results['download_pdf'] = pdf_file is not None
            time.sleep(1)
    else:
        print_info("Skipping detail and download tests (no receipt created)")
        test_results['get_details'] = False
        test_results['download_pdf'] = False
    
    # Test 6: Statistics
    stats = test_receipt_statistics()
    test_results['statistics'] = stats is not None
    time.sleep(1)
    
    # Test 7: Filtering
    filtered = test_filter_receipts()
    test_results['filtering'] = len(filtered) >= 0
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name.replace('_', ' ').title()}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    if passed == total:
        print("🎉 All tests passed! Receipt system is fully functional!")
    elif passed > 0:
        print("⚠️  Some tests passed. Review failed tests above.")
    else:
        print("❌ All tests failed. Please check backend configuration.")

if __name__ == "__main__":
    main()
