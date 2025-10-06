"""
Analytics API Router
Advanced business intelligence and comparative analysis endpoints
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Import analytics services
from .business_intelligence import BusinessIntelligenceService, ComparativeAnalysisService

logger = logging.getLogger(__name__)

class AnalyticsRouter:
    """Analytics API endpoints using simple HTTP handler approach"""
    
    def __init__(self):
        self.bi_service = BusinessIntelligenceService()
        self.comparative_service = ComparativeAnalysisService()
        
        # Sample business data for demonstration
        self.sample_data = {
            'accounts_receivable': 45000,
            'total_sales': 180000,
            'inventory_days': 25,
            'receivables_days': 28,
            'payables_days': 15,
            'avg_order_value': 1200,
            'purchase_frequency': 2.5,
            'customer_lifespan_months': 18,
            'gross_margin': 0.35,
            'customer_acquisition_cost': 300,
            'industry': 'retail',
            'transactions': [
                {'status': 'completed', 'amount': 1500},
                {'status': 'completed', 'amount': 800},
                {'status': 'failed', 'amount': 200},
                {'status': 'completed', 'amount': 2200},
                {'status': 'completed', 'amount': 950}
            ]
        }
    
    def handle_request(self, method: str, path: str, data: Dict = None) -> Dict[str, Any]:
        """Handle analytics API requests"""
        try:
            if method == "GET" and path == "/api/analytics/metrics":
                return self.get_business_metrics(data or {})
            elif method == "POST" and path == "/api/analytics/compare-periods":
                return self.compare_periods(data or {})
            elif method == "GET" and path == "/api/analytics/seasonal-patterns":
                return self.get_seasonal_patterns(data or {})
            elif method == "POST" and path == "/api/analytics/industry-benchmark":
                return self.compare_industry_benchmark(data or {})
            elif method == "GET" and path == "/api/analytics/health":
                return self.health_check()
            else:
                return {"error": "Endpoint not found", "status": 404}
                
        except Exception as e:
            logger.error(f"Analytics request error: {e}")
            return {"error": f"Request failed: {str(e)}", "status": 500}
    
    def get_business_metrics(self, params: Dict = None) -> Dict[str, Any]:
        """
        Get comprehensive business intelligence metrics
        
        Query parameters:
        - industry: Business industry (retail/manufacturing/services)
        - include_trends: Include trend analysis (default: true)
        """
        try:
            # Use sample data or provided data
            business_data = {**self.sample_data, **(params.get('business_data', {}))}
            
            # Generate comprehensive metrics
            metrics = self.bi_service.generate_comprehensive_metrics(business_data)
            
            # Format response
            metrics_response = {}
            for metric_name, metric_obj in metrics.items():
                metrics_response[metric_name] = {
                    'value': metric_obj.value,
                    'unit': metric_obj.unit,
                    'description': metric_obj.description,
                    'status': metric_obj.status,
                    'benchmark': metric_obj.benchmark,
                    'trend': metric_obj.trend,
                    'metric_type': metric_obj.metric_type.value
                }
            
            return {
                'success': True,
                'metrics': metrics_response,
                'industry': business_data.get('industry', 'unknown'),
                'analysis_date': datetime.now().isoformat(),
                'summary': {
                    'total_metrics': len(metrics),
                    'good_metrics': sum(1 for m in metrics.values() if m.status == 'good'),
                    'warning_metrics': sum(1 for m in metrics.values() if m.status == 'warning'),
                    'critical_metrics': sum(1 for m in metrics.values() if m.status == 'critical')
                }
            }
            
        except Exception as e:
            logger.error(f"Business metrics error: {e}")
            return {'error': f"Failed to generate metrics: {str(e)}", 'status': 500}
    
    def compare_periods(self, data: Dict) -> Dict[str, Any]:
        """
        Compare performance between time periods
        
        Expected data:
        - comparison_type: 'month_over_month' or 'year_over_year'
        - current_period: Current period data
        - previous_period: Previous period data (for MoM)
        - current_year: Current year data (for YoY)  
        - previous_year: Previous year data (for YoY)
        """
        try:
            comparison_type = data.get('comparison_type', 'month_over_month')
            
            if comparison_type == 'month_over_month':
                current_data = data.get('current_period', {
                    'revenue': 45000, 'expenses': 28000, 
                    'net_income': 17000, 'cash_flow': 15000
                })
                previous_data = data.get('previous_period', {
                    'revenue': 42000, 'expenses': 26000,
                    'net_income': 16000, 'cash_flow': 14000
                })
                
                analysis = self.comparative_service.month_over_month_analysis(current_data, previous_data)
                
            elif comparison_type == 'year_over_year':
                current_year = data.get('current_year', [
                    {'date': '2024-01-01', 'amount': 15000},
                    {'date': '2024-02-01', 'amount': 18000},
                    {'date': '2024-03-01', 'amount': 22000}
                ])
                previous_year = data.get('previous_year', [
                    {'date': '2023-01-01', 'amount': 12000},
                    {'date': '2023-02-01', 'amount': 14000},
                    {'date': '2023-03-01', 'amount': 16000}
                ])
                
                analysis = self.comparative_service.year_over_year_growth(current_year, previous_year)
                
            else:
                return {'error': 'Invalid comparison type', 'status': 400}
            
            return {
                'success': True,
                'comparison_analysis': analysis,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Period comparison error: {e}")
            return {'error': f"Comparison failed: {str(e)}", 'status': 500}
    
    def get_seasonal_patterns(self, params: Dict = None) -> Dict[str, Any]:
        """
        Analyze seasonal patterns in financial data
        
        Query parameters:
        - years: Number of years to analyze (default: 2)
        - data_type: Type of data to analyze (revenue/expenses/all)
        """
        try:
            # Generate sample historical data
            years = params.get('years', 2)
            historical_data = []
            
            # Create sample data for seasonal analysis
            base_date = datetime(2023, 1, 1)
            for i in range(365 * years):
                date = base_date + timedelta(days=i)
                # Add seasonal variation
                seasonal_multiplier = 1 + 0.3 * (date.month - 6) / 6  # Peak in Dec/Jan
                base_amount = 10000 + (i % 30) * 500  # Monthly variation
                amount = base_amount * seasonal_multiplier
                
                historical_data.append({
                    'date': date.isoformat(),
                    'amount': amount
                })
            
            # Analyze patterns
            analysis = self.comparative_service.seasonal_pattern_analysis(historical_data, years)
            
            return {
                'success': True,
                'seasonal_analysis': analysis,
                'data_period': f'{years} years',
                'total_data_points': len(historical_data),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Seasonal analysis error: {e}")
            return {'error': f"Seasonal analysis failed: {str(e)}", 'status': 500}
    
    def compare_industry_benchmark(self, data: Dict) -> Dict[str, Any]:
        """
        Compare business metrics against industry benchmarks
        
        Expected data:
        - industry: Industry type (retail/manufacturing/services)
        - metrics: Business metrics to compare
        """
        try:
            industry = data.get('industry', 'services')
            business_metrics = data.get('metrics', {
                'gross_margin': 28.5,
                'net_margin': 8.2,
                'inventory_turnover': 7.5,
                'receivables_turnover': 10.2
            })
            
            comparison = self.comparative_service.industry_benchmark_comparison(
                business_metrics, industry
            )
            
            return {
                'success': True,
                'benchmark_comparison': comparison,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Benchmark comparison error: {e}")
            return {'error': f"Benchmark comparison failed: {str(e)}", 'status': 500}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for analytics service"""
        try:
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'business_intelligence': 'operational',
                    'comparative_analysis': 'operational',
                    'metrics_calculation': 'operational'
                },
                'available_endpoints': [
                    '/api/analytics/metrics',
                    '/api/analytics/compare-periods',
                    '/api/analytics/seasonal-patterns',
                    '/api/analytics/industry-benchmark'
                ],
                'supported_industries': ['retail', 'manufacturing', 'services'],
                'supported_comparisons': [
                    'month_over_month',
                    'year_over_year',
                    'seasonal_patterns',
                    'industry_benchmark'
                ]
            }
            
        except Exception as e:
            logger.error(f"Analytics health check error: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Create global router instance
analytics_router = AnalyticsRouter()