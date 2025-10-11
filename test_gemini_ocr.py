#!/usr/bin/env python3
"""
Test Gemini OCR Engine
"""
import sys
import os
import asyncio
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from backend.ocr.gemini_ocr_engine import create_gemini_ocr_engine

async def test_gemini_ocr():
    """Test Gemini OCR capabilities"""
    print("🤖 Testing Gemini OCR Engine")
    print("=" * 40)
    
    # Create Gemini OCR engine
    gemini_ocr = create_gemini_ocr_engine()
    
    if not gemini_ocr:
        print("❌ Gemini OCR Engine not available")
        print("   Make sure you have:")
        print("   1. GEMINI_API_KEY environment variable set")
        print("   2. google-generativeai package installed")
        return
    
    print("✅ Gemini OCR Engine initialized")
    print(f"🔌 Engine enabled: {gemini_ocr.enabled}")
    print()
    
    # Create test receipt image
    test_image = create_test_receipt()
    if not test_image:
        print("❌ Could not create test image")
        return
    
    print(f"🖼️  Test image: {test_image}")
    print()
    
    # Test 1: Text extraction only
    print("📝 Test 1: Text Extraction")
    print("-" * 30)
    
    start_time = time.time()
    text_result = await gemini_ocr.extract_text_only(test_image)
    text_duration = time.time() - start_time
    
    print(f"⏱️  Processing time: {text_duration:.2f}s")
    print(f"📊 Confidence: {text_result.get('confidence', 0):.2%}")
    print(f"🔧 Engine: {text_result.get('engine', 'unknown')}")
    
    if text_result.get('error'):
        print(f"❌ Error: {text_result['error']}")
    else:
        print("📄 Extracted text:")
        print(text_result.get('text', 'No text extracted')[:300])
        if len(text_result.get('text', '')) > 300:
            print("... (truncated)")
    
    print()
    
    # Test 2: Structured data extraction
    print("🏗️  Test 2: Structured Data Extraction")
    print("-" * 40)
    
    start_time = time.time()
    structured_result = await gemini_ocr.extract_structured_data(test_image)
    structured_duration = time.time() - start_time
    
    print(f"⏱️  Processing time: {structured_duration:.2f}s")
    print(f"📊 Confidence: {structured_result.get('confidence', 0):.2%}")
    print(f"🔧 Engine: {structured_result.get('engine', 'unknown')}")
    
    if structured_result.get('error'):
        print(f"❌ Error: {structured_result['error']}")
    else:
        structured_data = structured_result.get('structured_data', {})
        print("📋 Structured Data:")
        
        # Display vendor info
        vendor = structured_data.get('vendor', {})
        if vendor:
            print("  👤 Vendor:")
            for key, value in vendor.items():
                if value:
                    print(f"    {key}: {value}")
        
        # Display totals
        totals = structured_data.get('totals', {})
        if totals:
            print("  💰 Totals:")
            for key, value in totals.items():
                if value:
                    print(f"    {key}: {value}")
        
        # Display payment
        payment = structured_data.get('payment', {})
        if payment:
            print("  💳 Payment:")
            for key, value in payment.items():
                if value:
                    print(f"    {key}: {value}")
        
        # Display transaction
        transaction = structured_data.get('transaction', {})
        if transaction:
            print("  📅 Transaction:")
            for key, value in transaction.items():
                if value:
                    print(f"    {key}: {value}")
    
    print()
    
    # Test 3: Comprehensive analysis
    print("🎯 Test 3: Comprehensive Analysis")
    print("-" * 35)
    
    start_time = time.time()
    comprehensive_result = await gemini_ocr.comprehensive_analysis(test_image)
    comprehensive_duration = time.time() - start_time
    
    print(f"⏱️  Total processing time: {comprehensive_duration:.2f}s")
    print(f"📊 Combined confidence: {comprehensive_result.get('confidence', 0):.2%}")
    print(f"📊 Text confidence: {comprehensive_result.get('text_confidence', 0):.2%}")
    print(f"📊 Structured confidence: {comprehensive_result.get('structured_confidence', 0):.2%}")
    print(f"🔧 Engine: {comprehensive_result.get('engine', 'unknown')}")
    
    errors = comprehensive_result.get('errors', {})
    if errors.get('text_error') or errors.get('structured_error'):
        print("⚠️  Errors:")
        if errors.get('text_error'):
            print(f"    Text: {errors['text_error']}")
        if errors.get('structured_error'):
            print(f"    Structured: {errors['structured_error']}")
    
    print()
    print("✅ Gemini OCR testing completed!")
    
    # Cleanup
    try:
        if os.path.exists(test_image):
            os.remove(test_image)
    except:
        pass

def create_test_receipt():
    """Create a test receipt image for OCR testing"""
    try:
        import cv2
        import numpy as np
        
        # Create receipt image
        height, width = 500, 400
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        receipt_lines = [
            ("NAIVAS SUPERMARKET", 0.8, (20, 40)),
            ("Junction Mall Branch", 0.6, (20, 70)),
            ("P.O Box 1234, Nairobi", 0.5, (20, 95)),
            ("PIN: A012345678B", 0.5, (20, 120)),
            ("", 0.5, (20, 140)),
            ("Date: 11/10/2025", 0.6, (20, 165)),
            ("Time: 15:30", 0.6, (20, 190)),
            ("Cashier: Mary K.", 0.5, (20, 215)),
            ("", 0.5, (20, 235)),
            ("2x Bread Loaf", 0.6, (20, 260)),
            ("  @ KSH 85.00 each", 0.5, (30, 285)),
            ("1x Milk 1L", 0.6, (20, 310)),
            ("  @ KSH 120.00", 0.5, (30, 335)),
            ("", 0.5, (20, 355)),
            ("Subtotal: KSH 290.00", 0.6, (20, 380)),
            ("VAT (16%): KSH 46.40", 0.6, (20, 405)),
            ("TOTAL: KSH 336.40", 0.8, (20, 435)),
            ("", 0.5, (20, 455)),
            ("Payment: M-Pesa", 0.6, (20, 480)),
            ("Ref: QX12345ABC", 0.6, (20, 505)),
            ("Till: 567890", 0.6, (20, 530)),
            ("Phone: 0712345678", 0.6, (20, 555)),
            ("", 0.5, (20, 575)),
            ("Thank you for shopping!", 0.5, (20, 600))
        ]
        
        for text, scale, (x, y) in receipt_lines:
            if text and y < height - 20:
                cv2.putText(image, text, (x, y), font, scale, (0, 0, 0), 1)
        
        # Save image
        test_path = os.path.join(project_root, "test_gemini_receipt.png")
        cv2.imwrite(test_path, image)
        
        return test_path
        
    except Exception as e:
        print(f"❌ Could not create test image: {e}")
        return None

if __name__ == "__main__":
    print("🤖 Gemini OCR Engine Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or api_key == "your-api-key":
        print("⚠️  Warning: GEMINI_API_KEY not set!")
        print("   Set your API key: export GEMINI_API_KEY='your-actual-key'")
        print("   Tests will run in demo mode.")
        print()
    
    asyncio.run(test_gemini_ocr())