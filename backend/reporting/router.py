"""
API Router for financial reports
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from database.mongodb import get_database, Database
from .service import ReportingService
from .models import ReportTypesResponse
from .tax_service import TaxService
from .tax_models import VATReport, TaxPeriod
from .customer_service import CustomerStatementService
from .reconciliation_report_service import ReconciliationReportService
from .predictive_service import PredictiveAnalyticsService
from .ai_reports_service import CustomAIReportsService as CustomAIReportService

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


@router.get("/tax/vat-summary", response_model=VATReport)
async def get_vat_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    include_transactions: bool = Query(True, description="Include detailed transactions"),
    db: Database = Depends(get_database)
):
    """
    Generate VAT Summary Report
    
    Comprehensive VAT/Tax report including:
    - Output VAT (sales/invoices)
    - Input VAT (purchases/expenses)
    - VAT breakdown by rate
    - Net VAT payable/refundable
    - Compliance status and filing deadline
    - Detailed transactions (optional)
    
    Perfect for tax filing and compliance checks.
    """
    try:
        service = TaxService(db)
        vat_report = await service.generate_vat_report(
            start_date=start_date,
            end_date=end_date,
            include_transactions=include_transactions
        )
        return vat_report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating VAT report: {str(e)}")


@router.get("/tax/periods/{year}", response_model=list[TaxPeriod])
async def get_tax_periods(
    year: int,
    db: Database = Depends(get_database)
):
    """
    Get tax filing periods for a year
    
    Returns all tax periods (monthly for Kenya VAT) including:
    - Period start and end dates
    - Filing deadlines
    - Status (open, filed, overdue)
    
    Useful for tax calendar and compliance planning.
    """
    try:
        service = TaxService(db)
        periods = await service.get_tax_periods(year)
        return periods
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tax periods: {str(e)}")


@router.get("/tax/filing-export")
async def export_for_filing(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Database = Depends(get_database)
):
    """
    Export VAT report in format ready for tax authority filing
    
    Returns structured data formatted for:
    - KRA iTax portal (Kenya)
    - Other tax authority systems
    
    Includes all required fields for electronic filing.
    """
    try:
        service = TaxService(db)
        vat_report = await service.generate_vat_report(
            start_date=start_date,
            end_date=end_date,
            include_transactions=False
        )
        filing_data = await service.export_vat_report_for_filing(vat_report)
        return filing_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting filing data: {str(e)}")


# ==================== CUSTOMER STATEMENT ENDPOINTS ====================

@router.get("/customer-statement/{customer_id}")
async def get_customer_statement(
    customer_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    include_paid: bool = Query(True, description="Include paid invoices and transactions"),
    db: Database = Depends(get_database)
):
    """
    Generate detailed customer statement
    
    Shows complete transaction history for a customer including:
    - Opening balance
    - All invoices (with status and due dates)
    - All payments received
    - Running balance after each transaction
    - Aging breakdown (current, 30, 60, 90+ days)
    - Summary metrics
    
    Parameters:
    - customer_id: Customer ID
    - start_date: Optional start date (defaults to 90 days ago)
    - end_date: Optional end date (defaults to today)
    - include_paid: Include paid invoices (default: true)
    """
    try:
        service = CustomerStatementService(db)
        statement = await service.generate_customer_statement(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            include_paid=include_paid
        )
        return statement
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating customer statement: {str(e)}")


@router.get("/customers")
async def get_customer_list(
    db: Database = Depends(get_database)
):
    """
    Get list of all customers with outstanding balances
    
    Returns:
    - Customer ID, name, contact info
    - Outstanding balance
    - Number of pending invoices
    
    Sorted by outstanding balance (highest first)
    """
    try:
        service = CustomerStatementService(db)
        customers = await service.get_customer_list()
        return {
            "customers": customers,
            "total_customers": len(customers),
            "total_outstanding": round(sum(c["outstanding_balance"] for c in customers), 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customer list: {str(e)}")


# ==================== RECONCILIATION REPORT ENDPOINTS ====================

@router.get("/reconciliation")
async def get_reconciliation_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status: matched, unmatched, partial, needs_review"),
    db: Database = Depends(get_database)
):
    """
    Generate reconciliation report
    
    Shows payment matching status including:
    - Matched transactions (payments linked to invoices)
    - Unmatched transactions (payments without invoices)
    - Partial matches (payments partially applied)
    - Transactions needing review (low confidence matches)
    - Unmatched invoices (invoices without payments)
    - Common reconciliation issues
    - Match rate statistics
    
    Parameters:
    - start_date: Optional start date (defaults to 30 days ago)
    - end_date: Optional end date (defaults to today)
    - status: Optional filter (matched, unmatched, partial, needs_review)
    """
    try:
        service = ReconciliationReportService(db)
        report = await service.generate_reconciliation_report(
            start_date=start_date,
            end_date=end_date,
            status=status
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating reconciliation report: {str(e)}")


@router.get("/reconciliation/summary")
async def get_reconciliation_summary(
    days: int = Query(30, description="Number of days to include in summary"),
    db: Database = Depends(get_database)
):
    """
    Get high-level reconciliation summary
    
    Quick overview for dashboard showing:
    - Total transactions
    - Count by status (matched, unmatched, etc.)
    - Amount by status
    - Match rate percentage
    - Number needing attention
    
    Parameters:
    - days: Number of days to include (default: 30)
    """
    try:
        service = ReconciliationReportService(db)
        summary = await service.get_reconciliation_summary(days=days)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching reconciliation summary: {str(e)}")


# ==================== PREDICTIVE ANALYTICS ENDPOINTS ====================

@router.get("/predictive/revenue-forecast")
async def get_revenue_forecast(
    months_ahead: int = Query(3, description="Number of months to forecast", ge=1, le=12),
    include_confidence: bool = Query(True, description="Include confidence intervals"),
    db: Database = Depends(get_database)
):
    """
    Generate revenue forecast using historical data
    
    Uses statistical analysis of historical invoice data to predict future revenue:
    - Simple moving average with growth rate adjustment
    - Confidence intervals based on historical volatility
    - Trend analysis (increasing, decreasing, stable)
    - Accuracy metrics
    
    Parameters:
    - months_ahead: Number of months to forecast (1-12, default: 3)
    - include_confidence: Include confidence intervals (default: true)
    
    Returns:
    - Monthly revenue predictions
    - Historical summary and trends
    - Confidence intervals (if requested)
    - Accuracy metrics
    """
    try:
        service = PredictiveAnalyticsService(db)
        forecast = await service.generate_revenue_forecast(
            months_ahead=months_ahead,
            include_confidence=include_confidence
        )
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating revenue forecast: {str(e)}")


@router.get("/predictive/expense-forecast")
async def get_expense_forecast(
    months_ahead: int = Query(3, description="Number of months to forecast", ge=1, le=12),
    include_confidence: bool = Query(True, description="Include confidence intervals"),
    db: Database = Depends(get_database)
):
    """
    Generate expense forecast using historical transaction data
    
    Analyzes historical expense patterns to predict future expenses:
    - Monthly expense predictions
    - Category-wise breakdown
    - Growth trends
    - Top expense categories
    
    Parameters:
    - months_ahead: Number of months to forecast (1-12, default: 3)
    - include_confidence: Include confidence intervals (default: true)
    
    Returns:
    - Monthly expense predictions
    - Top expense categories
    - Trends and patterns
    - Confidence intervals (if requested)
    """
    try:
        service = PredictiveAnalyticsService(db)
        forecast = await service.generate_expense_forecast(
            months_ahead=months_ahead,
            include_confidence=include_confidence
        )
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating expense forecast: {str(e)}")


@router.get("/predictive/cash-flow-forecast")
async def get_cash_flow_forecast(
    months_ahead: int = Query(3, description="Number of months to forecast", ge=1, le=12),
    db: Database = Depends(get_database)
):
    """
    Generate cash flow forecast combining revenue and expense predictions
    
    Comprehensive cash flow analysis:
    - Net cash flow predictions (revenue - expenses)
    - Positive/negative cash flow identification
    - Average monthly cash flow
    - AI-generated insights
    
    Parameters:
    - months_ahead: Number of months to forecast (1-12, default: 3)
    
    Returns:
    - Monthly cash flow predictions
    - Total and average net cash flow
    - Cash flow status (positive/negative)
    - Actionable insights
    """
    try:
        service = PredictiveAnalyticsService(db)
        forecast = await service.generate_cash_flow_forecast(months_ahead=months_ahead)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cash flow forecast: {str(e)}")


@router.get("/predictive/summary")
async def get_predictive_summary(
    db: Database = Depends(get_database)
):
    """
    Get high-level predictive analytics summary for dashboard
    
    Quick overview of next month's predictions:
    - Predicted revenue
    - Predicted expenses
    - Net prediction
    - Trends (increasing, decreasing, stable)
    
    Useful for dashboard widgets and quick insights.
    """
    try:
        service = PredictiveAnalyticsService(db)
        summary = await service.get_predictive_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching predictive summary: {str(e)}")


# ==================== CUSTOM AI REPORTS ENDPOINTS ====================

@router.post("/ai/custom-report")
async def generate_custom_ai_report(
    query: str = Query(..., description="Natural language query for report"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    include_data: bool = Query(True, description="Include supporting data"),
    db: Database = Depends(get_database)
):
    """
    Generate custom financial report using AI
    
    Ask natural language questions about your financial data:
    - "What are my top performing customers?"
    - "Why are my expenses increasing?"
    - "How can I improve collections?"
    - "What trends do you see in my revenue?"
    
    The AI will analyze your financial data and provide:
    - Detailed insights
    - Key findings
    - Actionable recommendations
    - Supporting data
    
    Parameters:
    - query: Your question in natural language
    - start_date: Optional date filter
    - end_date: Optional date filter
    - include_data: Include raw data in response
    
    Note: Requires AI service to be configured
    """
    try:
        service = CustomAIReportService(db)
        report = await service.generate_custom_report(
            query=query,
            start_date=start_date,
            end_date=end_date,
            include_data=include_data
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating custom AI report: {str(e)}")


@router.get("/ai/anomaly-detection")
async def detect_anomalies(
    days: int = Query(30, description="Number of days to analyze", ge=7, le=365),
    db: Database = Depends(get_database)
):
    """
    Detect financial anomalies using AI analysis
    
    Automatically identifies unusual patterns:
    - Unusual transaction amounts (statistical outliers)
    - Duplicate transactions
    - Unusual invoice patterns
    - High overdue rates
    - Other irregularities
    
    Each anomaly is classified by severity:
    - HIGH: Requires immediate attention
    - MEDIUM: Should be reviewed
    - LOW: Informational
    
    Parameters:
    - days: Number of days to analyze (7-365, default: 30)
    
    Returns:
    - List of detected anomalies with descriptions
    - Severity classification
    - Summary statistics
    """
    try:
        service = CustomAIReportService(db)
        anomalies = await service.detect_anomalies(days=days)
        return anomalies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")


@router.get("/ai/executive-summary")
async def get_executive_summary(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (defaults to current month)"),
    db: Database = Depends(get_database)
):
    """
    Generate executive summary for a month using AI
    
    Comprehensive monthly overview including:
    - Key metrics (revenue, expenses, profit)
    - Collection rate and invoice statistics
    - Highlights (positive achievements)
    - Concerns (issues requiring attention)
    - Recommendations (action items)
    
    Perfect for monthly board meetings or executive reports.
    
    Parameters:
    - month: Target month in YYYY-MM format (defaults to current month)
    
    Returns:
    - Executive summary with AI-enhanced insights
    - Key performance metrics
    - Highlights, concerns, and recommendations
    """
    try:
        service = CustomAIReportService(db)
        summary = await service.generate_executive_summary(month=month)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating executive summary: {str(e)}")
