"""
Invoice Router - API Endpoints for Invoices
"""
from fastapi import APIRouter, HTTPException, Query, status, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])

# Initialize receipt integration
invoice_receipt_integration = None
receipt_integration_available = False

def init_receipt_integration():
    """Initialize receipt integration with database"""
    global invoice_receipt_integration, receipt_integration_available
    try:
        from receipts.service import ReceiptService
        from receipts.integrations.invoice_integration import InvoiceReceiptIntegration
        from database.mongodb import Database
        
        db = Database.get_instance()
        receipt_service = ReceiptService(db=db)
        invoice_receipt_integration = InvoiceReceiptIntegration(receipt_service)
        receipt_integration_available = True
        logger.info("Receipt integration initialized for invoices")
    except Exception as e:
        logger.warning(f"Receipt integration not available for invoices: {str(e)}")


@router.get(
    "",
    summary="Get all invoices",
    description="Get invoices from database with optional filtering"
)
async def get_invoices(
    status_filter: Optional[str] = Query(None, description="Filter by status: paid, pending, overdue"),
    search: Optional[str] = Query(None, description="Search by invoice number or customer name"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results")
) -> Dict[str, Any]:
    """Get all invoices from database"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Build query
        query = {}
        
        # Add status filter
        if status_filter:
            query["status"] = status_filter
        
        # Add search filter (will search invoice numbers first, then join with customers)
        if search:
            query["invoice_number"] = {"$regex": search, "$options": "i"}
        
        # Get invoices with normalized schema
        cursor = db.invoices.find(query).sort("created_at", -1).limit(limit)
        
        invoices = []
        async for doc in cursor:
            # Get customer name from customers collection
            customer_name = "Unknown"
            if doc.get('customer_id'):
                customer = await db.customers.find_one({"customer_id": doc.get('customer_id')})
                if customer:
                    customer_name = customer.get('name', 'Unknown')
            
            # Parse dates safely
            date_issued = doc.get('date_issued')
            if isinstance(date_issued, str):
                date_issued = datetime.fromisoformat(date_issued.replace(' ', 'T'))
            elif not isinstance(date_issued, datetime):
                date_issued = datetime.utcnow()
                
            due_date = doc.get('due_date')
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace(' ', 'T'))
            elif not isinstance(due_date, datetime):
                due_date = datetime.utcnow()
            
            created_at = doc.get('created_at')
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))
            elif not isinstance(created_at, datetime):
                created_at = datetime.utcnow()
            
            # Use normalized schema fields: total_amount instead of amount
            total_amount = doc.get('total_amount', 0)
            
            invoices.append({
                "id": str(doc.get('_id')),
                "number": doc.get('invoice_number', 'N/A'),
                "client": customer_name,
                "date": date_issued.strftime("%Y-%m-%d"),
                "dueDate": due_date.strftime("%Y-%m-%d"),
                "amount": f"KES {total_amount:,.2f}",
                "amountRaw": total_amount,
                "status": doc.get('status', 'pending').capitalize(),
                "description": doc.get('notes', ''),
                "created_at": created_at.isoformat(),
            })
        
        return {
            "invoices": invoices,
            "total": len(invoices),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching invoices: {str(e)}")
        return {
            "invoices": [],
            "total": 0,
            "status": "error",
            "message": str(e)
        }


@router.get(
    "/by-number/{invoice_number}",
    summary="Get invoice by invoice number",
    description="Get a single invoice by its invoice number (e.g., INV-2021-02-0290)"
)
async def get_invoice_by_number(invoice_number: str) -> Dict[str, Any]:
    """Get single invoice details by invoice number"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Find invoice by invoice_number field
        doc = await db.invoices.find_one({"invoice_number": invoice_number})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoice {invoice_number} not found"
            )
        
        # Get customer info using normalized schema
        customer_name = "Unknown"
        customer_email = ""
        customer_phone = ""
        if doc.get('customer_id'):
            customer = await db.customers.find_one({"customer_id": doc.get('customer_id')})
            if customer:
                customer_name = customer.get('name', 'Unknown')
                customer_email = customer.get('email', '')
                customer_phone = customer.get('phone', '')
        
        # Get invoice items from invoice_items collection using normalized schema
        items = []
        invoice_id_for_items = doc.get('invoice_id')
        if invoice_id_for_items:
            cursor = db.invoice_items.find({"invoice_id": invoice_id_for_items})
            async for item_doc in cursor:
                # Use product_snapshot for better description
                product_name = ''
                if 'product_snapshot' in item_doc and item_doc['product_snapshot']:
                    product_name = item_doc['product_snapshot'].get('name', '')
                
                description = item_doc.get('description', '')
                if product_name and description:
                    full_description = f"{product_name} - {description}"
                elif product_name:
                    full_description = product_name
                else:
                    full_description = description or 'Service/Product'
                
                items.append({
                    "description": full_description,
                    "quantity": item_doc.get('quantity', 0),
                    "unit_price": item_doc.get('unit_price', 0),
                    "amount": item_doc.get('line_total', 0),
                })
        
        # Get payments from payments collection using normalized schema
        payments = []
        if invoice_id_for_items:
            payment_cursor = db.payments.find({"invoice_id": invoice_id_for_items})
            async for payment_doc in payment_cursor:
                payment_date = payment_doc.get('payment_date')
                if isinstance(payment_date, str):
                    payment_date = datetime.fromisoformat(payment_date.replace(' ', 'T'))
                elif not isinstance(payment_date, datetime):
                    payment_date = datetime.utcnow()
                    
                payments.append({
                    "method": payment_doc.get('payment_method', 'Unknown'),
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "amount": payment_doc.get('amount', 0),
                    "transactionId": payment_doc.get('transaction_reference', 'N/A'),
                })
        
        # Parse dates safely
        date_issued = doc.get('date_issued')
        if isinstance(date_issued, str):
            date_issued = datetime.fromisoformat(date_issued.replace(' ', 'T'))
        elif not isinstance(date_issued, datetime):
            date_issued = datetime.utcnow()
            
        due_date = doc.get('due_date')
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace(' ', 'T'))
        elif not isinstance(due_date, datetime):
            due_date = datetime.utcnow()
            
        created_at = doc.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))
        elif not isinstance(created_at, datetime):
            created_at = datetime.utcnow()
        
        invoice = {
            "id": str(doc.get('_id')),
            "number": doc.get('invoice_number', 'N/A'),
            "client": customer_name,
            "customerEmail": customer_email,
            "customerPhone": customer_phone,
            "issueDate": date_issued.strftime("%Y-%m-%d"),
            "dueDate": due_date.strftime("%Y-%m-%d"),
            "amount": doc.get('total_amount', 0),
            "currency": doc.get('currency', 'KES'),
            "status": doc.get('status', 'pending').capitalize(),
            "description": doc.get('notes', ''),
            "items": items,
            "payments": payments,
            "notes": doc.get('notes', ''),
            "created_at": created_at.isoformat(),
        }
        
        return invoice
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoice by number {invoice_number}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoice: {str(e)}"
        )


