"""
Custom AI Reports Service
Generates custom financial reports using AI-powered insights and natural language queries
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.mongodb import Database
from ai_agent.gemini.service import GeminiService

class CustomAIReportService:
    """Service for generating custom AI-powered financial reports"""
    
    def __init__(self, db: Database):
        self.db = db
        self.ai_service = GeminiService()
        
    async def generate_custom_report(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        include_data: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a custom report based on natural language query
        
        Args:
            query: Natural language query (e.g., "What are my top customers?")
            start_date: Optional start date filter
            end_date: Optional end date filter
            include_data: Include raw data in response
            
        Returns:
            AI-generated report with insights
        """
        # Parse dates
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = datetime.now()
            
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start = end - timedelta(days=30)
        
        # Gather relevant financial data
        financial_data = await self._gather_financial_context(start, end)
        
        # Build context for AI
        context = self._build_ai_context(financial_data, query, start, end)
        
        # Get AI insights
        try:
            ai_response = await self.ai_service.generate_financial_insights(context)
            
            report = {
                "query": query,
                "period": {
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "days": (end - start).days
                },
                "ai_insights": ai_response.get("insights", "No insights generated"),
                "recommendations": ai_response.get("recommendations", []),
                "key_findings": ai_response.get("key_findings", []),
                "generated_at": datetime.now().isoformat()
            }
            
            if include_data:
                report["supporting_data"] = financial_data
            
            return report
            
        except Exception as e:
            return {
                "error": f"Failed to generate AI report: {str(e)}",
                "query": query,
                "fallback_data": financial_data if include_data else None
            }
    
    async def detect_anomalies(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect financial anomalies using AI analysis
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Anomalies and unusual patterns detected
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get transactions
        transactions = await self.db.transactions.find({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }).to_list(length=None)
        
        # Get invoices
        invoices = await self.db.invoices.find({
            "date_issued": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        anomalies = []
        
        # 1. Unusual transaction amounts
        amounts = [txn.get("amount", 0) for txn in transactions]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            std_dev = (sum((x - avg_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
            
            for txn in transactions:
                amount = txn.get("amount", 0)
                if amount > avg_amount + (2 * std_dev):
                    anomalies.append({
                        "type": "unusual_transaction_amount",
                        "severity": "medium",
                        "description": f"Transaction of {amount} is significantly above average ({avg_amount:.2f})",
                        "reference": txn.get("mpesa_receipt_number") or txn.get("reference"),
                        "amount": amount,
                        "date": txn.get("timestamp").isoformat() if isinstance(txn.get("timestamp"), datetime) else txn.get("timestamp")
                    })
        
        # 2. Duplicate transactions
        seen_refs = {}
        for txn in transactions:
            ref = txn.get("mpesa_receipt_number") or txn.get("reference")
            if ref in seen_refs:
                anomalies.append({
                    "type": "duplicate_transaction",
                    "severity": "high",
                    "description": f"Duplicate transaction detected: {ref}",
                    "reference": ref,
                    "occurrences": 2
                })
            else:
                seen_refs[ref] = True
        
        # 3. Unusual invoice patterns
        invoice_amounts = [inv.get("total_amount", 0) for inv in invoices]
        if invoice_amounts:
            avg_invoice = sum(invoice_amounts) / len(invoice_amounts)
            
            for inv in invoices:
                amount = inv.get("total_amount", 0)
                if amount > avg_invoice * 3:
                    anomalies.append({
                        "type": "unusual_invoice_amount",
                        "severity": "low",
                        "description": f"Invoice amount {amount} is 3x above average ({avg_invoice:.2f})",
                        "invoice_number": inv.get("invoice_number"),
                        "amount": amount
                    })
        
        # 4. Late payments
        overdue_invoices = [inv for inv in invoices if inv.get("status") == "overdue"]
        if len(overdue_invoices) > len(invoices) * 0.3:  # More than 30% overdue
            anomalies.append({
                "type": "high_overdue_rate",
                "severity": "high",
                "description": f"{len(overdue_invoices)} out of {len(invoices)} invoices are overdue ({len(overdue_invoices)/len(invoices)*100:.1f}%)",
                "count": len(overdue_invoices)
            })
        
        return {
            "analysis_period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "days": days
            },
            "summary": {
                "total_anomalies": len(anomalies),
                "high_severity": len([a for a in anomalies if a["severity"] == "high"]),
                "medium_severity": len([a for a in anomalies if a["severity"] == "medium"]),
                "low_severity": len([a for a in anomalies if a["severity"] == "low"])
            },
            "anomalies": anomalies,
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_executive_summary(
        self,
        month: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate executive summary for a given month using AI
        
        Args:
            month: Month in YYYY-MM format (defaults to current month)
            
        Returns:
            Executive summary with AI insights
        """
        if month:
            target_date = datetime.strptime(month, "%Y-%m")
        else:
            target_date = datetime.now()
        
        # Get start and end of month
        start_date = target_date.replace(day=1)
        if target_date.month == 12:
            end_date = target_date.replace(year=target_date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = target_date.replace(month=target_date.month + 1, day=1) - timedelta(days=1)
        
        # Gather comprehensive data
        financial_data = await self._gather_financial_context(start_date, end_date)
        
        # Calculate key metrics
        total_revenue = sum(inv.get("total_amount", 0) for inv in financial_data.get("invoices", []) if inv.get("status") == "paid")
        total_expenses = sum(txn.get("amount", 0) for txn in financial_data.get("transactions", []))
        net_income = total_revenue - total_expenses
        
        # Invoice metrics
        total_invoices = len(financial_data.get("invoices", []))
        paid_invoices = len([inv for inv in financial_data.get("invoices", []) if inv.get("status") == "paid"])
        collection_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        
        summary = {
            "month": target_date.strftime("%Y-%m"),
            "period": {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d")
            },
            "key_metrics": {
                "total_revenue": round(total_revenue, 2),
                "total_expenses": round(total_expenses, 2),
                "net_income": round(net_income, 2),
                "profit_margin": round((net_income / total_revenue * 100) if total_revenue > 0 else 0, 2),
                "total_invoices": total_invoices,
                "collection_rate": round(collection_rate, 2)
            },
            "highlights": [],
            "concerns": [],
            "recommendations": []
        }
        
        # Add highlights
        if net_income > 0:
            summary["highlights"].append(f"✅ Profitable month with net income of KES {net_income:,.2f}")
        if collection_rate > 80:
            summary["highlights"].append(f"✅ Strong collection rate of {collection_rate:.1f}%")
        
        # Add concerns
        if net_income < 0:
            summary["concerns"].append(f"⚠️ Negative net income of KES {net_income:,.2f}")
        if collection_rate < 60:
            summary["concerns"].append(f"⚠️ Low collection rate of {collection_rate:.1f}%")
        
        # Add recommendations
        if collection_rate < 70:
            summary["recommendations"].append("📌 Focus on improving collections - consider payment reminders")
        if total_expenses > total_revenue * 0.8:
            summary["recommendations"].append("📌 Review expenses - they represent a high percentage of revenue")
        
        summary["generated_at"] = datetime.now().isoformat()
        
        return summary
    
    async def _gather_financial_context(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Gather financial data for AI context"""
        
        # Get invoices
        invoices = await self.db.invoices.find({
            "date_issued": {"$gte": start_date, "$lte": end_date}
        }).to_list(length=None)
        
        # Get transactions
        transactions = await self.db.transactions.find({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "status": "completed"
        }).to_list(length=None)
        
        # Get customers
        customers = await self.db.customers.find({}).to_list(length=None)
        
        # Calculate summaries
        total_revenue = sum(inv.get("total_amount", 0) for inv in invoices if inv.get("status") in ["paid", "sent"])
        total_expenses = sum(txn.get("amount", 0) for txn in transactions)
        
        # Customer metrics
        customer_revenue = {}
        for inv in invoices:
            customer_name = inv.get("customer_name") or inv.get("customer", {}).get("name", "Unknown")
            amount = inv.get("total_amount", 0)
            if customer_name not in customer_revenue:
                customer_revenue[customer_name] = 0
            customer_revenue[customer_name] += amount
        
        top_customers = sorted(customer_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
                "days": (end_date - start_date).days
            },
            "summary": {
                "total_revenue": round(total_revenue, 2),
                "total_expenses": round(total_expenses, 2),
                "net_income": round(total_revenue - total_expenses, 2),
                "invoice_count": len(invoices),
                "transaction_count": len(transactions),
                "customer_count": len(customers)
            },
            "top_customers": [{"name": name, "revenue": round(rev, 2)} for name, rev in top_customers],
            "invoices": invoices[:20],  # Limit for AI context
            "transactions": transactions[:20]  # Limit for AI context
        }
    
    def _build_ai_context(
        self,
        financial_data: Dict[str, Any],
        query: str,
        start_date: datetime,
        end_date: datetime
    ) -> str:
        """Build context string for AI"""
        
        context = f"""
Financial Report Query: {query}
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

Financial Summary:
- Total Revenue: KES {financial_data['summary']['total_revenue']:,.2f}
- Total Expenses: KES {financial_data['summary']['total_expenses']:,.2f}
- Net Income: KES {financial_data['summary']['net_income']:,.2f}
- Number of Invoices: {financial_data['summary']['invoice_count']}
- Number of Transactions: {financial_data['summary']['transaction_count']}
- Number of Customers: {financial_data['summary']['customer_count']}

Top Customers by Revenue:
"""
        for customer in financial_data["top_customers"]:
            context += f"- {customer['name']}: KES {customer['revenue']:,.2f}\n"
        
        context += "\nPlease analyze this financial data and provide insights relevant to the query."
        
        return context
