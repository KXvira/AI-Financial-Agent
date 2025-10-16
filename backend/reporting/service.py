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
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        
        # ========== CASH INFLOWS (Payment Transactions) ==========
        
        # Query for completed payment transactions
        # Note: The actual MongoDB field values are lowercase (e.g., "completed", "pending")
        # The API router capitalizes them in responses
        inflow_match = {
            "status": {"$in": ["completed", "successful", "paid"]}
        }
        
        # Add date filter - MongoDB stores payment_date as datetime objects
        if start_date and end_date:
            inflow_match["payment_date"] = {
                "$gte": start_dt,  # Use datetime object, not string
                "$lte": end_dt
            }
        
        logger.info(f"Inflow match query: {inflow_match}")
        
        # Use payments collection for inflows
        inflow_count = await self.db.payments.count_documents(inflow_match)
        
        # Sum up amount field (the actual numeric field in MongoDB)
        # Note: amountRaw is created by the API router, not stored in MongoDB
        inflow_pipeline = [
            {"$match": inflow_match},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        
        inflow_result = await self.db.payments.aggregate(inflow_pipeline).to_list(1)
        total_inflows = inflow_result[0]["total"] if inflow_result else 0.0
        
        logger.info(f"Found {inflow_count} payment transactions with total inflows: {total_inflows:,.2f}")
        
        cash_inflows = CashFlowInflows(
            total_inflows=round(total_inflows, 2),
            customer_payments=round(total_inflows, 2),  # All inflows are customer payments
            other_income=0.0,
            transaction_count=inflow_count
        )
        
        # ========== CASH OUTFLOWS (Expenses + Refunds) ==========
        
        # 1. Get expenses from receipts collection - use same logic as expenses API
        expense_match = {
            "$or": [
                {"receipt_type": "expense"},
                {"receipt_type": "refund"},
                {"ocr_data.extracted_data.total_amount": {"$exists": True}}
            ]
        }
        
        if start_date and end_date:
            expense_match["created_at"] = {
                "$gte": start_dt,
                "$lte": end_dt
            }
        
        logger.info(f"Querying expenses with filter: {expense_match}")
        
        # Get all expense receipts
        expense_receipts = await self.db.db["receipts"].find(expense_match).to_list(None)
        
        logger.info(f"Found {len(expense_receipts)} expense receipts")
        
        # Calculate total by iterating through receipts (same logic as expenses service)
        total_expenses = 0.0
        expenses_by_category = {}
        
        for receipt in expense_receipts:
            amount = 0.0
            
            # Priority 1: OCR extracted data (most reliable)
            if receipt.get("ocr_data"):
                amount = receipt["ocr_data"]["extracted_data"].get("total_amount", 0)
            
            # Priority 2: Tax breakdown (for manual receipts)
            elif receipt.get("tax_breakdown"):
                tax_breakdown = receipt["tax_breakdown"]
                amount = tax_breakdown.get("subtotal", 0) + tax_breakdown.get("vat_amount", 0)
            
            # Priority 3: Line items (for itemized receipts)
            elif receipt.get("line_items"):
                line_items = receipt["line_items"]
                amount = sum(item.get("total", 0) for item in line_items)
            
            if amount > 0:
                total_expenses += amount
                
                # Get category for breakdown
                category = "Other Expenses"
                if receipt.get("ocr_data"):
                    category = receipt["ocr_data"]["extracted_data"].get("merchant_name", "Other Expenses")
                elif receipt.get("category"):
                    category = receipt["category"]
                
                expenses_by_category[category] = expenses_by_category.get(category, 0) + amount
        
        expense_count = len(expense_receipts)
        
        logger.info(f"Total expenses: Ksh {total_expenses:,.2f} from {expense_count} receipts")
        logger.info(f"Expense categories: {list(expenses_by_category.keys())}")
        
        # 2. Get refunds from payments collection
        refund_match = {
            "status": {"$in": ["refunded", "Refunded", "failed", "Failed", "returned", "Returned"]}
        }
        if start_date and end_date:
            refund_match["payment_date"] = {
                "$gte": start_dt,
                "$lte": end_dt
            }
        
        refund_count = await self.db.payments.count_documents(refund_match)
        
        # Calculate refunds using amount field
        refund_pipeline = [
            {"$match": refund_match},
            {"$group": {
                "_id": None,
                "total": {"$sum": "$amount"}
            }}
        ]
        
        refund_result = await self.db.payments.aggregate(refund_pipeline).to_list(1)
        total_refunds = round(refund_result[0]["total"], 2) if refund_result and refund_result[0].get("total") else 0.0
        
        # Combine expenses and refunds
        total_outflows = total_expenses + total_refunds
        outflow_count = expense_count + refund_count
        
        # Build outflows by category - use expense categories + refunds
        outflows_by_category = {k: round(v, 2) for k, v in expenses_by_category.items()}
        if total_refunds > 0:
            outflows_by_category["Payment Refunds"] = total_refunds
        
        logger.info(f"Found {expense_count} expense transactions (Ksh {total_expenses:,.2f}) and {refund_count} refunds (Ksh {total_refunds:,.2f})")
        logger.info(f"Total outflows: {total_outflows:,.2f} from {outflow_count} transactions")
        
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
        logger.info(f"Filters: {filters}")
        
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
        
        # Calculate invoice totals from invoice_items collection (normalized schema)
        # and populate customer names if missing
        total_outstanding = 0.0
        for invoice in outstanding_invoices:
            invoice_id = invoice.get("invoice_id")
            items = await self.db.invoice_items.find({"invoice_id": invoice_id}).to_list(length=None)
            # Calculate total from items - use "line_total" field
            calculated_total = sum(item.get("line_total", item.get("total", 0)) for item in items)
            invoice["calculated_total"] = calculated_total if calculated_total > 0 else invoice.get("total", invoice.get("amount", 0))
            total_outstanding += invoice["calculated_total"]
            
            # Populate customer_name if missing (Priority 2 fix)
            if not invoice.get("customer_name") or invoice.get("customer_name") == "Unknown":
                customer_id = invoice.get("customer_id")
                if customer_id:
                    try:
                        # Try to find customer by UUID string (not ObjectId)
                        # First try customer_id field (string UUID)
                        customer = await self.db.customers.find_one({"customer_id": customer_id})
                        
                        # If not found, try _id field
                        if not customer:
                            try:
                                from bson import ObjectId
                                customer = await self.db.customers.find_one({"_id": ObjectId(customer_id)})
                            except:
                                pass  # customer_id is not a valid ObjectId, skip
                        
                        if customer:
                            # Get customer name from various possible fields
                            customer_name = (
                                customer.get("name") or 
                                customer.get("customer_name") or 
                                customer.get("company_name") or
                                f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or
                                "Unknown"
                            )
                            invoice["customer_name"] = customer_name
                    except Exception as e:
                        logger.debug(f"Could not fetch customer for invoice {invoice.get('invoice_number')}: {e}")
                        # Keep as Unknown, don't spam logs
        
        total_invoices = len(outstanding_invoices)
        logger.info(f"Found {total_invoices} outstanding invoices with total: {total_outstanding:,.2f}")
        
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
                issue_date_str = invoice.get("issue_date", invoice.get("date", ""))
                if not issue_date_str:
                    # If no issue_date, try created_at or use current date
                    issue_date_str = invoice.get("created_at", as_of_date)
                
                try:
                    # Parse date string - handle multiple formats
                    from dateutil import parser as date_parser
                    if isinstance(issue_date_str, datetime):
                        invoice_date = issue_date_str
                    else:
                        # Try parsing with dateutil (handles most formats)
                        invoice_date = date_parser.parse(str(issue_date_str))
                except Exception as e:
                    # If parsing fails, log and use as_of_date (0 days outstanding)
                    logger.warning(f"Failed to parse date '{issue_date_str}' for invoice {invoice.get('invoice_number', 'unknown')}: {e}")
                    invoice_date = as_of_dt
                
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
                    # Use calculated_total from invoice_items
                    amount = invoice.get("calculated_total", invoice.get("amount", 0))
                    
                    # Format date for display
                    if isinstance(invoice_date, datetime):
                        date_issued_display = invoice_date.strftime("%Y-%m-%d")
                    elif isinstance(issue_date_str, str) and issue_date_str:
                        date_issued_display = issue_date_str.split()[0] if ' ' in issue_date_str else issue_date_str
                    else:
                        date_issued_display = "N/A"
                    
                    bucket_invoices.append({
                        "invoice_id": str(invoice.get("_id")),
                        "invoice_number": invoice.get("invoice_number", "N/A"),
                        "customer_name": invoice.get("customer_name", "Unknown"),
                        "amount": round(amount, 2),
                        "date_issued": date_issued_display,
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
            
            logger.info(f"Bucket '{bucket_def['name']}': {len(bucket_invoices)} invoices, Total: {bucket_total:,.2f} ({percentage:.1f}%)")
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
            # Use calculated_total from invoice_items
            amount = invoice.get("calculated_total", invoice.get("amount", 0))
            
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
    
    async def get_revenue_trends(self, period: str = "monthly", months: int = 12) -> Dict[str, Any]:
        """Get revenue trends over time"""
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Aggregate revenue by period
        pipeline = [
            {
                "$match": {
                    "payment_date": {
                        "$gte": start_date.strftime("%Y-%m-%d"),
                        "$lte": end_date.strftime("%Y-%m-%d")
                    },
                    "status": "Paid"
                }
            },
            {
                "$addFields": {
                    "year": {"$substr": ["$payment_date", 0, 4]},
                    "month": {"$substr": ["$payment_date", 5, 2]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month"
                    },
                    "revenue": {"$sum": "$amount"},
                    "invoice_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        
        results = await self.db.invoices.aggregate(pipeline).to_list(None)
        
        # Format results
        trends = []
        prev_revenue = None
        
        for item in results:
            period_label = f"{item['_id']['year']}-{item['_id']['month']}"
            revenue = item['revenue']
            
            # Calculate change from previous period
            change_pct = 0.0
            if prev_revenue and prev_revenue > 0:
                change_pct = ((revenue - prev_revenue) / prev_revenue) * 100
            
            trends.append({
                "period": period_label,
                "revenue": round(revenue, 2),
                "invoice_count": item['invoice_count'],
                "change_pct": round(change_pct, 2) if prev_revenue else None,
                "trend": "up" if change_pct > 5 else "down" if change_pct < -5 else "stable"
            })
            
            prev_revenue = revenue
        
        # Calculate overall trend
        overall_trend = "stable"
        if len(trends) >= 2:
            first_revenue = trends[0]['revenue']
            last_revenue = trends[-1]['revenue']
            if last_revenue > first_revenue * 1.1:
                overall_trend = "up"
            elif last_revenue < first_revenue * 0.9:
                overall_trend = "down"
        
        return {
            "period": period,
            "months_included": months,
            "overall_trend": overall_trend,
            "data": trends
        }
    
    async def get_expense_trends(self, period: str = "monthly", months: int = 12) -> Dict[str, Any]:
        """Get expense trends over time"""
        from dateutil.relativedelta import relativedelta
        
        end_date = datetime.now()
        start_date = end_date - relativedelta(months=months)
        
        # Aggregate expenses by period
        pipeline = [
            {
                "$match": {
                    "transaction_date": {
                        "$gte": start_date.strftime("%Y-%m-%d"),
                        "$lte": end_date.strftime("%Y-%m-%d")
                    },
                    "type": "expense"
                }
            },
            {
                "$addFields": {
                    "year": {"$substr": ["$transaction_date", 0, 4]},
                    "month": {"$substr": ["$transaction_date", 5, 2]}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": "$year",
                        "month": "$month"
                    },
                    "expenses": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        
        results = await self.db.transactions.aggregate(pipeline).to_list(None)
        
        # Format results
        trends = []
        prev_expenses = None
        
        for item in results:
            period_label = f"{item['_id']['year']}-{item['_id']['month']}"
            expenses = item['expenses']
            
            # Calculate change from previous period
            change_pct = 0.0
            if prev_expenses and prev_expenses > 0:
                change_pct = ((expenses - prev_expenses) / prev_expenses) * 100
            
            trends.append({
                "period": period_label,
                "expenses": round(expenses, 2),
                "transaction_count": item['transaction_count'],
                "change_pct": round(change_pct, 2) if prev_expenses else None,
                "trend": "up" if change_pct > 5 else "down" if change_pct < -5 else "stable"
            })
            
            prev_expenses = expenses
        
        # Calculate overall trend
        overall_trend = "stable"
        if len(trends) >= 2:
            first_expenses = trends[0]['expenses']
            last_expenses = trends[-1]['expenses']
            if last_expenses > first_expenses * 1.1:
                overall_trend = "up"
            elif last_expenses < first_expenses * 0.9:
                overall_trend = "down"
        
        return {
            "period": period,
            "months_included": months,
            "overall_trend": overall_trend,
            "data": trends
        }
    
    async def get_month_over_month_comparison(self) -> Dict[str, Any]:
        """Compare current month metrics with previous month"""
        from dateutil.relativedelta import relativedelta
        
        now = datetime.now()
        
        # Current month
        current_start = datetime(now.year, now.month, 1)
        current_end = now
        
        # Previous month
        prev_start = (current_start - relativedelta(months=1))
        prev_end = current_start - timedelta(days=1)
        
        async def get_period_metrics(start: datetime, end: datetime):
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            
            # Revenue
            revenue_pipeline = [
                {"$match": {"payment_date": {"$gte": start_str, "$lte": end_str}, "status": "Paid"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]
            revenue_result = await self.db.invoices.aggregate(revenue_pipeline).to_list(None)
            revenue = revenue_result[0]['total'] if revenue_result else 0
            invoice_count = revenue_result[0]['count'] if revenue_result else 0
            
            # Expenses
            expense_pipeline = [
                {"$match": {"transaction_date": {"$gte": start_str, "$lte": end_str}, "type": "expense"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]
            expense_result = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
            expenses = expense_result[0]['total'] if expense_result else 0
            
            return {
                "revenue": round(revenue, 2),
                "expenses": round(expenses, 2),
                "net_income": round(revenue - expenses, 2),
                "invoice_count": invoice_count
            }
        
        current = await get_period_metrics(current_start, current_end)
        previous = await get_period_metrics(prev_start, prev_end)
        
        # Calculate changes
        revenue_change = ((current['revenue'] - previous['revenue']) / previous['revenue'] * 100) if previous['revenue'] > 0 else 0
        expense_change = ((current['expenses'] - previous['expenses']) / previous['expenses'] * 100) if previous['expenses'] > 0 else 0
        net_income_change = ((current['net_income'] - previous['net_income']) / abs(previous['net_income']) * 100) if previous['net_income'] != 0 else 0
        
        return {
            "period": "Month-over-Month",
            "current_month": current_start.strftime("%B %Y"),
            "previous_month": prev_start.strftime("%B %Y"),
            "current": current,
            "previous": previous,
            "changes": {
                "revenue_change_pct": round(revenue_change, 2),
                "expense_change_pct": round(expense_change, 2),
                "net_income_change_pct": round(net_income_change, 2)
            }
        }
    
    async def get_year_over_year_comparison(self) -> Dict[str, Any]:
        """Compare current year metrics with previous year"""
        now = datetime.now()
        
        # Current year
        current_start = datetime(now.year, 1, 1)
        current_end = now
        
        # Previous year
        prev_start = datetime(now.year - 1, 1, 1)
        prev_end = datetime(now.year - 1, now.month, now.day)
        
        async def get_period_metrics(start: datetime, end: datetime):
            start_str = start.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")
            
            # Revenue
            revenue_pipeline = [
                {"$match": {"payment_date": {"$gte": start_str, "$lte": end_str}, "status": "Paid"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
            ]
            revenue_result = await self.db.invoices.aggregate(revenue_pipeline).to_list(None)
            revenue = revenue_result[0]['total'] if revenue_result else 0
            invoice_count = revenue_result[0]['count'] if revenue_result else 0
            
            # Expenses
            expense_pipeline = [
                {"$match": {"transaction_date": {"$gte": start_str, "$lte": end_str}, "type": "expense"}},
                {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
            ]
            expense_result = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
            expenses = expense_result[0]['total'] if expense_result else 0
            
            return {
                "revenue": round(revenue, 2),
                "expenses": round(expenses, 2),
                "net_income": round(revenue - expenses, 2),
                "invoice_count": invoice_count
            }
        
        current = await get_period_metrics(current_start, current_end)
        previous = await get_period_metrics(prev_start, prev_end)
        
        # Calculate changes
        revenue_change = ((current['revenue'] - previous['revenue']) / previous['revenue'] * 100) if previous['revenue'] > 0 else 0
        expense_change = ((current['expenses'] - previous['expenses']) / previous['expenses'] * 100) if previous['expenses'] > 0 else 0
        net_income_change = ((current['net_income'] - previous['net_income']) / abs(previous['net_income']) * 100) if previous['net_income'] != 0 else 0
        
        return {
            "period": "Year-over-Year",
            "current_year": current_start.year,
            "previous_year": prev_start.year,
            "current": current,
            "previous": previous,
            "changes": {
                "revenue_growth_pct": round(revenue_change, 2),
                "expense_growth_pct": round(expense_change, 2),
                "net_income_growth_pct": round(net_income_change, 2)
            }
        }
