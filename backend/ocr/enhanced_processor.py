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
import time

from .models import OCRResult, ProcessingStatus

logger = logging.getLogger("financial-agent.ocr.enhanced_processor")

class EnhancedReceiptProcessor:
    """
    Advanced receipt processor with multiple OCR engines
    """
    
    def __init__(self):
        # Initialize OCR engines
        try:
            self.easyocr_reader = easyocr.Reader(['en'])
            logger.info("EasyOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR: {str(e)}")
            self.easyocr_reader = None
        
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
            
            # 2. EasyOCR (if Tesseract confidence is low and EasyOCR is available)
            if tesseract_result.confidence < 0.7 and self.easyocr_reader:
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
            if not self.easyocr_reader:
                raise Exception("EasyOCR reader not initialized")
                
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
            angle = int(re.search(r'(?<=Rotate: )\d+', osd).group(0))
            
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