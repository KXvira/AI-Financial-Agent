"""
Service for generating financial reports and analytics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from .models import (
    IncomeStatementReport,
    RevenueSection,
    ExpenseSection,
    CashFlowReport,
    CashFlowInflows,
    CashFlowOutflows,
    ARAgingReport,
    AgingBucket,
    DashboardMetrics,
    ReportTypeInfo,
    ReportTypesResponse,
)

logger = logging.getLogger("financial-agent.reporting")


class ReportingService:
    """Service for generating various financial reports"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_report_types(self) -> ReportTypesResponse:
        """Get list of available report types"""
        report_types = [
            ReportTypeInfo(
                id="income_statement",
                name="Income Statement",
                description="Profit & Loss statement showing revenue and expenses for a period",
                category="financial",
                icon="📊",
                requires_date_range=True,
                available_formats=["json", "pdf", "excel", "csv"],
                estimated_time="2-3 seconds"
            ),
            ReportTypeInfo(
                id="cash_flow",
                name="Cash Flow Statement",
                description="Shows cash inflows and outflows during a period",
                category="financial",
                icon="💰",
                requires_date_range=True,
                available_formats=["json", "pdf", "excel", "csv"],
                estimated_time="2-3 seconds"
            ),
            ReportTypeInfo(
                id="ar_aging",
                name="Accounts Receivable Aging",
                description="Outstanding invoices grouped by age (current, 30, 60, 90+ days)",
                category="receivables",
                icon="📅",
                requires_date_range=False,
                available_formats=["json", "pdf", "excel", "csv"],
                estimated_time="1-2 seconds"
            ),
            ReportTypeInfo(
                id="dashboard_metrics",
                name="Dashboard Metrics",
                description="Key performance indicators and real-time metrics",
                category="analytics",
                icon="📈",
                requires_date_range=False,
                available_formats=["json"],
                estimated_time="1 second"
            ),
        ]
        
        categories = list(set(rt.category for rt in report_types))
        
        return ReportTypesResponse(
            report_types=report_types,
            total=len(report_types),
            categories=sorted(categories)
        )
    
    async def generate_income_statement(
        self,
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> IncomeStatementReport:
        """Generate income statement for date range - based on working demo script"""
        logger.info(f"Generating income statement from {start_date} to {end_date}")
        
        if filters is None:
            filters = {}
        
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # Revenue from paid invoices
        invoice_match = {"date_issued": {"$gte": start_dt, "$lte": end_dt}}
        if "customer_id" in filters:
            invoice_match["customer_id"] = filters["customer_id"]
        
        total_invoices = await self.db.invoices.count_documents(invoice_match)
        
        invoiced_pipeline = [
            {"$match": invoice_match},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        invoiced_result = await self.db.invoices.aggregate(invoiced_pipeline).to_list(1)
        total_invoiced = invoiced_result[0]["total"] if invoiced_result else 0.0
        
        paid_match = {**invoice_match, "status": "paid"}
        paid_invoices = await self.db.invoices.count_documents(paid_match)
        
        paid_pipeline = [
            {"$match": paid_match},
            {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
        ]
        paid_result = await self.db.invoices.aggregate(paid_pipeline).to_list(1)
        total_paid = paid_result[0]["total"] if paid_result else 0.0
        
        total_pending = total_invoiced - total_paid
        
        revenue_section = RevenueSection(
            total_revenue=total_paid,
            invoiced_amount=total_invoiced,
            paid_amount=total_paid,
            pending_amount=total_pending,
            invoice_count=total_invoices,
            paid_invoice_count=paid_invoices
        )
        
        # Expenses from transactions
        expense_match = {"date": {"$gte": start_dt, "$lte": end_dt}, "type": "expense"}
        expense_count = await self.db.transactions.count_documents(expense_match)
        
        expense_pipeline = [
            {"$match": expense_match},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}}
        ]
        
        expense_results = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
        expenses_by_category = {result["_id"]: result["total"] for result in expense_results}
        total_expenses = sum(expenses_by_category.values())
        
        top_categories = []
        for category, amount in sorted(expenses_by_category.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (amount / total_expenses * 100) if total_expenses > 0 else 0
            top_categories.append({
                "category": category,
                "amount": amount,
                "percentage": round(percentage, 1)
            })
        
        expense_section = ExpenseSection(
            total_expenses=total_expenses,
            by_category=expenses_by_category,
            transaction_count=expense_count,
            top_categories=top_categories
        )
        
        # Calculations
        net_income = total_paid - total_expenses
        net_margin = (net_income / total_paid * 100) if total_paid > 0 else 0.0
        avg_invoice = total_paid / paid_invoices if paid_invoices > 0 else 0.0
        
        metrics = {
            "average_invoice_value": round(avg_invoice, 2),
            "collection_rate": round((total_paid / total_invoiced * 100) if total_invoiced > 0 else 0, 1),
            "expense_ratio": round((total_expenses / total_paid * 100) if total_paid > 0 else 0, 1),
            "invoice_count": total_invoices,
            "paid_invoice_count": paid_invoices,
            "pending_invoice_count": total_invoices - paid_invoices
        }
        
        return IncomeStatementReport(
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now().isoformat(),
            revenue=revenue_section,
            expenses=expense_section,
            net_income=round(net_income, 2),
            net_margin=round(net_margin, 2),
            metrics=metrics
        )
    
    async def generate_cash_flow(
        self,
        start_date: str,
        end_date: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> CashFlowReport:
        """Generate cash flow statement - TO BE IMPLEMENTED"""
        logger.info(f"Generating cash flow from {start_date} to {end_date}")
        
        # Stub implementation - returns zero values
        return CashFlowReport(
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now().isoformat(),
            inflows=CashFlowInflows(total_inflows=0.0, customer_payments=0.0, other_income=0.0, transaction_count=0),
            outflows=CashFlowOutflows(total_outflows=0.0, by_category={}, transaction_count=0),
            net_cash_flow=0.0,
            opening_balance=0.0,
            closing_balance=0.0
        )
    
    async def generate_ar_aging(
        self,
        as_of_date: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> ARAgingReport:
        """Generate AR aging report - TO BE IMPLEMENTED"""
        if as_of_date is None:
            as_of_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Generating AR aging as of {as_of_date}")
        
        # Stub implementation
        return ARAgingReport(
            as_of_date=as_of_date,
            generated_at=datetime.now().isoformat(),
            total_outstanding=0.0,
            total_invoices=0,
            buckets=[],
            current_percentage=0.0,
            overdue_percentage=0.0,
            collection_risk_score=0.0,
            top_customers=[]
        )
    
    async def get_dashboard_metrics(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> DashboardMetrics:
        """Get dashboard metrics - TO BE IMPLEMENTED"""
        logger.info("Generating dashboard metrics")
        
        # Stub implementation
        return DashboardMetrics(
            generated_at=datetime.now().isoformat(),
            total_revenue=0.0,
            revenue_trend="stable",
            revenue_change_pct=0.0,
            total_invoices=0,
            paid_invoices=0,
            pending_invoices=0,
            overdue_invoices=0,
            average_invoice_value=0.0,
            total_customers=0,
            active_customers=0,
            revenue_per_customer=0.0,
            total_outstanding=0.0,
            collection_rate=0.0,
            dso=0.0,
            total_expenses=0.0,
            top_expense_category="N/A",
            expense_trend="stable",
            net_income=0.0,
            profit_margin=0.0,
            transaction_count=0,
            reconciled_transactions=0,
            reconciliation_rate=0.0
        )
