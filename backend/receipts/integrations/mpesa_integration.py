"""
M-Pesa Integration for Automatic Receipt Generation

This module integrates with the M-Pesa payment system to automatically
generate and email receipts when payments are successful.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from bson import ObjectId

from ..models import ReceiptType, PaymentMethod, LineItem, CustomerInfo, ReceiptGenerateRequest, ReceiptMetadata
from ..service import ReceiptService

logger = logging.getLogger("financial-agent.receipts.mpesa-integration")


class MpesaReceiptIntegration:
    """
    Handles automatic receipt generation for M-Pesa payments
    """
    
    def __init__(self, receipt_service: ReceiptService):
        """
        Initialize M-Pesa receipt integration
        
        Args:
            receipt_service: Receipt service instance
        """
        self.receipt_service = receipt_service
        logger.info("M-Pesa receipt integration initialized")
    
    async def process_successful_payment(
        self,
        payment_data: Dict[str, Any],
        transaction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Process successful M-Pesa payment and generate receipt
        
        Args:
            payment_data: Payment details from M-Pesa callback
                - amount: Payment amount
                - receipt_number: M-Pesa receipt number
                - phone_number: Customer phone number
                - transaction_date: Transaction timestamp
            transaction_data: Transaction record from database
                - reference: Transaction reference
                - description: Transaction description
                - customer_name: Customer name (optional)
                - customer_email: Customer email (optional)
                
        Returns:
            Receipt generation result with receipt ID and number
        """
        try:
            logger.info(f"Processing M-Pesa payment for receipt generation: {payment_data.get('receipt_number')}")
            
            # Extract payment details
            amount = float(payment_data.get("amount", 0))
            mpesa_receipt = payment_data.get("receipt_number")
            phone_number = str(payment_data.get("phone_number", ""))
            transaction_date = payment_data.get("transaction_date")
            
            # Extract transaction details
            reference = transaction_data.get("reference", "N/A")
            description = transaction_data.get("description", "M-Pesa Payment")
            customer_name = transaction_data.get("customer_name")
            customer_email = transaction_data.get("customer_email")
            invoice_id = transaction_data.get("invoice_id")
            
            # Format phone number for customer info
            if phone_number and not phone_number.startswith("+"):
                if phone_number.startswith("254"):
                    phone_number = f"+{phone_number}"
                elif phone_number.startswith("0"):
                    phone_number = f"+254{phone_number[1:]}"
                else:
                    phone_number = f"+254{phone_number}"
            
            # Determine customer name
            if not customer_name:
                # Try to extract from transaction metadata
                customer_name = transaction_data.get("metadata", {}).get("customer_name", "M-Pesa Customer")
            
            # Create customer info
            customer_info = CustomerInfo(
                name=customer_name,
                phone=phone_number,
                email=customer_email if customer_email else None,
                address=None
            )
            
            # Create line item for the payment
            line_items = [
                LineItem(
                    description=description,
                    quantity=1,
                    unit_price=amount,
                    total=amount,
                    tax_rate=0.0  # M-Pesa payments don't include VAT
                )
            ]
            
            # Calculate amounts (no tax for M-Pesa payments)
            subtotal = amount
            tax_total = 0.0
            total = amount
            
            # Create receipt metadata
            receipt_metadata = ReceiptMetadata(
                transaction_id=mpesa_receipt,
                mpesa_receipt=mpesa_receipt,
                reference_number=reference,
                notes=f"Payment received via M-Pesa. Transaction Reference: {reference}"
            )
            if invoice_id:
                receipt_metadata.invoice_id = str(invoice_id)
            
            # Create receipt generation request
            receipt_request = ReceiptGenerateRequest(
                receipt_type=ReceiptType.PAYMENT,
                customer=customer_info,
                payment_method=PaymentMethod.MPESA,
                payment_date=None,  # Will use current date
                amount=total,
                description=description,
                line_items=line_items,
                include_vat=False,  # M-Pesa payments don't include VAT
                metadata=receipt_metadata,
                send_email=bool(customer_email)
            )
            
            # Generate the receipt
            receipt = await self.receipt_service.generate_receipt(receipt_request)
            
            logger.info(f"Receipt generated for M-Pesa payment: {receipt.receipt_number}")
            
            return {
                "success": True,
                "receipt_id": receipt.id,
                "receipt_number": receipt.receipt_number,
                "pdf_path": receipt.pdf_path,
                "email_sent": bool(customer_email),
                "message": "Receipt generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating receipt for M-Pesa payment: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate receipt"
            }
    
    async def generate_refund_receipt(
        self,
        refund_data: Dict[str, Any],
        original_transaction: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate receipt for M-Pesa refund
        
        Args:
            refund_data: Refund details
            original_transaction: Original transaction data
            
        Returns:
            Receipt generation result
        """
        try:
            logger.info(f"Processing M-Pesa refund for receipt generation")
            
            # Extract refund details
            amount = float(refund_data.get("amount", 0))
            refund_reference = refund_data.get("refund_reference")
            phone_number = str(refund_data.get("phone_number", ""))
            
            # Extract original transaction details
            customer_name = original_transaction.get("customer_name", "M-Pesa Customer")
            customer_email = original_transaction.get("customer_email")
            original_reference = original_transaction.get("reference")
            
            # Format phone number
            if phone_number and not phone_number.startswith("+"):
                if phone_number.startswith("254"):
                    phone_number = f"+{phone_number}"
                elif phone_number.startswith("0"):
                    phone_number = f"+254{phone_number[1:]}"
                else:
                    phone_number = f"+254{phone_number}"
            
            # Create customer info
            customer_info = CustomerInfo(
                name=customer_name,
                phone=phone_number,
                email=customer_email if customer_email else None,
                address=None
            )
            
            # Create line item for the refund
            line_items = [
                LineItem(
                    description=f"Refund for transaction {original_reference}",
                    quantity=1,
                    unit_price=amount,
                    total=amount,
                    tax_rate=0.0
                )
            ]
            
            # Create receipt metadata
            receipt_metadata = ReceiptMetadata(
                transaction_id=refund_reference,
                reference_number=original_reference,
                notes=f"Refund for original transaction: {original_reference}"
            )
            
            # Create receipt generation request
            receipt_request = ReceiptGenerateRequest(
                receipt_type=ReceiptType.REFUND,
                customer=customer_info,
                payment_method=PaymentMethod.MPESA,
                payment_date=None,
                amount=amount,
                description=f"Refund for transaction {original_reference}",
                line_items=line_items,
                include_vat=False,
                metadata=receipt_metadata,
                send_email=bool(customer_email)
            )
            
            # Generate the receipt
            receipt = await self.receipt_service.generate_receipt(receipt_request)
            
            logger.info(f"Refund receipt generated: {receipt.receipt_number}")
            
            return {
                "success": True,
                "receipt_id": receipt.id,
                "receipt_number": receipt.receipt_number,
                "email_sent": bool(customer_email)
            }
            
        except Exception as e:
            logger.error(f"Error generating refund receipt: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
