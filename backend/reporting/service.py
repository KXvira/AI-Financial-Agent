"""
Financial reporting and monitoring service
"""
import logging
from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta

from ai_agent.gemini import GeminiService

logger = logging.getLogger("financial-agent.reporting")

class ReportingService:
    """
    Service for generating financial reports and monitoring
    """
    
    def __init__(self):
        self.gemini_service = GeminiService()
        
    async def generate_financial_report(self, 
                                  report_type: str, 
                                  start_date: str, 
                                  end_date: str,
                                  filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate a financial report
        
        Args:
            report_type: Type of report to generate (e.g., "cash_flow", "revenue", "expenses")
            start_date: Start date for the report (YYYY-MM-DD)
            end_date: End date for the report (YYYY-MM-DD)
            filters: Additional filters for the report
            
        Returns:
            Dict with the report data
        """
        try:
            if filters is None:
                filters = {}
                
            # Log the report generation attempt
            logger.info(f"Generating {report_type} report from {start_date} to {end_date} with filters: {json.dumps(filters)}")
            
            # In a real implementation, we would fetch the financial data from the database
            # financial_data = await self.db.get_financial_data(start_date, end_date, filters)
            
            # For demonstration purposes, we'll use mock financial data
            financial_data = self._get_mock_financial_data(report_type, start_date, end_date)
            
            # Use Gemini to generate insights for the report
            financial_data["report_type"] = report_type
            financial_data["start_date"] = start_date
            financial_data["end_date"] = end_date
            financial_data["filters"] = filters
            
            insights = await self.gemini_service.generate_financial_insights(financial_data)
            
            # Combine the data and insights
            report = {
                "report_type": report_type,
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters,
                "generated_at": datetime.now().isoformat(),
                "data": financial_data,
                "insights": insights
            }
            
            # In a real implementation, we would store the report
            # await self.db.store_report(report)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating {report_type} report: {str(e)}")
            raise
    
    async def get_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get real-time dashboard metrics
        
        Returns:
            Dict with dashboard metrics
        """
        try:
            # Log the dashboard metrics request
            logger.info("Getting dashboard metrics")
            
            # In a real implementation, we would fetch the metrics from the database
            # metrics = await self.db.get_dashboard_metrics()
            
            # For demonstration purposes, we'll use mock metrics
            metrics = self._get_mock_dashboard_metrics()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise
    
    async def monitor_transaction_anomalies(self) -> Dict[str, Any]:
        """
        Monitor for transaction anomalies
        
        Returns:
            Dict with anomaly detection results
        """
        try:
            # Log the anomaly detection request
            logger.info("Monitoring for transaction anomalies")
            
            # In a real implementation, we would fetch recent transactions
            # recent_transactions = await self.db.get_recent_transactions()
            # historical_transactions = await self.db.get_historical_transactions()
            
            # For demonstration purposes, we'll use mock transactions
            recent_transactions = self._get_mock_recent_transactions()
            historical_transactions = self._get_mock_historical_transactions()
            
            results = {
                "total_transactions": len(recent_transactions),
                "anomalies_detected": 0,
                "anomalies": []
            }
            
            # Process each transaction
            for transaction in recent_transactions:
                # Use Gemini to detect anomalies
                anomaly_result = await self.gemini_service.detect_anomalies(
                    transaction, historical_transactions
                )
                
                if anomaly_result.get("is_anomalous", False):
                    results["anomalies_detected"] += 1
                    results["anomalies"].append({
                        "transaction_id": transaction.get("id", "unknown"),
                        "anomaly_result": anomaly_result
                    })
                    
                    # In a real implementation, we would flag the anomaly
                    # await self.db.flag_transaction_anomaly(transaction, anomaly_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error monitoring for transaction anomalies: {str(e)}")
            raise
    
    async def schedule_recurring_report(self, 
                                  report_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Schedule a recurring report
        
        Args:
            report_config: Configuration for the recurring report
            
        Returns:
            Dict with scheduling result
        """
        try:
            # Log the scheduling request
            logger.info(f"Scheduling recurring report: {json.dumps(report_config)}")
            
            # Validate the schedule
            schedule = report_config.get("schedule")
            if not schedule:
                raise ValueError("Report schedule is required")
                
            # In a real implementation, we would store the schedule
            # schedule_id = await self.db.store_report_schedule(report_config)
            
            # For demonstration purposes, we'll just return a success message
            return {
                "success": True,
                "message": "Report scheduled successfully",
                "schedule_id": "SCH-001",
                "next_run": self._calculate_next_run(schedule)
            }
            
        except Exception as e:
            logger.error(f"Error scheduling recurring report: {str(e)}")
            raise
    
    def _calculate_next_run(self, schedule: Dict[str, Any]) -> str:
        """
        Calculate the next run time for a schedule
        """
        frequency = schedule.get("frequency")
        now = datetime.now()
        
        if frequency == "daily":
            next_run = now + timedelta(days=1)
        elif frequency == "weekly":
            next_run = now + timedelta(weeks=1)
        elif frequency == "monthly":
            # Approximate a month as 30 days
            next_run = now + timedelta(days=30)
        else:
            next_run = now + timedelta(days=1)  # Default to daily
        
        return next_run.isoformat()
    
    def _get_mock_financial_data(self, report_type: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get mock financial data for testing
        """
        # Convert start and end dates to datetime objects
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Generate some mock data based on the report type
        if report_type == "cash_flow":
            return {
                "cash_inflow": {
                    "sales": 120000,
                    "accounts_receivable": 45000,
                    "investments": 30000,
                    "total": 195000
                },
                "cash_outflow": {
                    "expenses": 75000,
                    "inventory": 25000,
                    "payroll": 45000,
                    "taxes": 15000,
                    "total": 160000
                },
                "net_cash_flow": 35000,
                "daily_cash_balance": [
                    {"date": "2025-06-01", "balance": 100000},
                    {"date": "2025-06-02", "balance": 105000},
                    {"date": "2025-06-03", "balance": 115000},
                    # More daily balances...
                    {"date": "2025-06-30", "balance": 135000}
                ]
            }
        elif report_type == "revenue":
            return {
                "total_revenue": 150000,
                "by_category": {
                    "product_sales": 80000,
                    "services": 55000,
                    "subscriptions": 15000
                },
                "by_customer": [
                    {"customer": "ABC Corp", "amount": 45000},
                    {"customer": "XYZ Ltd", "amount": 35000},
                    {"customer": "123 Industries", "amount": 25000},
                    # More customers...
                ],
                "monthly_trend": [
                    {"month": "January", "amount": 125000},
                    {"month": "February", "amount": 130000},
                    {"month": "March", "amount": 140000},
                    {"month": "April", "amount": 135000},
                    {"month": "May", "amount": 145000},
                    {"month": "June", "amount": 150000}
                ]
            }
        elif report_type == "expenses":
            return {
                "total_expenses": 120000,
                "by_category": {
                    "rent": 20000,
                    "utilities": 5000,
                    "payroll": 60000,
                    "marketing": 15000,
                    "software": 8000,
                    "office_supplies": 5000,
                    "travel": 7000
                },
                "monthly_trend": [
                    {"month": "January", "amount": 110000},
                    {"month": "February", "amount": 105000},
                    {"month": "March", "amount": 115000},
                    {"month": "April", "amount": 118000},
                    {"month": "May", "amount": 125000},
                    {"month": "June", "amount": 120000}
                ]
            }
        else:
            return {
                "message": f"No mock data available for report type: {report_type}"
            }
    
    def _get_mock_dashboard_metrics(self) -> Dict[str, Any]:
        """
        Get mock dashboard metrics for testing
        """
        return {
            "cash_position": {
                "current_balance": 135000,
                "change_since_yesterday": 5000,
                "pending_payables": 25000,
                "pending_receivables": 40000
            },
            "revenue_metrics": {
                "mtd": 75000,
                "ytd": 780000,
                "growth_yoy": 12.5
            },
            "expense_metrics": {
                "mtd": 60000,
                "ytd": 650000,
                "largest_category": "payroll"
            },
            "payment_metrics": {
                "paid_on_time_rate": 85,
                "average_days_to_payment": 12,
                "reconciliation_rate": 95
            },
            "recent_activity": [
                {"type": "payment", "amount": 5000, "timestamp": "2025-06-07T09:15:30", "status": "reconciled"},
                {"type": "invoice", "amount": 7500, "timestamp": "2025-06-07T10:20:45", "status": "sent"},
                {"type": "expense", "amount": 1200, "timestamp": "2025-06-07T11:30:00", "status": "categorized"}
            ]
        }
    
    def _get_mock_recent_transactions(self) -> List[Dict[str, Any]]:
        """
        Get mock recent transactions for testing
        """
        return [
            {
                "id": "TRX-001",
                "type": "payment",
                "amount": 5000,
                "timestamp": "2025-06-07T09:15:30",
                "source": "M-Pesa",
                "phone_number": "254712345678",
                "description": "Payment for INV-001"
            },
            {
                "id": "TRX-002",
                "type": "payment",
                "amount": 7500,  # Unusual amount for this customer
                "timestamp": "2025-06-07T10:20:45",
                "source": "M-Pesa",
                "phone_number": "254723456789",
                "description": "Payment for INV-002"
            },
            {
                "id": "TRX-003",
                "type": "payment",
                "amount": 2000,
                "timestamp": "2025-06-07T01:30:00",  # Unusual time
                "source": "M-Pesa",
                "phone_number": "254734567890",
                "description": "Payment for INV-003"
            }
        ]
    
    def _get_mock_historical_transactions(self) -> List[Dict[str, Any]]:
        """
        Get mock historical transactions for testing
        """
        return [
            # Customer 1 history
            {
                "id": "HIST-001",
                "customer_phone": "254712345678",
                "average_amount": 5000,
                "usual_time_range": "08:00 - 17:00",
                "frequency": "monthly",
                "last_payments": [
                    {"amount": 5000, "timestamp": "2025-05-07T14:25:10"},
                    {"amount": 4800, "timestamp": "2025-04-05T11:12:30"},
                    {"amount": 5200, "timestamp": "2025-03-08T10:45:22"}
                ]
            },
            # Customer 2 history
            {
                "id": "HIST-002",
                "customer_phone": "254723456789",
                "average_amount": 3000,  # Current payment is much larger
                "usual_time_range": "09:00 - 18:00",
                "frequency": "monthly",
                "last_payments": [
                    {"amount": 3000, "timestamp": "2025-05-10T15:30:00"},
                    {"amount": 3200, "timestamp": "2025-04-12T14:22:30"},
                    {"amount": 2800, "timestamp": "2025-03-15T16:05:45"}
                ]
            },
            # Customer 3 history
            {
                "id": "HIST-003",
                "customer_phone": "254734567890",
                "average_amount": 2000,
                "usual_time_range": "08:00 - 18:00",  # Current payment is outside this range
                "frequency": "monthly",
                "last_payments": [
                    {"amount": 2000, "timestamp": "2025-05-20T10:30:00"},
                    {"amount": 2000, "timestamp": "2025-04-22T14:45:30"},
                    {"amount": 2000, "timestamp": "2025-03-21T11:15:45"}
                ]
            }
        ]
