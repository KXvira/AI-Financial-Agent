"""
Advanced Business Intelligence and Analytics
Comprehensive financial metrics and comparative analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class MetricType(str, Enum):
    """Types of financial metrics"""
    CASH_FLOW = "cash_flow"
    PROFITABILITY = "profitability"
    EFFICIENCY = "efficiency"
    LIQUIDITY = "liquidity"
    GROWTH = "growth"

class TimeFrame(str, Enum):
    """Analysis time frames"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class FinancialMetric(BaseModel):
    """Single financial metric result"""
    metric_name: str
    metric_type: MetricType
    value: float
    unit: str
    description: str
    benchmark: Optional[float] = None
    status: str  # "good", "warning", "critical"
    trend: Optional[str] = None  # "improving", "declining", "stable"

class BusinessIntelligenceService:
    """Advanced financial metrics calculator"""
    
    def __init__(self):
        self.industry_benchmarks = {
            'dso': {'retail': 15, 'manufacturing': 45, 'services': 30},
            'cash_conversion_cycle': {'retail': 20, 'manufacturing': 60, 'services': 35},
            'current_ratio': {'all': 2.0},
            'quick_ratio': {'all': 1.0}
        }
    
    def calculate_cash_conversion_cycle(self, data: Dict[str, Any]) -> FinancialMetric:
        """Calculate Cash Conversion Cycle (CCC)"""
        try:
            # CCC = DIO + DSO - DPO
            # DIO = Days Inventory Outstanding
            # DSO = Days Sales Outstanding  
            # DPO = Days Payable Outstanding
            
            inventory_days = data.get('inventory_days', 0)
            receivables_days = data.get('receivables_days', 30)
            payables_days = data.get('payables_days', 15)
            
            ccc = inventory_days + receivables_days - payables_days
            
            # Determine status based on industry benchmark
            industry = data.get('industry', 'services')
            benchmark = self.industry_benchmarks['cash_conversion_cycle'].get(industry, 35)
            
            if ccc <= benchmark * 0.8:
                status = "good"
            elif ccc <= benchmark * 1.2:
                status = "warning"
            else:
                status = "critical"
            
            return FinancialMetric(
                metric_name="Cash Conversion Cycle",
                metric_type=MetricType.EFFICIENCY,
                value=ccc,
                unit="days",
                description="Time to convert investments into cash flows",
                benchmark=benchmark,
                status=status,
                trend=self._calculate_trend(data.get('historical_ccc', [ccc]))
            )
            
        except Exception as e:
            logger.error(f"CCC calculation error: {e}")
            raise ValueError(f"Failed to calculate Cash Conversion Cycle: {e}")
    
    def calculate_days_sales_outstanding(self, data: Dict[str, Any]) -> FinancialMetric:
        """Calculate Days Sales Outstanding (DSO)"""
        try:
            accounts_receivable = data.get('accounts_receivable', 0)
            total_sales = data.get('total_sales', 1)
            days_in_period = data.get('days_in_period', 365)
            
            dso = (accounts_receivable / total_sales) * days_in_period
            
            # Benchmark comparison
            industry = data.get('industry', 'services')
            benchmark = self.industry_benchmarks['dso'].get(industry, 30)
            
            if dso <= benchmark * 0.8:
                status = "good"
            elif dso <= benchmark * 1.3:
                status = "warning"
            else:
                status = "critical"
            
            return FinancialMetric(
                metric_name="Days Sales Outstanding",
                metric_type=MetricType.EFFICIENCY,
                value=round(dso, 1),
                unit="days",
                description="Average days to collect receivables",
                benchmark=benchmark,
                status=status,
                trend=self._calculate_trend(data.get('historical_dso', [dso]))
            )
            
        except Exception as e:
            logger.error(f"DSO calculation error: {e}")
            raise ValueError(f"Failed to calculate DSO: {e}")
    
    def calculate_customer_lifetime_value(self, data: Dict[str, Any]) -> FinancialMetric:
        """Calculate Customer Lifetime Value (CLV)"""
        try:
            avg_order_value = data.get('avg_order_value', 0)
            purchase_frequency = data.get('purchase_frequency', 0)
            customer_lifespan = data.get('customer_lifespan_months', 12)
            gross_margin = data.get('gross_margin', 0.3)
            
            clv = avg_order_value * purchase_frequency * (customer_lifespan / 12) * gross_margin
            
            # Status based on customer acquisition cost
            customer_acquisition_cost = data.get('customer_acquisition_cost', 0)
            clv_cac_ratio = clv / customer_acquisition_cost if customer_acquisition_cost > 0 else float('inf')
            
            if clv_cac_ratio >= 3.0:
                status = "good"
            elif clv_cac_ratio >= 1.5:
                status = "warning" 
            else:
                status = "critical"
            
            return FinancialMetric(
                metric_name="Customer Lifetime Value",
                metric_type=MetricType.PROFITABILITY,
                value=round(clv, 2),
                unit="KES",
                description="Total revenue expected from a customer",
                benchmark=customer_acquisition_cost * 3 if customer_acquisition_cost > 0 else None,
                status=status,
                trend=self._calculate_trend(data.get('historical_clv', [clv]))
            )
            
        except Exception as e:
            logger.error(f"CLV calculation error: {e}")
            raise ValueError(f"Failed to calculate CLV: {e}")
    
    def calculate_payment_success_rate(self, transactions: List[Dict[str, Any]]) -> FinancialMetric:
        """Calculate payment success rate analytics"""
        try:
            if not transactions:
                return FinancialMetric(
                    metric_name="Payment Success Rate",
                    metric_type=MetricType.EFFICIENCY,
                    value=0,
                    unit="%",
                    description="Percentage of successful payments",
                    status="critical"
                )
            
            successful_payments = sum(1 for t in transactions if t.get('status') == 'completed')
            total_payments = len(transactions)
            success_rate = (successful_payments / total_payments) * 100
            
            if success_rate >= 95:
                status = "good"
            elif success_rate >= 85:
                status = "warning"
            else:
                status = "critical"
            
            return FinancialMetric(
                metric_name="Payment Success Rate",
                metric_type=MetricType.EFFICIENCY,
                value=round(success_rate, 1),
                unit="%",
                description="Percentage of successful payments",
                benchmark=95.0,
                status=status
            )
            
        except Exception as e:
            logger.error(f"Payment success rate calculation error: {e}")
            raise ValueError(f"Failed to calculate payment success rate: {e}")
    
    def _calculate_trend(self, historical_values: List[float]) -> str:
        """Calculate trend from historical values"""
        if len(historical_values) < 2:
            return "stable"
        
        recent_avg = np.mean(historical_values[-3:]) if len(historical_values) >= 3 else historical_values[-1]
        older_avg = np.mean(historical_values[:-3]) if len(historical_values) >= 6 else historical_values[0]
        
        change_percent = ((recent_avg - older_avg) / older_avg) * 100 if older_avg != 0 else 0
        
        if change_percent > 5:
            return "improving"
        elif change_percent < -5:
            return "declining"
        else:
            return "stable"
    
    def generate_comprehensive_metrics(self, business_data: Dict[str, Any]) -> Dict[str, FinancialMetric]:
        """Generate all financial metrics"""
        try:
            metrics = {}
            
            # Cash Conversion Cycle
            if all(key in business_data for key in ['inventory_days', 'receivables_days', 'payables_days']):
                metrics['cash_conversion_cycle'] = self.calculate_cash_conversion_cycle(business_data)
            
            # Days Sales Outstanding
            if all(key in business_data for key in ['accounts_receivable', 'total_sales']):
                metrics['days_sales_outstanding'] = self.calculate_days_sales_outstanding(business_data)
            
            # Customer Lifetime Value
            if all(key in business_data for key in ['avg_order_value', 'purchase_frequency']):
                metrics['customer_lifetime_value'] = self.calculate_customer_lifetime_value(business_data)
            
            # Payment Success Rate
            if 'transactions' in business_data:
                metrics['payment_success_rate'] = self.calculate_payment_success_rate(business_data['transactions'])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Comprehensive metrics error: {e}")
            raise ValueError(f"Failed to generate comprehensive metrics: {e}")

