"""
Celery Tasks for OCR Processing
"""
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any

from celery import current_task
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

from backend.celery_app import celery_app
from backend.ocr.enhanced_processor import EnhancedReceiptProcessor  
from backend.ocr.service import OCRService
from backend.database.mongodb import Database

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
        processor = EnhancedReceiptProcessor()
        
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
                'vendor': updated_receipt.vendor.name if updated_receipt.vendor else 'Unknown',
                'total_amount': updated_receipt.total_amount or 0.0,
                'date': updated_receipt.date.isoformat() if updated_receipt.date else None,
                'category': updated_receipt.category.value if updated_receipt.category else 'other',
                'confidence': updated_receipt.confidence or 0.0
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to process receipt {receipt_id}: {str(e)}")
        
        # Update receipt status to failed
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
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

@celery_app.task
def test_ocr_processing() -> Dict[str, Any]:
    """
    Test task to verify OCR processing pipeline
    """
    try:
        processor = EnhancedReceiptProcessor()
        
        # Create a simple test image with text
        from PIL import Image, ImageDraw, ImageFont
        import io
        import tempfile
        
        # Create test receipt image
        img = Image.new('RGB', (400, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add test text
        test_text = [
            "NAKUMATT SUPERMARKET",
            "PIN: A123456789B",
            "Date: 2024-10-11",
            "Time: 14:30",
            "",
            "1x Bread          KES 50.00",
            "2x Milk           KES 120.00",
            "1x Sugar          KES 80.00",
            "",
            "Total:            KES 250.00",
            "Payment: M-Pesa",
            "Ref: QW12345ABC"
        ]
        
        y_position = 50
        for line in test_text:
            draw.text((20, y_position), line, fill='black')
            y_position += 30
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            img.save(tmp_file.name)
            temp_path = tmp_file.name
        
        # Process with OCR
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(processor.process_receipt(temp_path))
        
        # Clean up
        Path(temp_path).unlink(missing_ok=True)
        loop.close()
        
        return {
            'status': 'success',
            'ocr_result': {
                'text_length': len(result.text),
                'confidence': result.confidence,
                'processing_time': result.processing_time,
                'engine': result.engine,
                'structured_data': result.structured_data if hasattr(result, 'structured_data') else {}
            }
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e)
        }