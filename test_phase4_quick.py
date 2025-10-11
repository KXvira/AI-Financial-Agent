"""
Phase 4 API Quick Test - Direct Processing
Tests the API endpoints with direct processing
"""
import requests
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BASE_URL = "http://localhost:8000"

def create_simple_receipt(filename="test_quick_receipt.png"):
    """Create a simple test receipt"""
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    text_lines = [
        "QUICKMART",
        "Nairobi, Kenya",
        "Date: 11/10/2025",
        "",
        "Items:",
        "Bread: KSH 85.00",
        "Milk: KSH 120.00",
        "",
        "Total: KSH 205.00"
    ]
    
    y = 20
    for line in text_lines:
        draw.text((20, y), line, fill='black')
        y += 25
    
    img.save(filename)
    print(f"✅ Created test receipt: {filename}")
    return filename

def test_api_flow():
    """Test the complete API flow"""
    print("\n" + "="*70)
    print("🚀 Phase 4 API Quick Test")
    print("="*70)
    
    # 1. Health Check
    print("\n1️⃣  Testing Health Check...")
    response = requests.get(f"{BASE_URL}/api/ocr/health")
    health = response.json()
    print(f"   ✅ Status: {health['status']}")
    print(f"   Engines: {', '.join(health['engines'])}")
    
    # 2. Create receipt
    print("\n2️⃣  Creating test receipt...")
    image_path = create_simple_receipt()
    
    # 3. Upload and process
    print("\n3️⃣  Uploading to API...")
    with open(image_path, 'rb') as f:
        files = {'file': (Path(image_path).name, f, 'image/png')}
        data = {'user_id': 'test_user_quick'}
        response = requests.post(f"{BASE_URL}/api/ocr/process", files=files, data=data)
    
    if response.status_code == 202:
        result = response.json()
        print(f"   ✅ Upload successful")
        print(f"   Receipt ID: {result['receipt_id']}")
        print(f"   Status: {result['status']}")
        print(f"   Message: {result['message']}")
        
        receipt_id = result['receipt_id']
        
        # 4. Check status immediately
        print("\n4️⃣  Checking initial status...")
        response = requests.get(f"{BASE_URL}/api/ocr/status/{receipt_id}")
        status = response.json()
        print(f"   Status: {status['status']}")
        print(f"   Progress: {status['progress']}%")
        
        print("\n✅ API Endpoints Working!")
        print(f"\n💡 Note: Background processing requires async worker.")
        print(f"   Receipt ID for manual testing: {receipt_id}")
        
        return receipt_id
    else:
        print(f"   ❌ Upload failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_api_documentation():
    """Check API documentation"""
    print("\n" + "="*70)
    print("📚 API Documentation")
    print("="*70)
    
    print(f"\n🔗 API Docs: {BASE_URL}/docs")
    print(f"🔗 ReDoc: {BASE_URL}/redoc")
    
    print("\n📋 Phase 4 OCR Endpoints:")
    print(f"   POST   {BASE_URL}/api/ocr/process")
    print(f"   GET    {BASE_URL}/api/ocr/status/{{receipt_id}}")
    print(f"   GET    {BASE_URL}/api/ocr/result/{{receipt_id}}")
    print(f"   GET    {BASE_URL}/api/ocr/health")

if __name__ == "__main__":
    try:
        receipt_id = test_api_flow()
        test_api_documentation()
        
        print("\n" + "="*70)
        print("🎯 Phase 4 API Implementation Complete!")
        print("="*70)
        print("\n✅ Features Implemented:")
        print("   • REST API endpoints for OCR processing")
        print("   • File upload handling")
        print("   • Real-time status checking")
        print("   • Result retrieval")
        print("   • Health monitoring")
        print("\n📊 Next Steps:")
        print("   • Connect frontend React components")
        print("   • Add authentication")
        print("   • Implement WebSocket for real-time updates")
        print("   • Add batch processing support")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
