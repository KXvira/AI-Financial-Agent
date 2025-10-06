"""
OCR Service - Orchestrates receipt processing pipeline
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from ..database.mongodb import Database
from ..ai_agent.gemini.service import GeminiService
from .models import (
    Receipt, ReceiptCreate, ReceiptUpdate, OCRResult, 
    ProcessingStatus, ExpenseCategory, PaymentMethod,
    ExpenseFilter, ExpenseSummary, VerificationStatus
)
from .processor import ReceiptProcessor
from .uploader import FileUploader

logger = logging.getLogger("financial-agent.ocr.service")

class OCRService:
    """Main service for OCR receipt processing and expense management"""
    
    def __init__(self, db: Database, ai_service: Optional[GeminiService] = None):
        self.db = db
        self.ai_service = ai_service or GeminiService()
        self.processor = ReceiptProcessor()
        self.uploader = FileUploader()
        
        # Collections
        self.receipts_collection = "receipts"
        
    async def create_receipt_record(
        self, 
        user_id: str, 
        file_path: str, 
        original_filename: str,
        file_size: int,
        mime_type: str
    ) -> Receipt:
        """Create initial receipt record in database"""
        try:
            receipt = Receipt(
                user_id=user_id,
                file_path=file_path,
                original_filename=original_filename,
                file_size=file_size,
                mime_type=mime_type,
                total_amount=0.0,  # Will be updated after processing
                processing_status=ProcessingStatus.PENDING
            )
            
            # Save to database
            receipt_dict = receipt.dict()
            await self.db.create_document(self.receipts_collection, receipt_dict)
            
            logger.info(f"Receipt record created: {receipt.id}")
            return receipt
            
        except Exception as e:
            logger.error(f"Failed to create receipt record: {str(e)}")
            raise Exception(f"Failed to create receipt record: {str(e)}")
    
    async def process_receipt_async(self, receipt_id: str) -> Receipt:
        """Process receipt asynchronously with OCR and AI"""
        try:
            # Get receipt record
            receipt = await self.get_receipt(receipt_id)
            if not receipt:
                raise Exception(f"Receipt not found: {receipt_id}")
            
            # Update status to processing
            await self.update_receipt_status(receipt_id, ProcessingStatus.PROCESSING)
            
            # Step 1: OCR Processing
            image_path = Path(receipt.file_path)
            ocr_result = await self.processor.process_receipt(image_path)
            
            # Step 2: Parse basic receipt data
            parsed_data = await self.processor.parse_receipt_data(ocr_result)
            
            # Step 3: AI-enhanced processing
            ai_enhanced_data = await self._enhance_with_ai(ocr_result.raw_text, parsed_data)
            
            # Step 4: Update receipt with processed data
            updated_receipt = await self._update_receipt_with_processed_data(
                receipt_id, ocr_result, parsed_data, ai_enhanced_data
            )
            
            # Step 5: Determine final status
            final_status = ProcessingStatus.COMPLETED
            if ocr_result.confidence_score < 0.7:
                final_status = ProcessingStatus.NEEDS_REVIEW
            
            await self.update_receipt_status(receipt_id, final_status)
            
            logger.info(f"Receipt processing completed: {receipt_id}")
            return updated_receipt
            
        except Exception as e:
            logger.error(f"Receipt processing failed: {str(e)}")
            await self.update_receipt_status(receipt_id, ProcessingStatus.FAILED)
            raise Exception(f"Receipt processing failed: {str(e)}")
    
    async def _enhance_with_ai(self, raw_text: str, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to enhance and validate extracted data"""
        try:
            if not self.ai_service:
                return {}
            
            # Construct AI prompt for receipt analysis
            prompt = f\"\"\"
            Analyze this Kenyan receipt text and extract/enhance the following information:
            
            Raw OCR Text:
            {raw_text}
            
            Already parsed data:
            - Total Amount: {parsed_data.get('total_amount', 'Unknown')}
            - Date: {parsed_data.get('transaction_date', 'Unknown')}
            - Vendor: {parsed_data.get('vendor_info', {}).get('name', 'Unknown')}
            
            Please provide in JSON format:
            1. Vendor name (clean, proper capitalization)
            2. Expense category from: {', '.join([cat.value for cat in ExpenseCategory])}
            3. Payment method from: {', '.join([method.value for method in PaymentMethod])}
            4. Tax amount (if identifiable)
            5. Confidence score for the classification (0.0-1.0)
            6. Any corrections to the parsed data
            7. Business context (is this a business expense?)
            
            Focus on Kenyan business context and common expense types.
            \"\"\"
            
            # Get AI analysis
            ai_response = await self.ai_service.analyze_text(prompt)
            
            # Parse AI response (implement JSON extraction)
            ai_data = self._parse_ai_response(ai_response.response)
            
            return ai_data
            
        except Exception as e:
            logger.warning(f"AI enhancement failed: {str(e)}")
            return {}
    
    def _parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            import json
            import re
            
            # Try to extract JSON from response
            json_match = re.search(r'{.*}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                # Fallback: extract key information using regex
                data = {}
                
                # Extract category
                for category in ExpenseCategory:
                    if category.value.lower() in ai_response.lower():
                        data['category'] = category.value
                        break
                
                # Extract payment method
                for method in PaymentMethod:
                    if method.value.lower() in ai_response.lower():
                        data['payment_method'] = method.value
                        break
                
                return data
                
        except Exception as e:
            logger.warning(f"Failed to parse AI response: {str(e)}")
            return {}
    
    async def _update_receipt_with_processed_data(
        self, 
        receipt_id: str, 
        ocr_result: OCRResult,
        parsed_data: Dict[str, Any],
        ai_data: Dict[str, Any]
    ) -> Receipt:
        """Update receipt with all processed data"""
        try:
            update_data = {
                'ocr_result': ocr_result.dict(),
                'ai_extracted_data': ai_data,
                'processed_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Update basic extracted data
            if parsed_data.get('total_amount'):
                update_data['total_amount'] = parsed_data['total_amount']
            
            if parsed_data.get('transaction_date'):
                update_data['transaction_date'] = parsed_data['transaction_date']
            
            if parsed_data.get('vendor_info'):
                update_data['vendor'] = parsed_data['vendor_info']
            
            if parsed_data.get('receipt_number'):
                update_data['receipt_number'] = parsed_data['receipt_number']
            
            if parsed_data.get('items'):
                update_data['items'] = [item.dict() for item in parsed_data['items']]
            
            # Apply AI enhancements
            if ai_data.get('category'):
                try:
                    update_data['category'] = ExpenseCategory(ai_data['category'])
                except ValueError:
                    pass
            
            if ai_data.get('payment_method'):
                try:
                    update_data['payment_method'] = PaymentMethod(ai_data['payment_method'])
                except ValueError:
                    pass
            
            if ai_data.get('confidence_score'):
                update_data['classification_confidence'] = float(ai_data['confidence_score'])
            
            # Update in database
            await self.db.update_document(
                self.receipts_collection, 
                {"id": receipt_id}, 
                update_data
            )
            
            # Return updated receipt
            return await self.get_receipt(receipt_id)
            
        except Exception as e:
            logger.error(f"Failed to update receipt data: {str(e)}")
            raise Exception(f"Failed to update receipt data: {str(e)}")
    
    async def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        """Get receipt by ID"""
        try:
            doc = await self.db.find_one(self.receipts_collection, {"id": receipt_id})
            if doc:
                return Receipt(**doc)
            return None
        except Exception as e:
            logger.error(f"Failed to get receipt: {str(e)}")
            return None
    
    async def get_user_receipts(
        self, 
        user_id: str, 
        filters: Optional[ExpenseFilter] = None,
        limit: int = 50,
        skip: int = 0
    ) -> List[Receipt]:
        """Get receipts for a user with optional filtering"""
        try:
            query = {"user_id": user_id}
            
            # Apply filters
            if filters:
                if filters.start_date:
                    query["transaction_date"] = {"$gte": filters.start_date}
                if filters.end_date:
                    if "transaction_date" in query:
                        query["transaction_date"]["$lte"] = filters.end_date
                    else:
                        query["transaction_date"] = {"$lte": filters.end_date}
                
                if filters.category:
                    query["category"] = filters.category.value
                
                if filters.min_amount or filters.max_amount:
                    amount_query = {}
                    if filters.min_amount:
                        amount_query["$gte"] = filters.min_amount
                    if filters.max_amount:
                        amount_query["$lte"] = filters.max_amount
                    query["total_amount"] = amount_query
                
                if filters.vendor_name:
                    query["vendor.name"] = {"$regex": filters.vendor_name, "$options": "i"}
                
                if filters.payment_method:
                    query["payment_method"] = filters.payment_method.value
                
                if filters.verification_status:
                    query["verification_status"] = filters.verification_status.value
            
            docs = await self.db.find_many(
                self.receipts_collection, 
                query, 
                limit=limit, 
                skip=skip,
                sort=[("created_at", -1)]
            )
            
            return [Receipt(**doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Failed to get user receipts: {str(e)}")
            return []
    
    async def update_receipt(self, receipt_id: str, update_data: ReceiptUpdate) -> Optional[Receipt]:
        """Update receipt with user corrections"""
        try:
            update_dict = {}
            
            # Only update provided fields
            for field, value in update_data.dict(exclude_unset=True).items():
                if value is not None:
                    update_dict[field] = value
            
            update_dict['updated_at'] = datetime.now()
            
            if update_data.verification_status:
                update_dict['verification_status'] = update_data.verification_status.value
            
            await self.db.update_document(
                self.receipts_collection, 
                {"id": receipt_id}, 
                update_dict
            )
            
            return await self.get_receipt(receipt_id)
            
        except Exception as e:
            logger.error(f"Failed to update receipt: {str(e)}")
            return None
    
    async def delete_receipt(self, receipt_id: str, user_id: str) -> bool:
        """Delete receipt and associated file"""
        try:
            receipt = await self.get_receipt(receipt_id)
            if not receipt or receipt.user_id != user_id:
                return False
            
            # Delete file
            file_path = Path(receipt.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete from database
            result = await self.db.delete_document(
                self.receipts_collection, 
                {"id": receipt_id, "user_id": user_id}
            )
            
            return result > 0
            
        except Exception as e:
            logger.error(f"Failed to delete receipt: {str(e)}")
            return False
    
    async def get_expense_summary(
        self, 
        user_id: str, 
        filters: Optional[ExpenseFilter] = None
    ) -> ExpenseSummary:
        """Generate expense summary and analytics"""
        try:
            receipts = await self.get_user_receipts(user_id, filters, limit=1000)
            
            if not receipts:
                return ExpenseSummary(
                    total_amount=0.0,
                    total_count=0,
                    category_breakdown={},
                    monthly_trend=[],
                    top_vendors=[],
                    average_expense=0.0
                )
            
            # Calculate totals
            total_amount = sum(r.total_amount for r in receipts)
            total_count = len(receipts)
            average_expense = total_amount / total_count if total_count > 0 else 0
            
            # Category breakdown
            category_breakdown = {}
            for receipt in receipts:
                category = receipt.category.value
                category_breakdown[category] = category_breakdown.get(category, 0) + receipt.total_amount
            
            # Top vendors
            vendor_totals = {}
            for receipt in receipts:
                vendor_name = receipt.vendor.name or "Unknown"
                vendor_totals[vendor_name] = vendor_totals.get(vendor_name, 0) + receipt.total_amount
            
            top_vendors = [
                {"name": vendor, "amount": amount}
                for vendor, amount in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:10]
            ]
            
            # Monthly trend (simplified)
            monthly_trend = []  # TODO: Implement monthly aggregation
            
            return ExpenseSummary(
                total_amount=total_amount,
                total_count=total_count,
                category_breakdown=category_breakdown,
                monthly_trend=monthly_trend,
                top_vendors=top_vendors,
                average_expense=average_expense
            )
            
        except Exception as e:
            logger.error(f"Failed to generate expense summary: {str(e)}")
            return ExpenseSummary(
                total_amount=0.0,
                total_count=0,
                category_breakdown={},
                monthly_trend=[],
                top_vendors=[],
                average_expense=0.0
            )
    
    async def update_receipt_status(self, receipt_id: str, status: ProcessingStatus) -> bool:
        """Update receipt processing status"""
        try:
            await self.db.update_document(
                self.receipts_collection,
                {"id": receipt_id},
                {"processing_status": status.value, "updated_at": datetime.now()}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to update receipt status: {str(e)}")
            return False