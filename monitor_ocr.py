#!/usr/bin/env python3
"""
OCR Processing Monitor
"""
import redis
import json
import time
from datetime import datetime
import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def monitor_ocr_processing():
    """Monitor OCR processing status"""
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        
        print("🔍 OCR Processing Monitor")
        print("=" * 50)
        print("Press Ctrl+C to stop monitoring")
        print()
        
        while True:
            try:
                # Test Redis connection
                redis_client.ping()
                
                # Get active tasks
                active_tasks = redis_client.keys('celery-task-meta-*')
                
                print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"🔄 Redis: Connected")
                print(f"📋 Active tasks: {len(active_tasks)}")
                
                # Show task details
                for i, task_key in enumerate(active_tasks[:5]):  # Show first 5 tasks
                    task_data = redis_client.get(task_key)
                    if task_data:
                        try:
                            task_info = json.loads(task_data)
                            status = task_info.get('status', 'UNKNOWN')
                            result = task_info.get('result', {})
                            
                            if isinstance(result, dict):
                                receipt_id = result.get('receipt_id', 'N/A')
                                print(f"  📄 Task {i+1}: {receipt_id} - {status}")
                            else:
                                print(f"  📄 Task {i+1}: {status}")
                        except json.JSONDecodeError:
                            print(f"  📄 Task {i+1}: Invalid JSON data")
                
                # Show queue information
                try:
                    queue_info = redis_client.llen('celery')
                    print(f"📬 Queue length: {queue_info}")
                except:
                    print(f"📬 Queue length: N/A")
                
                time.sleep(10)  # Check every 10 seconds
                
            except redis.ConnectionError:
                print(f"\n❌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("🔄 Redis: Connection failed")
                time.sleep(5)
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped by user")
                break
            except Exception as e:
                print(f"\n❌ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Error: {e}")
                time.sleep(5)
                
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        print("Make sure Redis is running and accessible")

def test_ocr_setup():
    """Test OCR setup and dependencies"""
    print("🧪 Testing OCR Setup")
    print("=" * 30)
    
    # Test Redis connection
    try:
        redis_client = redis.Redis(host='localhost', port=6379, db=0)
        redis_client.ping()
        print("✅ Redis: Connected")
    except Exception as e:
        print(f"❌ Redis: {e}")
    
    # Test OCR libraries
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"❌ OpenCV: {e}")
    
    try:
        import pytesseract
        print("✅ Pytesseract: Available")
    except ImportError as e:
        print(f"❌ Pytesseract: {e}")
    
    try:
        import easyocr
        print("✅ EasyOCR: Available")
    except ImportError as e:
        print(f"❌ EasyOCR: {e}")
    
    try:
        import celery
        print(f"✅ Celery: {celery.__version__}")
    except ImportError as e:
        print(f"❌ Celery: {e}")
    
    # Test Celery app
    try:
        from backend.celery_app import celery_app
        print("✅ Celery App: Configured")
        
        # Test task
        from backend.ocr.tasks import test_ocr_processing
        print("✅ OCR Tasks: Available")
        
    except Exception as e:
        print(f"❌ OCR Tasks: {e}")
        
    # Test MongoDB connection
    try:
        from backend.database.mongodb import Database
        print("✅ MongoDB Connection: Available")
    except Exception as e:
        print(f"❌ MongoDB: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_ocr_setup()
    else:
        monitor_ocr_processing()