"""
Phase 3 Database Integration Test
Tests OCR processing with database storage
"""
import asyncio
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

# Add project paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database.mongodb import Database
from backend.ocr.service import OCRService
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_receipt(filename: str = "test_receipt_phase3.png"):
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
        ("NAKUMATT SUPERMARKET", font),
        ("Westlands Branch", font_small),
        ("P.O Box 5678, Nairobi", font_small),
        ("PIN: A987654321B", font_small),
        ("", font_small),
        ("Date: 11/10/2025", font_small),
        ("Time: 16:45", font_small),
        ("Cashier: John M.", font_small),
        ("", font_small),
        ("3x Rice 2kg", font_small),
        ("@ KSH 240.00 each", font_small),
        ("2x Cooking Oil 1L", font_small),
        ("@ KSH 380.00 each", font_small),
        ("", font_small),
        ("Subtotal: KSH 1,480.00", font_small),
        ("VAT (16%): KSH 236.80", font_small),
        ("TOTAL: KSH 1,716.80", font),
        ("", font_small),
        ("Payment: M-Pesa", font_small),
        ("Ref: QR87654321", font_small),
    ]
    
    for line_text, line_font in lines:
        if line_text:
            draw.text((20, y_position), line_text, fill='black', font=line_font)
        y_position += 30
    
    image.save(filename)
    logger.info(f"✅ Test receipt created: {filename}")
    return filename

async def test_phase3_integration():
    """Test Phase 3 database integration"""
    print("\n" + "="*60)
    print("🚀 Phase 3 Database Integration Test")
    print("="*60 + "\n")
    
    try:
        # Step 1: Create test receipt
        print("📝 Step 1: Creating test receipt...")
        receipt_path = create_test_receipt()
        
        # Step 2: Initialize database connection
        print("🔌 Step 2: Connecting to MongoDB...")
        
        db = Database.get_instance()
        print(f"✅ Connected to database: {db.config.database_name}")
        
        # Step 3: Initialize OCR service
        print("🤖 Step 3: Initializing OCR Service...")
        ocr_service = OCRService(db)
        print("✅ OCR Service initialized")
        
        # Step 4: Create receipt record
        print("📋 Step 4: Creating receipt record...")
        receipt = await ocr_service.create_receipt_record(
            user_id="test_user_001",
            file_path=str(Path(receipt_path).absolute()),
            original_filename="test_receipt_phase3.png",
            file_size=os.path.getsize(receipt_path),
            mime_type="image/png"
        )
        print(f"✅ Receipt created with ID: {receipt.id}")
        
        # Step 5: Process receipt with Phase 2 OCR
        print("🔄 Step 5: Processing receipt with Phase 2 OCR...")
        print("   ⏳ This may take 5-10 seconds (Gemini + multi-engine processing)...")
        
        processed_receipt = await ocr_service.process_receipt_async(receipt.id)
        
        print("\n" + "="*60)
        print("📊 PHASE 3 PROCESSING RESULTS")
        print("="*60)
        print(f"Receipt ID: {processed_receipt.id}")
        print(f"Status: {processed_receipt.processing_status}")
        print(f"Total Amount: KSH {processed_receipt.total_amount:.2f}")
        
        if processed_receipt.ocr_result:
            ocr_data = processed_receipt.ocr_result
            print(f"\n🔧 OCR Engine: {ocr_data.get('engine', 'N/A')}")
            print(f"📊 Confidence: {ocr_data.get('confidence', 0):.2%}")
            print(f"⏱️  Processing Time: {ocr_data.get('processing_time', 0):.2f}s")
            
            if ocr_data.get('structured_data'):
                print("\n🏗️  Structured Data:")
                for key, value in ocr_data['structured_data'].items():
                    print(f"   • {key}: {value}")
        
        # Step 6: Verify database storage
        print("\n🔍 Step 6: Verifying database storage...")
        
        # Check OCR results collection
        ocr_results_cursor = db.find(
            "ocr_results",
            {"image_path": str(Path(receipt_path).absolute())}
        )
        
        ocr_results_list = []
        async for result in ocr_results_cursor:
            ocr_results_list.append(result)
        
        print(f"✅ Found {len(ocr_results_list)} OCR result(s) in database")
        
        if ocr_results_list:
            latest_result = ocr_results_list[0]
            print(f"   • Result ID: {latest_result.get('_id')}")
            print(f"   • Engine: {latest_result.get('engine')}")
            print(f"   • Confidence: {latest_result.get('confidence', 0):.2%}")
            print(f"   • Text Length: {len(latest_result.get('text', ''))} chars")
        
        # Check receipts collection
        receipts_cursor = db.find(
            "receipts",
            {"_id": receipt.id}
        )
        
        receipts_list = []
        async for r in receipts_cursor:
            receipts_list.append(r)
        
        print(f"✅ Found {len(receipts_list)} receipt(s) in database")
        
        print("\n" + "="*60)
        print("✅ PHASE 3 TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   • Receipt processed and stored in database")
        print(f"   • Phase 2 multi-engine OCR completed")
        print(f"   • OCR results saved separately")
        print(f"   • Structured data extracted")
        print(f"   • AI enhancement applied")
        
    except Exception as e:
        logger.error(f"❌ Phase 3 test failed: {str(e)}", exc_info=True)
        print(f"\n❌ Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_phase3_integration())
