"""
Database Model for Storing OCR Results
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class OCRResult(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    image_path: str
    status: str
    engine: str
    confidence: float
    processing_time: float
    text: str
    structured_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "image_path": "/path/to/image.png",
                "status": "completed",
                "engine": "phase2_combined(2_engines)",
                "confidence": 0.72,
                "processing_time": 7.62,
                "text": "Extracted text here...",
                "structured_data": {
                    "total_amount": 928.0,
                    "vendor_name": "JAVA HOUSE COFFEE"
                }
            }
        }
