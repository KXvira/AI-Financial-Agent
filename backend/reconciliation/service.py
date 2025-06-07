"""
Reconciliation service for matching payments to invoices
"""
import logging
from typing import Dict, Any, List, Optional, Union
import json
from datetime import datetime
import asyncio

# Import AI and database services
try:
    from ai_agent.gemini import GeminiService
    from database.mongodb import Database
    services_available = True
except ImportError:
    services_available = False
    print("Database or AI services not available. Using mock data only.")

logger = logging.getLogger("financial-agent.reconciliation")

class ReconciliationService:
    """
    Service for reconciling payments with invoices
    """
    
    def __init__(self):
        if services_available:
            self.gemini_service = GeminiService()
            self.db = Database.get_instance()
        else:
            self.gemini_service = None
            self.db = None
        
    async def reconcile_payment(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconcile an incoming payment against pending invoices
        
        Args:
            payment_data: Payment data from M-Pesa
            
        Returns:
            Dict with reconciliation result
        """
        try:
            # Log the reconciliation attempt
            logger.info(f"Reconciling payment: {json.dumps(payment_data)}")
            
            # Get pending invoices from database or use mock data
            if self.db is not None:
                pending_invoices = await self.db.get_pending_invoices()
                logger.info(f"Found {len(pending_invoices)} pending invoices for reconciliation")
            else:
                # Use mock data for testing
                pending_invoices = self._get_mock_invoices()
                logger.info(f"Using {len(pending_invoices)} mock invoices for reconciliation")
            
            # Check if there are any invoices to reconcile against
            if not pending_invoices:
                logger.info("No pending invoices found for reconciliation")
                return {
                    "success": False,
                    "message": "No pending invoices found",
                    "matched_invoice_id": None,
                    "confidence_score": 0
                }
            
            # Use Gemini to reconcile payment if available
            if self.gemini_service is not None:
                result = await self.gemini_service.reconcile_payment(payment_data, pending_invoices)
            else:
                # Simple fallback reconciliation logic
                result = self._basic_reconciliation(payment_data, pending_invoices)
            
            # Store reconciliation log if database is available
            if self.db is not None:
                log_data = {
                    "payment_data": payment_data,
                    "result": result,
                    "timestamp": datetime.now()
                }
                await self.db.store_reconciliation_log(log_data)
                
            # Check confidence score to determine if we need human review
            if result.get("action_required", True):
                # Flag for human review
                logger.info(f"Payment requires human review. Confidence: {result.get('confidence_score', 0)}")
                
                # Update transaction if available
                if self.db is not None and "transaction_id" in payment_data:
                    await self.db.update_transaction(payment_data["transaction_id"], {
                        "reconciliation_status": "needs_review",
                        "confidence_score": result.get("confidence_score", 0),
                        "needs_review": True,
                        "review_reason": result.get("review_reason", "Low confidence match")
                    })
                
                return {
                    "success": True,
                    "message": "Payment reconciliation requires human review",
                    "needs_review": True,
                    **result
                }
                
            # Process successful reconciliation
            matched_invoice_id = result.get("matched_invoice_id")
            if matched_invoice_id:
                # Update invoice and transaction status if database is available
                if self.db is not None:
                    # Check if this is a partial payment
                    is_partial = result.get("partial_payment", False)
                    new_status = "partially_paid" if is_partial else "paid"
                    
                    # Update invoice status
                    await self.db.update_invoice(matched_invoice_id, {
                        "status": new_status,
                        "amount_paid": result.get("amount_paid", 0),
                        "balance": result.get("balance", 0),
                        "payment_transactions": [payment_data.get("transaction_id", "unknown")]
                    })
                    
                    # Update transaction reconciliation status
                    if "transaction_id" in payment_data:
                        await self.db.update_transaction(payment_data["transaction_id"], {
                            "reconciliation_status": "matched" if not is_partial else "partial",
                            "matched_invoice_id": matched_invoice_id,
                            "confidence_score": result.get("confidence_score", 0),
                            "needs_review": False
                        })
                
                logger.info(f"Payment successfully reconciled with invoice {matched_invoice_id}")
                
                return {
                    "success": True,
                    "message": "Payment successfully reconciled",
                    "needs_review": False,
                    **result
                }
            else:
                # No match found
                logger.info("No matching invoice found for payment")
                
                # Update transaction if available
                if self.db is not None and "transaction_id" in payment_data:
                    await self.db.update_transaction(payment_data["transaction_id"], {
                        "reconciliation_status": "unmatched",
                        "needs_review": True,
                        "review_reason": "No matching invoice found"
                    })
                
                return {
                    "success": False,
                    "message": "No matching invoice found",
                    "needs_review": True,
                    **result
                }
                
        except Exception as e:
            logger.error(f"Error in payment reconciliation: {str(e)}")
            raise
    
    def _basic_reconciliation(self, payment_data: Dict[str, Any], pending_invoices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Basic reconciliation logic when AI is not available
        
        Args:
            payment_data: Payment data
            pending_invoices: List of pending invoices
            
        Returns:
            Dict with reconciliation result
        """
        best_match = None
        highest_score = 0
        payment_amount = float(payment_data.get("amount", 0))
        payment_phone = str(payment_data.get("phone_number", ""))
        payment_reference = payment_data.get("reference", "").lower()
        
        for invoice in pending_invoices:
            # Initial score
            score = 0
            
            # Compare amount (most important factor)
            invoice_amount = float(invoice.get("total", 0))
            if abs(payment_amount - invoice_amount) < 1:  # Exact match within 1 KES
                score += 60
            elif abs(payment_amount - invoice_amount) / invoice_amount < 0.05:  # Within 5%
                score += 40
            elif payment_amount > 0 and payment_amount < invoice_amount:  # Partial payment
                score += 30
                
            # Compare phone number
            customer = invoice.get("customer", {})
            invoice_phone = customer.get("phone_number", "")
            if invoice_phone and invoice_phone == payment_phone:
                score += 25
                
            # Compare reference with invoice number
            invoice_number = invoice.get("invoice_number", "").lower()
            if payment_reference and (
                payment_reference in invoice_number or 
                invoice_number in payment_reference
            ):
                score += 15
                
            # Keep track of best match
            if score > highest_score:
                highest_score = score
                best_match = invoice
        
        # Prepare result based on match score
        if best_match and highest_score >= 70:  # Good match above 70%
            invoice_amount = float(best_match.get("total", 0))
            result = {
                "matched_invoice_id": best_match.get("id"),
                "confidence_score": highest_score,
                "action_required": False if highest_score >= 80 else True,
                "review_reason": "Medium confidence match" if highest_score < 80 else None,
                "partial_payment": payment_amount < invoice_amount,
                "amount_paid": payment_amount,
                "balance": max(0, invoice_amount - payment_amount),
                "invoice_details": {
                    "invoice_number": best_match.get("invoice_number"),
                    "customer": best_match.get("customer", {}).get("name"),
                    "amount": invoice_amount
                }
            }
        else:
            # No good match found
            result = {
                "matched_invoice_id": None,
                "confidence_score": highest_score,
                "action_required": True,
                "review_reason": "No strong match found" if best_match else "No match found",
                "partial_payment": False,
                "best_potential_match": best_match.get("id") if best_match else None
            }
            
        return result
        
    async def queue_for_reconciliation(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Queue a payment for reconciliation
        
        Args:
            payment_data: The payment data from M-Pesa
            
        Returns:
            Dict with queuing result
        """
        try:
            # Log the queuing
            logger.info(f"Queueing payment for reconciliation: {json.dumps(payment_data)}")
            
            # Store payment record if database is available
            stored_id = None
            if self.db is not None and "transaction_id" not in payment_data:
                # Create transaction record if it doesn't already exist
                transaction_data = {
                    "reference": payment_data.get("reference", ""),
                    "gateway": "mpesa",
                    "amount": float(payment_data.get("amount", 0)),
                    "phone_number": payment_data.get("phone_number", ""),
                    "status": "completed",
                    "gateway_reference": payment_data.get("receipt_number", ""),
                    "request_timestamp": datetime.now(),
                    "completion_timestamp": datetime.now(),
                    "reconciliation_status": "pending"
                }
                
                stored_id = await self.db.store_transaction(transaction_data)
                payment_data["transaction_id"] = stored_id
            
            # Start reconciliation in the background
            asyncio.create_task(self.reconcile_payment(payment_data))
            
            return {
                "success": True,
                "message": "Payment queued for reconciliation",
                "payment_id": payment_data.get("receipt_number", "unknown"),
                "transaction_id": payment_data.get("transaction_id", stored_id)
            }
            
        except Exception as e:
            logger.error(f"Error queueing payment for reconciliation: {str(e)}")
            raise
    
    async def process_batch_reconciliation(self) -> Dict[str, Any]:
        """
        Process batch reconciliation for unreconciled payments
        
        Returns:
            Dict with batch processing results
        """
        try:
            # Get unreconciled payments from database or use mock data
            if self.db is not None:
                unreconciled_payments = await self.db.get_unreconciled_transactions()
                logger.info(f"Found {len(unreconciled_payments)} unreconciled payments for batch processing")
            else:
                # Use mock data for testing
                unreconciled_payments = self._get_mock_unreconciled_payments()
                logger.info(f"Using {len(unreconciled_payments)} mock unreconciled payments")
            
            results = {
                "total_processed": len(unreconciled_payments),
                "reconciled": 0,
                "needs_review": 0,
                "failed": 0,
                "details": []
            }
            
            # Process each payment
            for payment in unreconciled_payments:
                try:
                    result = await self.reconcile_payment(payment)
                    
                    if result.get("success") and not result.get("needs_review"):
                        results["reconciled"] += 1
                    elif result.get("needs_review"):
                        results["needs_review"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["details"].append({
                        "payment_id": payment.get("receipt_number", payment.get("id", "unknown")),
                        "result": result
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing payment in batch: {str(e)}")
                    results["failed"] += 1
                    results["details"].append({
                        "payment_id": payment.get("receipt_number", payment.get("id", "unknown")),
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch reconciliation: {str(e)}")
            raise
    
    def _get_mock_invoices(self) -> List[Dict[str, Any]]:
        """
        Get mock invoices for testing
        """
        return [
            {
                "invoice_id": "INV-001",
                "customer_name": "John Doe",
                "customer_phone": "254712345678",
                "amount": 1000,
                "date_issued": "2025-05-01",
                "due_date": "2025-06-01",
                "status": "pending"
            },
            {
                "invoice_id": "INV-002",
                "customer_name": "Jane Smith",
                "customer_phone": "254723456789",
                "amount": 1500,
                "date_issued": "2025-05-05",
                "due_date": "2025-06-05",
                "status": "pending"
            },
            {
                "invoice_id": "INV-003",
                "customer_name": "Bob Johnson",
                "customer_phone": "254734567890",
                "amount": 2000,
                "date_issued": "2025-05-10",
                "due_date": "2025-06-10",
                "status": "pending"
            }
        ]
    
    def _get_mock_unreconciled_payments(self) -> List[Dict[str, Any]]:
        """
        Get mock unreconciled payments for testing
        """
        return [
            {
                "receipt_number": "QWE12345",
                "phone_number": "254712345678",
                "amount": 1000,
                "transaction_date": "20250520123456"
            },
            {
                "receipt_number": "ASD67890",
                "phone_number": "254723456789",
                "amount": 1450,  # Slightly less than the invoice amount
                "transaction_date": "20250522134567"
            }
        ]
