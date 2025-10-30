"""
Mock Gemini Service for Sprint 7 Testing
Provides simulated AI responses for demonstration purposes
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List

class MockGeminiService:
    """Mock Gemini service for testing Sprint 7 agents"""
    
    def __init__(self):
        self.call_count = 0
        
        # Mock response templates
        self.response_templates = {
            'cash_flow_forecasting': self._mock_cash_flow_response,
            'trend_analysis': self._mock_trend_analysis_response,
            'anomaly_detection': self._mock_anomaly_detection_response,
            'alert_generation': self._mock_alert_generation_response,
            'insight_generation': self._mock_insight_generation_response,
            'recommendation_engine': self._mock_recommendation_response,
            'task_assignment': self._mock_task_assignment_response,
            'integration_testing': self._mock_integration_response
        }

    async def generate_content(self, prompt: str) -> str:
        """Generate mock AI content based on prompt analysis"""
        self.call_count += 1
        
        # Analyze prompt to determine response type
        response_type = self._analyze_prompt_type(prompt)
        
        # Generate appropriate mock response
        if response_type in self.response_templates:
            response_data = self.response_templates[response_type](prompt)
        else:
            response_data = self._default_mock_response(prompt)
        
        return json.dumps(response_data, indent=2)

    def _analyze_prompt_type(self, prompt: str) -> str:
        """Analyze prompt to determine expected response type"""
        prompt_lower = prompt.lower()
        
        if 'cash flow' in prompt_lower and 'forecast' in prompt_lower:
            return 'cash_flow_forecasting'
        elif 'trend analysis' in prompt_lower:
            return 'trend_analysis'
        elif 'anomal' in prompt_lower:
            return 'anomaly_detection'
        elif 'alert' in prompt_lower:
            return 'alert_generation'
        elif 'insight' in prompt_lower:
            return 'insight_generation'
        elif 'recommendation' in prompt_lower:
            return 'recommendation_engine'
        elif 'task' in prompt_lower and 'assign' in prompt_lower:
            return 'task_assignment'
        elif 'integration' in prompt_lower:
            return 'integration_testing'
        else:
            return 'default'

    def _mock_cash_flow_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock cash flow forecasting response"""
        # Extract forecast period from prompt
        forecast_days = 30  # Default
        if 'forecast_period' in prompt:
            try:
                import re
                match = re.search(r'forecast_period.*?(\d+)', prompt)
                if match:
                    forecast_days = int(match.group(1))
            except:
                pass
        
        # Generate realistic predictions
        predictions = []
        base_amount = random.uniform(2000, 5000)
        
        for i in range(min(forecast_days, 30)):
            date = (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d')
            
            # Simulate trend and seasonality
            trend = i * random.uniform(10, 50)
            seasonal = 1000 * random.uniform(-0.3, 0.3)
            noise = random.uniform(-500, 500)
            
            amount = base_amount + trend + seasonal + noise
            confidence = max(0.6, 0.95 - (i * 0.01))
            
            predictions.append({
                "date": date,
                "amount": round(amount, 2),
                "confidence": round(confidence, 3),
                "trend_component": round(trend, 2),
                "seasonal_component": round(seasonal, 2)
            })
        
        return {
            "forecast": {
                "predictions": predictions,
                "trend": random.choice(["increasing", "decreasing", "stable"]),
                "seasonal_pattern": "Monthly revenue cycles with weekly fluctuations",
                "growth_rate": round(random.uniform(-0.05, 0.15), 3)
            },
            "risks": [
                {
                    "type": "market_volatility",
                    "probability": round(random.uniform(0.2, 0.8), 2),
                    "impact": random.choice(["low", "medium", "high"])
                },
                {
                    "type": "cash_flow_gap",
                    "probability": round(random.uniform(0.1, 0.4), 2),
                    "impact": "medium"
                }
            ],
            "insights": [
                {
                    "title": "Revenue Growth Pattern",
                    "description": "Consistent growth trajectory with seasonal variations",
                    "impact": random.randint(6, 9)
                },
                {
                    "title": "Cash Flow Stability",
                    "description": "Strong cash position with manageable fluctuations", 
                    "impact": random.randint(7, 10)
                }
            ],
            "recommendations": [
                "Maintain cash reserves for seasonal variations",
                "Consider invoice payment term optimization",
                "Monitor weekly cash flow patterns closely"
            ],
            "confidence_score": round(random.uniform(0.75, 0.95), 2)
        }

    def _mock_trend_analysis_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock trend analysis response"""
        return {
            "trend_summary": {
                "direction": random.choice(["upward", "downward", "stable", "volatile"]),
                "strength": round(random.uniform(0.3, 0.9), 2),
                "volatility": round(random.uniform(0.1, 0.6), 2),
                "consistency": round(random.uniform(0.5, 0.95), 2)
            },
            "statistical_analysis": {
                "mean": round(random.uniform(2000, 8000), 2),
                "median": round(random.uniform(1800, 7500), 2),
                "std_dev": round(random.uniform(500, 2000), 2),
                "coefficient_of_variation": round(random.uniform(0.15, 0.45), 3)
            },
            "patterns": [
                {
                    "type": "seasonal",
                    "description": "Monthly revenue cycles",
                    "frequency": "monthly"
                },
                {
                    "type": "weekly",
                    "description": "End-of-week payment patterns",
                    "frequency": "weekly"
                }
            ],
            "insights": [
                {
                    "category": "growth", 
                    "finding": "Consistent month-over-month growth",
                    "significance": round(random.uniform(0.6, 0.9), 2)
                },
                {
                    "category": "efficiency",
                    "finding": "Improved collection cycles",
                    "significance": round(random.uniform(0.5, 0.8), 2)
                }
            ],
            "recommendations": [
                "Continue monitoring growth trajectory",
                "Optimize payment collection processes",
                "Implement predictive cash flow management"
            ]
        }

    def _mock_anomaly_detection_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock anomaly detection response"""
        # Generate random anomalies
        anomalies = []
        num_anomalies = random.randint(0, 3)
        
        for i in range(num_anomalies):
            date = (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d')
            anomalies.append({
                "date": date,
                "value": round(random.uniform(500, 15000), 2),
                "expected_range": [
                    round(random.uniform(2000, 4000), 2),
                    round(random.uniform(6000, 8000), 2)
                ],
                "severity": random.choice(["low", "medium", "high"]),
                "type": random.choice(["outlier", "pattern_break", "trend_change"]),
                "description": f"Unusual transaction pattern detected on {date}",
                "potential_causes": [
                    random.choice([
                        "Large customer payment",
                        "Seasonal variation", 
                        "One-time expense",
                        "Data collection error"
                    ])
                ],
                "business_impact": random.choice([
                    "Positive cash flow impact",
                    "Neutral - likely normal variation",
                    "Requires investigation"
                ])
            })
        
        severity_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for anomaly in anomalies:
            severity_dist[anomaly["severity"]] += 1
        
        return {
            "anomalies": anomalies,
            "summary": {
                "total_anomalies": len(anomalies),
                "severity_distribution": severity_dist,
                "most_affected_periods": [
                    "End of month periods",
                    "Holiday seasons"
                ] if anomalies else [],
                "overall_health_score": round(random.uniform(7.0, 9.5), 1)
            },
            "recommendations": [
                {
                    "priority": "high",
                    "action": "Investigate high-severity anomalies",
                    "rationale": "Unusual patterns may indicate opportunities or risks",
                    "expected_outcome": "Improved financial predictability"
                },
                {
                    "priority": "medium", 
                    "action": "Enhance monitoring for pattern detection",
                    "rationale": "Early detection prevents issues",
                    "expected_outcome": "Proactive financial management"
                }
            ]
        }

    def _mock_alert_generation_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock alert generation response"""
        # Generate sample alerts based on prompt context
        alerts = []
        alert_types = [
            ("info", "Cash Flow Update", "Regular cash flow monitoring update"),
            ("warning", "Low Cash Alert", "Cash balance below 30-day threshold"), 
            ("critical", "Revenue Decline", "Significant revenue decrease detected"),
            ("warning", "Expense Spike", "Unusual expense pattern identified")
        ]
        
        num_alerts = random.randint(1, 3)
        selected_alerts = random.sample(alert_types, min(num_alerts, len(alert_types)))
        
        for severity, title, description in selected_alerts:
            alert_id = f"alert_{datetime.now().timestamp()}_{random.randint(1000, 9999)}"
            
            alerts.append({
                "id": alert_id,
                "severity": severity,
                "category": random.choice(["cash_flow", "expense", "revenue", "compliance"]),
                "title": title,
                "description": description,
                "trigger_conditions": {
                    "threshold_exceeded": True,
                    "timeframe": "24_hours",
                    "confidence": round(random.uniform(0.7, 0.95), 2)
                },
                "business_impact": {
                    "financial": f"Potential {random.choice(['positive', 'negative', 'neutral'])} impact",
                    "operational": "Requires management attention",
                    "risk_level": severity
                },
                "recommended_actions": [
                    {
                        "action": f"Review {title.lower()} details",
                        "priority": "immediate" if severity == "critical" else "normal",
                        "timeline": "Within 24 hours",
                        "responsible": "Finance Team"
                    }
                ],
                "escalation_rules": {
                    "if_not_resolved": "Escalate to management",
                    "escalate_to": "Finance Director",
                    "escalation_time": "48 hours"
                }
            })
        
        critical_count = sum(1 for alert in alerts if alert["severity"] == "critical")
        
        return {
            "alerts": alerts,
            "summary": {
                "total_alerts": len(alerts),
                "critical_count": critical_count,
                "requires_immediate_action": critical_count,
                "overall_system_health": "critical" if critical_count > 0 else "warning" if len(alerts) > 1 else "healthy"
            }
        }

    def _mock_insight_generation_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock business insights response"""
        insights = [
            {
                "category": "performance",
                "title": "Revenue Growth Acceleration", 
                "description": "Monthly recurring revenue shows 15% growth trajectory",
                "supporting_data": {"growth_rate": 0.15, "confidence": 0.87},
                "confidence_level": round(random.uniform(0.8, 0.95), 2),
                "impact_score": random.randint(7, 10),
                "timeframe": "short_term",
                "recommendations": [
                    {
                        "action": "Increase marketing spend to capitalize on growth",
                        "expected_benefit": "Accelerated customer acquisition",
                        "implementation_effort": "medium",
                        "timeline": "30 days"
                    }
                ]
            },
            {
                "category": "efficiency",
                "title": "Cash Collection Optimization",
                "description": "Days Sales Outstanding can be reduced by 8 days",
                "supporting_data": {"current_dso": 32.1, "target_dso": 24.0},
                "confidence_level": round(random.uniform(0.75, 0.9), 2),
                "impact_score": random.randint(6, 9),
                "timeframe": "medium_term",
                "recommendations": [
                    {
                        "action": "Implement automated invoice follow-up",
                        "expected_benefit": "Improved cash flow by KES 50,000/month",
                        "implementation_effort": "low",
                        "timeline": "14 days"
                    }
                ]
            },
            {
                "category": "risk",
                "title": "Expense Management Opportunity",
                "description": "Operating expenses growing faster than revenue",
                "supporting_data": {"expense_growth": 0.12, "revenue_growth": 0.08},
                "confidence_level": round(random.uniform(0.7, 0.85), 2),
                "impact_score": random.randint(5, 8),
                "timeframe": "immediate",
                "recommendations": [
                    {
                        "action": "Conduct expense audit and optimization",
                        "expected_benefit": "10-15% expense reduction",
                        "implementation_effort": "high",
                        "timeline": "60 days"
                    }
                ]
            }
        ]
        
        return {
            "insights": insights,
            "key_metrics": {
                "revenue_growth": round(random.uniform(0.05, 0.20), 3),
                "expense_efficiency": round(random.uniform(0.75, 0.95), 2),
                "cash_flow_stability": round(random.uniform(0.8, 0.95), 2),
                "profitability_trend": round(random.uniform(0.1, 0.25), 3)
            },
            "strategic_priorities": [
                {
                    "priority": "Accelerate revenue growth",
                    "rationale": "Strong market position and demand",
                    "success_metrics": ["Monthly recurring revenue", "Customer acquisition cost"],
                    "timeline": "90 days"
                },
                {
                    "priority": "Optimize operational efficiency",
                    "rationale": "Scale operations without proportional cost increase",
                    "success_metrics": ["Expense ratio", "Productivity metrics"],
                    "timeline": "180 days"
                }
            ]
        }

    def _mock_recommendation_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock recommendation engine response"""
        recommendations = [
            {
                "id": "rec_001",
                "category": "revenue_growth",
                "title": "Implement Dynamic Pricing Strategy",
                "description": "Optimize pricing based on demand patterns and customer segments",
                "rationale": "Data shows 20% pricing elasticity opportunity",
                "expected_impact": {
                    "financial": "15-25% revenue increase",
                    "operational": "Automated pricing decisions",
                    "timeline": "90 days"
                },
                "implementation": {
                    "steps": [
                        "Analyze current pricing vs market",
                        "Develop pricing algorithms",
                        "A/B test new pricing",
                        "Full implementation"
                    ],
                    "resources_needed": ["Data analyst", "Pricing software"],
                    "estimated_cost": "KES 150,000",
                    "implementation_time": "6 weeks",
                    "success_metrics": ["Revenue per customer", "Market share"]
                },
                "priority_score": 8.5,
                "confidence_level": 0.82
            },
            {
                "id": "rec_002", 
                "category": "cost_optimization",
                "title": "Automate Invoice Processing",
                "description": "Implement AI-powered invoice processing and approval workflows",
                "rationale": "Manual processing costs KES 45 per invoice",
                "expected_impact": {
                    "financial": "65% processing cost reduction",
                    "operational": "2-hour faster processing time", 
                    "timeline": "45 days"
                },
                "implementation": {
                    "steps": [
                        "Select automation platform",
                        "Configure workflows",
                        "Train staff",
                        "Go live"
                    ],
                    "resources_needed": ["Automation software", "Training time"],
                    "estimated_cost": "KES 80,000",
                    "implementation_time": "4 weeks",
                    "success_metrics": ["Processing time", "Error rate", "Cost per invoice"]
                },
                "priority_score": 7.2,
                "confidence_level": 0.88
            }
        ]
        
        return {
            "recommendations": recommendations,
            "priority_matrix": {
                "quick_wins": ["rec_002"],
                "major_projects": ["rec_001"],
                "long_term_strategies": []
            },
            "implementation_roadmap": {
                "immediate": ["Begin automation platform evaluation"],
                "30_days": ["Start pricing analysis", "Implement invoice automation"],
                "90_days": ["Complete pricing strategy rollout"],
                "6_months": ["Evaluate results and optimize"]
            }
        }

    def _mock_task_assignment_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock task assignment response"""
        return {
            "task_assignments": {
                "PRED-001": "prediction_agent",
                "PRED-002": "prediction_agent",
                "PRED-003": "prediction_agent", 
                "ANALYTICS-001": "analytics_agent",
                "ANALYTICS-002": "analytics_agent",
                "ALERTS-001": "alert_agent",
                "EXPLAI-001": "prediction_agent"
            },
            "rationale": {
                "PRED-001": "Prophet model best suited for prediction agent's time-series expertise",
                "PRED-002": "LSTM implementation aligns with prediction agent's ML capabilities",
                "PRED-003": "Ensemble approach leverages prediction agent's model comparison skills",
                "ANALYTICS-001": "Business intelligence matches analytics agent's specialty",
                "ANALYTICS-002": "Comparative analysis fits analytics agent's reporting strength",
                "ALERTS-001": "Alert system design suited to alert agent's monitoring expertise", 
                "EXPLAI-001": "Explainable AI complements prediction agent's model transparency"
            },
            "execution_order": [
                "PRED-001", "ANALYTICS-001", "PRED-002",
                "ANALYTICS-002", "ALERTS-001", "PRED-003", "EXPLAI-001"
            ],
            "parallel_execution": [
                ["PRED-001", "ANALYTICS-001"],
                ["PRED-002", "ANALYTICS-002"], 
                ["ALERTS-001"],
                ["PRED-003", "EXPLAI-001"]
            ]
        }

    def _mock_integration_response(self, prompt: str) -> Dict[str, Any]:
        """Generate mock integration testing response"""
        return {
            "integration_tests": [
                {
                    "test_id": "api_endpoints",
                    "component": "forecasting_service",
                    "test_type": "api",
                    "description": "Test all forecasting API endpoints",
                    "expected_result": "200 OK responses with valid JSON",
                    "status": "pass"
                },
                {
                    "test_id": "data_flow_validation",
                    "component": "analytics_service", 
                    "test_type": "data_flow",
                    "description": "Validate data processing pipeline",
                    "expected_result": "Accurate metric calculations",
                    "status": "pass"
                },
                {
                    "test_id": "alert_system_performance",
                    "component": "alerts_service",
                    "test_type": "performance",
                    "description": "Test alert generation response time",
                    "expected_result": "< 500ms response time",
                    "status": "pass"
                }
            ],
            "system_health": {
                "forecasting_service": "operational",
                "analytics_service": "operational", 
                "alerts_service": "operational",
                "explainable_ai": "operational"
            },
            "performance_metrics": {
                "forecast_generation_time": "1,250ms",
                "analytics_calculation_time": "890ms", 
                "alert_processing_time": "340ms"
            },
            "readiness_score": f"{random.randint(85, 98)}%"
        }

    def _default_mock_response(self, prompt: str) -> Dict[str, Any]:
        """Generate default mock response"""
        return {
            "status": "success",
            "message": "Mock AI response generated",
            "analysis": "Comprehensive analysis completed using simulated AI intelligence",
            "recommendations": [
                "Continue system monitoring",
                "Review results and optimize",
                "Plan next development iteration"
            ],
            "confidence": round(random.uniform(0.75, 0.95), 2),
            "timestamp": datetime.now().isoformat()
        }

# Replace the real GeminiService with MockGeminiService for testing
GeminiService = MockGeminiService