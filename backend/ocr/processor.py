"""
Receipt Processing Pipeline with OpenCV and Tesseract OCR
"""
import cv2
import numpy as np
import pytesseract
from PIL import Image
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
import re
from datetime import datetime

from .models import OCRResult, ExpenseItem, VendorInfo

logger = logging.getLogger("financial-agent.ocr.processor")

class ReceiptProcessor:
    """Process receipt images using OCR and image preprocessing"""
    
    def __init__(self):
        # OCR configuration
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/: '
        
        # Text extraction patterns
        self.patterns = {
            'total': [
                r'total[:\s]*(\d+[\.,]\d{2})',
                r'amount[:\s]*(\d+[\.,]\d{2})',
                r'ksh[:\s]*(\d+[\.,]\d{2})',
                r'(\d+[\.,]\d{2})\s*total'
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
            'amount': r'(\d+[\.,]\d{2})',
            'receipt_number': [
                r'receipt[:\s#]*(\w+)',
                r'ref[:\s#]*(\w+)',
                r'transaction[:\s#]*(\w+)'
            ]
        }
    
    async def process_receipt(self, image_path: Path) -> OCRResult:
        """Main receipt processing pipeline"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing receipt: {image_path}")
            
            # Step 1: Load and preprocess image
            processed_image = await self._preprocess_image(image_path)
            
            # Step 2: Extract text using OCR
            raw_text = await self._extract_text(processed_image)
            
            # Step 3: Calculate confidence score
            confidence = await self._calculate_confidence(raw_text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create OCR result
            ocr_result = OCRResult(
                raw_text=raw_text,
                confidence_score=confidence,
                processing_time=processing_time,
                preprocessed=True
            )
            
            logger.info(f"OCR processing completed. Confidence: {confidence:.2f}")
            return ocr_result
            
        except Exception as e:
            logger.error(f"Receipt processing error: {str(e)}")
            raise Exception(f"Failed to process receipt: {str(e)}")
    
    async def _preprocess_image(self, image_path: Path) -> np.ndarray:
        """Preprocess image for better OCR results"""
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Enhance contrast using CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Apply Gaussian blur to smooth noise
            blurred = cv2.GaussianBlur(enhanced, (1, 1), 0)
            
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            logger.debug("Image preprocessing completed")
            return processed
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {str(e)}")
            # Fallback to original image
            return cv2.imread(str(image_path))
    
    async def _extract_text(self, image: np.ndarray) -> str:
        """Extract text from preprocessed image using Tesseract"""
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(
                pil_image,
                config=self.tesseract_config,
                lang='eng'
            )
            
            # Clean up extracted text
            cleaned_text = self._clean_text(text)
            
            logger.debug(f"Extracted text length: {len(cleaned_text)} characters")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Text extraction error: {str(e)}")
            return ""
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove non-printable characters except newlines
        cleaned = re.sub(r'[^\x20-\x7E\n]', '', cleaned)
        
        return cleaned
    
    async def _calculate_confidence(self, text: str) -> float:
        """Calculate confidence score based on text quality"""
        if not text or len(text) < 10:
            return 0.0
        
        score = 0.0
        factors = []
        
        # Check for common receipt elements
        if self._extract_total_amount(text):
            score += 0.3
            factors.append("total_found")
        
        if self._extract_vendor_info(text).name:
            score += 0.2
            factors.append("vendor_found")
        
        if self._extract_date(text):
            score += 0.2
            factors.append("date_found")
        
        # Text quality metrics
        word_count = len(text.split())
        if word_count > 20:
            score += 0.1
            factors.append("sufficient_text")
        
        # Check for numeric patterns (prices, amounts)
        amount_matches = len(re.findall(self.patterns['amount'], text))
        if amount_matches > 0:
            score += min(0.2, amount_matches * 0.05)
            factors.append(f"{amount_matches}_amounts")
        
        logger.debug(f"Confidence factors: {factors}")
        return min(1.0, score)
    
    def _extract_total_amount(self, text: str) -> Optional[float]:
        """Extract total amount from text"""
        for pattern in self.patterns['total']:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    amount_str = match.group(1).replace(',', '.')
                    return float(amount_str)
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract transaction date from text"""
        for pattern in self.patterns['date']:
            match = re.search(pattern, text)
            if match:
                date_str = match.group(0)
                # Try to parse various date formats
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y', '%Y/%m/%d', '%Y-%m-%d']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
        return None
    
    def _extract_vendor_info(self, text: str) -> VendorInfo:
        """Extract vendor information from text"""
        vendor_info = VendorInfo()
        
        # Extract phone numbers
        for pattern in self.patterns['phone']:
            match = re.search(pattern, text)
            if match:
                vendor_info.phone = match.group(0)
                break
        
        # Extract potential business name (first few lines of text)
        lines = text.split('\n')[:5]  # Check first 5 lines
        for line in lines:
            line = line.strip()
            if len(line) > 5 and not re.match(r'^\d+[\.,]\d{2}$', line):
                # Skip lines that are just amounts
                if not re.search(r'total|amount|ksh|receipt|date', line.lower()):
                    vendor_info.name = line
                    break
        
        # Set confidence based on found information
        confidence = 0.0
        if vendor_info.name:
            confidence += 0.6
        if vendor_info.phone:
            confidence += 0.4
        
        vendor_info.confidence_score = confidence
        return vendor_info
    
    async def parse_receipt_data(self, ocr_result: OCRResult) -> Dict[str, Any]:
        """Parse structured data from OCR text"""
        text = ocr_result.raw_text
        
        parsed_data = {
            'total_amount': self._extract_total_amount(text),
            'transaction_date': self._extract_date(text),
            'vendor_info': self._extract_vendor_info(text),
            'receipt_number': self._extract_receipt_number(text),
            'items': await self._extract_items(text)
        }
        
        logger.info("Receipt data parsing completed")
        return parsed_data
    
    def _extract_receipt_number(self, text: str) -> Optional[str]:
        """Extract receipt number from text"""
        for pattern in self.patterns['receipt_number']:
            match = re.search(pattern, text.lower())
            if match:
                return match.group(1)
        return None
    
    async def _extract_items(self, text: str) -> list:
        """Extract individual items from receipt text"""
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for lines with price patterns
            amount_matches = re.findall(self.patterns['amount'], line)
            if amount_matches:
                # Extract the last amount as the total price
                try:
                    price = float(amount_matches[-1].replace(',', '.'))
                    description = re.sub(self.patterns['amount'], '', line).strip()
                    
                    if description and len(description) > 2:
                        item = ExpenseItem(
                            description=description,
                            total_price=price,
                            confidence_score=0.7  # Default confidence for parsed items
                        )
                        items.append(item)
                except ValueError:
                    continue
        
        return items