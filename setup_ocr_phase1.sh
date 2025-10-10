#!/bin/bash

# OCR Implementation Phase 1 Setup Script
# This script sets up the foundation for real OCR functionality

echo "🚀 Setting up OCR Implementation Phase 1..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Please activate your virtual environment first"
    echo "Run: source venv-fresh/bin/activate"
    exit 1
fi

echo "📦 Installing OCR dependencies..."

# Core OCR libraries
pip install opencv-python>=4.8.0
pip install pytesseract>=0.3.10
pip install easyocr>=1.7.0
pip install pdf2image>=1.16.3
pip install python-magic>=0.4.27

# Background processing
pip install redis>=4.5.0
pip install celery>=5.3.4

# Additional image processing
pip install scikit-image>=0.21.0
pip install numpy>=1.24.0

# System dependencies check
echo "🔍 Checking system dependencies..."

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. Installing..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
        sudo apt-get install -y libmagic1
        echo "✅ Tesseract installed for Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install tesseract
        brew install libmagic
        echo "✅ Tesseract installed for macOS"
    else
        echo "❌ Please install Tesseract manually for your OS"
        echo "Visit: https://github.com/tesseract-ocr/tesseract"
    fi
else
    echo "✅ Tesseract OCR found"
fi

# Check if Redis is running
if ! pgrep -x redis-server > /dev/null; then
    echo "⚠️  Redis server not running. Starting..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start redis-server
        sudo systemctl enable redis-server
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start redis
    fi
    
    echo "✅ Redis server started"
else
    echo "✅ Redis server running"
fi

# Create directory structure
echo "📁 Creating OCR directory structure..."

mkdir -p uploads/receipts
mkdir -p uploads/processed
mkdir -p uploads/temp
mkdir -p logs/ocr

echo "✅ Directories created"

# Create Celery configuration
echo "⚙️  Creating Celery configuration..."

cat > backend/celery_app.py << 'EOF'
"""
Celery Configuration for Background OCR Processing
"""
from celery import Celery
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "financial_agent_ocr",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["backend.ocr.tasks"]
)

# Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Nairobi",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Task routing
celery_app.conf.task_routes = {
    'backend.ocr.tasks.process_receipt_task': {'queue': 'ocr_processing'},
    'backend.ocr.tasks.batch_process_receipts': {'queue': 'batch_processing'},
}

if __name__ == "__main__":
    celery_app.start()
EOF

# Create OCR tasks file
echo "📝 Creating OCR tasks..."

