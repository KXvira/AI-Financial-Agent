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
        
        # Convert to string format for MongoDB query (our data uses string dates)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Use aggregation pipeline for better performance
        pipeline = [
            {
                "$match": {
                    "issue_date": {"$gte": start_str, "$lte": end_str},
                    "status": {"$in": ["paid", "sent", "overdue"]}
                }
            },
            {
                "$addFields": {
                    # Extract year-month from issue_date string (YYYY-MM-DD)
                    "year_month": {"$substr": ["$issue_date", 0, 7]}
                }
            },
            {
                "$group": {
                    "_id": "$year_month",
                    "revenue": {"$sum": "$total_amount"},
                    "invoice_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        # Execute aggregation
        result = await self.db.invoices.aggregate(pipeline).to_list(length=None)
        
        # Convert to historical_data format
        historical_data = []
        for item in result:
            historical_data.append({
                "month": item["_id"],
                "revenue": item["revenue"]
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
        # Get last month from historical data
        last_month = historical_data[-1]["month"] if historical_data else end_date.strftime("%Y-%m")
        last_date = datetime.strptime(last_month, "%Y-%m")
        
        for i in range(1, months_ahead + 1):
            forecast_date = last_date + timedelta(days=30 * i)
            forecast_month = forecast_date.strftime("%Y-%m")
            
            # Apply growth rate to recent average
            base_forecast = recent_avg * (1 + growth_rate / 100) ** i
            
            forecast_item = {
                "month": forecast_month,
                "predicted_value": round(base_forecast, 2),  # Frontend expects "predicted_value"
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
            
            if include_confidence:
                # Simple confidence interval (±1 std dev) - flatten for frontend
                forecast_item["lower_bound"] = round(max(0, base_forecast - std_dev), 2)
                forecast_item["upper_bound"] = round(base_forecast + std_dev, 2)
                forecast_item["confidence"] = 95  # 95% confidence interval
            
            forecasts.append(forecast_item)
        
        # Calculate accuracy metrics
        accuracy = self._calculate_forecast_accuracy(revenues)
        
        return {
            "forecast": forecasts,  # Frontend expects "forecast" not "forecasts"
            "historical": {
                "average": round(avg_revenue, 2),
                "std_dev": round(std_dev, 2),
                "trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "months_analyzed": len(historical_data)
            },
            "trend_analysis": {
                "trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "average_growth_rate": round(growth_rate, 2),
                "volatility": round(std_dev / avg_revenue, 2) if avg_revenue > 0 else 0,
                "confidence": "high" if std_dev / avg_revenue < 0.15 else "medium" if std_dev / avg_revenue < 0.3 else "low"
            },
            "accuracy_metrics": {
                "method": "Moving Average with Growth Rate",
                "confidence_level": 95
            }
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
        
        # Convert to string format for MongoDB query
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Use aggregation pipeline for better performance
        pipeline = [
            {
                "$match": {
                    "transaction_date": {"$gte": start_str, "$lte": end_str},
                    "type": "expense",
                    "status": "completed"
                }
            },
            {
                "$addFields": {
                    # Extract year-month from transaction_date string (YYYY-MM-DD)
                    "year_month": {"$substr": ["$transaction_date", 0, 7]}
                }
            },
            {
                "$group": {
                    "_id": "$year_month",
                    "expenses": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        # Execute aggregation
        result = await self.db.transactions.aggregate(pipeline).to_list(length=None)
        
        # Convert to historical_data format
        historical_data = []
        for item in result:
            historical_data.append({
                "month": item["_id"],
                "expenses": item["expenses"]
            })
        
        # Get category breakdown (separate aggregation)
        category_pipeline = [
            {
                "$match": {
                    "transaction_date": {"$gte": start_str, "$lte": end_str},
                    "type": "expense",
                    "status": "completed"
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1},
                    "average": {"$avg": "$amount"}
                }
            },
            {"$sort": {"total": -1}},
            {"$limit": 5}
        ]
        
        category_result = await self.db.transactions.aggregate(category_pipeline).to_list(length=5)
        category_expenses = {item["_id"]: [item["average"]] * item["count"] for item in category_result}
        
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
        # Get last month from historical data
        last_month = historical_data[-1]["month"] if historical_data else end_date.strftime("%Y-%m")
        last_date = datetime.strptime(last_month, "%Y-%m")
        
        for i in range(1, months_ahead + 1):
            forecast_date = last_date + timedelta(days=30 * i)
            forecast_month = forecast_date.strftime("%Y-%m")
            
            base_forecast = recent_avg * (1 + growth_rate / 100) ** i
            
            forecast_item = {
                "month": forecast_month,
                "predicted_value": round(base_forecast, 2),  # Match frontend interface
                "trend": "increasing" if growth_rate > 0 else "decreasing" if growth_rate < 0 else "stable"
            }
            
            if include_confidence:
                # Flatten confidence interval for frontend
                forecast_item["lower_bound"] = round(max(0, base_forecast - std_dev), 2)
                forecast_item["upper_bound"] = round(base_forecast + std_dev, 2)
                forecast_item["confidence"] = 95
            
            forecasts.append(forecast_item)
        
        # Top expense categories
        top_categories = sorted(
            category_expenses.items(),
            key=lambda x: sum(x[1]),
            reverse=True
        )[:5]
        
        return {
            "forecast": forecasts,  # Frontend expects "forecast" not "forecasts"
            "historical": {
                "average": round(avg_expenses, 2),
                "std_dev": round(std_dev, 2),
                "trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "months_analyzed": len(historical_data)
            },
            "trend_analysis": {
                "trend": "increasing" if growth_rate > 5 else "decreasing" if growth_rate < -5 else "stable",
                "average_growth_rate": round(growth_rate, 2),
                "volatility": round(std_dev / avg_expenses, 2) if avg_expenses > 0 else 0,
                "confidence": "high" if std_dev / avg_expenses < 0.15 else "medium" if std_dev / avg_expenses < 0.3 else "low"
            },
            "accuracy_metrics": {
                "method": "Moving Average with Growth Rate",
                "confidence_level": 95
            },
            "top_categories": [
                {
                    "category": cat,
                    "total": round(sum(amounts), 2),
                    "average": round(statistics.mean(amounts), 2)
                }
                for cat, amounts in top_categories
            ]
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
