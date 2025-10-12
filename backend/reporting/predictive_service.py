"""
Predictive Analytics Service
Provides revenue forecasting, expense predictions, and cash flow forecasting using statistical methods
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from database.mongodb import Database
import statistics

class PredictiveAnalyticsService:
    """Service for generating predictive analytics and forecasts"""
    
    def __init__(self, db: Database):
        self.db = db
        
    async def generate_revenue_forecast(
        self,
        months_ahead: int = 3,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate revenue forecast using historical data
        
        Args:
            months_ahead: Number of months to forecast
            include_confidence: Include confidence intervals
            
        Returns:
            Revenue forecast with predictions and trends
        """
        # Get historical revenue data (last 12 months)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        # Query invoices for historical data
        invoices = await self.db.invoices.find({
            "date_issued": {"$gte": start_date, "$lte": end_date},
            "status": {"$in": ["paid", "sent", "overdue"]}
        }).to_list(length=None)
        
        # Group by month
        monthly_revenue = {}
        for invoice in invoices:
            date_issued = invoice.get("date_issued")
            if isinstance(date_issued, str):
                date_issued = datetime.fromisoformat(date_issued.replace('Z', '+00:00'))
            
            month_key = date_issued.strftime("%Y-%m")
            amount = invoice.get("total_amount", 0)
            
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += amount
        
        # Convert to sorted list
        historical_data = []
        sorted_months = sorted(monthly_revenue.keys())
        for month in sorted_months:
            historical_data.append({
                "month": month,
                "revenue": monthly_revenue[month]
            })
        
        # Calculate trends
        revenues = [item["revenue"] for item in historical_data]
        
        if len(revenues) < 3:
            return {
                "error": "Insufficient historical data for forecasting (need at least 3 months)",
                "historical_data": historical_data
            }
        
        # Simple moving average forecast
        avg_revenue = statistics.mean(revenues)
        std_dev = statistics.stdev(revenues) if len(revenues) > 1 else 0
        
        # Calculate growth rate
        recent_avg = statistics.mean(revenues[-3:]) if len(revenues) >= 3 else avg_revenue
        older_avg = statistics.mean(revenues[:3]) if len(revenues) >= 6 else avg_revenue
        growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        # Generate forecasts
        forecasts = []
        last_date = datetime.strptime(sorted_months[-1], "%Y-%m")
        
        for i in range(1, months_ahead + 1):
            forecast_date = last_date + timedelta(days=30 * i)
            forecast_month = forecast_date.strftime("%Y-%m")
            
            # Apply growth rate to recent average
            base_forecast = recent_avg * (1 + growth_rate / 100) ** i
            
            forecast_item = {
                "month": forecast_month,
                "predicted_revenue": round(base_forecast, 2),
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
            
            if include_confidence:
                # Simple confidence interval (±1 std dev)
                forecast_item["confidence_interval"] = {
                    "lower": round(max(0, base_forecast - std_dev), 2),
                    "upper": round(base_forecast + std_dev, 2)
                }
            
            forecasts.append(forecast_item)
        
        # Calculate accuracy metrics
        accuracy = self._calculate_forecast_accuracy(revenues)
        
        return {
            "forecast_period": {
                "start_month": forecasts[0]["month"] if forecasts else None,
                "end_month": forecasts[-1]["month"] if forecasts else None,
                "months_ahead": months_ahead
            },
            "historical_summary": {
                "months_analyzed": len(historical_data),
                "average_revenue": round(avg_revenue, 2),
                "min_revenue": round(min(revenues), 2) if revenues else 0,
                "max_revenue": round(max(revenues), 2) if revenues else 0,
                "std_deviation": round(std_dev, 2),
                "growth_rate": round(growth_rate, 2)
            },
            "forecasts": forecasts,
            "trends": {
                "overall_trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "growth_rate": round(growth_rate, 2),
                "volatility": "high" if std_dev / avg_revenue > 0.3 else "medium" if std_dev / avg_revenue > 0.15 else "low"
            },
            "accuracy": accuracy,
            "historical_data": historical_data[-6:],  # Last 6 months
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_expense_forecast(
        self,
        months_ahead: int = 3,
        include_confidence: bool = True
    ) -> Dict[str, Any]:
        """
        Generate expense forecast using historical transaction data
        
        Args:
            months_ahead: Number of months to forecast
            include_confidence: Include confidence intervals
            
        Returns:
            Expense forecast with predictions
        """
        # Get historical expense data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        transactions = await self.db.transactions.find({
            "timestamp": {"$gte": start_date, "$lte": end_date},
            "type": {"$in": ["expense", "payment"]},
            "status": "completed"
        }).to_list(length=None)
        
        # Group by month
        monthly_expenses = {}
        category_expenses = {}
        
        for txn in transactions:
            timestamp = txn.get("timestamp")
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            month_key = timestamp.strftime("%Y-%m")
            amount = txn.get("amount", 0)
            category = txn.get("category", "Uncategorized")
            
            if month_key not in monthly_expenses:
                monthly_expenses[month_key] = 0
            monthly_expenses[month_key] += amount
            
            if category not in category_expenses:
                category_expenses[category] = []
            category_expenses[category].append(amount)
        
        # Convert to sorted list
        historical_data = []
        sorted_months = sorted(monthly_expenses.keys())
        for month in sorted_months:
            historical_data.append({
                "month": month,
                "expenses": monthly_expenses[month]
            })
        
        expenses = [item["expenses"] for item in historical_data]
        
        if len(expenses) < 3:
            return {
                "error": "Insufficient historical data for forecasting",
                "historical_data": historical_data
            }
        
        # Calculate statistics
        avg_expenses = statistics.mean(expenses)
        std_dev = statistics.stdev(expenses) if len(expenses) > 1 else 0
        
        # Calculate trend
        recent_avg = statistics.mean(expenses[-3:])
        older_avg = statistics.mean(expenses[:3]) if len(expenses) >= 6 else avg_expenses
        growth_rate = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        
        # Generate forecasts
        forecasts = []
        last_date = datetime.strptime(sorted_months[-1], "%Y-%m")
        
        for i in range(1, months_ahead + 1):
            forecast_date = last_date + timedelta(days=30 * i)
            forecast_month = forecast_date.strftime("%Y-%m")
            
            base_forecast = recent_avg * (1 + growth_rate / 100) ** i
            
            forecast_item = {
                "month": forecast_month,
                "predicted_expenses": round(base_forecast, 2),
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
            
            if include_confidence:
                forecast_item["confidence_interval"] = {
                    "lower": round(max(0, base_forecast - std_dev), 2),
                    "upper": round(base_forecast + std_dev, 2)
                }
            
            forecasts.append(forecast_item)
        
        # Top expense categories
        top_categories = sorted(
            category_expenses.items(),
            key=lambda x: sum(x[1]),
            reverse=True
        )[:5]
        
        return {
            "forecast_period": {
                "start_month": forecasts[0]["month"] if forecasts else None,
                "end_month": forecasts[-1]["month"] if forecasts else None,
                "months_ahead": months_ahead
            },
            "historical_summary": {
                "months_analyzed": len(historical_data),
                "average_expenses": round(avg_expenses, 2),
                "min_expenses": round(min(expenses), 2),
                "max_expenses": round(max(expenses), 2),
                "std_deviation": round(std_dev, 2),
                "growth_rate": round(growth_rate, 2)
            },
            "forecasts": forecasts,
            "top_categories": [
                {
                    "category": cat,
                    "total": round(sum(amounts), 2),
                    "average": round(statistics.mean(amounts), 2)
                }
                for cat, amounts in top_categories
            ],
            "trends": {
                "overall_trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "growth_rate": round(growth_rate, 2)
            },
            "historical_data": historical_data[-6:],
            "generated_at": datetime.now().isoformat()
        }
    
    async def generate_cash_flow_forecast(
        self,
        months_ahead: int = 3
    ) -> Dict[str, Any]:
        """
        Generate cash flow forecast combining revenue and expense predictions
        
        Args:
            months_ahead: Number of months to forecast
            
        Returns:
            Cash flow forecast
        """
        # Get both forecasts
        revenue_forecast = await self.generate_revenue_forecast(months_ahead, include_confidence=False)
        expense_forecast = await self.generate_expense_forecast(months_ahead, include_confidence=False)
        
        if "error" in revenue_forecast or "error" in expense_forecast:
            return {
                "error": "Insufficient data for cash flow forecasting",
                "revenue_status": revenue_forecast.get("error"),
                "expense_status": expense_forecast.get("error")
            }
        
        # Combine forecasts
        forecasts = []
        for i in range(months_ahead):
            rev = revenue_forecast["forecasts"][i]
            exp = expense_forecast["forecasts"][i]
            
            predicted_revenue = rev["predicted_revenue"]
            predicted_expenses = exp["predicted_expenses"]
            net_cash_flow = predicted_revenue - predicted_expenses
            
            forecasts.append({
                "month": rev["month"],
                "predicted_revenue": predicted_revenue,
                "predicted_expenses": predicted_expenses,
                "net_cash_flow": round(net_cash_flow, 2),
                "cash_flow_status": "positive" if net_cash_flow > 0 else "negative"
            })
        
        # Calculate summary
        total_revenue = sum(f["predicted_revenue"] for f in forecasts)
        total_expenses = sum(f["predicted_expenses"] for f in forecasts)
        total_net = total_revenue - total_expenses
        
        return {
            "forecast_period": {
                "start_month": forecasts[0]["month"],
                "end_month": forecasts[-1]["month"],
                "months_ahead": months_ahead
            },
            "summary": {
                "total_predicted_revenue": round(total_revenue, 2),
                "total_predicted_expenses": round(total_expenses, 2),
                "total_net_cash_flow": round(total_net, 2),
                "average_monthly_cash_flow": round(total_net / months_ahead, 2),
                "overall_status": "positive" if total_net > 0 else "negative"
            },
            "forecasts": forecasts,
            "insights": self._generate_cash_flow_insights(forecasts),
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_forecast_accuracy(self, historical_values: List[float]) -> Dict[str, Any]:
        """Calculate forecast accuracy metrics"""
        if len(historical_values) < 6:
            return {"note": "Insufficient data for accuracy calculation"}
        
        # Simple accuracy: compare last 3 actual vs what would have been predicted
        recent = historical_values[-3:]
        older = historical_values[-6:-3]
        
        predicted_avg = statistics.mean(older)
        actual_avg = statistics.mean(recent)
        
        accuracy_pct = max(0, 100 - abs((actual_avg - predicted_avg) / actual_avg * 100)) if actual_avg > 0 else 0
        
        return {
            "accuracy_percentage": round(accuracy_pct, 2),
            "confidence_level": "high" if accuracy_pct > 80 else "medium" if accuracy_pct > 60 else "low",
            "note": "Based on simple moving average comparison"
        }
    
    def _generate_cash_flow_insights(self, forecasts: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from cash flow forecast"""
        insights = []
        
        # Check for negative months
        negative_months = [f for f in forecasts if f["net_cash_flow"] < 0]
        if negative_months:
            insights.append(f"⚠️ Warning: {len(negative_months)} month(s) predicted with negative cash flow")
        
        # Check for improving/declining trend
        if len(forecasts) >= 2:
            first_half = statistics.mean([f["net_cash_flow"] for f in forecasts[:len(forecasts)//2]])
            second_half = statistics.mean([f["net_cash_flow"] for f in forecasts[len(forecasts)//2:]])
            
            if second_half > first_half * 1.1:
                insights.append("✅ Cash flow trend is improving")
            elif second_half < first_half * 0.9:
                insights.append("⚠️ Cash flow trend is declining")
        
        # Check volatility
        net_flows = [f["net_cash_flow"] for f in forecasts]
        if len(net_flows) > 1:
            std_dev = statistics.stdev(net_flows)
            avg = statistics.mean(net_flows)
            if abs(std_dev / avg) > 0.5 if avg != 0 else False:
                insights.append("⚠️ High volatility expected in cash flow")
        
        if not insights:
            insights.append("✅ Cash flow forecast looks stable")
        
        return insights
    
    async def get_predictive_summary(self) -> Dict[str, Any]:
        """Get high-level predictive analytics summary for dashboard"""
        revenue_forecast = await self.generate_revenue_forecast(months_ahead=1, include_confidence=False)
        expense_forecast = await self.generate_expense_forecast(months_ahead=1, include_confidence=False)
        
        summary = {
            "next_month_prediction": {
                "revenue": None,
                "expenses": None,
                "net": None
            },
            "trends": {
                "revenue": None,
                "expenses": None
            }
        }
        
        if "error" not in revenue_forecast and revenue_forecast["forecasts"]:
            rev = revenue_forecast["forecasts"][0]
            summary["next_month_prediction"]["revenue"] = rev["predicted_revenue"]
            summary["trends"]["revenue"] = revenue_forecast["trends"]["overall_trend"]
        
        if "error" not in expense_forecast and expense_forecast["forecasts"]:
            exp = expense_forecast["forecasts"][0]
            summary["next_month_prediction"]["expenses"] = exp["predicted_expenses"]
            summary["trends"]["expenses"] = expense_forecast["trends"]["overall_trend"]
        
        if summary["next_month_prediction"]["revenue"] and summary["next_month_prediction"]["expenses"]:
            summary["next_month_prediction"]["net"] = round(
                summary["next_month_prediction"]["revenue"] - summary["next_month_prediction"]["expenses"],
                2
            )
        
        return summary
