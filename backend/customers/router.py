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
    Get overall customer statistics with real-time financial data from AR Aging
    
    Returns:
    - Total number of customers
    - Active/inactive breakdown
    - Total outstanding balance (from AR Aging)
    - Customers with overdue payments (from AR Aging)
    - Top 5 customers by outstanding balance
    """
    try:
        # Import here to avoid circular dependency
        from reporting.service import ReportingService
        
        # Get basic customer counts
        all_customers = await service.customers.find().to_list(length=None)
        total_customers = len(all_customers)
        active_customers = sum(1 for c in all_customers if c.get("status") == "active")
        inactive_customers = total_customers - active_customers
        
        # Get AR Aging data for accurate financial stats
        reporting_service = ReportingService(service.db)
        aging_report_model = await reporting_service.generate_ar_aging(as_of_date=None, filters={})
        aging_report = aging_report_model.model_dump() if hasattr(aging_report_model, 'model_dump') else aging_report_model
        
        # Process AR aging buckets to aggregate by customer
        aging_by_customer = {}
        
        for bucket in aging_report.get('buckets', []):
            bucket_name = bucket.get('bucket_name', '')
            is_overdue = any(x in bucket_name for x in ['31-60', '61-90', '90+', 'over 90'])
            
            for invoice in bucket.get('invoices', []):
                customer_name = invoice.get('customer_name', '')
                amount = invoice.get('amount', 0)
                
                if customer_name not in aging_by_customer:
                    aging_by_customer[customer_name] = {
                        'total_outstanding': 0,
                        'overdue_amount': 0,
                        'has_overdue': False
                    }
                
                aging_by_customer[customer_name]['total_outstanding'] += amount
                if is_overdue:
                    aging_by_customer[customer_name]['overdue_amount'] += amount
                    aging_by_customer[customer_name]['has_overdue'] = True
        
        # Use AR Aging report's total (already calculated correctly from all invoices)
        total_outstanding = aging_report.get('total_outstanding', 0)
        customers_with_overdue = sum(1 for data in aging_by_customer.values() if data['has_overdue'])
        avg_outstanding = total_outstanding / total_customers if total_customers > 0 else 0
        
        # Get top 5 customers by outstanding balance
        top_customers_data = sorted(
            aging_by_customer.items(),
            key=lambda x: x[1]['total_outstanding'],
            reverse=True
        )[:5]
        
        top_customers_list = [
            {
                "customer_id": "",  # We don't have ID in aging report
                "name": name,
                "total_billed": data['total_outstanding'],
                "total_paid": 0,
                "outstanding_balance": data['total_outstanding']
            }
            for name, data in top_customers_data
        ]
        
        return CustomerStats(
            total_customers=total_customers,
            active_customers=active_customers,
            inactive_customers=inactive_customers,
            total_outstanding=round(total_outstanding, 2),
            customers_with_overdue=customers_with_overdue,
            average_outstanding=round(avg_outstanding, 2),
            top_customers=top_customers_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")


@router.get("/with-financials", response_model=dict)
async def get_customers_with_financials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    service: CustomerService = Depends(get_customer_service)
):
    """
    Get customers enriched with real-time financial data from AR Aging report
    
    Returns customers with:
    - outstanding_balance: Total unpaid amount
    - overdue_amount: Amount past due date
    - current_amount: Amount not yet due (0-30 days)
    - aging_30_60: Amount 31-60 days old
    - aging_61_90: Amount 61-90 days old
    - aging_over_90: Amount over 90 days old
    - total_invoices: Count of invoices
    - payment_status: 'overdue', 'current', or 'paid'
    
    This endpoint uses AR Aging aggregation for real-time accuracy.
    """
    try:
        # Import here to avoid circular dependency
        from reporting.service import ReportingService
        
        # 1. Get AR Aging data (source of truth for financial data)
        reporting_service = ReportingService(service.db)
        aging_report_model = await reporting_service.generate_ar_aging(as_of_date=None, filters={})
        
        # Convert to dict for easier processing
        aging_report = aging_report_model.model_dump() if hasattr(aging_report_model, 'model_dump') else aging_report_model
        
        # 2. Get basic customer list
        customers, total = await service.get_customers(skip=skip, limit=limit)
        
        # 3. Process AR aging buckets to aggregate by customer
        aging_by_customer = {}
        
        for bucket in aging_report.get('buckets', []):
            bucket_name = bucket.get('bucket_name', '')
            is_current = '0-30' in bucket_name
            is_30_60 = '31-60' in bucket_name
            is_61_90 = '61-90' in bucket_name
            is_over_90 = '90+' in bucket_name or 'over 90' in bucket_name.lower()
            
            for invoice in bucket.get('invoices', []):
                customer_name = invoice.get('customer_name', '')
                amount = invoice.get('amount', 0)
                days_outstanding = invoice.get('days_outstanding', 0)
                
                if customer_name not in aging_by_customer:
                    aging_by_customer[customer_name] = {
                        'total_outstanding': 0,
                        'overdue_amount': 0,
                        'current': 0,
                        'days_31_60': 0,
                        'days_61_90': 0,
                        'over_90_days': 0,
                        'invoice_count': 0
                    }
                
                aging_by_customer[customer_name]['total_outstanding'] += amount
                aging_by_customer[customer_name]['invoice_count'] += 1
                
                # Categorize by aging bucket
                if is_current:
                    aging_by_customer[customer_name]['current'] += amount
                elif is_30_60:
                    aging_by_customer[customer_name]['days_31_60'] += amount
                    aging_by_customer[customer_name]['overdue_amount'] += amount
                elif is_61_90:
                    aging_by_customer[customer_name]['days_61_90'] += amount
                    aging_by_customer[customer_name]['overdue_amount'] += amount
                elif is_over_90:
                    aging_by_customer[customer_name]['over_90_days'] += amount
                    aging_by_customer[customer_name]['overdue_amount'] += amount
        
        # 4. Enrich customers with financial data
        enriched_customers = []
        for customer in customers:
            customer_dict = customer.model_dump()
            customer_name = customer_dict.get('name')
            
            # Get aging data for this customer (by name)
            aging_data = aging_by_customer.get(customer_name, {})
            
            # Add financial fields
            customer_dict['outstanding_balance'] = aging_data.get('total_outstanding', 0)
            customer_dict['overdue_amount'] = aging_data.get('overdue_amount', 0)
            customer_dict['current_amount'] = aging_data.get('current', 0)
            customer_dict['aging_30_60'] = aging_data.get('days_31_60', 0)
            customer_dict['aging_61_90'] = aging_data.get('days_61_90', 0)
            customer_dict['aging_over_90'] = aging_data.get('over_90_days', 0)
            customer_dict['total_invoices'] = aging_data.get('invoice_count', 0)
            
            # Determine payment status based on aging data
            if aging_data.get('overdue_amount', 0) > 0:
                customer_dict['payment_status'] = 'overdue'
            elif aging_data.get('total_outstanding', 0) > 0:
                customer_dict['payment_status'] = 'current'
            else:
                customer_dict['payment_status'] = 'paid'
            
            enriched_customers.append(customer_dict)
        
        return {
            "customers": enriched_customers,
            "total": total,
            "limit": limit,
            "skip": skip,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers with financials: {str(e)}")


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


@router.post("/bulk/refresh-financials", status_code=200)
async def bulk_refresh_customer_financials(
    service: CustomerService = Depends(get_customer_service)
):
    """
    Recalculate financial summaries for ALL customers
    
    Use this endpoint to sync all customer financials with invoice data.
    This may take a while for large customer bases.
    """
    try:
        # Get all customers
        customers = await service.customers.find({}).to_list(length=None)
        
        updated = 0
        failed = 0
        
        for customer in customers:
            customer_id = customer.get("customer_id")
            if not customer_id:
                failed += 1
                continue
            
            try:
                success = await service.refresh_customer_financials(customer_id)
                if success:
                    updated += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
        
        return {
            "status": "success",
            "message": f"Refreshed financials for {updated} customers",
            "updated": updated,
            "failed": failed,
            "total": len(customers)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh customer financials: {str(e)}")
