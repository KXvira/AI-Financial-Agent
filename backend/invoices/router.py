"""
Invoice Router - API Endpoints for Invoices
"""
from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


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
        
        # Add search filter
        if search:
            query["$or"] = [
                {"invoice_number": {"$regex": search, "$options": "i"}},
                {"customer_name": {"$regex": search, "$options": "i"}}
            ]
        
        # Get invoices
        cursor = db.invoices.find(query).sort("created_at", -1).limit(limit)
        
        invoices = []
        async for doc in cursor:
            invoices.append({
                "id": str(doc.get('_id')),
                "number": doc.get('invoice_number', 'N/A'),
                "client": doc.get('customer_name', 'Unknown'),
                "date": doc.get('issue_date', doc.get('created_at', datetime.utcnow())).strftime("%Y-%m-%d"),
                "dueDate": doc.get('due_date', datetime.utcnow()).strftime("%Y-%m-%d"),
                "amount": f"KES {doc.get('amount', 0):,.0f}",
                "amountRaw": doc.get('amount', 0),
                "status": doc.get('status', 'pending').capitalize(),
                "description": doc.get('description', ''),
                "created_at": doc.get('created_at', datetime.utcnow()).isoformat(),
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
        
        invoice = {
            "id": str(doc.get('_id')),
            "number": doc.get('invoice_number', 'N/A'),
            "client": doc.get('customer_name', 'Unknown'),
            "customerEmail": doc.get('customer_email', ''),
            "date": doc.get('issue_date', doc.get('created_at', datetime.utcnow())).strftime("%Y-%m-%d"),
            "dueDate": doc.get('due_date', datetime.utcnow()).strftime("%Y-%m-%d"),
            "amount": doc.get('amount', 0),
            "currency": doc.get('currency', 'KES'),
            "status": doc.get('status', 'pending').capitalize(),
            "description": doc.get('description', ''),
            "created_at": doc.get('created_at', datetime.utcnow()).isoformat(),
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
