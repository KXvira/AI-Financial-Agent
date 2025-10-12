"""
Pydantic models for financial reports
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# ============================================================================
# REQUEST MODELS
# ============================================================================

class ReportRequest(BaseModel):
    """Generic report generation request"""
    report_type: str = Field(..., description="Type of report to generate")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional filters")
    format: str = Field("json", description="Output format: json, pdf, excel, csv")


class DateRangeFilter(BaseModel):
    """Date range filter for reports"""
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    preset: Optional[str] = Field(None, description="Preset: today, this_week, this_month, this_quarter, this_year, last_month, last_quarter, last_year, custom")


class ExportRequest(BaseModel):
    """Request to export a report"""
    report_type: str = Field(..., description="Type of report to export")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    format: str = Field(..., description="Export format: pdf, excel, csv")


# ============================================================================
# INCOME STATEMENT MODELS
# ============================================================================

class RevenueSection(BaseModel):
    """Revenue section of income statement"""
    total_revenue: float = Field(..., description="Total revenue")
    invoiced_amount: float = Field(..., description="Total amount invoiced")
    paid_amount: float = Field(..., description="Amount received")
    pending_amount: float = Field(..., description="Amount pending/unpaid")
    invoice_count: int = Field(..., description="Number of invoices")
    paid_invoice_count: int = Field(..., description="Number of paid invoices")


class ExpenseSection(BaseModel):
    """Expense section of income statement"""
    total_expenses: float = Field(..., description="Total expenses")
    by_category: Dict[str, float] = Field(..., description="Expenses grouped by category")
    transaction_count: int = Field(..., description="Number of expense transactions")
    top_categories: List[Dict[str, Any]] = Field(default_factory=list, description="Top expense categories with percentages")


class IncomeStatementReport(BaseModel):
    """Complete income statement (P&L) report"""
    report_type: str = Field("income_statement", description="Report type identifier")
    report_name: str = Field("Income Statement", description="Human-readable report name")
    period_start: str = Field(..., description="Report period start date")
    period_end: str = Field(..., description="Report period end date")
    generated_at: str = Field(..., description="Timestamp when report was generated")
    currency: str = Field("KES", description="Currency code")
    
    # Financial data
    revenue: RevenueSection = Field(..., description="Revenue section")
    expenses: ExpenseSection = Field(..., description="Expenses section")
    
    # Calculations
    net_income: float = Field(..., description="Net income (revenue - expenses)")
    net_margin: float = Field(..., description="Net profit margin percentage")
    
    # Additional metrics
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Additional key metrics")


# ============================================================================
# CASH FLOW MODELS
# ============================================================================

class CashFlowInflows(BaseModel):
    """Cash inflows section"""
    total_inflows: float = Field(..., description="Total cash inflows")
    customer_payments: float = Field(..., description="Payments from customers")
    other_income: float = Field(..., description="Other income sources")
    transaction_count: int = Field(..., description="Number of inflow transactions")


class CashFlowOutflows(BaseModel):
    """Cash outflows section"""
    total_outflows: float = Field(..., description="Total cash outflows")
    by_category: Dict[str, float] = Field(..., description="Outflows grouped by category")
    transaction_count: int = Field(..., description="Number of outflow transactions")


class CashFlowReport(BaseModel):
    """Cash flow statement report"""
    report_type: str = Field("cash_flow", description="Report type identifier")
    report_name: str = Field("Cash Flow Statement", description="Human-readable report name")
    period_start: str = Field(..., description="Report period start date")
    period_end: str = Field(..., description="Report period end date")
    generated_at: str = Field(..., description="Timestamp when report was generated")
    currency: str = Field("KES", description="Currency code")
    
    # Cash flow data
    inflows: CashFlowInflows = Field(..., description="Cash inflows")
    outflows: CashFlowOutflows = Field(..., description="Cash outflows")
    
    # Calculations
    net_cash_flow: float = Field(..., description="Net cash flow (inflows - outflows)")
    opening_balance: float = Field(0.0, description="Opening cash balance")
    closing_balance: float = Field(..., description="Closing cash balance")
    
    # Metrics
    burn_rate: Optional[float] = Field(None, description="Monthly burn rate if negative")
    runway_months: Optional[float] = Field(None, description="Months of runway remaining")


# ============================================================================
# ACCOUNTS RECEIVABLE AGING MODELS
# ============================================================================

class AgingBucket(BaseModel):
    """Single aging bucket"""
    bucket_name: str = Field(..., description="Bucket name (e.g., 'Current', '31-60 days')")
    min_days: int = Field(..., description="Minimum days overdue")
    max_days: Optional[int] = Field(None, description="Maximum days overdue (None for 90+)")
    invoice_count: int = Field(..., description="Number of invoices in bucket")
    total_amount: float = Field(..., description="Total amount in bucket")
    percentage: float = Field(..., description="Percentage of total outstanding")
    invoices: List[Dict[str, Any]] = Field(default_factory=list, description="List of invoices in bucket")


class ARAgingReport(BaseModel):
    """Accounts Receivable Aging Report"""
    report_type: str = Field("ar_aging", description="Report type identifier")
    report_name: str = Field("Accounts Receivable Aging", description="Human-readable report name")
    as_of_date: str = Field(..., description="Report as-of date")
    generated_at: str = Field(..., description="Timestamp when report was generated")
    currency: str = Field("KES", description="Currency code")
    
    # AR data
    total_outstanding: float = Field(..., description="Total outstanding amount")
    total_invoices: int = Field(..., description="Total number of outstanding invoices")
    
    # Aging buckets
    buckets: List[AgingBucket] = Field(..., description="Aging buckets")
    
    # Summary metrics
    current_percentage: float = Field(..., description="Percentage of current receivables")
    overdue_percentage: float = Field(..., description="Percentage overdue")
    collection_risk_score: float = Field(..., description="Risk score (0-100, higher is riskier)")
    
    # Top customers with outstanding balances
    top_customers: List[Dict[str, Any]] = Field(default_factory=list, description="Top customers by outstanding amount")


# ============================================================================
# DASHBOARD METRICS MODELS
# ============================================================================

class DashboardMetrics(BaseModel):
    """Dashboard metrics and KPIs"""
    report_type: str = Field("dashboard_metrics", description="Report type identifier")
    report_name: str = Field("Dashboard Metrics", description="Human-readable report name")
    generated_at: str = Field(..., description="Timestamp when report was generated")
    currency: str = Field("KES", description="Currency code")
    
    # Revenue metrics
    total_revenue: float = Field(..., description="Total revenue")
    revenue_trend: str = Field(..., description="Revenue trend: up, down, stable")
    revenue_change_pct: float = Field(..., description="Revenue change percentage")
    
    # Invoice metrics
    total_invoices: int = Field(..., description="Total number of invoices")
    paid_invoices: int = Field(..., description="Number of paid invoices")
    pending_invoices: int = Field(..., description="Number of pending invoices")
    overdue_invoices: int = Field(..., description="Number of overdue invoices")
    average_invoice_value: float = Field(..., description="Average invoice value")
    
    # Customer metrics
    total_customers: int = Field(..., description="Total number of customers")
    active_customers: int = Field(..., description="Active customers (with recent transactions)")
    revenue_per_customer: float = Field(..., description="Average revenue per customer")
    
    # Collection metrics
    total_outstanding: float = Field(..., description="Total outstanding amount")
    collection_rate: float = Field(..., description="Collection rate percentage")
    dso: float = Field(..., description="Days Sales Outstanding")
    
    # Expense metrics
    total_expenses: float = Field(..., description="Total expenses")
    top_expense_category: str = Field(..., description="Top expense category")
    expense_trend: str = Field(..., description="Expense trend: up, down, stable")
    
    # Profitability
    net_income: float = Field(..., description="Net income")
    profit_margin: float = Field(..., description="Profit margin percentage")
    
    # Transaction volume
    transaction_count: int = Field(..., description="Total transactions")
    reconciled_transactions: int = Field(..., description="Reconciled transactions")
    reconciliation_rate: float = Field(..., description="Reconciliation rate percentage")


# ============================================================================
# REPORT TYPE METADATA
# ============================================================================

class ReportTypeInfo(BaseModel):
    """Information about a report type"""
    id: str = Field(..., description="Report type identifier")
    name: str = Field(..., description="Display name")
    description: str = Field(..., description="Report description")
    category: str = Field(..., description="Category: financial, receivables, analytics, operational")
    icon: str = Field(..., description="Icon/emoji for display")
    requires_date_range: bool = Field(..., description="Whether date range is required")
    available_formats: List[str] = Field(..., description="Available export formats")
    estimated_time: str = Field(..., description="Estimated generation time")


class ReportTypesResponse(BaseModel):
    """Response with available report types"""
    report_types: List[ReportTypeInfo] = Field(..., description="List of available report types")
    total: int = Field(..., description="Total number of report types")
    categories: List[str] = Field(..., description="Available categories")


# ============================================================================
# ERROR MODELS
# ============================================================================

class ReportError(BaseModel):
    """Report generation error"""
    error: str = Field(..., description="Error message")
    report_type: str = Field(..., description="Report type that failed")
    timestamp: str = Field(..., description="Error timestamp")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
