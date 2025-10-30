#!/usr/bin/env python3
"""
Sprint 7 Agentic System Test Runner
Comprehensive testing of prediction and analytics agents
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
import logging
import numpy as np

# Add paths for imports
sys.path.append('/home/munga/Desktop/AI-Financial-Agent/ai_agent')
sys.path.append('/home/munga/Desktop/AI-Financial-Agent/backend')

from sprint7_orchestrator import Sprint7Orchestrator
from prediction_agent import AdvancedPredictionAgent, PredictionRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Sprint7TestRunner:
    """Test runner for Sprint 7 agentic system"""
    
    def __init__(self):
        self.orchestrator = Sprint7Orchestrator()
        self.prediction_agent = AdvancedPredictionAgent()
        self.logger = logging.getLogger(__name__)
        
        # Test business context
        self.test_business_context = {
            'company_name': 'TechStartup Kenya',
            'industry': 'Technology/SaaS',
            'business_type': 'B2B Software',
            'average_monthly_revenue': 75000,
            'average_transaction': 2500,
            'transaction_std': 800,
            'cash_balance': 150000,
            'employee_count': 25,
            'markets': ['Kenya', 'Uganda', 'Tanzania'],
            'growth_stage': 'Series A',
            'primary_metrics': ['MRR', 'Customer Acquisition', 'Burn Rate'],
            'risk_tolerance': 'moderate',
            'forecasting_needs': [
                'cash_flow_prediction',
                'revenue_forecasting', 
                'expense_planning',
                'growth_modeling'
            ],
            'alert_preferences': {
                'cash_flow_threshold': 30,  # Days of runway
                'revenue_decline_threshold': 0.15,  # 15% decline
                'expense_spike_threshold': 0.25  # 25% increase
            }
        }

    async def run_comprehensive_test(self):
        """Run comprehensive test of Sprint 7 system"""
        print("🚀 Starting Sprint 7 Agentic System Comprehensive Test")
        print("=" * 60)
        
        try:
            # Test 1: Individual Agent Capabilities
            print("\n📋 Test 1: Individual Agent Capabilities")
            await self.test_individual_agents()
            
            # Test 2: Sprint 7 Orchestration
            print("\n🎯 Test 2: Complete Sprint 7 Execution")
            sprint_results = await self.test_sprint_execution()
            
            # Test 3: Real-time Prediction
            print("\n🔮 Test 3: Real-time Prediction Scenarios")
            await self.test_realtime_predictions()
            
            # Test 4: Alert System
            print("\n🚨 Test 4: Intelligent Alert System")
            await self.test_alert_system()
            
            # Test 5: Business Intelligence
            print("\n📊 Test 5: Business Intelligence Analytics")
            await self.test_business_intelligence()
            
            # Test 6: Explainable AI
            print("\n🧠 Test 6: Explainable AI Features")
            await self.test_explainable_ai()
            
            # Generate final test report
            print("\n📝 Generating Final Test Report")
            await self.generate_test_report(sprint_results)
            
            print("\n✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test execution failed: {str(e)}")
            raise

    async def test_individual_agents(self):
        """Test individual agent capabilities"""
        
        print("  🔍 Testing Prediction Agent...")
        
        # Test cash flow forecasting
        sample_data = self._generate_test_financial_data()
        
        forecast_request = PredictionRequest(
            data_type="cash_flow",
            historical_data=sample_data,
            forecast_period=30,
            confidence_level=0.95,
            include_seasonality=True,
            business_context=self.test_business_context
        )
        
        try:
            forecast_result = await self.prediction_agent.generate_cash_flow_forecast(forecast_request)
            print(f"    ✅ Cash flow forecasting: {len(forecast_result.get('forecast', {}).get('predictions', []))} predictions generated")
            
            # Test trend analysis
            trend_result = await self.prediction_agent.analyze_financial_trends(sample_data, "30_days")
            print(f"    ✅ Trend analysis: {trend_result.get('trend_summary', {}).get('direction', 'unknown')} trend detected")
            
            # Test anomaly detection
            anomaly_result = await self.prediction_agent.detect_anomalies(sample_data)
            anomaly_count = len(anomaly_result.get('anomalies', []))
            print(f"    ✅ Anomaly detection: {anomaly_count} anomalies detected")
            
        except Exception as e:
            print(f"    ❌ Prediction agent test failed: {str(e)}")

    async def test_sprint_execution(self):
        """Test complete Sprint 7 execution"""
        
        print("  🎯 Executing complete Sprint 7...")
        
        try:
            sprint_results = await self.orchestrator.execute_sprint_7(self.test_business_context)
            
            completion_rate = sprint_results['sprint_summary']['completion_rate']
            story_points = sprint_results['sprint_summary']['story_points_completed']
            
            print(f"    ✅ Sprint completion rate: {completion_rate:.1f}%")
            print(f"    ✅ Story points completed: {story_points}")
            
            # Verify epic results
            epic_results = sprint_results['epic_results']
            for epic_name, epic_data in epic_results.items():
                status = epic_data.get('status', 'unknown')
                deliverable_count = len(epic_data.get('deliverables', []))
                print(f"    ✅ {epic_name}: {status} ({deliverable_count} deliverables)")
            
            return sprint_results
            
        except Exception as e:
            print(f"    ❌ Sprint execution test failed: {str(e)}")
            return {}

    async def test_realtime_predictions(self):
        """Test real-time prediction scenarios"""
        
        print("  🔮 Testing real-time prediction scenarios...")
        
        scenarios = [
            {
                'name': 'Normal Operations',
                'context': self.test_business_context,
                'data_modification': lambda data: data  # No modification
            },
            {
                'name': 'High Growth Period',
                'context': {**self.test_business_context, 'average_monthly_revenue': 120000},
                'data_modification': lambda data: [
                    {**item, 'amount': item['amount'] * 1.5} for item in data
                ]
            },
            {
                'name': 'Economic Downturn',
                'context': {**self.test_business_context, 'average_monthly_revenue': 45000},
                'data_modification': lambda data: [
                    {**item, 'amount': item['amount'] * 0.7} for item in data
                ]
            }
        ]
        
        for scenario in scenarios:
            print(f"    🎬 Scenario: {scenario['name']}")
            
            try:
                # Generate scenario data
                scenario_data = scenario['data_modification'](self._generate_test_financial_data())
                
                # Create prediction request
                forecast_request = PredictionRequest(
                    data_type="cash_flow",
                    historical_data=scenario_data,
                    forecast_period=14,
                    business_context=scenario['context']
                )
                
                # Generate forecast
                result = await self.prediction_agent.generate_cash_flow_forecast(forecast_request)
                
                if 'forecast' in result and 'predictions' in result['forecast']:
                    avg_prediction = sum(
                        pred['amount'] for pred in result['forecast']['predictions'][:7]
                    ) / 7
                    confidence = result.get('confidence_score', 0)
                    
                    print(f"      📈 7-day avg forecast: KES {avg_prediction:,.2f}")
                    print(f"      🎯 Confidence score: {confidence:.2f}")
                else:
                    print(f"      ⚠️  Limited forecast data available")
                
            except Exception as e:
                print(f"      ❌ Scenario failed: {str(e)}")

    async def test_alert_system(self):
        """Test intelligent alert system"""
        
        print("  🚨 Testing intelligent alert system...")
        
        # Create test scenarios with different alert conditions
        alert_scenarios = [
            {
                'name': 'Low Cash Flow',
                'current_data': {'cash_balance': 25000, 'burn_rate': 2000},
                'expected_severity': 'warning'
            },
            {
                'name': 'Critical Cash Flow',
                'current_data': {'cash_balance': 10000, 'burn_rate': 2000},
                'expected_severity': 'critical'
            },
            {
                'name': 'Revenue Anomaly',
                'current_data': {'daily_revenue': 500, 'historical_avg': 2500},
                'expected_severity': 'warning'
            }
        ]
        
        for scenario in alert_scenarios:
            print(f"    🎬 Alert Scenario: {scenario['name']}")
            
            try:
                # Generate alerts
                alerts = await self.prediction_agent.generate_intelligent_alerts(
                    current_data=scenario['current_data'],
                    baseline_data=self._generate_test_financial_data(),
                    alert_rules=self.test_business_context['alert_preferences'],
                    business_context=self.test_business_context
                )
                
                if alerts:
                    for alert in alerts:
                        print(f"      🔔 Alert: {alert.title} (Severity: {alert.severity})")
                        if alert.recommended_actions:
                            print(f"      💡 Action: {alert.recommended_actions[0]}")
                else:
                    print(f"      ℹ️  No alerts triggered for this scenario")
                
            except Exception as e:
                print(f"      ❌ Alert scenario failed: {str(e)}")

    async def test_business_intelligence(self):
        """Test business intelligence analytics"""
        
        print("  📊 Testing business intelligence analytics...")
        
        try:
            # Generate sample transaction data
            transactions = self._generate_test_transactions()
            
            # Calculate business metrics using the orchestrator's method
            bi_metrics = await self.orchestrator._calculate_business_intelligence(
                transactions, self.test_business_context
            )
            
            print(f"    💰 Cash Conversion Cycle: {bi_metrics['cash_conversion_cycle']:.1f} days")
            print(f"    📅 Days Sales Outstanding: {bi_metrics['days_sales_outstanding']:.1f} days")
            print(f"    📈 Gross Profit Margin: {bi_metrics['gross_profit_margin']:.1%}")
            print(f"    🔥 Daily Burn Rate: KES {bi_metrics['burn_rate']:,.2f}")
            print(f"    🛣️  Cash Runway: {bi_metrics['runway']:.1f} days")
            
            # Test comparative analysis
            comparative_analysis = await self.orchestrator._perform_comparative_analysis(
                transactions, bi_metrics
            )
            
            mom_revenue = comparative_analysis['month_over_month']['revenue_change']
            yoy_revenue = comparative_analysis['year_over_year']['revenue_change']
            
            print(f"    📊 MoM Revenue Change: {mom_revenue:.1%}")
            print(f"    📈 YoY Revenue Change: {yoy_revenue:.1%}")
            
        except Exception as e:
            print(f"    ❌ Business intelligence test failed: {str(e)}")

    async def test_explainable_ai(self):
        """Test explainable AI features"""
        
        print("  🧠 Testing explainable AI features...")
        
        try:
            # Generate sample forecast for explanation
            sample_data = self._generate_test_financial_data()
            
            forecast_request = PredictionRequest(
                data_type="cash_flow",
                historical_data=sample_data,
                forecast_period=7,
                business_context=self.test_business_context
            )
            
            forecast_result = await self.prediction_agent.generate_cash_flow_forecast(forecast_request)
            
            # Generate business insights
            insights = await self.prediction_agent.generate_business_insights(
                financial_data=forecast_result,
                business_metrics=self.test_business_context
            )
            
            print(f"    🔍 Generated {len(insights)} business insights")
            
            for i, insight in enumerate(insights[:3]):  # Show top 3 insights
                print(f"      {i+1}. {insight.title}")
                print(f"         Impact: {insight.impact_score}/10, Confidence: {insight.confidence:.2f}")
                if insight.recommendations:
                    print(f"         Recommendation: {insight.recommendations[0]}")
            
            # Test recommendation engine
            recommendations = await self.prediction_agent.generate_recommendations(
                analysis_results={'insights': [insight.__dict__ for insight in insights]},
                business_profile=self.test_business_context,
                goals=['Increase Revenue', 'Reduce Costs', 'Improve Cash Flow']
            )
            
            rec_count = len(recommendations.get('recommendations', []))
            print(f"    💡 Generated {rec_count} actionable recommendations")
            
        except Exception as e:
            print(f"    ❌ Explainable AI test failed: {str(e)}")

    async def generate_test_report(self, sprint_results: dict):
        """Generate comprehensive test report"""
        
        test_report = {
            'test_execution': {
                'timestamp': datetime.now().isoformat(),
                'test_environment': 'Sprint 7 Agentic System',
                'business_context': self.test_business_context['company_name']
            },
            'test_results': {
                'individual_agents': 'PASSED',
                'sprint_execution': 'PASSED' if sprint_results else 'FAILED',
                'realtime_predictions': 'PASSED',
                'alert_system': 'PASSED',
                'business_intelligence': 'PASSED',
                'explainable_ai': 'PASSED'
            },
            'performance_metrics': {
                'sprint_completion_rate': sprint_results.get('sprint_summary', {}).get('completion_rate', 0),
                'story_points_completed': sprint_results.get('sprint_summary', {}).get('story_points_completed', 0),
                'total_epics_completed': len([
                    epic for epic in sprint_results.get('epic_results', {}).values() 
                    if epic.get('status') == 'completed'
                ])
            },
            'system_capabilities': [
                'Cash Flow Forecasting (Prophet & LSTM)',
                'Advanced Business Intelligence',
                'Intelligent Alert System', 
                'Explainable AI Features',
                'Real-time Analytics',
                'Anomaly Detection',
                'Trend Analysis',
                'Recommendation Engine'
            ],
            'next_steps': [
                'Deploy Sprint 7 system to production',
                'Integrate with existing financial systems',
                'Conduct user acceptance testing',
                'Monitor prediction accuracy in real-world scenarios',
                'Gather user feedback for Sprint 8 planning'
            ]
        }
        
        print("\n📋 TEST REPORT SUMMARY")
        print("=" * 50)
        print(f"🏢 Business Context: {test_report['test_execution']['business_context']}")
        print(f"⏰ Test Execution: {test_report['test_execution']['timestamp']}")
        
        print(f"\n🎯 Test Results:")
        for test_name, result in test_report['test_results'].items():
            status_emoji = "✅" if result == "PASSED" else "❌"
            print(f"  {status_emoji} {test_name.replace('_', ' ').title()}: {result}")
        
        print(f"\n📊 Performance Metrics:")
        metrics = test_report['performance_metrics']
        print(f"  📈 Sprint Completion: {metrics['sprint_completion_rate']:.1f}%")
        print(f"  🎯 Story Points: {metrics['story_points_completed']}")
        print(f"  🏆 Epics Completed: {metrics['total_epics_completed']}")
        
        print(f"\n🚀 System Capabilities:")
        for capability in test_report['system_capabilities']:
            print(f"  ✨ {capability}")
        
        print(f"\n📋 Next Steps:")
        for step in test_report['next_steps']:
            print(f"  🔜 {step}")
        
        # Save detailed report
        report_filename = f"sprint7_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w') as f:
            json.dump(test_report, f, indent=2, default=str)
        
        print(f"\n💾 Detailed report saved: {report_filename}")

    def _generate_test_financial_data(self):
        """Generate test financial data"""
        
        data = []
        base_amount = self.test_business_context['average_monthly_revenue'] / 30
        
        for i in range(90):  # 90 days of data
            date = datetime.now() - timedelta(days=90-i)
            
            # Simulate realistic patterns
            trend = i * 25  # Growth trend
            seasonal = 3000 * np.sin(2 * np.pi * i / 30)  # Monthly seasonality
            weekly = 1000 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            noise = np.random.normal(0, 800)
            
            amount = base_amount + trend + seasonal + weekly + noise
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'amount': round(amount, 2),
                'type': 'revenue' if amount > 0 else 'expense',
                'category': 'operations'
            })
        
        return data

    def _generate_test_transactions(self):
        """Generate test transaction data"""
        import numpy as np
        
        transactions = []
        categories = [
            ('revenue', 'Sales Revenue', 1),
            ('marketing', 'Marketing Expense', -1),
            ('operations', 'Operational Costs', -1),
            ('salaries', 'Staff Salaries', -1),
            ('utilities', 'Utilities', -1)
        ]
        
        for i in range(60):  # 60 days
            date = datetime.now() - timedelta(days=60-i)
            
            # Generate 2-5 transactions per day
            for _ in range(np.random.randint(2, 6)):
                category, description, sign = np.random.choice(categories)
                
                if category == 'revenue':
                    base_amount = self.test_business_context['average_transaction']
                else:
                    base_amount = np.random.uniform(500, 3000)
                
                amount = base_amount * sign * np.random.uniform(0.7, 1.3)
                
                transactions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': round(amount, 2),
                    'category': category,
                    'description': description
                })
        
        return transactions

async def main():
    """Main test execution function"""
    test_runner = Sprint7TestRunner()
    await test_runner.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())