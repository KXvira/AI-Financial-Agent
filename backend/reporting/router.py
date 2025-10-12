"""
API Router for financial reports
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.mongodb import get_database
from .service import ReportingService
from .models import ReportTypesResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/types", response_model=ReportTypesResponse)
async def get_report_types(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get list of available report types
    
    Returns information about all available financial reports including:
    - Report ID and name
    - Description
    - Category
    - Whether date range is required
    - Available export formats
    - Estimated generation time
    """
    try:
        service = ReportingService(db)
        return await service.get_report_types()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching report types: {str(e)}")


@router.get("/income-statement")
async def get_income_statement(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)", example="2025-01-01"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)", example="2025-12-31"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate Income Statement (Profit & Loss) report
    
    Shows revenue, expenses, and net income for the specified period.
    
    Parameters:
    - **start_date**: Start date of the reporting period (YYYY-MM-DD)
    - **end_date**: End date of the reporting period (YYYY-MM-DD)
    - **customer_id**: Optional filter for specific customer
    
    Returns:
    - Revenue section (total, paid, pending)
    - Expenses by category
    - Net income and profit margin
    - Key metrics (average invoice, collection rate, etc.)
    """
    try:
        service = ReportingService(db)
        
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        
        report = await service.generate_income_statement(start_date, end_date, filters)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating income statement: {str(e)}")


@router.get("/cash-flow")
async def get_cash_flow(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)", example="2025-01-01"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)", example="2025-12-31"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate Cash Flow Statement
    
    Shows cash inflows and outflows for the specified period.
    
    Parameters:
    - **start_date**: Start date of the reporting period (YYYY-MM-DD)
    - **end_date**: End date of the reporting period (YYYY-MM-DD)
    
    Returns:
    - Cash inflows (customer payments, other income)
    - Cash outflows (expenses by category)
    - Net cash flow
    - Opening and closing balances
    - Burn rate and runway (if negative cash flow)
    """
    try:
        service = ReportingService(db)
        report = await service.generate_cash_flow(start_date, end_date)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cash flow: {str(e)}")


@router.get("/ar-aging")
async def get_ar_aging(
    as_of_date: Optional[str] = Query(None, description="Calculate aging as of this date (YYYY-MM-DD), defaults to today"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate Accounts Receivable Aging Report
    
    Shows outstanding invoices grouped by age (current, 31-60, 61-90, 90+ days).
    
    Parameters:
    - **as_of_date**: Date to calculate aging as of (defaults to today)
    - **customer_id**: Optional filter for specific customer
    
    Returns:
    - Total outstanding amount and invoice count
    - Aging buckets with amounts and percentages
    - Collection risk score
    - Top customers with outstanding balances
    """
    try:
        service = ReportingService(db)
        
        filters = {}
        if customer_id:
            filters["customer_id"] = customer_id
        
        report = await service.generate_ar_aging(as_of_date, filters)
        return report
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating AR aging: {str(e)}")


@router.get("/dashboard-metrics")
async def get_dashboard_metrics(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get Dashboard Metrics and KPIs
    
    Returns real-time key performance indicators and metrics.
    
    Returns:
    - Revenue metrics (total, trend, average invoice)
    - Invoice metrics (total, paid, pending, overdue)
    - Customer metrics (total, active, revenue per customer)
    - Collection metrics (outstanding, collection rate, DSO)
    - Expense metrics (total, top category, trend)
    - Profitability (net income, profit margin)
    - Transaction metrics (total, reconciled, reconciliation rate)
    """
    try:
        service = ReportingService(db)
        metrics = await service.get_dashboard_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard metrics: {str(e)}")
