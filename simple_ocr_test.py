#!/usr/bin/env python3
"""
Simple OCR Task Test - Non-blocking
"""
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from backend.ocr.tasks import test_ocr_processing

def test_ocr_submit():
    """Submit OCR test task without waiting"""
    print("🧪 Simple OCR Task Test")
    print("=" * 30)
    
    try:
        # Submit test task
        result = test_ocr_processing.delay()
        print(f"✅ Task submitted successfully!")
        print(f"📋 Task ID: {result.id}")
        print(f"🔄 Task State: {result.state}")
        
        # Quick check if ready (non-blocking)
        if result.ready():
            print(f"✅ Task completed: {result.get()}")
        else:
            print("⏳ Task is processing in background...")
            print("💡 Use 'python monitor_ocr.py' to monitor progress")
            
    except Exception as e:
        print(f"❌ Task submission failed: {e}")

if __name__ == "__main__":
    test_ocr_submit()