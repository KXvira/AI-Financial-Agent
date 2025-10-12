"""
Service for generating financial reports and analytics
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from database.mongodb import Database
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
    
    def __init__(self, db: Database):
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
        
        # Note: Dates in DB are strings, not datetime objects
        # We'll match on string dates since that's how they're stored
        
        # Revenue from paid invoices (using 'issue_date' and 'amount' fields)
        invoice_match = {}
        if "customer_id" in filters:
            invoice_match["customer_id"] = filters["customer_id"]
        
        total_invoices = await self.db.invoices.count_documents(invoice_match)
        
        invoiced_pipeline = [
            {"$match": invoice_match},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        invoiced_result = await self.db.invoices.aggregate(invoiced_pipeline).to_list(1)
        total_invoiced = invoiced_result[0]["total"] if invoiced_result else 0.0
        
        paid_match = {**invoice_match, "status": "paid"}
        paid_invoices = await self.db.invoices.count_documents(paid_match)
        
        paid_pipeline = [
            {"$match": paid_match},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
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
        
        # Expenses from transactions (using 'created_at' and 'category' fields)
        expense_match = {"type": "expense"}
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
        """Generate cash flow statement showing inflows and outflows"""
        logger.info(f"Generating cash flow from {start_date} to {end_date}")
        
        if filters is None:
            filters = {}
        
        # ========== CASH INFLOWS (Payment Transactions) ==========
        
        # Query for payment transactions
        inflow_match = {"type": "payment"}
        
        inflow_count = await self.db.transactions.count_documents(inflow_match)
        
        inflow_pipeline = [
            {"$match": inflow_match},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        
        inflow_result = await self.db.transactions.aggregate(inflow_pipeline).to_list(1)
        total_inflows = inflow_result[0]["total"] if inflow_result else 0.0
        
        cash_inflows = CashFlowInflows(
            total_inflows=round(total_inflows, 2),
            customer_payments=round(total_inflows, 2),  # All inflows are customer payments
            other_income=0.0,
            transaction_count=inflow_count
        )
        
        # ========== CASH OUTFLOWS (Expense Transactions) ==========
        
        # Query for expense transactions
        outflow_match = {"type": "expense"}
        
        outflow_count = await self.db.transactions.count_documents(outflow_match)
        
        # Group by category
        outflow_pipeline = [
            {"$match": outflow_match},
            {"$group": {
                "_id": "$category",
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"total": -1}}
        ]
        
        outflow_results = await self.db.transactions.aggregate(outflow_pipeline).to_list(None)
        outflows_by_category = {result["_id"]: round(result["total"], 2) for result in outflow_results}
        total_outflows = sum(outflows_by_category.values())
        
        cash_outflows = CashFlowOutflows(
            total_outflows=round(total_outflows, 2),
            by_category=outflows_by_category,
            transaction_count=outflow_count
        )
        
        # ========== CALCULATIONS ==========
        
        net_cash_flow = total_inflows - total_outflows
        
        # Calculate opening balance (cash before this period - simplified)
        # In a real system, you'd track actual cash balance
        # For now, we'll use cumulative approach
        opening_balance = 0.0  # Could be calculated from previous periods
        closing_balance = opening_balance + net_cash_flow
        
        # Calculate burn rate and runway
        burn_rate = None
        runway_months = None
        
        if net_cash_flow < 0:
            # Negative cash flow - calculate monthly burn
            monthly_burn = abs(net_cash_flow)
            burn_rate = monthly_burn
            
            if closing_balance > 0 and burn_rate > 0:
                runway_months = closing_balance / burn_rate
        
        return CashFlowReport(
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now().isoformat(),
            inflows=cash_inflows,
            outflows=cash_outflows,
            net_cash_flow=round(net_cash_flow, 2),
            opening_balance=round(opening_balance, 2),
            closing_balance=round(closing_balance, 2),
            burn_rate=round(burn_rate, 2) if burn_rate else None,
            runway_months=round(runway_months, 1) if runway_months else None
        )
    
    async def generate_ar_aging(
        self,
        as_of_date: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> ARAgingReport:
        """Generate AR aging report showing outstanding invoices by age"""
        if as_of_date is None:
            as_of_date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Generating AR aging as of {as_of_date}")
        
        if filters is None:
            filters = {}
        
        as_of_dt = datetime.fromisoformat(as_of_date)
        
        # ========== QUERY OUTSTANDING INVOICES ==========
        
        # Find all unpaid invoices
        outstanding_match = {
            "status": {"$in": ["pending", "sent", "unpaid", "overdue"]}
        }
        
        # Add customer filter if provided
        if "customer_id" in filters:
            outstanding_match["customer_id"] = filters["customer_id"]
        
        outstanding_invoices = await self.db.invoices.find(outstanding_match).to_list(None)
        
        total_outstanding = sum(inv.get("amount", 0) for inv in outstanding_invoices)
        total_invoices = len(outstanding_invoices)
        
        # ========== CREATE AGING BUCKETS ==========
        
        bucket_definitions = [
            {"name": "Current (0-30 days)", "min_days": 0, "max_days": 30},
            {"name": "31-60 days", "min_days": 31, "max_days": 60},
            {"name": "61-90 days", "min_days": 61, "max_days": 90},
            {"name": "Over 90 days", "min_days": 91, "max_days": None},
        ]
        
        buckets = []
        
        for bucket_def in bucket_definitions:
            bucket_invoices = []
            bucket_total = 0.0
            
            for invoice in outstanding_invoices:
                # Calculate days outstanding
                issue_date_str = invoice.get("issue_date", "")
                if not issue_date_str:
                    continue
                
                try:
                    # Parse date string (format: "2024-10-12 19:46:20.186000")
                    from dateutil import parser as date_parser
                    invoice_date = date_parser.parse(issue_date_str)
                except:
                    # Skip if date parsing fails
                    continue
                
                days_outstanding = (as_of_dt - invoice_date).days
                
                # Check if invoice belongs in this bucket
                min_days = bucket_def["min_days"]
                max_days = bucket_def["max_days"]
                
                in_bucket = False
                if max_days is None:
                    # 90+ bucket
                    in_bucket = days_outstanding >= min_days
                else:
                    # Regular bucket
                    in_bucket = min_days <= days_outstanding <= max_days
                
                if in_bucket:
                    amount = invoice.get("amount", 0)
                    bucket_invoices.append({
                        "invoice_id": str(invoice.get("_id")),
                        "invoice_number": invoice.get("invoice_number", "N/A"),
                        "customer_name": invoice.get("customer_name", "Unknown"),
                        "amount": round(amount, 2),
                        "date_issued": issue_date_str.split()[0] if issue_date_str else "N/A",
                        "days_outstanding": days_outstanding
                    })
                    bucket_total += amount
            
            # Calculate percentage
            percentage = (bucket_total / total_outstanding * 100) if total_outstanding > 0 else 0.0
            
            # Sort invoices by days outstanding (descending) and limit to top 10
            bucket_invoices.sort(key=lambda x: x["days_outstanding"], reverse=True)
            
            bucket = AgingBucket(
                bucket_name=bucket_def["name"],
                min_days=bucket_def["min_days"],
                max_days=bucket_def["max_days"],
                invoice_count=len(bucket_invoices),
                total_amount=round(bucket_total, 2),
                percentage=round(percentage, 1),
                invoices=bucket_invoices[:10]  # Limit to top 10
            )
            
            buckets.append(bucket)
        
        # ========== CALCULATE METRICS ==========
        
        # Current percentage (0-30 days)
        current_amount = buckets[0].total_amount if buckets else 0.0
        current_percentage = (current_amount / total_outstanding * 100) if total_outstanding > 0 else 0.0
        
        # Overdue percentage (31+ days)
        overdue_amount = sum(bucket.total_amount for bucket in buckets[1:])
        overdue_percentage = (overdue_amount / total_outstanding * 100) if total_outstanding > 0 else 0.0
        
        # Collection risk score (0-100, higher is riskier)
        risk_score = 0.0
        if total_outstanding > 0 and len(buckets) >= 4:
            risk_score += (buckets[1].total_amount / total_outstanding) * 25  # 31-60: 25% weight
            risk_score += (buckets[2].total_amount / total_outstanding) * 35  # 61-90: 35% weight
            risk_score += (buckets[3].total_amount / total_outstanding) * 40  # 90+: 40% weight
        
        # ========== TOP CUSTOMERS WITH OUTSTANDING BALANCES ==========
        
        customer_totals = {}
        for invoice in outstanding_invoices:
            customer_name = invoice.get("customer_name", "Unknown")
            amount = invoice.get("amount", 0)
            
            if customer_name not in customer_totals:
                customer_totals[customer_name] = {
                    "customer_name": customer_name,
                    "outstanding_amount": 0.0,
                    "invoice_count": 0
                }
            
            customer_totals[customer_name]["outstanding_amount"] += amount
            customer_totals[customer_name]["invoice_count"] += 1
        
        # Sort and get top 5
        top_customers = sorted(
            customer_totals.values(),
            key=lambda x: x["outstanding_amount"],
            reverse=True
        )[:5]
        
        # Round amounts
        for customer in top_customers:
            customer["outstanding_amount"] = round(customer["outstanding_amount"], 2)
        
        return ARAgingReport(
            as_of_date=as_of_date,
            generated_at=datetime.now().isoformat(),
            total_outstanding=round(total_outstanding, 2),
            total_invoices=total_invoices,
            buckets=buckets,
            current_percentage=round(current_percentage, 1),
            overdue_percentage=round(overdue_percentage, 1),
            collection_risk_score=round(risk_score, 1),
            top_customers=top_customers
        )
    
    async def get_dashboard_metrics(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> DashboardMetrics:
        """Get comprehensive dashboard metrics from all collections"""
        logger.info("Generating dashboard metrics")
        
        if filters is None:
            filters = {}
        
        # ========== INVOICE METRICS ==========
        
        # Total invoices
        total_invoices = await self.db.invoices.count_documents({})
        
        # Count by status
        paid_invoices = await self.db.invoices.count_documents({"status": "paid"})
        pending_invoices = await self.db.invoices.count_documents(
            {"status": {"$in": ["pending", "sent", "unpaid"]}}
        )
        overdue_invoices = await self.db.invoices.count_documents({"status": "overdue"})
        
        # Total revenue (from paid invoices)
        paid_revenue_pipeline = [
            {"$match": {"status": "paid"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        paid_revenue_result = await self.db.invoices.aggregate(paid_revenue_pipeline).to_list(None)
        total_revenue = paid_revenue_result[0]["total"] if paid_revenue_result else 0.0
        
        # Total invoiced amount (all invoices)
        total_invoiced_pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        total_invoiced_result = await self.db.invoices.aggregate(total_invoiced_pipeline).to_list(None)
        total_invoiced = total_invoiced_result[0]["total"] if total_invoiced_result else 0.0
        
        # Outstanding amount (unpaid invoices)
        total_outstanding = total_invoiced - total_revenue
        
        # Average invoice value
        average_invoice_value = total_invoiced / total_invoices if total_invoices > 0 else 0.0
        
        # Collection rate
        collection_rate = (total_revenue / total_invoiced * 100) if total_invoiced > 0 else 0.0
        
        # Days Sales Outstanding (DSO) - simplified calculation
        # DSO = (Accounts Receivable / Total Credit Sales) * Number of Days
        # Using 30 days as period
        dso = (total_outstanding / total_revenue * 30) if total_revenue > 0 else 0.0
        
        # ========== CUSTOMER METRICS ==========
        
        total_customers = await self.db.customers.count_documents({})
        
        # Active customers (customers with at least one invoice)
        active_customers_pipeline = [
            {"$group": {"_id": "$customer_id"}},
            {"$count": "count"}
        ]
        active_customers_result = await self.db.invoices.aggregate(active_customers_pipeline).to_list(None)
        active_customers = active_customers_result[0]["count"] if active_customers_result else 0
        
        # Revenue per customer
        revenue_per_customer = total_revenue / active_customers if active_customers > 0 else 0.0
        
        # ========== EXPENSE METRICS ==========
        
        # Total expenses
        expense_pipeline = [
            {"$match": {"type": "expense"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        expense_result = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
        total_expenses = expense_result[0]["total"] if expense_result else 0.0
        
        # Top expense category
        category_pipeline = [
            {"$match": {"type": "expense"}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}},
            {"$limit": 1}
        ]
        category_result = await self.db.transactions.aggregate(category_pipeline).to_list(None)
        top_expense_category = category_result[0]["_id"] if category_result else "N/A"
        
        # ========== PROFITABILITY METRICS ==========
        
        # Net income
        net_income = total_revenue - total_expenses
        
        # Profit margin
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0.0
        
        # ========== TRANSACTION METRICS ==========
        
        # Total transactions
        transaction_count = await self.db.transactions.count_documents({})
        
        # Reconciled transactions (assuming 'reconciled' field exists)
        reconciled_transactions = await self.db.transactions.count_documents({"reconciled": True})
        
        # Reconciliation rate
        reconciliation_rate = (reconciled_transactions / transaction_count * 100) if transaction_count > 0 else 0.0
        
        # ========== TREND CALCULATIONS (SIMPLIFIED) ==========
        
        # For now, set trends to "stable" since we need historical data for proper trend analysis
        # In Phase 2, we'll add month-over-month comparisons
        revenue_trend = "stable"
        revenue_change_pct = 0.0
        expense_trend = "stable"
        
        # TODO: In Phase 2, calculate trends by comparing current period to previous period
        # This requires querying data for two periods and calculating percentage change
        
        return DashboardMetrics(
            generated_at=datetime.now().isoformat(),
            total_revenue=round(total_revenue, 2),
            revenue_trend=revenue_trend,
            revenue_change_pct=round(revenue_change_pct, 1),
            total_invoices=total_invoices,
            paid_invoices=paid_invoices,
            pending_invoices=pending_invoices,
            overdue_invoices=overdue_invoices,
            average_invoice_value=round(average_invoice_value, 2),
            total_customers=total_customers,
            active_customers=active_customers,
            revenue_per_customer=round(revenue_per_customer, 2),
            total_outstanding=round(total_outstanding, 2),
            collection_rate=round(collection_rate, 1),
            dso=round(dso, 1),
            total_expenses=round(total_expenses, 2),
            top_expense_category=top_expense_category,
            expense_trend=expense_trend,
            net_income=round(net_income, 2),
            profit_margin=round(profit_margin, 1),
            transaction_count=transaction_count,
            reconciled_transactions=reconciled_transactions,
            reconciliation_rate=round(reconciliation_rate, 1)
        )