class ComparativeAnalysisService:
    """Service for comparative financial analysis"""
    
    def __init__(self):
        self.supported_comparisons = [
            'month_over_month',
            'year_over_year', 
            'quarter_over_quarter',
            'industry_benchmark',
            'seasonal_pattern'
        ]
    
    def month_over_month_analysis(self, current_data: Dict, previous_data: Dict) -> Dict[str, Any]:
        """Calculate month-over-month changes"""
        try:
            analysis = {}
            
            for metric in ['revenue', 'expenses', 'net_income', 'cash_flow']:
                current_value = current_data.get(metric, 0)
                previous_value = previous_data.get(metric, 0)
                
                if previous_value != 0:
                    change_percent = ((current_value - previous_value) / previous_value) * 100
                    change_amount = current_value - previous_value
                else:
                    change_percent = 0 if current_value == 0 else 100
                    change_amount = current_value
                
                analysis[metric] = {
                    'current_value': current_value,
                    'previous_value': previous_value,
                    'change_amount': change_amount,
                    'change_percent': round(change_percent, 2),
                    'trend': 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable'
                }
            
            return {
                'analysis_type': 'month_over_month',
                'metrics': analysis,
                'summary': self._generate_summary(analysis)
            }
            
        except Exception as e:
            logger.error(f"Month-over-month analysis error: {e}")
            raise ValueError(f"Failed to perform month-over-month analysis: {e}")
    
    def year_over_year_growth(self, current_year_data: List[Dict], previous_year_data: List[Dict]) -> Dict[str, Any]:
        """Calculate year-over-year growth patterns"""
        try:
            current_total = sum(item.get('amount', 0) for item in current_year_data)
            previous_total = sum(item.get('amount', 0) for item in previous_year_data)
            
            if previous_total != 0:
                growth_rate = ((current_total - previous_total) / previous_total) * 100
            else:
                growth_rate = 100 if current_total > 0 else 0
            
            # Monthly breakdown
            monthly_analysis = []
            current_monthly = self._group_by_month(current_year_data)
            previous_monthly = self._group_by_month(previous_year_data)
            
            for month in range(1, 13):
                current_month_total = sum(current_monthly.get(month, []))
                previous_month_total = sum(previous_monthly.get(month, []))
                
                if previous_month_total != 0:
                    month_growth = ((current_month_total - previous_month_total) / previous_month_total) * 100
                else:
                    month_growth = 100 if current_month_total > 0 else 0
                
                monthly_analysis.append({
                    'month': month,
                    'current_amount': current_month_total,
                    'previous_amount': previous_month_total,
                    'growth_rate': round(month_growth, 2)
                })
            
            return {
                'analysis_type': 'year_over_year',
                'overall_growth_rate': round(growth_rate, 2),
                'current_year_total': current_total,
                'previous_year_total': previous_total,
                'monthly_breakdown': monthly_analysis,
                'trend_assessment': self._assess_growth_trend(growth_rate)
            }
            
        except Exception as e:
            logger.error(f"Year-over-year analysis error: {e}")
            raise ValueError(f"Failed to perform year-over-year analysis: {e}")
    
    def seasonal_pattern_analysis(self, historical_data: List[Dict], years: int = 2) -> Dict[str, Any]:
        """Identify seasonal patterns in financial data"""
        try:
            monthly_patterns = {}
            quarterly_patterns = {}
            
            # Group data by month and quarter
            for item in historical_data:
                date = pd.to_datetime(item.get('date', datetime.now()))
                month = date.month
                quarter = (month - 1) // 3 + 1
                amount = item.get('amount', 0)
                
                if month not in monthly_patterns:
                    monthly_patterns[month] = []
                monthly_patterns[month].append(amount)
                
                if quarter not in quarterly_patterns:
                    quarterly_patterns[quarter] = []
                quarterly_patterns[quarter].append(amount)
            
            # Calculate averages and seasonality indices
            monthly_analysis = {}
            overall_monthly_avg = np.mean([np.mean(amounts) for amounts in monthly_patterns.values()])
            
            for month, amounts in monthly_patterns.items():
                avg_amount = np.mean(amounts)
                seasonality_index = (avg_amount / overall_monthly_avg) * 100 if overall_monthly_avg > 0 else 100
                
                monthly_analysis[month] = {
                    'average_amount': round(avg_amount, 2),
                    'seasonality_index': round(seasonality_index, 2),
                    'pattern': 'above_average' if seasonality_index > 110 else 'below_average' if seasonality_index < 90 else 'average'
                }
            
            # Quarterly analysis
            quarterly_analysis = {}
            overall_quarterly_avg = np.mean([np.mean(amounts) for amounts in quarterly_patterns.values()])
            
            for quarter, amounts in quarterly_patterns.items():
                avg_amount = np.mean(amounts)
                seasonality_index = (avg_amount / overall_quarterly_avg) * 100 if overall_quarterly_avg > 0 else 100
                
                quarterly_analysis[quarter] = {
                    'average_amount': round(avg_amount, 2),
                    'seasonality_index': round(seasonality_index, 2),
                    'pattern': 'peak' if seasonality_index > 120 else 'trough' if seasonality_index < 80 else 'normal'
                }
            
            return {
                'analysis_type': 'seasonal_patterns',
                'monthly_patterns': monthly_analysis,
                'quarterly_patterns': quarterly_analysis,
                'peak_months': [month for month, data in monthly_analysis.items() if data['pattern'] == 'above_average'],
                'low_months': [month for month, data in monthly_analysis.items() if data['pattern'] == 'below_average'],
                'recommendations': self._generate_seasonal_recommendations(monthly_analysis, quarterly_analysis)
            }
            
        except Exception as e:
            logger.error(f"Seasonal pattern analysis error: {e}")
            raise ValueError(f"Failed to perform seasonal pattern analysis: {e}")
    
    def industry_benchmark_comparison(self, business_metrics: Dict[str, float], industry: str) -> Dict[str, Any]:
        """Compare business metrics against industry benchmarks"""
        try:
            # Industry benchmark data (mock - would come from external sources)
            benchmarks = {
                'retail': {
                    'gross_margin': 25.0,
                    'net_margin': 3.5,
                    'inventory_turnover': 8.0,
                    'receivables_turnover': 12.0
                },
                'manufacturing': {
                    'gross_margin': 35.0,
                    'net_margin': 8.0,
                    'inventory_turnover': 6.0,
                    'receivables_turnover': 8.0
                },
                'services': {
                    'gross_margin': 60.0,
                    'net_margin': 15.0,
                    'inventory_turnover': None,
                    'receivables_turnover': 12.0
                }
            }
            
            industry_benchmarks = benchmarks.get(industry, benchmarks['services'])
            comparison_results = {}
            
            for metric, business_value in business_metrics.items():
                benchmark_value = industry_benchmarks.get(metric)
                
                if benchmark_value is not None:
                    variance = ((business_value - benchmark_value) / benchmark_value) * 100
                    
                    if abs(variance) <= 10:
                        performance = 'on_par'
                    elif variance > 10:
                        performance = 'above_benchmark'
                    else:
                        performance = 'below_benchmark'
                    
                    comparison_results[metric] = {
                        'business_value': business_value,
                        'industry_benchmark': benchmark_value,
                        'variance_percent': round(variance, 2),
                        'performance': performance
                    }
            
            return {
                'analysis_type': 'industry_benchmark',
                'industry': industry,
                'comparison_results': comparison_results,
                'overall_assessment': self._assess_overall_performance(comparison_results)
            }
            
        except Exception as e:
            logger.error(f"Industry benchmark comparison error: {e}")
            raise ValueError(f"Failed to perform industry benchmark comparison: {e}")
    
    def _group_by_month(self, data: List[Dict]) -> Dict[int, List[float]]:
        """Group data by month"""
        monthly_data = {}
        for item in data:
            date = pd.to_datetime(item.get('date', datetime.now()))
            month = date.month
            amount = item.get('amount', 0)
            
            if month not in monthly_data:
                monthly_data[month] = []
            monthly_data[month].append(amount)
        
        return monthly_data
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary from analysis data"""
        positive_trends = sum(1 for metric in analysis.values() if metric.get('trend') == 'up')
        negative_trends = sum(1 for metric in analysis.values() if metric.get('trend') == 'down')
        
        return {
            'positive_trends': positive_trends,
            'negative_trends': negative_trends,
            'overall_direction': 'positive' if positive_trends > negative_trends else 'negative' if negative_trends > positive_trends else 'mixed'
        }
    
    def _assess_growth_trend(self, growth_rate: float) -> str:
        """Assess growth trend based on growth rate"""
        if growth_rate > 20:
            return 'high_growth'
        elif growth_rate > 5:
            return 'moderate_growth'
        elif growth_rate > -5:
            return 'stable'
        else:
            return 'declining'
    
    def _generate_seasonal_recommendations(self, monthly_analysis: Dict, quarterly_analysis: Dict) -> List[str]:
        """Generate recommendations based on seasonal patterns"""
        recommendations = []
        
        peak_months = [month for month, data in monthly_analysis.items() if data['pattern'] == 'above_average']
        low_months = [month for month, data in monthly_analysis.items() if data['pattern'] == 'below_average']
        
        if peak_months:
            recommendations.append(f"Peak performance months: {', '.join(map(str, peak_months))}. Consider increasing inventory and staffing.")
        
        if low_months:
            recommendations.append(f"Low performance months: {', '.join(map(str, low_months))}. Plan cost reduction strategies.")
        
        return recommendations
    
    def _assess_overall_performance(self, comparison_results: Dict) -> str:
        """Assess overall performance against benchmarks"""
        above_benchmark = sum(1 for result in comparison_results.values() if result['performance'] == 'above_benchmark')
        below_benchmark = sum(1 for result in comparison_results.values() if result['performance'] == 'below_benchmark')
        
        if above_benchmark > below_benchmark:
            return 'outperforming'
        elif below_benchmark > above_benchmark:
            return 'underperforming'
        else:
            return 'competitive'