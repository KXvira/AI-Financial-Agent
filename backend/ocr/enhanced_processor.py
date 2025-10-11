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
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .models import OCRResult, ProcessingStatus
from .gemini_ocr_engine import create_gemini_ocr_engine
from dataclasses import dataclass

logger = logging.getLogger("financial-agent.ocr.enhanced_processor")

@dataclass
class Phase2OCRResult:
    """Phase 2 OCR Result with enhanced fields"""
    text: str
    confidence: float
    processing_time: float
    status: ProcessingStatus = ProcessingStatus.COMPLETED
    engine: str = "phase2_enhanced"
    error: Optional[str] = None
    structured_data: Optional[Dict[str, any]] = None

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
        
        # Initialize Gemini OCR Engine
        self.gemini_ocr = create_gemini_ocr_engine()
        if self.gemini_ocr:
            logger.info("Gemini OCR Engine initialized successfully")
        else:
            logger.warning("Gemini OCR Engine not available")
        
        # Tesseract configuration for receipts
        self.tesseract_config = (
            '--oem 3 --psm 6 '
            '-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,-/:$ '
        )
        
        # Phase 2: Advanced preprocessing settings
        self.preprocessing_enabled = True
        self.multi_engine_enabled = True
        self.confidence_threshold = 0.7
        self.use_gemini_ocr = True  # Enable Gemini OCR by default
        
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
            # Phase 2: Advanced preprocessing pipeline
            processed_image_path = await self.preprocess_image(image_path)
            
            # Phase 2: Intelligent multi-engine processing with Gemini
            ocr_results = []
            
            # 1. Gemini Vision OCR (if available and enabled) - Most advanced
            gemini_result = None
            if self.use_gemini_ocr and self.gemini_ocr:
                try:
                    gemini_result = await self.gemini_ocr_advanced(image_path)  # Use original image for Gemini
                    ocr_results.append(gemini_result)
                    logger.info(f"Gemini OCR confidence: {gemini_result.confidence_score:.2%}")
                except Exception as e:
                    logger.warning(f"Gemini OCR failed, falling back to traditional OCR: {e}")
            
            # 2. Primary: Tesseract OCR with receipt-optimized config
            tesseract_result = await self.tesseract_ocr_advanced(processed_image_path)
            ocr_results.append(tesseract_result)
            
            # 3. Secondary: EasyOCR (if confidence is still low)
            best_confidence = max(r.confidence_score for r in ocr_results) if ocr_results else 0
            if self.multi_engine_enabled and self.easyocr_reader and best_confidence < self.confidence_threshold:
                easyocr_result = await self.easyocr_ocr_advanced(processed_image_path)
                ocr_results.append(easyocr_result)
            
            # Phase 2: Intelligent result combination
            final_result = self.combine_ocr_results_advanced(ocr_results)
            
            # Phase 2: Enhanced structured data extraction with Kenyan patterns
            structured_data = self.extract_structured_data_phase2(final_result.text)
            
            # Add structured data to result
            final_result.structured_data = structured_data
            
            return final_result
            
        except Exception as e:
            logger.error(f"OCR processing failed for {image_path}: {str(e)}")
            return Phase2OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                status=ProcessingStatus.FAILED,
                engine="phase2_enhanced",
                error=str(e)
            )
    
    async def preprocess_image(self, image_path: str) -> str:
        """
        Phase 2: Advanced image preprocessing pipeline
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Phase 2.1: Perspective correction
            image = self.correct_perspective(image)
            
            # Phase 2.2: Shadow removal
            image = self.remove_shadows(image)
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Phase 2.3: Auto-rotate with improved detection
            gray = self.auto_rotate_image_advanced(gray)
            
            # Phase 2.4: Advanced denoising
            denoised = self.advanced_denoise(gray)
            
            # Phase 2.5: Multi-stage contrast enhancement
            enhanced = self.multi_stage_enhance_contrast(denoised)
            
            # Phase 2.6: Adaptive thresholding
            thresh = self.adaptive_threshold(enhanced)
            
            # Phase 2.7: Morphological operations for text cleanup
            cleaned = self.morphological_cleanup(thresh)
            
            # Save processed image
            processed_path = str(Path(image_path).parent / f"processed_phase2_{Path(image_path).name}")
            cv2.imwrite(processed_path, cleaned)
            
            logger.info(f"Phase 2 preprocessing completed: {processed_path}")
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
    
    # ==================== PHASE 2: ENHANCED OCR METHODS ====================
    
    async def tesseract_ocr_advanced(self, image_path: str) -> OCRResult:
        """
        Phase 2: Advanced Tesseract OCR with receipt-specific optimizations
        """
        start_time = time.time()
        
        try:
            # Phase 2.1: Multiple configuration attempts for receipts
            configs = [
                '--oem 3 --psm 6',  # Default for receipts
                '--oem 3 --psm 4',  # Single text column
                '--oem 3 --psm 8',  # Single word
                '--oem 3 --psm 7',  # Single text line
            ]
            
            best_result = None
            best_confidence = 0
            
            for config in configs:
                try:
                    # Extract text with current config
                    text = pytesseract.image_to_string(
                        Image.open(image_path),
                        config=config
                    )
                    
                    # Get confidence data
                    data = pytesseract.image_to_data(
                        Image.open(image_path),
                        config=config,
                        output_type=pytesseract.Output.DICT
                    )
                    
                    # Calculate confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Keep best result
                    if avg_confidence > best_confidence:
                        best_confidence = avg_confidence
                        best_result = text
                        
                except Exception as e:
                    logger.warning(f"Tesseract config {config} failed: {e}")
                    continue
            
            if best_result is None:
                raise Exception("All Tesseract configurations failed")
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                raw_text=best_result.strip(),
                confidence_score=best_confidence / 100.0,
                processing_time=processing_time,
                preprocessed=True
            )
            
        except Exception as e:
            logger.error(f"Advanced Tesseract OCR failed: {str(e)}")
            return OCRResult(
                raw_text="",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                preprocessed=True
            )
    
    async def easyocr_ocr_advanced(self, image_path: str) -> OCRResult:
        """
        Phase 2: Advanced EasyOCR with receipt optimization
        """
        start_time = time.time()
        
        try:
            if not self.easyocr_reader:
                raise Exception("EasyOCR not initialized")
            
            # Phase 2.1: Multi-parameter EasyOCR
            results = []
            
            # Configuration 1: Standard
            try:
                result1 = self.easyocr_reader.readtext(
                    image_path,
                    detail=1,
                    paragraph=False,
                    width_ths=0.7,
                    height_ths=0.7
                )
                results.append(("standard", result1))
                
            except Exception as e:
                logger.warning(f"EasyOCR standard config failed: {e}")
            
            # Configuration 2: Receipt optimized
            try:
                result2 = self.easyocr_reader.readtext(
                    image_path,
                    detail=1,
                    paragraph=True,
                    width_ths=0.5,
                    height_ths=0.5,
                    x_ths=0.1,
                    y_ths=0.1
                )
                results.append(("receipt_optimized", result2))
                
            except Exception as e:
                logger.warning(f"EasyOCR receipt config failed: {e}")
            
            if not results:
                raise Exception("All EasyOCR configurations failed")
            
            # Phase 2.2: Choose best result based on confidence and text length
            best_config = None
            best_text = ""
            best_confidence = 0
            
            for config_name, easyocr_result in results:
                # Extract text and average confidence
                text_parts = []
                confidences = []
                
                for (bbox, text, conf) in easyocr_result:
                    text_parts.append(text)
                    confidences.append(conf)
                
                combined_text = '\n'.join(text_parts)
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # Score = confidence * text_length_factor
                text_score = len(combined_text.strip()) * 0.01  # Length bonus
                total_score = avg_confidence + text_score
                
                if total_score > best_confidence:
                    best_confidence = avg_confidence  # Use actual confidence, not score
                    best_text = combined_text
                    best_config = config_name
            
            processing_time = time.time() - start_time
            
            return OCRResult(
                raw_text=best_text.strip(),
                confidence_score=best_confidence,
                processing_time=processing_time,
                preprocessed=True
            )
            
        except Exception as e:
            logger.error(f"Advanced EasyOCR failed: {str(e)}")
            return OCRResult(
                raw_text="",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                preprocessed=True
            )
    
    async def gemini_ocr_advanced(self, image_path: str) -> OCRResult:
        """
        Phase 2: Advanced Gemini Vision OCR with structured data extraction
        """
        start_time = time.time()
        
        try:
            if not self.gemini_ocr:
                raise Exception("Gemini OCR not available")
            
            # Use Gemini's comprehensive analysis (text + structured data)
            result = await self.gemini_ocr.comprehensive_analysis(image_path)
            
            processing_time = time.time() - start_time
            
            if result.get("text") or result.get("structured_data"):
                confidence = result.get("confidence", 0.8)
                text = result.get("text", "")
                
                # If we have structured data, enhance the text with key information
                structured_data = result.get("structured_data", {})
                if structured_data and not text:
                    # Generate text from structured data if no raw text
                    text = self._generate_text_from_structured_data(structured_data)
                
                return OCRResult(
                    raw_text=text,
                    confidence_score=confidence,
                    processing_time=processing_time,
                    preprocessed=True
                )
            else:
                raise Exception("No text or structured data extracted")
                
        except Exception as e:
            logger.error(f"Gemini OCR failed: {str(e)}")
            return OCRResult(
                raw_text="",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                preprocessed=True
            )
    
    def _generate_text_from_structured_data(self, structured_data: Dict[str, Any]) -> str:
        """Generate text representation from structured data"""
        lines = []
        
        # Vendor information
        vendor = structured_data.get("vendor", {})
        if vendor.get("name"):
            lines.append(vendor["name"])
        if vendor.get("address"):
            lines.append(vendor["address"])
        if vendor.get("kra_pin"):
            lines.append(f"PIN: {vendor['kra_pin']}")
        
        lines.append("")  # Empty line
        
        # Transaction info
        transaction = structured_data.get("transaction", {})
        if transaction.get("date"):
            lines.append(f"Date: {transaction['date']}")
        if transaction.get("time"):
            lines.append(f"Time: {transaction['time']}")
        
        lines.append("")  # Empty line
        
        # Items
        items = structured_data.get("items", [])
        for item in items:
            if item.get("description"):
                item_line = item["description"]
                if item.get("total_price"):
                    item_line += f" - KSH {item['total_price']:.2f}"
                lines.append(item_line)
        
        # Totals
        totals = structured_data.get("totals", {})
        if totals.get("total"):
            lines.append("")
            lines.append(f"Total: KSH {totals['total']:.2f}")
        
        # Payment info
        payment = structured_data.get("payment", {})
        if payment.get("method"):
            lines.append(f"Payment: {payment['method']}")
        if payment.get("mpesa_reference"):
            lines.append(f"M-Pesa Ref: {payment['mpesa_reference']}")
        
        return "\n".join(lines)
    
    def combine_ocr_results_advanced(self, results: List[OCRResult]) -> Phase2OCRResult:
        """
        Phase 2: Intelligent OCR result combination with validation
        """
        # Filter successful results - OCRResult doesn't have status field, assume all are completed
        successful_results = results
        
        if not successful_results:
            return Phase2OCRResult(
                text="",
                confidence=0.0,
                processing_time=0.0,
                status=ProcessingStatus.FAILED,
                error="All OCR engines failed"
            )
        
        if len(successful_results) == 1:
            # Convert single OCRResult to Phase2OCRResult
            single_result = successful_results[0]
            return Phase2OCRResult(
                text=single_result.raw_text,
                confidence=single_result.confidence_score,
                processing_time=single_result.processing_time,
                status=ProcessingStatus.COMPLETED,
                engine="single_engine"
            )
        
        # Phase 2.1: Advanced combination strategy
        # Score each result based on multiple factors
        scored_results = []
        
        for result in successful_results:
            score = 0
            
            # Factor 1: Confidence (40% weight)
            score += result.confidence_score * 0.4
            
            # Factor 2: Text length (20% weight) - longer usually better for receipts
            text_length_score = min(len(result.raw_text) / 1000, 1.0)  # Normalize to 0-1
            score += text_length_score * 0.2
            
            # Factor 3: Receipt pattern matches (30% weight)
            pattern_score = self.calculate_receipt_pattern_score(result.raw_text)
            score += pattern_score * 0.3
            
            # Factor 4: Base engine reliability (10% weight)
            engine_score = 0.8  # Default score since we don't have engine info in OCRResult
            score += engine_score * 0.1
            
            scored_results.append((score, result))
        
        # Get best result
        best_score, best_result = max(scored_results, key=lambda x: x[0])
        
        # Phase 2.2: Text merging for complementary results
        merged_text = best_result.raw_text
        if len(successful_results) > 1:
            # Merge unique information from other results
            merged_text = self.merge_complementary_text(successful_results, best_result)
        
        # Combine processing times
        total_processing_time = sum(r.processing_time for r in results)
        
        # Return Phase2OCRResult
        return Phase2OCRResult(
            text=merged_text,
            confidence=best_result.confidence_score,
            processing_time=total_processing_time,
            status=ProcessingStatus.COMPLETED,
            engine=f"phase2_combined({len(successful_results)}_engines)"
        )
    
    def calculate_receipt_pattern_score(self, text: str) -> float:
        """Calculate how well text matches receipt patterns"""
        score = 0.0
        text_lower = text.lower()
        
        # Check for currency patterns
        for pattern in self.patterns['currency']:
            if re.search(pattern, text_lower):
                score += 0.2
                break
        
        # Check for date patterns
        for pattern in self.patterns['date']:
            if re.search(pattern, text_lower):
                score += 0.2
                break
        
        # Check for common Kenyan vendors
        for vendor in self.patterns.get('common_vendors', []):
            if vendor in text_lower:
                score += 0.3
                break
        
        # Check for business registration patterns
        for pattern in self.patterns.get('tax_numbers', []):
            if re.search(pattern, text_lower):
                score += 0.15
                break
        
        # Check for transaction references
        for pattern in self.patterns.get('mpesa', []):
            if re.search(pattern, text_lower):
                score += 0.15
                break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def merge_complementary_text(self, results: List[OCRResult], primary_result: OCRResult) -> str:
        """Merge unique information from multiple OCR results"""
        primary_text = primary_result.raw_text
        
        # Find unique lines from other results
        primary_lines = set(line.strip().lower() for line in primary_text.split('\n') if line.strip())
        
        additional_lines = []
        for result in results:
            if result == primary_result:
                continue
                
            for line in result.raw_text.split('\n'):
                line_clean = line.strip()
                if line_clean and line_clean.lower() not in primary_lines:
                    # Check if this line contains useful information
                    if self.is_useful_receipt_line(line_clean):
                        additional_lines.append(line_clean)
                        primary_lines.add(line_clean.lower())
        
        # Combine texts
        if additional_lines:
            return primary_text + '\n' + '\n'.join(additional_lines)
        
        return primary_text
    
    def is_useful_receipt_line(self, line: str) -> bool:
        """Check if a line contains useful receipt information"""
        line_lower = line.lower()
        
        # Skip very short lines
        if len(line.strip()) < 3:
            return False
        
        # Check for useful patterns
        useful_patterns = [
            r'\d+[\.,]\d{2}',  # Money amounts
            r'\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}',  # Dates
            r'(total|subtotal|tax|vat|pin|receipt|transaction)',  # Key terms
            r'[a-z0-9]{8,}',  # Reference numbers
        ]
        
        for pattern in useful_patterns:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def extract_structured_data_phase2(self, text: str) -> Dict[str, any]:
        """
        Phase 2: Enhanced structured data extraction with Kenyan patterns
        """
        structured_data = self.extract_structured_data(text)  # Start with basic extraction
        
        # Phase 2.1: Enhanced Kenyan business patterns
        enhanced_patterns = {
            'vendor_name': [
                r'(?:^|\n)([A-Z][A-Z\s&.,-]{2,30}?)(?:\n|$)',  # Capitalized business names
                r'(?:business|company|ltd|limited|shop)[:\s]*([^\n\r]+)',
            ],
            'kra_pin': [
                r'pin[:\s]*([a-z]\d{9}[a-z])',
                r'kra[:\s]*pin[:\s]*([a-z]\d{9}[a-z])',
                r'tax[:\s]*pin[:\s]*([a-z]\d{9}[a-z])',
            ],
            'vat_number': [
                r'vat[:\s]*no[:\s]*(\d{10})',
                r'vat[:\s]*(\d{10})',
            ],
            'mpesa_reference': [
                r'mpesa[:\s]*(?:ref|reference|code)[:\s]*([a-z0-9]{8,12})',
                r'transaction[:\s]*(?:ref|reference|id)[:\s]*([a-z0-9]{8,12})',
                r'ref[:\s]*no[:\s]*([a-z0-9]{8,12})',
            ],
            'phone_mpesa': [
                r'(?:from|to)[:\s]*(\d{10})',
                r'(?:07\d{8}|01\d{8}|\+254\d{9})',
            ],
            'till_number': [
                r'till[:\s]*(?:no|number)[:\s]*(\d{5,7})',
                r'paybill[:\s]*(\d{5,7})',
            ]
        }
        
        # Extract enhanced patterns
        for key, patterns in enhanced_patterns.items():
            if key not in structured_data or not structured_data[key]:
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        structured_data[key] = matches[0] if isinstance(matches[0], str) else matches[0][0]
                        break
        
        # Phase 2.2: Enhanced amount extraction with Kenyan currency
        amount_patterns = [
            r'total[:\s]*(?:ksh|kes)[:\s]*(\d+[\.,]\d{2})',
            r'total[:\s]*(\d+[\.,]\d{2})',
            r'amount[:\s]*(?:ksh|kes)[:\s]*(\d+[\.,]\d{2})', 
            r'(?:ksh|kes)[:\s]*(\d+[\.,]\d{2})',
            r'(\d+[\.,]\d{2})[:\s]*(?:ksh|kes)',
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                # Convert to float and find the largest amount (likely total)
                amounts = []
                for match in matches:
                    try:
                        amount = float(match.replace(',', ''))
                        amounts.append(amount)
                    except ValueError:
                        continue
                
                if amounts:
                    structured_data['total_amount'] = max(amounts)
                    structured_data['currency'] = 'KES'
                    break
        
        # Phase 2.3: Date extraction with Kenyan formats
        date_patterns = [
            r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{2,4})',
            r'date[:\s]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                structured_data['transaction_date'] = matches[0]
                break
        
        return structured_data
    
    def validate_and_score_result(self, result: OCRResult) -> OCRResult:
        """
        Phase 2: Validate and score the final result
        """
        # Validation checks
        validation_score = 1.0
        
        # Check 1: Text length
        if len(result.raw_text.strip()) < 10:
            validation_score -= 0.3
        
        # Check 2: Receipt patterns
        pattern_score = self.calculate_receipt_pattern_score(result.raw_text)
        validation_score = validation_score * 0.7 + pattern_score * 0.3
        
        # Check 3: Structured data completeness
        if result.structured_data:
            required_fields = ['total_amount', 'transaction_date', 'vendor_name']
            found_fields = sum(1 for field in required_fields if result.structured_data.get(field))
            completeness_score = found_fields / len(required_fields)
            validation_score = validation_score * 0.8 + completeness_score * 0.2
        
        # Update confidence with validation
        result.confidence_score = min(result.confidence_score * validation_score, 1.0)
        
        return result

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
            raw_text=best_result.raw_text,
            confidence_score=best_result.confidence_score,
            processing_time=total_processing_time,
            preprocessed=True
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
    
    # ==================== PHASE 2: ADVANCED PREPROCESSING METHODS ====================
    
    def correct_perspective(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.1: Automatic perspective correction for receipts
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour
            for contour in sorted(contours, key=cv2.contourArea, reverse=True):
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                if len(approx) == 4:
                    # Found a quadrilateral - assume it's the receipt
                    points = approx.reshape(4, 2).astype(np.float32)
                    
                    # Order points: top-left, top-right, bottom-right, bottom-left
                    rect = self.order_points(points)
                    
                    # Calculate dimensions
                    (tl, tr, br, bl) = rect
                    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
                    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
                    max_width = max(int(width_a), int(width_b))
                    
                    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
                    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
                    max_height = max(int(height_a), int(height_b))
                    
                    # Destination points
                    dst = np.array([
                        [0, 0],
                        [max_width - 1, 0],
                        [max_width - 1, max_height - 1],
                        [0, max_height - 1]], dtype=np.float32)
                    
                    # Perspective transform
                    matrix = cv2.getPerspectiveTransform(rect, dst)
                    warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
                    
                    return warped
            
            # If no quadrilateral found, return original
            return image
            
        except Exception as e:
            logger.warning(f"Perspective correction failed: {e}")
            return image
    
    def order_points(self, pts: np.ndarray) -> np.ndarray:
        """Helper to order points for perspective correction"""
        rect = np.zeros((4, 2), dtype=np.float32)
        
        # Sum and difference to find corners
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]  # top-left
        rect[2] = pts[np.argmax(s)]  # bottom-right
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]  # top-right
        rect[3] = pts[np.argmax(diff)]  # bottom-left
        
        return rect
    
    def remove_shadows(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.2: Remove shadows and uneven lighting
        """
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            
            # Merge channels
            lab = cv2.merge([l, a, b])
            
            # Convert back to BGR
            result = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            
            return result
            
        except Exception as e:
            logger.warning(f"Shadow removal failed: {e}")
            return image
    
    def auto_rotate_image_advanced(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.3: Advanced auto-rotation with multiple methods
        """
        try:
            # Method 1: Try Tesseract OSD
            try:
                osd = pytesseract.image_to_osd(image)
                angle = int(re.search(r'(?<=Rotate: )\d+', osd).group(0))
                if angle != 0:
                    return self.rotate_image(image, -angle)
            except:
                pass
            
            # Method 2: Use Hough lines to detect text orientation
            edges = cv2.Canny(image, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for line in lines:
                    rho, theta = line[0]
                    angle = theta * 180 / np.pi
                    # Convert to -90 to 90 range
                    if angle > 90:
                        angle -= 180
                    angles.append(angle)
                
                # Find most common angle
                if angles:
                    median_angle = np.median(angles)
                    if abs(median_angle) > 2:  # Only rotate if significant
                        return self.rotate_image(image, -median_angle)
            
            return image
            
        except Exception as e:
            logger.warning(f"Advanced auto-rotation failed: {e}")
            return image
    
    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """Helper to rotate image by given angle"""
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def advanced_denoise(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.4: Multi-stage denoising
        """
        try:
            # Stage 1: Non-local means denoising
            denoised = cv2.fastNlMeansDenoising(image, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # Stage 2: Bilateral filter for edge preservation
            bilateral = cv2.bilateralFilter(denoised, 9, 75, 75)
            
            # Stage 3: Gaussian blur for final smoothing
            smoothed = cv2.GaussianBlur(bilateral, (3, 3), 0)
            
            return smoothed
            
        except Exception as e:
            logger.warning(f"Advanced denoising failed: {e}")
            return cv2.fastNlMeansDenoising(image)
    
    def multi_stage_enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.5: Multi-stage contrast enhancement
        """
        try:
            # Stage 1: Histogram equalization
            equalized = cv2.equalizeHist(image)
            
            # Stage 2: CLAHE with optimal parameters for receipts
            clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
            clahe_result = clahe.apply(image)
            
            # Stage 3: Combine both methods with weighted average
            alpha = 0.3  # Weight for histogram equalization
            beta = 0.7   # Weight for CLAHE
            combined = cv2.addWeighted(equalized, alpha, clahe_result, beta, 0)
            
            # Stage 4: Gamma correction for final adjustment
            gamma = 1.2
            gamma_corrected = np.array(255 * (combined / 255) ** (1.0 / gamma), dtype=np.uint8)
            
            return gamma_corrected
            
        except Exception as e:
            logger.warning(f"Multi-stage contrast enhancement failed: {e}")
            return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(image)
    
    def adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.6: Adaptive thresholding for varying lighting
        """
        try:
            # Method 1: Adaptive Gaussian threshold
            adaptive_gaussian = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Method 2: Adaptive mean threshold
            adaptive_mean = cv2.adaptiveThreshold(
                image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Method 3: Otsu's threshold
            _, otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Combine methods - use the one with better text preservation
            # For receipts, Gaussian adaptive usually works best
            return adaptive_gaussian
            
        except Exception as e:
            logger.warning(f"Adaptive thresholding failed: {e}")
            return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    def morphological_cleanup(self, image: np.ndarray) -> np.ndarray:
        """
        Phase 2.7: Morphological operations for text cleanup
        """
        try:
            # Remove small noise
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
            
            # Close gaps in text
            kernel = np.ones((1, 2), np.uint8)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel)
            
            # Dilate to strengthen text
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.dilate(cleaned, kernel, iterations=1)
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Morphological cleanup failed: {e}")
            return image