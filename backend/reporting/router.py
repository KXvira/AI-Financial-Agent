"""
API Router for financial reports
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from database.mongodb import get_database, Database
from .service import ReportingService
from .models import ReportTypesResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/types", response_model=ReportTypesResponse)
async def get_report_types(
    db: Database = Depends(get_database)
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
    db: Database = Depends(get_database)
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
    db: Database = Depends(get_database)
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
    db: Database = Depends(get_database)
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
    db: Database = Depends(get_database)
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


@router.get("/trends/revenue")
async def get_revenue_trends(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, quarterly"),
    months: int = Query(12, description="Number of periods to include", ge=1, le=36),
    db: Database = Depends(get_database)
):
    """
    Get revenue trend analysis over time
    
    Parameters:
    - **period**: Aggregation period (daily, weekly, monthly, quarterly)
    - **months**: Number of periods to include (1-36)
    
    Returns:
    - Time series data of revenue
    - Month-over-month/period-over-period change percentages
    - Trend direction (up/down/stable)
    """
    try:
        service = ReportingService(db)
        trends = await service.get_revenue_trends(period, months)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating revenue trends: {str(e)}")


@router.get("/trends/expenses")
async def get_expense_trends(
    period: str = Query("monthly", description="Period: daily, weekly, monthly, quarterly"),
    months: int = Query(12, description="Number of periods to include", ge=1, le=36),
    db: Database = Depends(get_database)
):
    """
    Get expense trend analysis over time
    
    Parameters:
    - **period**: Aggregation period (daily, weekly, monthly, quarterly)
    - **months**: Number of periods to include (1-36)
    
    Returns:
    - Time series data of expenses by category
    - Month-over-month/period-over-period change percentages
    - Trend direction (up/down/stable)
    """
    try:
        service = ReportingService(db)
        trends = await service.get_expense_trends(period, months)
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating expense trends: {str(e)}")


@router.get("/comparison/mom")
async def get_month_over_month(
    db: Database = Depends(get_database)
):
    """
    Get Month-over-Month comparison
    
    Compares current month metrics with previous month:
    - Revenue comparison
    - Expense comparison
    - Net income comparison
    - Invoice metrics comparison
    - Collection rate comparison
    """
    try:
        service = ReportingService(db)
        comparison = await service.get_month_over_month_comparison()
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating MoM comparison: {str(e)}")


@router.get("/comparison/yoy")
async def get_year_over_year(
    db: Database = Depends(get_database)
):
    """
    Get Year-over-Year comparison
    
    Compares current year metrics with previous year:
    - Revenue comparison
    - Expense comparison
    - Net income comparison
    - Growth rates
    - Customer acquisition
    """
    try:
        service = ReportingService(db)
        comparison = await service.get_year_over_year_comparison()
        return comparison
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating YoY comparison: {str(e)}")