@router.get(
    "/{invoice_id}",
    summary="Get invoice by ID",
    description="Get a single invoice by its ID"
)
async def get_invoice_by_id(invoice_id: str) -> Dict[str, Any]:
    """Get single invoice details"""
    try:
        from database.mongodb import Database
        from bson import ObjectId
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Find invoice
        doc = await db.invoices.find_one({"_id": ObjectId(invoice_id)})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Get customer info using normalized schema
        customer_name = "Unknown"
        customer_email = ""
        customer_phone = ""
        if doc.get('customer_id'):
            customer = await db.customers.find_one({"customer_id": doc.get('customer_id')})
            if customer:
                customer_name = customer.get('name', 'Unknown')
                customer_email = customer.get('email', '')
                customer_phone = customer.get('phone', '')
        
        # Get invoice items from invoice_items collection
        items = []
        invoice_id_for_items = doc.get('invoice_id')
        if invoice_id_for_items:
            cursor = db.invoice_items.find({"invoice_id": invoice_id_for_items})
            async for item_doc in cursor:
                # Use product_snapshot for better description
                product_name = ''
                if 'product_snapshot' in item_doc and item_doc['product_snapshot']:
                    product_name = item_doc['product_snapshot'].get('name', '')
                
                description = item_doc.get('description', '')
                if product_name and description:
                    full_description = f"{product_name} - {description}"
                elif product_name:
                    full_description = product_name
                else:
                    full_description = description or 'Service/Product'
                
                items.append({
                    "description": full_description,
                    "quantity": item_doc.get('quantity', 0),
                    "unit_price": item_doc.get('unit_price', 0),
                    "amount": item_doc.get('line_total', 0),
                })
        
        # Get payments
        payments = []
        if invoice_id_for_items:
            payment_cursor = db.payments.find({"invoice_id": invoice_id_for_items})
            async for payment_doc in payment_cursor:
                payment_date = payment_doc.get('payment_date')
                if isinstance(payment_date, str):
                    payment_date = datetime.fromisoformat(payment_date.replace(' ', 'T'))
                elif not isinstance(payment_date, datetime):
                    payment_date = datetime.utcnow()
                    
                payments.append({
                    "method": payment_doc.get('payment_method', 'Unknown'),
                    "date": payment_date.strftime("%Y-%m-%d"),
                    "amount": payment_doc.get('amount', 0),
                    "transactionId": payment_doc.get('transaction_reference', 'N/A'),
                })
        
        # Parse dates safely
        date_issued = doc.get('date_issued')
        if isinstance(date_issued, str):
            date_issued = datetime.fromisoformat(date_issued.replace(' ', 'T'))
        elif not isinstance(date_issued, datetime):
            date_issued = datetime.utcnow()
            
        due_date = doc.get('due_date')
        if isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace(' ', 'T'))
        elif not isinstance(due_date, datetime):
            due_date = datetime.utcnow()
            
        created_at = doc.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))
        elif not isinstance(created_at, datetime):
            created_at = datetime.utcnow()
        
        invoice = {
            "id": str(doc.get('_id')),
            "number": doc.get('invoice_number', 'N/A'),
            "client": customer_name,
            "customerEmail": customer_email,
            "customerPhone": customer_phone,
            "date": date_issued.strftime("%Y-%m-%d"),
            "dueDate": due_date.strftime("%Y-%m-%d"),
            "amount": doc.get('total_amount', 0),
            "currency": doc.get('currency', 'KES'),
            "status": doc.get('status', 'pending').capitalize(),
            "description": doc.get('notes', ''),
            "items": items,
            "payments": payments,
            "notes": doc.get('notes', ''),
            "created_at": created_at.isoformat(),
        }
        
        return invoice
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching invoice {invoice_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch invoice: {str(e)}"
        )


