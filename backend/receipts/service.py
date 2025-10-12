"""
Receipt Service

Core business logic for receipt generation and management.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from bson import ObjectId
import os

from .models import (
    Receipt, ReceiptGenerateRequest, ReceiptType, ReceiptStatus,
    PaymentMethod, TaxBreakdown, LineItem, CustomerInfo,
    ReceiptSequence, ReceiptAuditLog, ReceiptTemplate,
    ReceiptMetadata, ReceiptStatistics
)
from .pdf_generator import ReceiptPDFGenerator
from .qr_generator import QRCodeGenerator
from backend.database.mongodb import Database


class ReceiptService:
    """Service for receipt generation and management"""
    
    def __init__(self, db: Database):
        """
        Initialize receipt service
        
        Args:
            db: Database instance
        """
        self.db = db
        self.receipts_collection = db.db["receipts"]
        self.sequences_collection = db.db["receipt_sequences"]
        self.audit_log_collection = db.db["receipt_audit_log"]
        self.templates_collection = db.db["receipt_templates"]
        
        self.pdf_generator = ReceiptPDFGenerator()
        self.qr_generator = QRCodeGenerator()
        
        # PDF storage path
        self.pdf_storage_path = os.path.join(os.getcwd(), "storage", "receipts")
        os.makedirs(self.pdf_storage_path, exist_ok=True)
    
    async def generate_receipt(
        self,
        request: ReceiptGenerateRequest,
        user_id: Optional[str] = None
    ) -> Receipt:
        """
        Generate a new receipt
        
        Args:
            request: Receipt generation request
            user_id: Optional user ID for audit
            
        Returns:
            Generated receipt
        """
        # Generate receipt number
        receipt_number = await self._generate_receipt_number()
        
        # Calculate tax breakdown
        tax_breakdown = self._calculate_tax_breakdown(
            amount=request.amount,
            include_vat=request.include_vat
        )
        
        # Create line items if not provided
        line_items = request.line_items or []
        if not line_items and request.description:
            line_items = [
                LineItem(
                    description=request.description,
                    quantity=1,
                    unit_price=tax_breakdown.subtotal,
                    total=tax_breakdown.subtotal
                )
            ]
        
        # Create receipt model
        receipt = Receipt(
            receipt_number=receipt_number,
            receipt_type=request.receipt_type,
            status=ReceiptStatus.DRAFT,
            customer=request.customer,
            payment_method=request.payment_method,
            payment_date=request.payment_date or datetime.utcnow(),
            line_items=line_items,
            tax_breakdown=tax_breakdown,
            business_name=request.business_name or "FinGuard Business",
            business_kra_pin=request.business_kra_pin,
            metadata=request.metadata or ReceiptMetadata(),
            created_by=user_id
        )
        
        # Generate QR code data
        receipt.qr_code_data = self.qr_generator.generate_receipt_qr_data(
            receipt_number=receipt.receipt_number,
            amount=tax_breakdown.total,
            customer_name=receipt.customer.name,
            payment_date=receipt.payment_date.strftime("%Y-%m-%d")
        )
        
        # Generate PDF
        pdf_bytes = self.pdf_generator.generate_receipt_pdf(receipt)
        
        # Save PDF to storage
        pdf_filename = f"{receipt_number}.pdf"
        pdf_path = os.path.join(self.pdf_storage_path, pdf_filename)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)
        
        receipt.pdf_path = pdf_path
        receipt.status = ReceiptStatus.GENERATED
        receipt.generated_at = datetime.utcnow()
        
        # Save to database
        receipt_dict = receipt.dict(by_alias=True, exclude={"id"})
        result = await self.receipts_collection.insert_one(receipt_dict)
        receipt.id = str(result.inserted_id)
        
        # Log audit event
        await self._log_audit(
            receipt_id=receipt.id,
            receipt_number=receipt.receipt_number,
            action="generated",
            user_id=user_id
        )
        
        # Send email if requested
        if request.send_email and receipt.customer.email:
            # TODO: Integrate with email service
            pass
        
        return receipt
    
    async def get_receipt(self, receipt_id: str) -> Optional[Receipt]:
        """
        Get receipt by ID
        
        Args:
            receipt_id: Receipt ID
            
        Returns:
            Receipt or None if not found
        """
        try:
            result = await self.receipts_collection.find_one({"_id": ObjectId(receipt_id)})
            if result:
                result["_id"] = str(result["_id"])
                return Receipt(**result)
            return None
        except Exception as e:
            print(f"Error getting receipt: {e}")
            return None
    
    async def get_receipt_by_number(self, receipt_number: str) -> Optional[Receipt]:
        """
        Get receipt by receipt number
        
        Args:
            receipt_number: Receipt number
            
        Returns:
            Receipt or None if not found
        """
        result = await self.receipts_collection.find_one({"receipt_number": receipt_number})
        if result:
            result["_id"] = str(result["_id"])
            return Receipt(**result)
        return None
    
    async def list_receipts(
        self,
        page: int = 1,
        page_size: int = 20,
        receipt_type: Optional[ReceiptType] = None,
        status: Optional[ReceiptStatus] = None,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        List receipts with filters
        
        Args:
            page: Page number
            page_size: Items per page
            receipt_type: Filter by receipt type
            status: Filter by status
            customer_id: Filter by customer
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Dict with receipts and pagination info
        """
        # Build query
        query = {}
        
        if receipt_type:
            query["receipt_type"] = receipt_type
        if status:
            query["status"] = status
        if customer_id:
            query["customer.customer_id"] = customer_id
        if start_date or end_date:
            query["payment_date"] = {}
            if start_date:
                query["payment_date"]["$gte"] = start_date
            if end_date:
                query["payment_date"]["$lte"] = end_date
        
        # Get total count
        total = await self.receipts_collection.count_documents(query)
        
        # Get receipts
        skip = (page - 1) * page_size
        cursor = self.receipts_collection.find(query).sort("created_at", -1).skip(skip).limit(page_size)
        
        receipts = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            try:
                receipts.append(Receipt(**doc))
            except Exception as e:
                # Skip documents that don't match the receipt schema (old data)
                print(f"Skipping invalid receipt document: {e}")
                continue
        
        return {
            "receipts": receipts,
            "total": len(receipts),  # Adjusted total for valid receipts only
            "page": page,
            "page_size": page_size,
            "total_pages": (len(receipts) + page_size - 1) // page_size
        }
    
    async def void_receipt(
        self,
        receipt_id: str,
        reason: str,
        user_id: Optional[str] = None
    ) -> Optional[Receipt]:
        """
        Void a receipt (cannot be deleted for compliance)
        
        Args:
            receipt_id: Receipt ID
            reason: Reason for voiding
            user_id: User performing the action
            
        Returns:
            Updated receipt or None if not found
        """
        receipt = await self.get_receipt(receipt_id)
        if not receipt:
            return None
        
        # Update receipt
        update_data = {
            "status": ReceiptStatus.VOIDED,
            "voided_at": datetime.utcnow(),
            "voided_by": user_id,
            "void_reason": reason,
            "updated_at": datetime.utcnow()
        }
        
        await self.receipts_collection.update_one(
            {"_id": ObjectId(receipt_id)},
            {"$set": update_data}
        )
        
        # Log audit event
        await self._log_audit(
            receipt_id=receipt_id,
            receipt_number=receipt.receipt_number,
            action="voided",
            user_id=user_id,
            details={"reason": reason}
        )
        
        # Get updated receipt
        return await self.get_receipt(receipt_id)
    
    async def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> ReceiptStatistics:
        """
        Get receipt statistics
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Receipt statistics
        """
        # Build query - only include valid receipts with required fields
        query = {
            "receipt_type": {"$exists": True, "$ne": None},
            "status": {"$exists": True, "$ne": None},
            "tax_breakdown": {"$exists": True}
        }
        
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        # Get total receipts
        total_receipts = await self.receipts_collection.count_documents(query)
        
        # Aggregate by type
        type_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$receipt_type", "count": {"$sum": 1}}}
        ]
        receipts_by_type = {}
        async for doc in self.receipts_collection.aggregate(type_pipeline):
            if doc["_id"]:  # Skip null types
                receipts_by_type[doc["_id"]] = doc["count"]
        
        # Aggregate by status
        status_pipeline = [
            {"$match": query},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        receipts_by_status = {}
        async for doc in self.receipts_collection.aggregate(status_pipeline):
            if doc["_id"]:  # Skip null statuses
                receipts_by_status[doc["_id"]] = doc["count"]
        
        # Aggregate by month
        month_pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        receipts_by_month = {}
        async for doc in self.receipts_collection.aggregate(month_pipeline):
            receipts_by_month[doc["_id"]] = doc["count"]
        
        # Calculate financial statistics
        amount_pipeline = [
            {"$match": {**query, "status": {"$ne": "voided"}}},
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$tax_breakdown.total"},
                    "average": {"$avg": "$tax_breakdown.total"}
                }
            }
        ]
        
        total_amount = 0.0
        average_amount = 0.0
        
        async for doc in self.receipts_collection.aggregate(amount_pipeline):
            total_amount = doc.get("total", 0.0)
            average_amount = doc.get("average", 0.0)
        
        # Count sent receipts
        receipts_sent = await self.receipts_collection.count_documents({
            **query,
            "status": "sent"
        })
        
        # Count voided receipts
        receipts_voided = await self.receipts_collection.count_documents({
            **query,
            "status": "voided"
        })
        
        return ReceiptStatistics(
            total_receipts=total_receipts,
            receipts_by_type=receipts_by_type,
            receipts_by_status=receipts_by_status,
            receipts_by_month=receipts_by_month,
            total_amount=total_amount,
            average_amount=average_amount,
            receipts_sent=receipts_sent,
            receipts_voided=receipts_voided
        )
    
    async def _generate_receipt_number(self) -> str:
        """
        Generate sequential receipt number
        
        Returns:
            Receipt number (e.g., RCP-2025-0001)
        """
        current_year = datetime.utcnow().year
        prefix = "RCP"
        
        # Find or create sequence for current year
        sequence = await self.sequences_collection.find_one({"year": current_year})
        
        if not sequence:
            # Create new sequence for year
            sequence = {
                "year": current_year,
                "prefix": prefix,
                "current_number": 1,
                "last_receipt_number": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.sequences_collection.insert_one(sequence)
            current_number = 1
        else:
            # Increment sequence
            current_number = sequence["current_number"] + 1
            await self.sequences_collection.update_one(
                {"year": current_year},
                {
                    "$set": {
                        "current_number": current_number,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        # Format receipt number
        receipt_number = f"{prefix}-{current_year}-{current_number:04d}"
        
        # Update last receipt number
        await self.sequences_collection.update_one(
            {"year": current_year},
            {"$set": {"last_receipt_number": receipt_number}}
        )
        
        return receipt_number
    
    def _calculate_tax_breakdown(
        self,
        amount: float,
        include_vat: bool = True,
        vat_rate: float = 0.16
    ) -> TaxBreakdown:
        """
        Calculate tax breakdown
        
        Args:
            amount: Total amount
            include_vat: Whether amount includes VAT
            vat_rate: VAT rate (default 16%)
            
        Returns:
            Tax breakdown
        """
        if include_vat:
            # Amount includes VAT, need to extract it
            total = amount
            subtotal = total / (1 + vat_rate)
            vat_amount = total - subtotal
        else:
            # Amount is pre-VAT
            subtotal = amount
            vat_amount = subtotal * vat_rate
            total = subtotal + vat_amount
        
        return TaxBreakdown(
            subtotal=round(subtotal, 2),
            vat_rate=vat_rate,
            vat_amount=round(vat_amount, 2),
            total=round(total, 2)
        )
    
    async def _log_audit(
        self,
        receipt_id: str,
        receipt_number: str,
        action: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log audit event
        
        Args:
            receipt_id: Receipt ID
            receipt_number: Receipt number
            action: Action performed
            user_id: Optional user ID
            details: Optional additional details
        """
        audit_log = ReceiptAuditLog(
            receipt_id=receipt_id,
            receipt_number=receipt_number,
            action=action,
            user_id=user_id,
            details=details
        )
        
        await self.audit_log_collection.insert_one(
            audit_log.dict(by_alias=True, exclude={"id"})
        )
