"""
Invoice Integration for Automatic Receipt Generation

This module integrates with the Invoice system to automatically
generate and email receipts when invoices are paid.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from bson import ObjectId

from ..models import ReceiptType, PaymentMethod, LineItem, CustomerInfo
from ..service import ReceiptService

logger = logging.getLogger("financial-agent.receipts.invoice-integration")


class InvoiceReceiptIntegration:
    """
    Handles automatic receipt generation for invoice payments
    """
    
    def __init__(self, receipt_service: ReceiptService):
        """
        Initialize invoice receipt integration
        
        Args:
            receipt_service: Receipt service instance
        """
        self.receipt_service = receipt_service
        logger.info("Invoice receipt integration initialized")
    
    async def process_invoice_payment(
        self,
        invoice_data: Dict[str, Any],
        payment_data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process invoice payment and generate receipt
        
        Args:
            invoice_data: Invoice details
                - invoice_number: Invoice number
                - customer: Customer info (name, phone, email, address)
                - items: List of invoice items
                - subtotal: Invoice subtotal
                - tax_total: Tax amount
                - total: Total amount
                - amount_paid: Amount paid
                - status: Invoice status
                - metadata: Additional metadata
            payment_data: Payment transaction details (optional)
                - payment_method: Payment method used
                - payment_reference: Payment reference/transaction ID
                - payment_date: Date of payment
                
        Returns:
            Receipt generation result with receipt ID and number
        """
        try:
            logger.info(f"Processing invoice payment for receipt generation: {invoice_data.get('invoice_number')}")
            
            # Extract invoice details
            invoice_number = invoice_data.get("invoice_number", "N/A")
            customer_data = invoice_data.get("customer", {})
            invoice_items = invoice_data.get("items", [])
            subtotal = float(invoice_data.get("subtotal", 0))
            tax_total = float(invoice_data.get("tax_total", 0))
            total = float(invoice_data.get("total", 0))
            amount_paid = float(invoice_data.get("amount_paid", total))
            invoice_status = invoice_data.get("status", "paid")
            
            # Determine receipt type based on payment amount
            if amount_paid >= total:
                receipt_type = ReceiptType.INVOICE
            else:
                receipt_type = ReceiptType.PARTIAL_PAYMENT
            
            # Create customer info
            customer_info = CustomerInfo(
                name=customer_data.get("name", "Customer"),
                phone=customer_data.get("phone_number", customer_data.get("phone", "")),
                email=customer_data.get("email"),
                address=customer_data.get("address")
            )
            
            # Convert invoice items to receipt line items
            line_items = []
            for item in invoice_items:
                line_item = LineItem(
                    description=item.get("description", "Item"),
                    quantity=float(item.get("quantity", 1)),
                    unit_price=float(item.get("unit_price", 0)),
                    total=float(item.get("total", item.get("amount", 0))),  # Use 'total' field
                    tax_rate=float(item.get("tax_rate", 0.16))  # Default 16% VAT
                )
                line_items.append(line_item)
            
            # Extract payment details
            payment_method = PaymentMethod.OTHER
            payment_reference = None
            
            if payment_data:
                # Map payment method
                method_str = payment_data.get("payment_method", "").lower()
                if "mpesa" in method_str or "m-pesa" in method_str:
                    payment_method = PaymentMethod.MPESA
                elif "bank" in method_str or "transfer" in method_str:
                    payment_method = PaymentMethod.BANK_TRANSFER
                elif "cash" in method_str:
                    payment_method = PaymentMethod.CASH
                elif "card" in method_str:
                    payment_method = PaymentMethod.CARD
                
                payment_reference = payment_data.get("payment_reference")
            
            # Prepare receipt metadata
            metadata = {
                "invoice_number": invoice_number,
                "invoice_id": str(invoice_data.get("_id", invoice_data.get("id"))),
                "invoice_status": invoice_status,
                "amount_paid": amount_paid,
                "invoice_total": total,
                "auto_generated": True,
                "generated_by": "invoice_integration",
            }
            
            # Add payment data to metadata if available
            if payment_data:
                metadata["payment_data"] = {
                    "payment_date": payment_data.get("payment_date"),
                    "payment_method": payment_data.get("payment_method"),
                    "payment_reference": payment_reference
                }
            
            # Prepare notes
            if receipt_type == ReceiptType.PARTIAL_PAYMENT:
                notes = f"Partial payment of KES {amount_paid:,.2f} received for Invoice #{invoice_number}. Remaining balance: KES {(total - amount_paid):,.2f}"
            else:
                notes = f"Full payment received for Invoice #{invoice_number}. Thank you for your business!"
            
            # Generate receipt
            receipt_data = {
                "receipt_type": receipt_type,
                "customer": customer_info,
                "line_items": line_items,
                "subtotal": subtotal,
                "tax_total": tax_total,
                "total": amount_paid,  # Use amount paid as total for partial payments
                "payment_method": payment_method,
                "payment_reference": payment_reference,
                "notes": notes,
                "metadata": metadata
            }
            
            # Generate the receipt
            receipt = await self.receipt_service.generate_receipt(receipt_data)
            
            logger.info(f"Receipt generated for invoice payment: {receipt['receipt_number']}")
            
            # Send email if customer email is available
            customer_email = customer_data.get("email")
            if customer_email:
                try:
                    email_result = await self.receipt_service.send_receipt_email(
                        receipt_id=str(receipt["_id"]),
                        email=customer_email,
                        template_id=None  # Use default template
                    )
                    logger.info(f"Receipt email sent to {customer_email}: {email_result.get('success')}")
                except Exception as email_error:
                    logger.error(f"Failed to send receipt email: {str(email_error)}")
                    # Don't fail the entire process if email fails
            
            return {
                "success": True,
                "receipt_id": str(receipt["_id"]),
                "receipt_number": receipt["receipt_number"],
                "pdf_path": receipt.get("pdf_path"),
                "email_sent": bool(customer_email),
                "invoice_number": invoice_number,
                "amount": amount_paid,
                "message": "Receipt generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating receipt for invoice payment: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate receipt"
            }
    
    async def process_invoice_refund(
        self,
        invoice_data: Dict[str, Any],
        refund_amount: float,
        refund_reference: Optional[str] = None,
        refund_reason: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate receipt for invoice refund
        
        Args:
            invoice_data: Original invoice details
            refund_amount: Amount being refunded
            refund_reference: Refund transaction reference
            refund_reason: Reason for refund
            
        Returns:
            Receipt generation result
        """
        try:
            logger.info(f"Processing invoice refund for receipt generation")
            
            # Extract invoice details
            invoice_number = invoice_data.get("invoice_number", "N/A")
            customer_data = invoice_data.get("customer", {})
            
            # Create customer info
            customer_info = CustomerInfo(
                name=customer_data.get("name", "Customer"),
                phone=customer_data.get("phone_number", customer_data.get("phone", "")),
                email=customer_data.get("email"),
                address=customer_data.get("address")
            )
            
            # Create line item for refund
            description = f"Refund for Invoice #{invoice_number}"
            if refund_reason:
                description += f" - {refund_reason}"
            
            line_items = [
                LineItem(
                    description=description,
                    quantity=1,
                    unit_price=refund_amount,
                    total=refund_amount,
                    tax_rate=0.0
                )
            ]
            
            # Prepare receipt metadata
            metadata = {
                "invoice_number": invoice_number,
                "invoice_id": str(invoice_data.get("_id", invoice_data.get("id"))),
                "refund_amount": refund_amount,
                "refund_reason": refund_reason,
                "auto_generated": True,
                "generated_by": "invoice_integration",
            }
            
            # Generate refund receipt
            receipt_data = {
                "receipt_type": ReceiptType.REFUND,
                "customer": customer_info,
                "line_items": line_items,
                "subtotal": refund_amount,
                "tax_total": 0.0,
                "total": refund_amount,
                "payment_method": PaymentMethod.OTHER,
                "payment_reference": refund_reference,
                "notes": f"Refund issued for Invoice #{invoice_number}. {refund_reason or ''}",
                "metadata": metadata
            }
            
            # Generate the receipt
            receipt = await self.receipt_service.generate_receipt(receipt_data)
            
            logger.info(f"Refund receipt generated: {receipt['receipt_number']}")
            
            # Send email if available
            customer_email = customer_data.get("email")
            if customer_email:
                try:
                    await self.receipt_service.send_receipt_email(
                        receipt_id=str(receipt["_id"]),
                        email=customer_email
                    )
                except Exception as email_error:
                    logger.error(f"Failed to send refund receipt email: {str(email_error)}")
            
            return {
                "success": True,
                "receipt_id": str(receipt["_id"]),
                "receipt_number": receipt["receipt_number"],
                "email_sent": bool(customer_email)
            }
            
        except Exception as e:
            logger.error(f"Error generating refund receipt: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