@router.get(
    "/stats/summary",
    summary="Get invoice statistics",
    description="Get invoice summary statistics"
)
async def get_invoice_stats() -> Dict[str, Any]:
    """Get invoice statistics"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Get total invoices
        total_invoices = await db.invoices.count_documents({})
        
        # Get paid invoices
        paid_count = await db.invoices.count_documents({"status": "paid"})
        
        # Get pending invoices
        pending_count = await db.invoices.count_documents({"status": "pending"})
        
        # Calculate totals
        paid_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        paid_result = await db.invoices.aggregate(paid_pipeline).to_list(None)
        paid_total = paid_result[0]['total'] if paid_result else 0.0
        
        pending_pipeline = [
            {"$match": {"status": "pending"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        pending_result = await db.invoices.aggregate(pending_pipeline).to_list(None)
        pending_total = pending_result[0]['total'] if pending_result else 0.0
        
        return {
            "totalInvoices": total_invoices,
            "paidCount": paid_count,
            "pendingCount": pending_count,
            "paidTotal": round(paid_total, 2),
            "pendingTotal": round(pending_total, 2),
            "totalAmount": round(paid_total + pending_total, 2)
        }
        
    except Exception as e:
        logger.error(f"Error fetching invoice stats: {str(e)}")
        return {
            "totalInvoices": 0,
            "paidCount": 0,
            "pendingCount": 0,
            "paidTotal": 0.0,
            "pendingTotal": 0.0,
            "totalAmount": 0.0
        }


@router.post(
    "/{invoice_id}/mark-paid",
    summary="Mark invoice as paid",
    description="Mark an invoice as paid and automatically generate a receipt"
)
async def mark_invoice_paid(
    invoice_id: str,
    payment_data: Optional[Dict[str, Any]] = Body(None)
) -> Dict[str, Any]:
    """
    Mark invoice as paid and generate receipt automatically
    
    Args:
        invoice_id: Invoice ID
        payment_data: Optional payment details
            - payment_method: Payment method (mpesa, bank_transfer, cash, card, other)
            - payment_reference: Payment reference/transaction ID
            - payment_date: Date of payment (ISO format)
            - amount_paid: Amount paid (optional, defaults to invoice total)
    """
    try:
        from database.mongodb import Database
        from bson import ObjectId
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Find invoice
        invoice = await db.invoices.find_one({"_id": ObjectId(invoice_id)})
        
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        
        # Extract payment details
        payment_method = payment_data.get("payment_method", "other") if payment_data else "other"
        payment_reference = payment_data.get("payment_reference") if payment_data else None
        payment_date = payment_data.get("payment_date") if payment_data else datetime.utcnow().isoformat()
        amount_paid = float(payment_data.get("amount_paid", invoice.get("amount", 0))) if payment_data else invoice.get("amount", 0)
        
        # Determine new status
        invoice_total = invoice.get("amount", 0)
        if amount_paid >= invoice_total:
            new_status = "paid"
        else:
            new_status = "partially_paid"
        
        # Update invoice status
        update_data = {
            "status": new_status,
            "payment_method": payment_method,
            "payment_reference": payment_reference,
            "payment_date": payment_date,
            "amount_paid": amount_paid,
            "updated_at": datetime.utcnow()
        }
        
        await db.invoices.update_one(
            {"_id": ObjectId(invoice_id)},
            {"$set": update_data}
        )
        
        # Initialize receipt integration if not already done
        if invoice_receipt_integration is None:
            init_receipt_integration()
        
        # Generate receipt automatically if integration available
        receipt_result = None
        if receipt_integration_available and invoice_receipt_integration:
            try:
                # Prepare invoice data for receipt generation
                # Calculate amounts
                subtotal_calc = amount_paid / 1.16  # Reverse calculate assuming 16% VAT
                tax_calc = amount_paid - subtotal_calc
                
                # Create simple line items for receipt
                receipt_items = [
                    {
                        "description": invoice.get("description", f"Payment for Invoice {invoice.get('invoice_number', 'N/A')}"),
                        "quantity": 1.0,
                        "unit_price": subtotal_calc,  # Unit price before tax
                        "total": amount_paid,  # Total including tax
                        "tax_rate": 0.16  # 16% VAT rate
                    }
                ]
                
                invoice_data = {
                    "_id": invoice["_id"],
                    "invoice_number": invoice.get("invoice_number", "N/A"),
                    "customer": {
                        "name": invoice.get("customer_name", "Customer"),
                        "phone": invoice.get("customer_phone", ""),
                        "email": invoice.get("customer_email"),
                        "address": invoice.get("customer_address")
                    },
                    "items": receipt_items,
                    "subtotal": subtotal_calc,
                    "tax_total": tax_calc,
                    "total": invoice_total,
                    "amount_paid": amount_paid,
                    "status": new_status
                }
                
                # Payment details
                payment_info = {
                    "payment_method": payment_method,
                    "payment_reference": payment_reference,
                    "payment_date": payment_date
                }
                
                receipt_result = await invoice_receipt_integration.process_invoice_payment(
                    invoice_data=invoice_data,
                    payment_data=payment_info
                )
                
                if receipt_result and receipt_result.get("success"):
                    logger.info(f"Auto-generated receipt for invoice {invoice_id}: {receipt_result.get('receipt_number')}")
                
            except Exception as receipt_error:
                logger.error(f"Failed to auto-generate receipt for invoice {invoice_id}: {str(receipt_error)}")
                # Don't fail the entire operation if receipt generation fails
                receipt_result = {
                    "success": False,
                    "error": str(receipt_error)
                }
        
        return {
            "success": True,
            "message": f"Invoice marked as {new_status}",
            "invoice_id": invoice_id,
            "status": new_status,
            "amount_paid": amount_paid,
            "receipt": receipt_result if receipt_result else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking invoice {invoice_id} as paid: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark invoice as paid: {str(e)}"
        )
