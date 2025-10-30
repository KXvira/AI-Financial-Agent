"""
Receipt Adapter - Backward Compatibility Layer
Transforms old receipt format to new format on-the-fly
"""
from typing import Dict, Any, Optional
from datetime import datetime


class ReceiptAdapter:
    """Adapter to transform old receipt format to new format"""
    
    @staticmethod
    def adapt_old_receipt(old_receipt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform old receipt structure to new structure
        
        Handles legacy receipts with flat structure:
        - customer_name, customer_email, customer_phone → customer object
        - amount → tax_breakdown object
        - status: "issued" → status: "generated"
        - issued_date → generated_at
        """
        # Check if already new format
        if 'customer' in old_receipt and isinstance(old_receipt['customer'], dict):
            # Already new format, but ensure all required fields exist
            return ReceiptAdapter._ensure_required_fields(old_receipt)
        
        # Transform old format to new
        adapted = {
            '_id': old_receipt.get('_id'),
            'receipt_number': old_receipt.get('receipt_number', 'UNKNOWN'),
            'receipt_type': old_receipt.get('receipt_type', 'payment'),
            
            # Transform customer fields
            'customer': {
                'name': old_receipt.get('customer_name', 'Unknown Customer'),
                'email': old_receipt.get('customer_email'),
                'phone': old_receipt.get('customer_phone'),
                'address': old_receipt.get('customer_address'),
                'customer_id': old_receipt.get('customer_id')
            },
            
            # Transform financial fields
            'tax_breakdown': ReceiptAdapter._calculate_tax_breakdown(
                old_receipt.get('amount', 0)
            ),
            
            # Generate line items from description if available
            'line_items': ReceiptAdapter._generate_line_items(old_receipt),
            
            # Map old status to new status
            'status': ReceiptAdapter._map_status(old_receipt.get('status', 'issued')),
            
            # Transform payment fields
            'payment_method': old_receipt.get('payment_method', 'cash'),
            'payment_reference': old_receipt.get('transaction_reference'),
            'payment_date': old_receipt.get('issued_date') or old_receipt.get('created_at'),
            
            # Dates
            'generated_at': old_receipt.get('issued_date') or old_receipt.get('created_at'),
            'issued_date': old_receipt.get('issued_date') or old_receipt.get('created_at'),
            'created_at': old_receipt.get('created_at'),
            'updated_at': old_receipt.get('updated_at'),
            
            # Files
            'pdf_path': old_receipt.get('pdf_path'),
            'qr_code_data': old_receipt.get('qr_code'),
            
            # Business info
            'business_name': old_receipt.get('business_name', 'FinGuard Business'),
            'business_kra_pin': old_receipt.get('business_kra_pin'),
            'business_address': old_receipt.get('business_address'),
            'business_phone': old_receipt.get('business_phone'),
            'business_email': old_receipt.get('business_email'),
            
            # Metadata
            'metadata': {
                'invoice_id': old_receipt.get('invoice_id'),
                'payment_id': old_receipt.get('payment_id'),
                'transaction_reference': old_receipt.get('transaction_reference'),
                'notes': old_receipt.get('notes') or old_receipt.get('description'),
                'reference_number': old_receipt.get('transaction_reference'),
                'legacy_format': True,  # Flag for tracking
                'migrated_at': datetime.utcnow().isoformat()
            },
            
            # Additional fields
            'notes': old_receipt.get('notes') or old_receipt.get('description'),
            'currency': old_receipt.get('currency', 'KES'),
            'generated_by': old_receipt.get('generated_by', 'system')
        }
        
        # Remove None values from top level
        adapted = {k: v for k, v in adapted.items() if v is not None}
        
        # Clean up nested objects
        if adapted.get('customer'):
            adapted['customer'] = {k: v for k, v in adapted['customer'].items() if v is not None}
        if adapted.get('metadata'):
            adapted['metadata'] = {k: v for k, v in adapted['metadata'].items() if v is not None}
        
        return adapted
    
    @staticmethod
    def _ensure_required_fields(receipt: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields exist in new format receipts"""
        # Ensure customer object exists
        if 'customer' not in receipt or not isinstance(receipt['customer'], dict):
            receipt['customer'] = {
                'name': 'Unknown Customer',
                'email': None,
                'phone': None
            }
        
        # Ensure tax_breakdown exists
        if 'tax_breakdown' not in receipt:
            total = receipt.get('total', 0) or receipt.get('amount', 0)
            receipt['tax_breakdown'] = ReceiptAdapter._calculate_tax_breakdown(total)
        
        # Ensure line_items exists
        if 'line_items' not in receipt or not receipt['line_items']:
            receipt['line_items'] = ReceiptAdapter._generate_line_items(receipt)
        
        # Ensure status is valid
        if 'status' not in receipt:
            receipt['status'] = 'generated'
        else:
            receipt['status'] = ReceiptAdapter._map_status(receipt['status'])
        
        return receipt
    
    @staticmethod
    def _calculate_tax_breakdown(total_amount: float) -> Dict[str, float]:
        """
        Calculate tax breakdown from total amount (assumes VAT included)
        
        Default assumption: 16% VAT is included in the total amount
        Formula: subtotal = total / (1 + vat_rate)
        """
        vat_rate = 0.16
        subtotal = total_amount / (1 + vat_rate)
        vat_amount = total_amount - subtotal
        
        return {
            'subtotal': round(subtotal, 2),
            'vat_rate': vat_rate,
            'vat_amount': round(vat_amount, 2),
            'total': round(total_amount, 2)
        }
    
    @staticmethod
    def _generate_line_items(old_receipt: Dict[str, Any]) -> list:
        """
        Generate line items from old receipt
        
        Creates a single line item from description/notes and amount
        """
        description = (
            old_receipt.get('description') or 
            old_receipt.get('notes') or 
            f"Payment - {old_receipt.get('receipt_type', 'General')}"
        )
        
        amount = old_receipt.get('amount', 0)
        
        # Calculate amount before VAT (assuming 16% VAT included)
        vat_rate = 0.16
        subtotal = amount / (1 + vat_rate) if amount > 0 else 0
        
        return [{
            'description': description,
            'quantity': 1.0,
            'unit_price': round(subtotal, 2),
            'total': round(subtotal, 2),
            'tax_rate': vat_rate,
            'tax_amount': round(subtotal * vat_rate, 2)
        }]
    
    @staticmethod
    def _map_status(old_status: str) -> str:
        """
        Map old status values to new status enum
        
        Old statuses: issued, pending, completed, cancelled
        New statuses: draft, generated, sent, viewed, downloaded, voided
        """
        if not old_status:
            return 'generated'
        
        status_map = {
            # Old statuses
            'issued': 'generated',
            'pending': 'draft',
            'completed': 'sent',
            'cancelled': 'voided',
            'failed': 'voided',
            
            # New statuses (pass through)
            'draft': 'draft',
            'generated': 'generated',
            'sent': 'sent',
            'viewed': 'viewed',
            'downloaded': 'downloaded',
            'voided': 'voided'
        }
        
        return status_map.get(old_status.lower(), 'generated')
    
    @staticmethod
    def adapt_receipt_list(receipts: list) -> list:
        """Adapt a list of receipts"""
        return [ReceiptAdapter.adapt_old_receipt(receipt) for receipt in receipts]
    
    @staticmethod
    def is_legacy_format(receipt: Dict[str, Any]) -> bool:
        """Check if receipt is in legacy format"""
        # Check for legacy indicators
        has_flat_customer = 'customer_name' in receipt
        missing_customer_object = 'customer' not in receipt or not isinstance(receipt.get('customer'), dict)
        missing_tax_breakdown = 'tax_breakdown' not in receipt
        
        return has_flat_customer or missing_customer_object or missing_tax_breakdown
