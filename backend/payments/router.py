"""
Payments Router - API Endpoints for Payments/Transactions
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.get(
    "",
    summary="Get all payments",
    description="Get payment transactions from database with optional filtering"
)
async def get_payments(
    search: Optional[str] = Query(None, description="Search by reference, customer name, or invoice number"),
    status_filter: Optional[str] = Query(None, description="Filter by status: completed, pending, failed"),
    limit: int = Query(100, ge=1, le=1000, description="Limit number of results")
) -> Dict[str, Any]:
    """Get all payment transactions from database"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Build query for payments collection
        query = {}
        
        # Add status filter
        if status_filter:
            query["status"] = status_filter
        
        # Add search filter
        if search:
            query["$or"] = [
                {"transaction_reference": {"$regex": search, "$options": "i"}},
                {"customer_id": {"$regex": search, "$options": "i"}},
                {"invoice_id": {"$regex": search, "$options": "i"}},
                {"notes": {"$regex": search, "$options": "i"}}
            ]
        
        # Get payments
        cursor = db.payments.find(query).sort("payment_date", -1).limit(limit)
        
        payments = []
        async for doc in cursor:
            # Get customer name
            customer_name = "Unknown"
            if doc.get('customer_id'):
                customer = await db.customers.find_one({"customer_id": doc.get('customer_id')})
                if customer:
                    customer_name = customer.get('name', 'Unknown')
            
            # Get invoice number
            invoice_number = ""
            if doc.get('invoice_id'):
                invoice = await db.invoices.find_one({"invoice_id": doc.get('invoice_id')})
                if invoice:
                    invoice_number = invoice.get('invoice_number', '')
            
            # Parse payment date
            payment_date = doc.get('payment_date')
            if isinstance(payment_date, str):
                try:
                    payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
                except:
                    payment_date = datetime.utcnow()
            elif not isinstance(payment_date, datetime):
                payment_date = datetime.utcnow()
            
            payments.append({
                "id": str(doc.get('_id')),
                "reference": doc.get('transaction_reference', str(doc.get('_id'))),
                "client": customer_name,
                "date": payment_date.strftime("%Y-%m-%d"),
                "amount": f"KES {doc.get('amount', 0):,.2f}",
                "amountRaw": doc.get('amount', 0),
                "method": doc.get('payment_method', 'M-Pesa').title(),
                "status": doc.get('status', 'pending').capitalize(),
                "invoiceNumber": invoice_number,
                "phoneNumber": "",  # Not in normalized schema
                "description": doc.get('notes', ''),
                "created_at": payment_date.isoformat(),
            })
        
        return {
            "payments": payments,
            "total": len(payments),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error fetching payments: {str(e)}")
        return {
            "payments": [],
            "total": 0,
            "status": "error",
            "message": str(e)
        }


@router.get(
    "/{reference}",
    summary="Get payment by reference",
    description="Get a single payment by its M-Pesa reference"
)
async def get_payment_by_reference(reference: str) -> Dict[str, Any]:
    """Get single payment details"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Find payment by reference
        doc = await db.payments.find_one({
            "transaction_reference": reference
        })
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Get customer name
        customer_name = "Unknown"
        if doc.get('customer_id'):
            customer = await db.customers.find_one({"customer_id": doc.get('customer_id')})
            if customer:
                customer_name = customer.get('name', 'Unknown')
        
        # Parse payment date
        payment_date = doc.get('payment_date')
        if isinstance(payment_date, str):
            try:
                payment_date = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
            except:
                payment_date = datetime.utcnow()
        elif not isinstance(payment_date, datetime):
            payment_date = datetime.utcnow()
        
        payment = {
            "id": str(doc.get('_id')),
            "reference": doc.get('transaction_reference', str(doc.get('_id'))),
            "client": customer_name,
            "date": payment_date.strftime("%Y-%m-%d"),
            "amount": doc.get('amount', 0),
            "currency": doc.get('currency', 'KES'),
            "method": doc.get('payment_method', 'M-Pesa'),
            "status": doc.get('status', 'pending'),
            "invoiceNumber": doc.get('invoice_number', ''),
            "invoiceId": doc.get('invoice_id', ''),
            "phoneNumber": doc.get('phone_number', ''),
            "description": doc.get('description', ''),
            "created_at": doc.get('created_at', datetime.utcnow()).isoformat(),
        }
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment {reference}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch payment: {str(e)}"
        )


@router.get(
    "/stats/summary",
    summary="Get payment statistics",
    description="Get payment summary statistics"
)
async def get_payment_stats() -> Dict[str, Any]:
    """Get payment statistics"""
    try:
        from database.mongodb import Database
        
        db_instance = Database.get_instance()
        db = db_instance.db
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get total payments
        total_payments = await db.payments.count_documents({})
        
        # Get completed payments
        completed_count = await db.payments.count_documents({
            "status": {"$in": ["completed", "success"]}
        })
        
        # Get pending payments
        pending_count = await db.payments.count_documents({
            "status": "pending"
        })
        
        # Calculate totals
        completed_pipeline = [
            {"$match": {
                "status": {"$in": ["completed", "success"]}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        completed_result = await db.payments.aggregate(completed_pipeline).to_list(None)
        completed_total = completed_result[0]['total'] if completed_result else 0.0
        
        # Monthly totals - payments in last 30 days
        monthly_pipeline = [
            {"$match": {
                "status": {"$in": ["completed", "success"]}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        monthly_result = await db.payments.aggregate(monthly_pipeline).to_list(None)
        monthly_total = monthly_result[0]['total'] if monthly_result else 0.0
        
        # Get AI matching statistics from summary collection
        ai_summary = await db.ai_matching_summary.find_one({})
        
        if ai_summary:
            matched_count = ai_summary.get('correct_matches', 0)
            unmatched_count = ai_summary.get('unmatched_count', 0)
            ai_accuracy = ai_summary.get('ai_accuracy', 0.0)
        else:
            # Fallback: Get matched vs unmatched from payments
            matched_count = await db.payments.count_documents({
                "ai_matched": True,
                "match_status": "correct"
            })
            
            unmatched_count = await db.payments.count_documents({
                "ai_matched": False
            })
            
            # Calculate AI accuracy
            total_ai_matched = await db.payments.count_documents({"ai_matched": True})
            ai_accuracy = round((matched_count / total_ai_matched * 100), 2) if total_ai_matched > 0 else 0.0
        
        return {
            "totalPayments": total_payments,
            "completedCount": completed_count,
            "pendingCount": pending_count,
            "completedTotal": round(completed_total, 2),
            "monthlyTotal": round(monthly_total, 2),
            "matchedCount": matched_count,
            "unmatchedCount": unmatched_count,
            "aiAccuracy": ai_accuracy
        }
        
    except Exception as e:
        logger.error(f"Error fetching payment stats: {str(e)}")
        return {
            "totalPayments": 0,
            "completedCount": 0,
            "pendingCount": 0,
            "completedTotal": 0.0,
            "monthlyTotal": 0.0,
            "matchedCount": 0,
            "unmatchedCount": 0,
            "aiAccuracy": 0
        }
