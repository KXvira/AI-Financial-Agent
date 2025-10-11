"""
Customer API router
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from database.mongodb import Database

from .models import (
    Customer, CustomerCreate, CustomerUpdate,
    CustomerListItem, CustomerStats, CustomerFinancialSummary
)
from .service import CustomerService

router = APIRouter(prefix="/api/customers", tags=["customers"])


def get_customer_service() -> CustomerService:
    """Dependency to get customer service"""
    db = Database.get_instance().db
    return CustomerService(db)


@router.get("/", response_model=dict)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = Query(None, regex="^(active|inactive|suspended)$"),
    payment_status: Optional[str] = Query(None, regex="^(good|warning|overdue)$"),
    search: Optional[str] = None,
    sort_by: str = Query("name", regex="^(name|customer_id|total_billed|outstanding_balance|last_invoice_date)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get list of customers with pagination and filters
    
    **Query Parameters:**
    - skip: Number of customers to skip (for pagination)
    - limit: Maximum number of customers to return
    - status: Filter by customer status (active, inactive, suspended)
    - payment_status: Filter by payment status (good, warning, overdue)
    - search: Search by name, email, phone, or customer ID
    - sort_by: Field to sort by
    - sort_order: Sort order (asc or desc)
    """
    try:
        customers, total = await service.get_customers(
            skip=skip,
            limit=limit,
            status=status,
            payment_status=payment_status,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "customers": [c.model_dump() for c in customers],
            "total": total,
            "limit": limit,
            "skip": skip,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")


@router.get("/stats/summary", response_model=CustomerStats)
async def get_customer_statistics(
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get overall customer statistics
    
    Returns:
    - Total number of customers
    - Active/inactive breakdown
    - Total outstanding balance
    - Customers with overdue payments
    - Top 5 customers by revenue
    """
    try:
        stats = await service.get_customer_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get detailed information about a specific customer
    
    **Path Parameters:**
    - customer_id: Unique customer identifier (e.g., CUST-0001)
    """
    customer = await service.get_customer(customer_id)
    
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    return customer


@router.get("/{customer_id}/financial-summary", response_model=CustomerFinancialSummary)
async def get_customer_financial_summary(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get detailed financial summary for a customer
    
    Includes:
    - Total invoices and amounts
    - Payment history metrics
    - Payment score (0-100)
    """
    summary = await service.get_customer_financial_summary(customer_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    return summary


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Create a new customer
    
    **Request Body:**
    - name: Customer name (required)
    - email: Primary email (required)
    - phone: Primary phone in format 254XXXXXXXXX (required)
    - Other fields optional
    """
    try:
        new_customer = await service.create_customer(customer)
        return new_customer
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(
    customer_id: str,
    customer: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Update an existing customer
    
    **Path Parameters:**
    - customer_id: Unique customer identifier
    
    **Request Body:**
    - All fields optional
    - Only provided fields will be updated
    """
    updated_customer = await service.update_customer(customer_id, customer)
    
    if not updated_customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    return updated_customer


@router.delete("/{customer_id}", status_code=200)
async def delete_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Delete a customer (soft delete - sets status to inactive)
    
    **Path Parameters:**
    - customer_id: Unique customer identifier
    """
    success = await service.delete_customer(customer_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    return {
        "status": "success",
        "message": f"Customer {customer_id} has been deactivated"
    }


@router.post("/{customer_id}/refresh-financials", status_code=200)
async def refresh_customer_financials(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
):
    """
    Recalculate customer financial summary from invoices
    
    Use this endpoint to sync customer financials with invoice data
    """
    success = await service.refresh_customer_financials(customer_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found or has no invoices")
    
    return {
        "status": "success",
        "message": f"Financial summary refreshed for customer {customer_id}"
    }


@router.get("/{customer_id}/invoices")
async def get_customer_invoices(
    customer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get all invoices for a specific customer
    
    **Path Parameters:**
    - customer_id: Unique customer identifier
    
    **Query Parameters:**
    - skip: Number of invoices to skip
    - limit: Maximum number of invoices to return
    """
    # Verify customer exists
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    # Get invoices
    invoices_cursor = service.invoices.find(
        {"customer_id": customer_id}
    ).sort("issue_date", -1).skip(skip).limit(limit)
    
    invoices = await invoices_cursor.to_list(length=limit)
    
    # Remove MongoDB _id and format
    for invoice in invoices:
        invoice.pop("_id", None)
        invoice["id"] = invoice.get("invoice_id", "")
    
    total = await service.invoices.count_documents({"customer_id": customer_id})
    
    return {
        "invoices": invoices,
        "total": total,
        "limit": limit,
        "skip": skip,
        "customer_id": customer_id
    }


@router.get("/{customer_id}/payments")
async def get_customer_payments(
    customer_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get payment history for a specific customer
    
    **Path Parameters:**
    - customer_id: Unique customer identifier
    """
    # Verify customer exists
    customer = await service.get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    
    # Get customer name to match transactions
    customer_name = customer.name
    
    # Get payments (transactions with type=payment for this customer)
    payments_cursor = service.transactions.find({
        "customer_name": customer_name,
        "type": "payment"
    }).sort("created_at", -1).skip(skip).limit(limit)
    
    payments = await payments_cursor.to_list(length=limit)
    
    # Format payments
    for payment in payments:
        payment.pop("_id", None)
        payment["id"] = str(payment.get("transaction_id", ""))
    
    total = await service.transactions.count_documents({
        "customer_name": customer_name,
        "type": "payment"
    })
    
    return {
        "payments": payments,
        "total": total,
        "limit": limit,
        "skip": skip,
        "customer_id": customer_id
    }
