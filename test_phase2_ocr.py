#!/usr/bin/env python3
"""
Phase 2 OCR Testing Script
Test the enhanced multi-engine OCR processing with advanced preprocessing
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

from backend.ocr.enhanced_processor import EnhancedReceiptProcessor
from backend.ocr.models import ProcessingStatus

async def test_phase2_ocr():
    """Test Phase 2 OCR enhancements"""
    print("🚀 Phase 2 OCR Enhancement Testing")
    print("=" * 50)
    
    # Initialize processor
    processor = EnhancedReceiptProcessor()
    print(f"✅ Processor initialized")
    print(f"📊 Multi-engine enabled: {processor.multi_engine_enabled}")
    print(f"🔧 Preprocessing enabled: {processor.preprocessing_enabled}")
    print(f"📈 Confidence threshold: {processor.confidence_threshold}")
    print()
    
    # Test with a dummy image path (we'll create a test receipt)
    test_image_path = create_test_receipt_image()
    
    if not test_image_path:
        print("❌ Could not create test image")
        return
    
    print(f"🖼️  Test image created: {test_image_path}")
    print()
    
    # Process receipt with Phase 2 enhancements
    print("🔄 Processing receipt with Phase 2 enhancements...")
    start_time = time.time()
    
    try:
        result = await processor.process_receipt(test_image_path)
        processing_time = time.time() - start_time
        
        print("=" * 50)
        print("📋 PHASE 2 OCR RESULTS")
        print("=" * 50)
        print(f"Status: {result.status.value}")
        print(f"Engine: {result.engine}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Processing Time: {processing_time:.2f}s")
        print()
        
        if result.status == ProcessingStatus.COMPLETED:
            print("📄 Extracted Text:")
            print("-" * 30)
            print(result.text[:500] + ("..." if len(result.text) > 500 else ""))
            print()
            
            if result.structured_data:
                print("🏗️  Structured Data (Phase 2 Enhanced):")
                print("-" * 40)
                for key, value in result.structured_data.items():
                    if value:
                        print(f"  {key}: {value}")
            
            print()
            print("✅ Phase 2 OCR processing completed successfully!")
            
        else:
            print(f"❌ Processing failed: {result.error}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Cleanup
    try:
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        processed_path = str(os.path.dirname(test_image_path)) + f"/processed_phase2_{os.path.basename(test_image_path)}"
        if os.path.exists(processed_path):
            os.remove(processed_path)
    except:
        pass

def create_test_receipt_image():
    """Create a simple test receipt image"""
    try:
        import cv2
        import numpy as np
        
        # Create a white image
        height, width = 400, 300
        image = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Add some text (simulating a receipt)
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        color = (0, 0, 0)  # Black
        thickness = 1
        
        receipt_lines = [
            "JAVA HOUSE COFFEE",
            "WESTGATE MALL",
            "Nairobi, Kenya",
            "PIN: A123456789Z",
            "",
            "Date: 11/10/2025",
            "Time: 14:30",
            "",
            "1x Cappuccino     KSH 350.00",
            "1x Sandwich       KSH 450.00",
            "",
            "Subtotal:         KSH 800.00",
            "VAT (16%):        KSH 128.00",
            "Total:            KSH 928.00",
            "",
            "Payment: M-Pesa",
            "Ref: QR12345678",
            "",
            "Thank you!"
        ]
        
        y_start = 30
        line_height = 20
        
        for i, line in enumerate(receipt_lines):
            y = y_start + i * line_height
            if y < height - 20:  # Ensure text fits in image
                cv2.putText(image, line, (20, y), font, font_scale, color, thickness)
        
        # Save test image
        test_path = os.path.join(project_root, "test_receipt_phase2.png")
        cv2.imwrite(test_path, image)
        
        return test_path
        
    except Exception as e:
        print(f"❌ Could not create test image: {e}")
        return None

async def test_individual_components():
    """Test individual Phase 2 components"""
    print("\n🧪 Testing Individual Phase 2 Components")
    print("=" * 50)
    
    processor = EnhancedReceiptProcessor()
    
    # Test pattern scoring
    test_text = """
    JAVA HOUSE COFFEE
    PIN: A123456789Z
    Total: KSH 928.00
    M-Pesa Ref: QR12345678
    Date: 11/10/2025
    """
    
    pattern_score = processor.calculate_receipt_pattern_score(test_text)
    print(f"📊 Pattern Recognition Score: {pattern_score:.2%}")
    
    # Test structured data extraction
    structured_data = processor.extract_structured_data_phase2(test_text)
    print(f"🏗️  Phase 2 Structured Data Fields: {len(structured_data)}")
    
    for key, value in structured_data.items():
        if value:
            print(f"  ✅ {key}: {value}")

if __name__ == "__main__":
    print("🎯 Starting Phase 2 OCR Testing Suite")
    print()
    
    # Run main test
    asyncio.run(test_phase2_ocr())
    
    # Run component tests
    asyncio.run(test_individual_components())
    
    print("\n🏁 Phase 2 testing completed!")