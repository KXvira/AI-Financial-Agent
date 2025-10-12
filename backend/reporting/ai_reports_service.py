"""
Custom AI Reports Service
Generates custom financial reports using Gemini AI based on natural language queries
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.mongodb import Database
import json

try:
    from ai_agent.gemini.service import GeminiService
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class CustomAIReportsService:
    """Service for generating AI-powered custom reports"""
    
    def __init__(self, db: Database):
        self.db = db
        if GEMINI_AVAILABLE:
            self.gemini_service = GeminiService()
        else:
            self.gemini_service = None
    
    async def generate_custom_report(
        self,
        query: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a custom report based on natural language query
        
        Args:
            query: Natural language query (e.g., "What were my top expenses last month?")
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            AI-generated report with insights
        """
        if not self.gemini_service:
            return {
                "error": "AI service not available",
                "message": "Gemini AI service is not configured"
            }
        
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
        financial_data = await self._gather_financial_data(start, end)
        
        # Create context for AI
        context = self._create_ai_context(financial_data, query)
        
        # Generate AI response
        try:
            ai_response = await self.gemini_service.generate_custom_report(context, query)
            
            return {
                "query": query,
                "period": {
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d")
                },
                "report": ai_response,
                "data_summary": self._create_data_summary(financial_data),
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": "AI generation failed",
                "message": str(e),
                "fallback_summary": self._create_data_summary(financial_data)
            }
    
    async def get_ai_insights(
        self,
        report_type: str = "general",
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get AI-powered insights for a specific report type
        
        Args:
            report_type: Type of insights (general, revenue, expenses, cash_flow)
            period_days: Number of days to analyze
            
        Returns:
            AI-generated insights
        """
        if not self.gemini_service:
            return {
                "error": "AI service not available",
                "message": "Gemini AI service is not configured"
            }
        
        end = datetime.now()
        start = end - timedelta(days=period_days)
        
        # Gather data based on report type
        financial_data = await self._gather_financial_data(start, end)
        
        # Generate insights
        try:
            insights = await self._generate_insights(financial_data, report_type)
            
            return {
                "report_type": report_type,
                "period_days": period_days,
                "insights": insights,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": "Insight generation failed",
                "message": str(e)
            }
    
    async def analyze_anomalies(
        self,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Detect anomalies in financial data using AI
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Detected anomalies with AI explanations
        """
        end = datetime.now()
        start = end - timedelta(days=period_days)
        
        financial_data = await self._gather_financial_data(start, end)
        
        # Detect statistical anomalies
        anomalies = self._detect_anomalies(financial_data)
        
        if not anomalies:
            return {
                "period_days": period_days,
                "anomalies_found": 0,
                "message": "No significant anomalies detected",
                "generated_at": datetime.now().isoformat()
            }
        
        # If AI available, get explanations
        if self.gemini_service:
            try:
                ai_explanations = await self._get_anomaly_explanations(anomalies, financial_data)
                for i, anomaly in enumerate(anomalies):
                    if i < len(ai_explanations):
                        anomaly["ai_explanation"] = ai_explanations[i]
            except:
                pass  # Continue without AI explanations
        
        return {
            "period_days": period_days,
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _gather_financial_data(
        self,
        start: datetime,
        end: datetime
    ) -> Dict[str, Any]:
        """Gather comprehensive financial data for the period"""
        # Get invoices
        invoices = await self.db.invoices.find({
            "date_issued": {"$gte": start, "$lte": end}
        }).to_list(length=None)
        
        # Get transactions
        transactions = await self.db.transactions.find({
            "timestamp": {"$gte": start, "$lte": end},
            "status": "completed"
        }).to_list(length=None)
        
        # Calculate summaries
        total_revenue = sum(inv.get("total_amount", 0) for inv in invoices if inv.get("status") in ["paid", "partially_paid"])
        total_invoiced = sum(inv.get("total_amount", 0) for inv in invoices)
        total_expenses = sum(txn.get("amount", 0) for txn in transactions if txn.get("transaction_type") == "expense")
        
        # Get customers
        customer_ids = list(set(inv.get("customer_id") for inv in invoices if inv.get("customer_id")))
        customers_count = len(customer_ids)
        
        return {
            "period": {
                "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d"),
                "days": (end - start).days
            },
            "invoices": {
                "total": len(invoices),
                "paid": len([i for i in invoices if i.get("status") == "paid"]),
                "pending": len([i for i in invoices if i.get("status") in ["sent", "overdue"]]),
                "total_amount": round(total_invoiced, 2),
                "paid_amount": round(total_revenue, 2)
            },
            "transactions": {
                "total": len(transactions),
                "expenses": len([t for t in transactions if t.get("transaction_type") == "expense"]),
                "total_expenses": round(total_expenses, 2)
            },
            "customers": {
                "active": customers_count
            },
            "net_income": round(total_revenue - total_expenses, 2)
        }
    
    def _create_ai_context(
        self,
        financial_data: Dict[str, Any],
        query: str
    ) -> str:
        """Create context string for AI"""
        context = f"""
Financial Data Summary for {financial_data['period']['start']} to {financial_data['period']['end']} ({financial_data['period']['days']} days):

INVOICES:
- Total Invoices: {financial_data['invoices']['total']}
- Paid Invoices: {financial_data['invoices']['paid']}
- Pending Invoices: {financial_data['invoices']['pending']}
- Total Invoiced Amount: KES {financial_data['invoices']['total_amount']:,.2f}
- Paid Amount: KES {financial_data['invoices']['paid_amount']:,.2f}

TRANSACTIONS:
- Total Transactions: {financial_data['transactions']['total']}
- Expense Transactions: {financial_data['transactions']['expenses']}
- Total Expenses: KES {financial_data['transactions']['total_expenses']:,.2f}

SUMMARY:
- Active Customers: {financial_data['customers']['active']}
- Net Income: KES {financial_data['net_income']:,.2f}

User Query: {query}
"""
        return context
    
    def _create_data_summary(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a structured data summary"""
        return {
            "period": financial_data["period"],
            "revenue": financial_data["invoices"]["paid_amount"],
            "expenses": financial_data["transactions"]["total_expenses"],
            "net_income": financial_data["net_income"],
            "invoices_count": financial_data["invoices"]["total"],
            "active_customers": financial_data["customers"]["active"]
        }
    
    async def _generate_insights(
        self,
        financial_data: Dict[str, Any],
        report_type: str
    ) -> List[Dict[str, Any]]:
        """Generate AI insights based on data"""
        insights = []
        
        # Revenue insights
        if report_type in ["general", "revenue"]:
            revenue = financial_data["invoices"]["paid_amount"]
            invoiced = financial_data["invoices"]["total_amount"]
            collection_rate = (revenue / invoiced * 100) if invoiced > 0 else 0
            
            insights.append({
                "type": "revenue",
                "metric": "Collection Rate",
                "value": f"{collection_rate:.1f}%",
                "insight": f"Collection rate is {collection_rate:.1f}%. " +
                          ("Good collection efficiency." if collection_rate > 80 else "Consider improving collection processes."),
                "severity": "info" if collection_rate > 80 else "warning"
            })
        
        # Expense insights
        if report_type in ["general", "expenses"]:
            expenses = financial_data["transactions"]["total_expenses"]
            revenue = financial_data["invoices"]["paid_amount"]
            expense_ratio = (expenses / revenue * 100) if revenue > 0 else 0
            
            insights.append({
                "type": "expenses",
                "metric": "Expense Ratio",
                "value": f"{expense_ratio:.1f}%",
                "insight": f"Expenses are {expense_ratio:.1f}% of revenue. " +
                          ("Healthy expense management." if expense_ratio < 70 else "Consider cost optimization."),
                "severity": "info" if expense_ratio < 70 else "warning"
            })
        
        # Profitability insights
        if report_type in ["general", "cash_flow"]:
            net_income = financial_data["net_income"]
            revenue = financial_data["invoices"]["paid_amount"]
            profit_margin = (net_income / revenue * 100) if revenue > 0 else 0
            
            insights.append({
                "type": "profitability",
                "metric": "Profit Margin",
                "value": f"{profit_margin:.1f}%",
                "insight": f"Net profit margin is {profit_margin:.1f}%. " +
                          ("Strong profitability." if profit_margin > 20 else 
                           "Moderate profitability." if profit_margin > 10 else
                           "Low profitability - review pricing and costs."),
                "severity": "success" if profit_margin > 20 else "info" if profit_margin > 10 else "warning"
            })
        
        return insights
    
    def _detect_anomalies(self, financial_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect statistical anomalies in financial data"""
        anomalies = []
        
        # Check for high expense ratio
        expenses = financial_data["transactions"]["total_expenses"]
        revenue = financial_data["invoices"]["paid_amount"]
        
        if revenue > 0:
            expense_ratio = expenses / revenue
            if expense_ratio > 0.9:
                anomalies.append({
                    "type": "high_expenses",
                    "severity": "high",
                    "metric": "Expense Ratio",
                    "value": f"{expense_ratio * 100:.1f}%",
                    "description": "Expenses are consuming more than 90% of revenue",
                    "recommendation": "Review and optimize expense categories"
                })
        
        # Check for low collection rate
        paid = financial_data["invoices"]["paid"]
        total = financial_data["invoices"]["total"]
        
        if total > 0:
            collection_rate = paid / total
            if collection_rate < 0.5:
                anomalies.append({
                    "type": "low_collection",
                    "severity": "medium",
                    "metric": "Collection Rate",
                    "value": f"{collection_rate * 100:.1f}%",
                    "description": "Less than 50% of invoices have been paid",
                    "recommendation": "Improve collection processes and follow-up"
                })
        
        # Check for negative cash flow
        if financial_data["net_income"] < 0:
            anomalies.append({
                "type": "negative_cash_flow",
                "severity": "high",
                "metric": "Net Income",
                "value": f"KES {financial_data['net_income']:,.2f}",
                "description": "Negative cash flow detected",
                "recommendation": "Urgent: Review expenses and accelerate collections"
            })
        
        return anomalies
    
    async def _get_anomaly_explanations(
        self,
        anomalies: List[Dict[str, Any]],
        financial_data: Dict[str, Any]
    ) -> List[str]:
        """Get AI explanations for anomalies"""
        explanations = []
        
        for anomaly in anomalies:
            explanation = f"This {anomaly['type']} anomaly suggests potential issues in {anomaly['metric']}. "
            explanation += f"Current value: {anomaly['value']}. "
            explanation += anomaly['recommendation']
            explanations.append(explanation)
        
        return explanations
