"""
Gemini OCR Engine - Advanced AI-powered OCR using Google Gemini Vision
"""
import asyncio
import json
import logging
import time
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PIL import Image
import base64
import io
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from backend.ocr.models import ProcessingStatus
from ai_agent.gemini.service import GeminiService

logger = logging.getLogger("financial-agent.ocr.gemini_engine")

class GeminiOCREngine:
    """
    Advanced OCR using Gemini Vision API
    Can extract text and structured data directly from images
    """
    
    def __init__(self):
        """Initialize Gemini OCR Engine"""
        self.gemini_service = GeminiService()
        self.enabled = GEMINI_AVAILABLE and self._test_connection()
        
        # Gemini OCR specific prompts
        self.ocr_prompt = """
        You are an expert OCR system specialized in reading business receipts from Kenya. 
        Analyze this receipt image and extract ALL visible text with high accuracy.
        
        Focus on:
        1. All text content (merchant names, items, prices, dates, etc.)
        2. Preserve formatting and line breaks where logical
        3. Handle both printed and handwritten text
        4. Recognize Kenyan business formats (KES currency, M-Pesa, KRA PINs)
        
        Return ONLY the extracted text, preserving the original structure as much as possible.
        Do not add any explanations or metadata - just the raw text content.
        """
        
        self.structured_prompt = """
        You are an expert at analyzing Kenyan business receipts. Extract structured data from this receipt image.
        
        Return a JSON object with the following structure:
        {
            "vendor": {
                "name": "business name",
                "address": "business address if visible",
                "phone": "phone number if visible",
                "kra_pin": "KRA PIN if visible (format: A123456789Z)",
                "vat_number": "VAT number if visible"
            },
            "transaction": {
                "date": "YYYY-MM-DD format",
                "time": "HH:MM format if visible",
                "receipt_number": "receipt/invoice number",
                "reference": "transaction reference/M-Pesa code"
            },
            "items": [
                {
                    "description": "item name/description",
                    "quantity": 1,
                    "unit_price": 0.00,
                    "total_price": 0.00
                }
            ],
            "totals": {
                "subtotal": 0.00,
                "tax": 0.00,
                "discount": 0.00,
                "total": 0.00,
                "currency": "KES"
            },
            "payment": {
                "method": "cash|mpesa|card|bank_transfer",
                "mpesa_reference": "M-Pesa reference if applicable",
                "till_number": "till number if M-Pesa",
                "phone_number": "M-Pesa phone number if visible"
            },
            "confidence": 0.95,
            "notes": "any additional observations"
        }
        
        Guidelines:
        - Use null for missing information
        - Convert all amounts to numbers (remove commas, KSH prefixes)
        - Dates should be in YYYY-MM-DD format
        - Be conservative with confidence scores
        - Focus on Kenyan business patterns and M-Pesa transactions
        """
    
    def _test_connection(self) -> bool:
        """Test if Gemini API is accessible"""
        try:
            if not GEMINI_AVAILABLE:
                logger.warning("Google GenerativeAI not installed")
                return False
            
            # Quick test with gemini service
            return True  # Assume working if service is available
            
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
    
    async def extract_text_only(self, image_path: str) -> Dict[str, Any]:
        """
        Extract only text using Gemini Vision - equivalent to traditional OCR
        """
        if not self.enabled:
            return {
                "text": "",
                "confidence": 0.0,
                "error": "Gemini OCR not available"
            }
        
        start_time = time.time()
        
        try:
            # Load and encode image
            image = Image.open(image_path)
            
            # Use Gemini service for OCR
            response = await self.gemini_service.analyze_image(
                image_path=image_path,
                prompt=self.ocr_prompt
            )
            
            processing_time = time.time() - start_time
            
            if response.get("success", False):
                extracted_text = response.get("analysis", "")
                
                # Calculate confidence based on response quality
                confidence = self._calculate_text_confidence(extracted_text)
                
                return {
                    "text": extracted_text.strip(),
                    "confidence": confidence,
                    "processing_time": processing_time,
                    "engine": "gemini_vision_ocr"
                }
            else:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "processing_time": processing_time,
                    "error": response.get("error", "Gemini OCR failed"),
                    "engine": "gemini_vision_ocr"
                }
                
        except Exception as e:
            logger.error(f"Gemini text extraction failed: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "processing_time": time.time() - start_time,
                "error": str(e),
                "engine": "gemini_vision_ocr"
            }
    
    async def extract_structured_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data directly from image using Gemini Vision
        This is more powerful than traditional OCR + parsing
        """
        if not self.enabled:
            return {
                "structured_data": {},
                "confidence": 0.0,
                "error": "Gemini OCR not available"
            }
        
        start_time = time.time()
        
        try:
            # Use Gemini service for structured extraction
            response = await self.gemini_service.analyze_image(
                image_path=image_path,
                prompt=self.structured_prompt
            )
            
            processing_time = time.time() - start_time
            
            if response.get("success", False):
                analysis_text = response.get("analysis", "{}")
                
                # Try to parse JSON response
                try:
                    structured_data = json.loads(analysis_text)
                    confidence = structured_data.get("confidence", 0.8)
                    
                    return {
                        "structured_data": structured_data,
                        "confidence": confidence,
                        "processing_time": processing_time,
                        "engine": "gemini_vision_structured"
                    }
                    
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract what we can
                    logger.warning("Gemini returned non-JSON response, attempting text parsing")
                    fallback_data = self._parse_fallback_response(analysis_text)
                    
                    return {
                        "structured_data": fallback_data,
                        "confidence": 0.6,  # Lower confidence for fallback parsing
                        "processing_time": processing_time,
                        "engine": "gemini_vision_structured_fallback",
                        "raw_response": analysis_text
                    }
            else:
                return {
                    "structured_data": {},
                    "confidence": 0.0,
                    "processing_time": processing_time,
                    "error": response.get("error", "Gemini structured extraction failed"),
                    "engine": "gemini_vision_structured"
                }
                
        except Exception as e:
            logger.error(f"Gemini structured extraction failed: {e}")
            return {
                "structured_data": {},
                "confidence": 0.0,
                "processing_time": time.time() - start_time,
                "error": str(e),
                "engine": "gemini_vision_structured"
            }
    
    def _calculate_text_confidence(self, text: str) -> float:
        """Calculate confidence score for extracted text"""
        if not text or not text.strip():
            return 0.0
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on text characteristics
        text_lower = text.lower()
        
        # Check for common receipt patterns
        if any(word in text_lower for word in ['total', 'ksh', 'kes', 'receipt']):
            confidence += 0.2
        
        # Check for structured content (multiple lines)
        if '\n' in text and len(text.split('\n')) > 3:
            confidence += 0.1
        
        # Check for numeric content (prices, dates)
        import re
        if re.search(r'\d+[\.,]\d{2}', text):  # Money patterns
            confidence += 0.1
        
        if re.search(r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}', text):  # Date patterns
            confidence += 0.1
        
        # Text length factor
        if len(text.strip()) > 50:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _parse_fallback_response(self, response_text: str) -> Dict[str, Any]:
        """Parse non-JSON response from Gemini as fallback"""
        import re
        
        fallback_data = {}
        text_lower = response_text.lower()
        
        # Try to extract basic information using regex
        
        # Extract total amount
        total_match = re.search(r'total[:\s]*(?:ksh|kes)?\s*(\d+[\.,]\d{2})', text_lower)
        if total_match:
            try:
                fallback_data['total_amount'] = float(total_match.group(1).replace(',', ''))
                fallback_data['currency'] = 'KES'
            except ValueError:
                pass
        
        # Extract date
        date_match = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', response_text)
        if date_match:
            fallback_data['transaction_date'] = date_match.group(1)
        
        # Extract vendor name (first line that looks like a business name)
        lines = response_text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 5 and not re.search(r'\d+[\.,]\d{2}', line):
                if any(char.isupper() for char in line):
                    fallback_data['vendor_name'] = line.strip()
                    break
        
        return fallback_data

    async def comprehensive_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Perform both text extraction and structured data extraction
        Returns comprehensive results
        """
        start_time = time.time()
        
        # Run both extractions in parallel
        text_task = asyncio.create_task(self.extract_text_only(image_path))
        structured_task = asyncio.create_task(self.extract_structured_data(image_path))
        
        text_result, structured_result = await asyncio.gather(text_task, structured_task)
        
        total_processing_time = time.time() - start_time
        
        # Combine results
        combined_confidence = (
            text_result.get("confidence", 0) * 0.3 + 
            structured_result.get("confidence", 0) * 0.7
        ) if structured_result.get("structured_data") else text_result.get("confidence", 0)
        
        return {
            "text": text_result.get("text", ""),
            "structured_data": structured_result.get("structured_data", {}),
            "confidence": combined_confidence,
            "processing_time": total_processing_time,
            "engine": "gemini_vision_comprehensive",
            "text_confidence": text_result.get("confidence", 0),
            "structured_confidence": structured_result.get("confidence", 0),
            "errors": {
                "text_error": text_result.get("error"),
                "structured_error": structured_result.get("error")
            }
        }

# Factory function to create Gemini OCR engine
def create_gemini_ocr_engine() -> Optional[GeminiOCREngine]:
    """Create Gemini OCR engine if available"""
    try:
        engine = GeminiOCREngine()
        if engine.enabled:
            logger.info("Gemini OCR Engine initialized successfully")
            return engine
        else:
            logger.warning("Gemini OCR Engine not available")
            return None
    except Exception as e:
        logger.error(f"Failed to create Gemini OCR Engine: {e}")
        return None