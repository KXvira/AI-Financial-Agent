"""
Explainable AI Service using SHAP-like feature importance
Provides interpretable explanations for AI decisions
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class FeatureImportance:
    """Individual feature importance result"""
    
    def __init__(self, feature_name: str, importance: float, contribution: float, description: str):
        self.feature_name = feature_name
        self.importance = importance  # 0-1 scale
        self.contribution = contribution  # Positive or negative contribution
        self.description = description

class Explanation:
    """Complete explanation for a prediction or decision"""
    
    def __init__(self, explanation_id: str, model_type: str, prediction_value: float):
        self.explanation_id = explanation_id
        self.model_type = model_type
        self.prediction_value = prediction_value
        self.feature_importances: List[FeatureImportance] = []
        self.natural_language_explanation = ""
        self.confidence_score = 0.0
        self.created_at = datetime.now()
    
    def add_feature_importance(self, feature: FeatureImportance):
        """Add feature importance to explanation"""
        self.feature_importances.append(feature)
    
    def generate_natural_language(self) -> str:
        """Generate human-readable explanation"""
        if not self.feature_importances:
            return "No feature importance data available."
        
        # Sort by absolute importance
        sorted_features = sorted(
            self.feature_importances, 
            key=lambda x: abs(x.importance), 
            reverse=True
        )
        
        explanation_parts = []
        
        # Main prediction statement
        if self.model_type == "cash_flow_forecast":
            explanation_parts.append(f"The predicted cash flow of KES {self.prediction_value:,.2f} is based on the following key factors:")
        elif self.model_type == "expense_category":
            explanation_parts.append(f"This expense was categorized with {self.confidence_score*100:.1f}% confidence based on:")
        else:
            explanation_parts.append(f"This prediction of {self.prediction_value} is primarily influenced by:")
        
        # Top 3 most important features
        for i, feature in enumerate(sorted_features[:3], 1):
            impact = "increases" if feature.contribution > 0 else "decreases"
            explanation_parts.append(
                f"{i}. {feature.description} ({impact} prediction by {abs(feature.contribution):.1%})"
            )
        
        # Additional context
        if len(sorted_features) > 3:
            explanation_parts.append(f"Plus {len(sorted_features) - 3} other factors with smaller influences.")
        
        self.natural_language_explanation = " ".join(explanation_parts)
        return self.natural_language_explanation

class CashFlowExplainer:
    """Explainer for cash flow predictions"""
    
    def __init__(self):
        self.feature_definitions = {
            'seasonal_pattern': 'Historical seasonal trends in your business',
            'recent_transactions': 'Recent transaction patterns and volumes',
            'invoice_aging': 'Outstanding invoices and payment expectations', 
            'expense_patterns': 'Regular expense obligations and patterns',
            'day_of_week': 'Day of week effects on cash flow',
            'month_trend': 'Monthly business cycle patterns',
            'payment_delays': 'Historical customer payment delays',
            'economic_indicators': 'External economic factors affecting business'
        }
    
    def explain_prediction(self, prediction_data: Dict[str, Any]) -> Explanation:
        """Generate explanation for cash flow prediction"""
        try:
            explanation = Explanation(
                explanation_id=f"cf_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_type="cash_flow_forecast",
                prediction_value=prediction_data.get('predicted_amount', 0)
            )
            
            # Mock feature importance calculation (would use actual SHAP values)
            base_amount = prediction_data.get('base_amount', 0)
            seasonal_factor = prediction_data.get('seasonal_factor', 0)
            trend_component = prediction_data.get('trend_component', 0)
            
            # Calculate feature importances
            features = [
                FeatureImportance(
                    'seasonal_pattern',
                    abs(seasonal_factor) / max(abs(base_amount), 1) if base_amount != 0 else 0,
                    seasonal_factor / max(abs(base_amount), 1) if base_amount != 0 else 0,
                    self.feature_definitions['seasonal_pattern']
                ),
                FeatureImportance(
                    'recent_transactions',
                    0.7,  # Mock importance
                    0.15,  # Mock contribution
                    self.feature_definitions['recent_transactions']
                ),
                FeatureImportance(
                    'invoice_aging',
                    0.4,
                    -0.08,
                    self.feature_definitions['invoice_aging']
                ),
                FeatureImportance(
                    'expense_patterns',
                    0.3,
                    -0.12,
                    self.feature_definitions['expense_patterns']
                )
            ]
            
            for feature in features:
                explanation.add_feature_importance(feature)
            
            explanation.confidence_score = 0.85  # Mock confidence
            explanation.generate_natural_language()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Cash flow explanation error: {e}")
            raise ValueError(f"Failed to generate cash flow explanation: {e}")

class ExpenseCategoryExplainer:
    """Explainer for expense categorization decisions"""
    
    def __init__(self):
        self.feature_definitions = {
            'vendor_name': 'Merchant or vendor name recognition',
            'transaction_amount': 'Transaction amount patterns for categories',
            'description_keywords': 'Keywords in transaction description',
            'time_patterns': 'Timing patterns typical for category',
            'location_data': 'Transaction location or merchant type',
            'historical_patterns': 'Your historical categorization patterns'
        }
    
    def explain_categorization(self, categorization_data: Dict[str, Any]) -> Explanation:
        """Generate explanation for expense categorization"""
        try:
            explanation = Explanation(
                explanation_id=f"cat_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_type="expense_category",
                prediction_value=0  # Not applicable for categorization
            )
            
            category = categorization_data.get('predicted_category', 'Unknown')
            confidence = categorization_data.get('confidence', 0.5)
            vendor = categorization_data.get('vendor', '')
            description = categorization_data.get('description', '')
            amount = categorization_data.get('amount', 0)
            
            # Mock feature importance for categorization
            features = []
            
            # Vendor name importance
            if vendor:
                vendor_importance = min(0.8, len(vendor) / 20)  # Mock calculation
                features.append(FeatureImportance(
                    'vendor_name',
                    vendor_importance,
                    confidence * 0.4,
                    f"Vendor '{vendor}' strongly indicates {category} category"
                ))
            
            # Description keywords
            if description:
                keyword_importance = min(0.6, len(description.split()) / 10)
                features.append(FeatureImportance(
                    'description_keywords',
                    keyword_importance,
                    confidence * 0.3,
                    f"Transaction description contains {category}-related keywords"
                ))
            
            # Amount patterns
            amount_importance = 0.4  # Mock
            features.append(FeatureImportance(
                'transaction_amount',
                amount_importance,
                confidence * 0.2,
                f"Amount of KES {amount:,.2f} is typical for {category} expenses"
            ))
            
            # Historical patterns
            features.append(FeatureImportance(
                'historical_patterns',
                0.5,
                confidence * 0.1,
                f"Your past transactions show similar patterns for {category}"
            ))
            
            for feature in features:
                explanation.add_feature_importance(feature)
            
            explanation.confidence_score = confidence
            explanation.generate_natural_language()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Categorization explanation error: {e}")
            raise ValueError(f"Failed to generate categorization explanation: {e}")

class AlertExplainer:
    """Explainer for alert generation decisions"""
    
    def __init__(self):
        self.alert_logic = {
            'cash_flow_low': 'Balance fell below configured threshold',
            'overdue_invoice': 'Invoice exceeded payment grace period',
            'unusual_transaction': 'Transaction pattern deviated from normal',
            'budget_variance': 'Spending exceeded budget allocation'
        }
    
    def explain_alert(self, alert_data: Dict[str, Any]) -> Explanation:
        """Generate explanation for why an alert was triggered"""
        try:
            explanation = Explanation(
                explanation_id=f"alert_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_type="alert_system",
                prediction_value=0  # Not applicable for alerts
            )
            
            alert_type = alert_data.get('alert_type', 'unknown')
            threshold_value = alert_data.get('threshold', 0)
            actual_value = alert_data.get('actual_value', 0)
            
            # Create feature importance for alert logic
            features = []
            
            if alert_type == 'cash_flow_low':
                features.append(FeatureImportance(
                    'balance_threshold',
                    1.0,
                    1.0,
                    f"Current balance (KES {actual_value:,.2f}) is below your threshold (KES {threshold_value:,.2f})"
                ))
                
                # Add trend analysis if available
                trend = alert_data.get('trend', 'stable')
                if trend == 'declining':
                    features.append(FeatureImportance(
                        'negative_trend',
                        0.8,
                        0.3,
                        "Balance has been declining over recent periods"
                    ))
            
            elif alert_type == 'overdue_invoice':
                days_overdue = alert_data.get('days_overdue', 0)
                features.append(FeatureImportance(
                    'payment_delay',
                    1.0,
                    1.0,
                    f"Invoice is {days_overdue} days past due date"
                ))
                
                customer_history = alert_data.get('customer_payment_history', 'unknown')
                if customer_history == 'poor':
                    features.append(FeatureImportance(
                        'customer_history',
                        0.6,
                        0.2,
                        "Customer has history of late payments"
                    ))
            
            for feature in features:
                explanation.add_feature_importance(feature)
            
            explanation.confidence_score = 0.95  # High confidence for rule-based alerts
            explanation.generate_natural_language()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Alert explanation error: {e}")
            raise ValueError(f"Failed to generate alert explanation: {e}")

class RecommendationExplainer:
    """Explainer for business recommendations"""
    
    def explain_recommendation(self, recommendation_data: Dict[str, Any]) -> Explanation:
        """Generate explanation for business recommendations"""
        try:
            explanation = Explanation(
                explanation_id=f"rec_exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                model_type="recommendation_system",
                prediction_value=0
            )
            
            rec_type = recommendation_data.get('type', 'general')
            impact_score = recommendation_data.get('impact_score', 0.5)
            
            features = []
            
            if rec_type == 'cost_reduction':
                features.append(FeatureImportance(
                    'expense_analysis',
                    0.9,
                    impact_score,
                    f"Analysis shows potential savings of {impact_score*100:.1f}% in identified areas"
                ))
                
                high_cost_categories = recommendation_data.get('high_cost_categories', [])
                if high_cost_categories:
                    features.append(FeatureImportance(
                        'category_analysis',
                        0.7,
                        0.3,
                        f"Categories {', '.join(high_cost_categories)} show above-average spending"
                    ))
            
            elif rec_type == 'cash_flow_improvement':
                features.append(FeatureImportance(
                    'payment_terms',
                    0.8,
                    impact_score * 0.6,
                    "Optimizing payment terms could improve cash flow timing"
                ))
                
                features.append(FeatureImportance(
                    'invoice_collection',
                    0.6,
                    impact_score * 0.4,
                    "Faster invoice collection would reduce cash flow gaps"
                ))
            
            for feature in features:
                explanation.add_feature_importance(feature)
            
            explanation.confidence_score = min(0.9, impact_score + 0.2)
            explanation.generate_natural_language()
            
            return explanation
            
        except Exception as e:
            logger.error(f"Recommendation explanation error: {e}")
            raise ValueError(f"Failed to generate recommendation explanation: {e}")

class ExplainableAIService:
    """Main service for generating AI explanations"""
    
    def __init__(self):
        self.cash_flow_explainer = CashFlowExplainer()
        self.category_explainer = ExpenseCategoryExplainer()
        self.alert_explainer = AlertExplainer()
        self.recommendation_explainer = RecommendationExplainer()
        self.explanation_storage = {}  # Would be database in production
    
    def explain_prediction(self, prediction_type: str, prediction_data: Dict[str, Any]) -> Explanation:
        """Generate explanation for any type of prediction"""
        try:
            if prediction_type == 'cash_flow_forecast':
                explanation = self.cash_flow_explainer.explain_prediction(prediction_data)
            elif prediction_type == 'expense_category':
                explanation = self.category_explainer.explain_categorization(prediction_data)
            elif prediction_type == 'alert':
                explanation = self.alert_explainer.explain_alert(prediction_data)
            elif prediction_type == 'recommendation':
                explanation = self.recommendation_explainer.explain_recommendation(prediction_data)
            else:
                raise ValueError(f"Unsupported prediction type: {prediction_type}")
            
            # Store explanation
            self.explanation_storage[explanation.explanation_id] = explanation
            
            return explanation
            
        except Exception as e:
            logger.error(f"Prediction explanation error: {e}")
            raise ValueError(f"Failed to generate explanation: {e}")
    
    def get_explanation(self, explanation_id: str) -> Optional[Explanation]:
        """Retrieve stored explanation"""
        return self.explanation_storage.get(explanation_id)
    
    def generate_feature_importance_summary(self, explanations: List[Explanation]) -> Dict[str, Any]:
        """Generate summary of feature importance across multiple explanations"""
        try:
            feature_summary = {}
            total_explanations = len(explanations)
            
            if total_explanations == 0:
                return {'error': 'No explanations provided'}
            
            # Aggregate feature importances
            for explanation in explanations:
                for feature in explanation.feature_importances:
                    if feature.feature_name not in feature_summary:
                        feature_summary[feature.feature_name] = {
                            'total_importance': 0,
                            'avg_contribution': 0,
                            'frequency': 0,
                            'description': feature.description
                        }
                    
                    feature_summary[feature.feature_name]['total_importance'] += feature.importance
                    feature_summary[feature.feature_name]['avg_contribution'] += feature.contribution
                    feature_summary[feature.feature_name]['frequency'] += 1
            
            # Calculate averages
            for feature_name, data in feature_summary.items():
                data['avg_importance'] = data['total_importance'] / data['frequency']
                data['avg_contribution'] = data['avg_contribution'] / data['frequency']
                data['usage_frequency'] = (data['frequency'] / total_explanations) * 100
            
            # Sort by average importance
            sorted_features = sorted(
                feature_summary.items(),
                key=lambda x: x[1]['avg_importance'],
                reverse=True
            )
            
            return {
                'total_explanations_analyzed': total_explanations,
                'top_features': dict(sorted_features[:10]),
                'feature_insights': self._generate_feature_insights(sorted_features)
            }
            
        except Exception as e:
            logger.error(f"Feature importance summary error: {e}")
            raise ValueError(f"Failed to generate feature importance summary: {e}")
    
    def _generate_feature_insights(self, sorted_features: List[Tuple[str, Dict]]) -> List[str]:
        """Generate insights from feature importance analysis"""
        insights = []
        
        if not sorted_features:
            return ["No feature data available for analysis."]
        
        # Most important feature
        top_feature = sorted_features[0]
        insights.append(
            f"'{top_feature[0]}' is consistently the most important factor in predictions "
            f"(avg importance: {top_feature[1]['avg_importance']:.2f})"
        )
        
        # High frequency features
        frequent_features = [
            name for name, data in sorted_features 
            if data['usage_frequency'] > 80
        ]
        
        if frequent_features:
            insights.append(
                f"Features used in >80% of predictions: {', '.join(frequent_features[:3])}"
            )
        
        # Positive vs negative contributors
        positive_contributors = sum(1 for _, data in sorted_features if data['avg_contribution'] > 0)
        negative_contributors = sum(1 for _, data in sorted_features if data['avg_contribution'] < 0)
        
        insights.append(
            f"Feature impact distribution: {positive_contributors} positive contributors, "
            f"{negative_contributors} negative contributors"
        )
        
        return insights