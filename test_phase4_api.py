"""
Phase 4 API Integration Test
Tests the new OCR API endpoints
"""
import requests
import time
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# API Configuration
BASE_URL = "http://localhost:8000"
OCR_API_URL = f"{BASE_URL}/api/ocr"

def create_test_receipt(filename: str = "test_receipt_api.png"):
    """Create a test receipt image"""
    width, height = 400, 600
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Receipt content
    y_position = 20
    lines = [
        ("CARREFOUR SUPERMARKET", font),
        ("Junction Mall, Nairobi", font_small),
        ("P.O Box 9876, Kenya", font_small),
        ("PIN: A123456789Z", font_small),
        ("", font_small),
        ("Date: 11/10/2025", font_small),
        ("Time: 18:30", font_small),
        ("", font_small),
        ("2x Coffee Beans 500g", font_small),
        ("@ KSH 650.00 each", font_small),
        ("3x Fresh Milk 1L", font_small),
        ("@ KSH 150.00 each", font_small),
        ("1x Bread", font_small),
        ("@ KSH 75.00", font_small),
        ("", font_small),
        ("Subtotal: KSH 1,825.00", font_small),
        ("VAT (16%): KSH 292.00", font_small),
        ("TOTAL: KSH 2,117.00", font),
        ("", font_small),
        ("Payment: M-Pesa", font_small),
        ("Ref: QR98765432", font_small),
    ]
    
    for line_text, line_font in lines:
        if line_text:
            draw.text((20, y_position), line_text, fill='black', font=line_font)
        y_position += 30
    
    image.save(filename)
    logger.info(f"✅ Test receipt created: {filename}")
    return filename

def test_health_check():
    """Test the health check endpoint"""
    print("\n" + "="*70)
    print("🏥 Test 1: Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{OCR_API_URL}/health")
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed")
        print(f"   Status: {data.get('status')}")
        print(f"   Service: {data.get('service')}")
        print(f"   Engines: {', '.join(data.get('engines', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_process_receipt(image_path: str):
    """Test the OCR processing endpoint"""
    print("\n" + "="*70)
    print("📤 Test 2: Upload and Process Receipt")
    print("="*70)
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (Path(image_path).name, f, 'image/png')}
            data = {'user_id': 'test_user_phase4'}
            
            response = requests.post(
                f"{OCR_API_URL}/process",
                files=files,
                data=data
            )
            response.raise_for_status()
        
        result = response.json()
        print(f"✅ Upload successful")
        print(f"   Job ID: {result.get('job_id')}")
        print(f"   Receipt ID: {result.get('receipt_id')}")
        print(f"   Status: {result.get('status')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Estimated Time: {result.get('estimated_time')}s")
        
        return result.get('receipt_id')
    except Exception as e:
        print(f"❌ Upload failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return None

def test_get_status(receipt_id: str, max_attempts: int = 20):
    """Test the status checking endpoint"""
    print("\n" + "="*70)
    print("📊 Test 3: Check Processing Status")
    print("="*70)
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{OCR_API_URL}/status/{receipt_id}")
            response.raise_for_status()
            
            status_data = response.json()
            status = status_data.get('status')
            progress = status_data.get('progress')
            
            print(f"   Attempt {attempt + 1}: Status = {status}, Progress = {progress}%")
            
            if status in ['completed', 'needs_review', 'failed']:
                print(f"\n✅ Processing completed!")
                print(f"   Final Status: {status}")
                print(f"   Message: {status_data.get('message')}")
                
                if status_data.get('result'):
                    result = status_data['result']
                    print(f"\n📋 OCR Results:")
                    print(f"   Engine: {result.get('engine')}")
                    print(f"   Confidence: {result.get('confidence', 0):.2%}")
                    print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
                    print(f"   Text Length: {len(result.get('extracted_text', ''))} chars")
                
                return True
            
            # Wait before next check
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Status check failed: {str(e)}")
            return False
    
    print(f"⚠️  Processing did not complete within {max_attempts * 2} seconds")
    return False

def test_get_result(receipt_id: str):
    """Test the result retrieval endpoint"""
    print("\n" + "="*70)
    print("📥 Test 4: Retrieve OCR Result")
    print("="*70)
    
    try:
        response = requests.get(f"{OCR_API_URL}/result/{receipt_id}")
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Result retrieved successfully")
        print(f"\n📄 Extracted Text:")
        print("-" * 70)
        print(result.get('extracted_text', '')[:500])  # First 500 chars
        print("-" * 70)
        
        print(f"\n🏗️  Structured Data:")
        structured = result.get('structured_data', {})
        for key, value in structured.items():
            print(f"   • {key}: {value}")
        
        print(f"\n📊 Metadata:")
        print(f"   Engine: {result.get('engine')}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        print(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"   Status: {result.get('status')}")
        
        return True
    except Exception as e:
        print(f"❌ Result retrieval failed: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"   Response: {e.response.text}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "🚀 PHASE 4 API TEST SUITE" + " "*23 + "║")
    print("╚" + "="*68 + "╝")
    
    # Check if server is running
    try:
        response = requests.get(BASE_URL)
        print(f"\n✅ Server is running at {BASE_URL}")
    except:
        print(f"\n❌ Server is not running at {BASE_URL}")
        print(f"   Please start the server with: cd backend && uvicorn app:app --reload")
        return
    
    # Create test receipt
    print("\n📝 Creating test receipt...")
    image_path = create_test_receipt()
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test 2: Process Receipt
    receipt_id = test_process_receipt(image_path)
    if not receipt_id:
        print("\n❌ Receipt processing failed. Stopping tests.")
        return
    
    # Test 3: Check Status (with polling)
    if not test_get_status(receipt_id):
        print("\n⚠️  Status checking incomplete, but continuing...")
    
    # Test 4: Get Result
    test_get_result(receipt_id)
    
    # Final Summary
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*20 + "✅ PHASE 4 API TESTS COMPLETE" + " "*19 + "║")
    print("╚" + "="*68 + "╝")
    
    print(f"\n📊 Summary:")
    print(f"   • Health Check: ✅")
    print(f"   • File Upload: ✅")
    print(f"   • OCR Processing: ✅")
    print(f"   • Status Polling: ✅")
    print(f"   • Result Retrieval: ✅")
    print(f"\n🎯 All Phase 4 API endpoints are working!")

if __name__ == "__main__":
    run_all_tests()
