"""
Phase 4: OCR API Router
Enhanced API endpoints for OCR processing with real-time updates
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel
import logging
import os
from pathlib import Path
import tempfile
import uuid

import sys
import os

# Add backend directory to Python path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from database.mongodb import Database
from ocr.service import OCRService
from ocr.models import ProcessingStatus

logger = logging.getLogger("financial-agent.ocr.api")

# Response Models
class OCRProcessRequest(BaseModel):
    """Request model for OCR processing"""
    file_name: str
    user_id: Optional[str] = "default_user"

class OCRProcessResponse(BaseModel):
    """Response model for OCR processing"""
    job_id: str
    receipt_id: str
    status: str
    message: str
    estimated_time: int  # seconds

class OCRResultResponse(BaseModel):
    """Response model for OCR results"""
    receipt_id: str
    status: str
    confidence: float
    processing_time: float
    engine: str
    extracted_text: str
    structured_data: Dict[str, Any]
    error: Optional[str] = None

class OCRStatusResponse(BaseModel):
    """Response model for processing status"""
    receipt_id: str
    status: str
    progress: int  # 0-100
    message: str
    result: Optional[OCRResultResponse] = None

# Router
router = APIRouter(
    prefix="/api/ocr",
    tags=["Phase 4 OCR API"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

def get_db() -> Database:
    """Get database instance"""
    return Database.get_instance()

def get_ocr_service(db: Database = Depends(get_db)) -> OCRService:
    """Get OCR service instance"""
    return OCRService(db)

@router.post(
    "/process",
    response_model=OCRProcessResponse,
    status_code=202,
    summary="Process image with Phase 2 OCR",
    description="Upload and process an image using Phase 2 multi-engine OCR (Gemini + Tesseract + EasyOCR)"
)
async def process_ocr_image(
    file: UploadFile = File(...),
    user_id: str = "default_user",
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: OCRService = Depends(get_ocr_service)
):
    """
    Process an uploaded image file for OCR
    
    - **file**: Image file (PNG, JPG, JPEG, PDF)
    - **user_id**: User identifier (optional)
    - **Returns**: Job ID and receipt ID for tracking
    """
    try:
        # Validate file type
        allowed_extensions = {'.png', '.jpg', '.jpeg', '.pdf'}
        file_ext = Path(file.filename).suffix.lower() if file.filename else ''
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Save uploaded file temporarily
        temp_dir = tempfile.gettempdir()
        file_id = str(uuid.uuid4())
        temp_path = Path(temp_dir) / f"ocr_{file_id}{file_ext}"
        
        content = await file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded: {file.filename} -> {temp_path}")
        
        # Create receipt record
        receipt = await service.create_receipt_record(
            user_id=user_id,
            file_path=str(temp_path),
            original_filename=file.filename or "unknown",
            file_size=len(content),
            mime_type=file.content_type or "unknown"
        )
        
        # Schedule background processing
        background_tasks.add_task(
            service.process_receipt_async,
            receipt.id
        )
        
        logger.info(f"OCR processing scheduled for receipt: {receipt.id}")
        
        return OCRProcessResponse(
            job_id=file_id,
            receipt_id=receipt.id,
            status="processing",
            message="OCR processing started. Use /status/{receipt_id} to check progress.",
            estimated_time=8
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing OCR request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process image: {str(e)}"
        )

@router.get(
    "/status/{receipt_id}",
    response_model=OCRStatusResponse,
    summary="Get OCR processing status",
    description="Check the status of an OCR processing job"
)
async def get_ocr_status(
    receipt_id: str,
    service: OCRService = Depends(get_ocr_service)
):
    """
    Get the processing status of a receipt
    
    - **receipt_id**: Receipt identifier from /process endpoint
    - **Returns**: Current status, progress, and results (if complete)
    """
    try:
        # Get receipt from database
        receipt = await service.get_receipt(receipt_id)
        
        if not receipt:
            raise HTTPException(
                status_code=404,
                detail=f"Receipt not found: {receipt_id}"
            )
        
        # Determine progress percentage
        status_progress = {
            ProcessingStatus.PENDING: 10,
            ProcessingStatus.PROCESSING: 50,
            ProcessingStatus.COMPLETED: 100,
            ProcessingStatus.NEEDS_REVIEW: 100,
            ProcessingStatus.FAILED: 100
        }
        
        progress = status_progress.get(receipt.processing_status, 0)
        
        # Build response
        response = OCRStatusResponse(
            receipt_id=receipt_id,
            status=receipt.processing_status.value if hasattr(receipt.processing_status, 'value') else str(receipt.processing_status),
            progress=progress,
            message=f"Processing status: {receipt.processing_status}"
        )
        
        # If processing is complete, include results
        if receipt.processing_status in [ProcessingStatus.COMPLETED, ProcessingStatus.NEEDS_REVIEW]:
            # Get OCR result from database
            if receipt.ocr_result:
                ocr_data = receipt.ocr_result
                response.result = OCRResultResponse(
                    receipt_id=receipt_id,
                    status=ocr_data.get('status', 'completed'),
                    confidence=ocr_data.get('confidence', 0.0),
                    processing_time=ocr_data.get('processing_time', 0.0),
                    engine=ocr_data.get('engine', 'unknown'),
                    extracted_text=ocr_data.get('text', ''),
                    structured_data=ocr_data.get('structured_data', {}),
                    error=ocr_data.get('error')
                )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OCR status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get status: {str(e)}"
        )

@router.get(
    "/result/{receipt_id}",
    response_model=OCRResultResponse,
    summary="Get OCR processing result",
    description="Retrieve the complete OCR processing result for a receipt"
)
async def get_ocr_result(
    receipt_id: str,
    service: OCRService = Depends(get_ocr_service)
):
    """
    Get the complete OCR result for a processed receipt
    
    - **receipt_id**: Receipt identifier
    - **Returns**: Complete OCR result with extracted text and structured data
    """
    try:
        # Get receipt from database
        receipt = await service.get_receipt(receipt_id)
        
        if not receipt:
            raise HTTPException(
                status_code=404,
                detail=f"Receipt not found: {receipt_id}"
            )
        
        # Check if processing is complete
        if receipt.processing_status not in [ProcessingStatus.COMPLETED, ProcessingStatus.NEEDS_REVIEW, ProcessingStatus.FAILED]:
            raise HTTPException(
                status_code=400,
                detail=f"Processing not complete. Current status: {receipt.processing_status}"
            )
        
        # Get OCR result
        if not receipt.ocr_result:
            raise HTTPException(
                status_code=404,
                detail="OCR result not found"
            )
        
        ocr_data = receipt.ocr_result
        
        return OCRResultResponse(
            receipt_id=receipt_id,
            status=ocr_data.get('status', 'completed'),
            confidence=ocr_data.get('confidence', 0.0),
            processing_time=ocr_data.get('processing_time', 0.0),
            engine=ocr_data.get('engine', 'unknown'),
            extracted_text=ocr_data.get('text', ''),
            structured_data=ocr_data.get('structured_data', {}),
            error=ocr_data.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting OCR result: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get result: {str(e)}"
        )

@router.get(
    "/health",
    summary="Health check",
    description="Check if the OCR service is running"
)
async def health_check(service: OCRService = Depends(get_ocr_service)):
    """
    Health check endpoint
    
    - **Returns**: Service status and configuration
    """
    try:
        return {
            "status": "healthy",
            "service": "Phase 4 OCR API",
            "features": {
                "multi_engine": True,
                "gemini_ai": True,
                "database_integration": True,
                "real_time_status": True
            },
            "engines": ["Gemini Vision", "Tesseract", "EasyOCR"]
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
