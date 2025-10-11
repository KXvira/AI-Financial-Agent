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
        
        # Build query - only get payment type transactions
        query = {"type": "payment"}
        
        # Add status filter
        if status_filter:
            query["status"] = status_filter
        
        # Add search filter
        if search:
            query["$or"] = [
                {"mpesa_reference": {"$regex": search, "$options": "i"}},
                {"customer_name": {"$regex": search, "$options": "i"}},
                {"invoice_number": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]
        
        # Get transactions
        cursor = db.transactions.find(query).sort("created_at", -1).limit(limit)
        
        payments = []
        async for doc in cursor:
            payments.append({
                "id": str(doc.get('_id')),
                "reference": doc.get('mpesa_reference', str(doc.get('_id'))),
                "client": doc.get('customer_name', 'Unknown'),
                "date": doc.get('created_at', datetime.utcnow()).strftime("%Y-%m-%d"),
                "amount": f"KES {doc.get('amount', 0):,.2f}",
                "amountRaw": doc.get('amount', 0),
                "method": doc.get('payment_method', 'M-Pesa').title(),
                "status": doc.get('status', 'pending').capitalize(),
                "invoiceNumber": doc.get('invoice_number', ''),
                "phoneNumber": doc.get('phone_number', ''),
                "description": doc.get('description', ''),
                "created_at": doc.get('created_at', datetime.utcnow()).isoformat(),
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
        doc = await db.transactions.find_one({
            "type": "payment",
            "mpesa_reference": reference
        })
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        payment = {
            "id": str(doc.get('_id')),
            "reference": doc.get('mpesa_reference', str(doc.get('_id'))),
            "client": doc.get('customer_name', 'Unknown'),
            "date": doc.get('created_at', datetime.utcnow()).strftime("%Y-%m-%d"),
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
        total_payments = await db.transactions.count_documents({"type": "payment"})
        
        # Get completed payments
        completed_count = await db.transactions.count_documents({
            "type": "payment",
            "status": {"$in": ["completed", "success"]}
        })
        
        # Get pending payments
        pending_count = await db.transactions.count_documents({
            "type": "payment",
            "status": "pending"
        })
        
        # Calculate totals
        completed_pipeline = [
            {"$match": {
                "type": "payment",
                "status": {"$in": ["completed", "success"]}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        completed_result = await db.transactions.aggregate(completed_pipeline).to_list(None)
        completed_total = completed_result[0]['total'] if completed_result else 0.0
        
        # Monthly totals
        monthly_pipeline = [
            {"$match": {
                "type": "payment",
                "status": {"$in": ["completed", "success"]},
                "created_at": {"$gte": start_date}
            }},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        monthly_result = await db.transactions.aggregate(monthly_pipeline).to_list(None)
        monthly_total = monthly_result[0]['total'] if monthly_result else 0.0
        
        # Get matched vs unmatched (payments with invoice_id vs without)
        matched_count = await db.transactions.count_documents({
            "type": "payment",
            "invoice_id": {"$exists": True, "$ne": None}
        })
        
        unmatched_count = total_payments - matched_count
        
        # Calculate AI accuracy (matched / total * 100)
        ai_accuracy = round((matched_count / total_payments * 100), 1) if total_payments > 0 else 0
        
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
