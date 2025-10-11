#!/usr/bin/env python3
"""
Test OCR Processing Task
"""
import sys
import os
import time

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from backend.ocr.tasks import test_ocr_processing

def test_ocr_task():
    """Test the OCR processing task"""
    print("🧪 Testing OCR Processing Task")
    print("=" * 40)
    
    try:
        # Submit test task
        result = test_ocr_processing.delay()
        print(f"✅ Task submitted: {result.id}")
        print("🔄 Waiting for result...")
        
        # Wait for result (timeout after 60 seconds)
        task_result = result.get(timeout=60)
        
        print("✅ Task completed successfully!")
        print(f"📋 Result: {task_result}")
        
    except Exception as e:
        print(f"❌ Task failed: {e}")

if __name__ == "__main__":
    test_ocr_task()