cat > backend/ocr/tasks.py << 'EOF'
"""
Celery Tasks for OCR Processing
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from celery import current_task
from ..celery_app import celery_app
from .processor import ReceiptProcessor  
from .service import OCRService
from database.mongodb import Database

logger = logging.getLogger("financial-agent.ocr.tasks")

@celery_app.task(bind=True)
def process_receipt_task(self, receipt_id: str, user_id: str) -> Dict[str, Any]:
    """
    Background task to process a single receipt
    """
    try:
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'receipt_id': receipt_id, 'status': 'Starting OCR processing...'}
        )
        
        # Initialize services
        db = Database.get_instance()
        ocr_service = OCRService(db)
        processor = ReceiptProcessor()
        
        # Get receipt record
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        receipt = loop.run_until_complete(ocr_service.get_receipt(receipt_id))
        if not receipt:
            raise Exception(f"Receipt {receipt_id} not found")
        
        # Update status
        self.update_state(
            state='PROCESSING',
            meta={'receipt_id': receipt_id, 'status': 'Processing image...'}
        )
        
        # Process the receipt
        ocr_result = loop.run_until_complete(
            processor.process_receipt(receipt.file_path)
        )
        
        # Update status  
        self.update_state(
            state='PROCESSING',
            meta={'receipt_id': receipt_id, 'status': 'Extracting data with AI...'}
        )
        
        # Extract structured data with AI
        receipt_data = loop.run_until_complete(
            ocr_service.extract_receipt_data(ocr_result, receipt.file_path)
        )
        
        # Update receipt in database
        updated_receipt = loop.run_until_complete(
            ocr_service.update_receipt_from_ocr(receipt_id, receipt_data)
        )
        
        logger.info(f"Successfully processed receipt {receipt_id}")
        
        return {
            'receipt_id': receipt_id,
            'status': 'completed',
            'data': {
                'vendor': updated_receipt.vendor.name,
                'total_amount': updated_receipt.total_amount,
                'date': updated_receipt.date.isoformat(),
                'category': updated_receipt.category.value,
                'confidence': updated_receipt.confidence
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to process receipt {receipt_id}: {str(e)}")
        
        # Update receipt status to failed
        try:
            loop.run_until_complete(
                ocr_service.update_receipt_status(receipt_id, "failed")
            )
        except:
            pass
            
        return {
            'receipt_id': receipt_id,
            'status': 'failed',
            'error': str(e)
        }
    finally:
        if 'loop' in locals():
            loop.close()

@celery_app.task(bind=True)
def batch_process_receipts(self, receipt_ids: list, user_id: str) -> Dict[str, Any]:
    """
    Background task to process multiple receipts
    """
    results = []
    total_receipts = len(receipt_ids)
    
    for i, receipt_id in enumerate(receipt_ids):
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={
                'current': i + 1,
                'total': total_receipts,
                'status': f'Processing receipt {i + 1} of {total_receipts}'
            }
        )
        
        # Process individual receipt
        result = process_receipt_task.apply(args=[receipt_id, user_id])
        results.append(result.get())
    
    # Summary
    successful = len([r for r in results if r['status'] == 'completed'])
    failed = len([r for r in results if r['status'] == 'failed'])
    
    return {
        'status': 'completed',
        'summary': {
            'total': total_receipts,
            'successful': successful,
            'failed': failed
        },
        'results': results
    }
EOF

# Create enhanced processor
echo "🔧 Creating enhanced OCR processor..."

cat > backend/ocr/enhanced_processor.py << 'EOF'
"""
Enhanced OCR Processor with Multiple Engines
"""
import cv2
import numpy as np
import easyocr
import pytesseract
from PIL import Image
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re

from .models import OCRResult, ProcessingStatus

logger = logging.getLogger("financial-agent.ocr.enhanced_processor")

class EnhancedReceiptProcessor:
    """
    Advanced receipt processor with multiple OCR engines
    """
    
    def __init__(self):
        # Initialize OCR engines
        self.easyocr_reader = easyocr.Reader(['en'])
        
        # Tesseract configuration for receipts
        self.tesseract_config = (
            '--oem 3 --psm 6 '
            '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/:$ '
        )
        
        # Kenyan business patterns
        self.patterns = {
            'currency': [
                r'ksh[:\s]*(\d+[\.,]\d{2})',
                r'kes[:\s]*(\d+[\.,]\d{2})',
                r'(\d+[\.,]\d{2})\s*kes',
                r'total[:\s]*(\d+[\.,]\d{2})'
            ],
            'date': [
                r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',
                r'\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4}',
                r'\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}'
            ],
            'phone': [
                r'(?:\+254|0)[7]\d{8}',
                r'\d{4}\s*\d{3}\s*\d{3}',
                r'\d{10}'
            ],
            'mpesa_reference': [
                r'[A-Z]{2}\d{8}[A-Z]{2}',
                r'mpesa[:\s]*([A-Z0-9]{10})',
                r'ref[:\s]*([A-Z0-9]+)'
            ]
        }
    
    async def process_receipt(self, image_path: str) -> OCRResult:
        """
        Process receipt with multiple OCR engines
        """
        try:
            # Preprocess image
            processed_image_path = await self.preprocess_image(image_path)
            
            # Try multiple OCR engines
            ocr_results = []
            
            # 1. Tesseract OCR
            tesseract_result = await self.tesseract_ocr(processed_image_path)
            ocr_results.append(tesseract_result)
            
            # 2. EasyOCR (if Tesseract confidence is low)
            if tesseract_result.confidence < 0.7:
                easyocr_result = await self.easyocr_ocr(processed_image_path)
                ocr_results.append(easyocr_result)
            
            # Combine results
            final_result = self.combine_ocr_results(ocr_results)
            
            # Extract structured data
            structured_data = self.extract_structured_data(final_result.text)
            final_result.structured_data = structured_data
            
            return final_result
            
        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {str(e)}")
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                status=ProcessingStatus.FAILED,
                error=str(e)
            )
    
    async def preprocess_image(self, image_path: str) -> str:
        """
        Preprocess image for better OCR results
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Auto-rotate if needed
            gray = self.auto_rotate_image(gray)
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Enhance contrast
            enhanced = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(denoised)
            
            # Threshold
            _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Save processed image
            processed_path = str(Path(image_path).parent / f"processed_{Path(image_path).name}")
            cv2.imwrite(processed_path, thresh)
            
            return processed_path
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed, using original: {str(e)}")
            return image_path
    
    async def tesseract_ocr(self, image_path: str) -> OCRResult:
        """
        Extract text using Tesseract OCR
        """
        try:
            import time
            start_time = time.time()
            
            # Extract text
            text = pytesseract.image_to_string(
                Image.open(image_path),
                config=self.tesseract_config
            )
            
            # Get confidence
            data = pytesseract.image_to_data(
                Image.open(image_path),
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,  # Convert to 0-1 scale
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED,
                engine="tesseract"
            )
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                status=ProcessingStatus.FAILED,
                engine="tesseract",
                error=str(e)
            )
    
    async def easyocr_ocr(self, image_path: str) -> OCRResult:
        """
        Extract text using EasyOCR
        """
        try:
            import time
            start_time = time.time()
            
            # Extract text
            results = self.easyocr_reader.readtext(image_path)
            
            # Combine text and calculate confidence
            text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter low confidence results
                    text_parts.append(text)
                    confidences.append(confidence)
            
            full_text = '\n'.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                text=full_text,
                confidence=avg_confidence,
                processing_time=processing_time,
                status=ProcessingStatus.COMPLETED,
                engine="easyocr"
            )
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {str(e)}")
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                status=ProcessingStatus.FAILED,
                engine="easyocr",
                error=str(e)
            )
    
    def combine_ocr_results(self, results: List[OCRResult]) -> OCRResult:
        """
        Combine results from multiple OCR engines
        """
        # Filter successful results
        successful_results = [r for r in results if r.status == ProcessingStatus.COMPLETED]
        
        if not successful_results:
            return OCRResult(
                text="",
                confidence=0.0,
                processing_time=sum(r.processing_time for r in results),
                status=ProcessingStatus.FAILED,
                error="All OCR engines failed"
            )
        
        # Use the result with highest confidence
        best_result = max(successful_results, key=lambda r: r.confidence)
        
        # Combine processing times
        total_processing_time = sum(r.processing_time for r in results)
        
        return OCRResult(
            text=best_result.text,
            confidence=best_result.confidence,
            processing_time=total_processing_time,
            status=ProcessingStatus.COMPLETED,
            engine=f"combined({best_result.engine})"
        )
    
    def extract_structured_data(self, text: str) -> Dict[str, any]:
        """
        Extract structured data from OCR text
        """
        data = {}
        
        # Extract amounts
        amounts = self.extract_amounts(text)
        if amounts:
            data['amounts'] = amounts
            data['total_amount'] = max(amounts)  # Assume highest is total
        
        # Extract dates
        dates = self.extract_dates(text)
        if dates:
            data['dates'] = dates
        
        # Extract phone numbers
        phones = self.extract_phones(text)
        if phones:
            data['phone_numbers'] = phones
        
        # Extract M-Pesa references
        mpesa_refs = self.extract_mpesa_references(text)
        if mpesa_refs:
            data['mpesa_references'] = mpesa_refs
        
        return data
    
    def extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts from text"""
        amounts = []
        for pattern in self.patterns['currency']:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                try:
                    # Clean and convert amount
                    amount_str = match.replace(',', '.')
                    amount = float(amount_str)
                    amounts.append(amount)
                except ValueError:
                    continue
        return list(set(amounts))  # Remove duplicates
    
    def extract_dates(self, text: str) -> List[str]:
        """Extract dates from text"""
        dates = []
        for pattern in self.patterns['date']:
            matches = re.findall(pattern, text)
            dates.extend(matches)
        return list(set(dates))
    
    def extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        phones = []
        for pattern in self.patterns['phone']:
            matches = re.findall(pattern, text)
            phones.extend(matches)
        return list(set(phones))
    
    def extract_mpesa_references(self, text: str) -> List[str]:
        """Extract M-Pesa reference numbers"""
        refs = []
        for pattern in self.patterns['mpesa_reference']:
            matches = re.findall(pattern, text.upper())
            refs.extend(matches)
        return list(set(refs))
    
    def auto_rotate_image(self, image: np.ndarray) -> np.ndarray:
        """
        Auto-rotate image based on text orientation
        """
        try:
            # Get text orientation using Tesseract
            osd = pytesseract.image_to_osd(image)
            angle = int(re.search('(?<=Rotate: )\d+', osd).group(0))
            
            if angle != 0:
                # Rotate image
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                matrix = cv2.getRotationMatrix2D(center, -angle, 1.0)
                rotated = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return rotated
            
            return image
            
        except Exception:
            # If rotation detection fails, return original
            return image
EOF

# Update requirements.txt
echo "📋 Updating requirements..."

cat >> backend/requirements.txt << 'EOF'

# Enhanced OCR Dependencies (Phase 1)
easyocr>=1.7.0
pdf2image>=1.16.3
redis>=4.5.0
celery>=5.3.4
scikit-image>=0.21.0
prometheus_client>=0.17.0
EOF

# Create startup script for Celery worker
echo "🔄 Creating Celery worker startup script..."

cat > start_celery_worker.sh << 'EOF'
#!/bin/bash

# Start Celery Worker for OCR Processing
echo "🚀 Starting Celery worker for OCR processing..."

# Check if Redis is running
if ! pgrep -x redis-server > /dev/null; then
    echo "❌ Redis server not running. Please start Redis first."
    exit 1
fi

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔄 Activating virtual environment..."
    source venv-fresh/bin/activate
fi

# Start Celery worker
cd backend
celery -A celery_app worker --loglevel=info --queues=ocr_processing,batch_processing --concurrency=2

EOF

chmod +x start_celery_worker.sh

# Create monitoring script
echo "📊 Creating monitoring script..."

cat > monitor_ocr.py << 'EOF'
#!/usr/bin/env python3
"""
OCR Processing Monitor
"""
import redis
import json
import time
from datetime import datetime

def monitor_ocr_processing():
    """Monitor OCR processing status"""
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    print("🔍 OCR Processing Monitor")
    print("=" * 40)
    
    while True:
        try:
            # Get active tasks
            active_tasks = redis_client.keys('celery-task-meta-*')
            
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"📋 Active tasks: {len(active_tasks)}")
            
            # Show task details
            for task_key in active_tasks[:5]:  # Show first 5 tasks
                task_data = redis_client.get(task_key)
                if task_data:
                    try:
                        task_info = json.loads(task_data)
                        status = task_info.get('status', 'UNKNOWN')
                        result = task_info.get('result', {})
                        
                        if isinstance(result, dict):
                            receipt_id = result.get('receipt_id', 'N/A')
                            print(f"  📄 {receipt_id}: {status}")
                    except json.JSONDecodeError:
                        pass
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_ocr_processing()
EOF

chmod +x monitor_ocr.py

echo ""
echo "✅ OCR Implementation Phase 1 Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Test the setup:"
echo "   python -c 'import cv2, easyocr, pytesseract; print(\"✅ All OCR libraries imported successfully\")'"
echo ""
echo "2. Start Celery worker:"
echo "   ./start_celery_worker.sh"
echo ""  
echo "3. Monitor OCR processing:"
echo "   python monitor_ocr.py"
echo ""
echo "4. Test OCR endpoint with file upload:"
echo "   curl -X POST http://localhost:8000/api/receipts/upload -F 'file=@test_receipt.jpg'"
echo ""
echo "📚 Documentation created:"
echo "   - docs/OCR_ROADMAP.md (Complete implementation roadmap)"
echo "   - backend/ocr/enhanced_processor.py (Multi-engine OCR processor)"
echo "   - backend/ocr/tasks.py (Background processing tasks)"
echo "   - backend/celery_app.py (Celery configuration)"
echo ""
echo "🎯 Phase 1 Focus:"
echo "   - Enhanced OCR processing with multiple engines"
echo "   - Background task processing with Celery"
echo "   - Improved image preprocessing"
echo "   - Kenyan business receipt optimization"
echo ""