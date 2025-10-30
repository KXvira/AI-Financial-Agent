"""
Alerts API Router  
Intelligent alert system endpoints for managing financial alerts
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

# Import alert services
from .system import AlertService, AlertType, AlertPriority, AlertStatus, NotificationChannel

logger = logging.getLogger(__name__)

class AlertsRouter:
    """Alerts API endpoints using simple HTTP handler approach"""
    
    def __init__(self):
        self.alert_service = AlertService()
        
        # Sample financial data for alert checking
        self.sample_financial_data = {
            'cash_flow': {
                'current_balance': 8500,  # Low balance to trigger alerts
                'predicted_balance_30d': 3200
            },
            'invoices': [
                {
                    'id': 'inv_001',
                    'amount': 15000,
                    'due_date': (datetime.now() - timedelta(days=15)).isoformat(),
                    'status': 'pending',
                    'customer_name': 'ABC Company'
                },
                {
                    'id': 'inv_002', 
                    'amount': 8500,
                    'due_date': (datetime.now() - timedelta(days=8)).isoformat(),
                    'status': 'pending',
                    'customer_name': 'XYZ Corp'
                }
            ],
            'transactions': [
                {'id': 'tx_001', 'amount': 25000, 'created_at': datetime.now().isoformat(), 'description': 'Large payment'},
                {'id': 'tx_002', 'amount': 1200, 'created_at': (datetime.now() - timedelta(hours=1)).isoformat(), 'description': 'Normal payment'},
                {'id': 'tx_003', 'amount': 800, 'created_at': (datetime.now() - timedelta(hours=2)).isoformat(), 'description': 'Small payment'}
            ],
            'transaction_stats': {
                'avg_amount': 5000,
                'daily_frequency': 3
            }
        }
    
    def handle_request(self, method: str, path: str, data: Dict = None) -> Dict[str, Any]:
        """Handle alerts API requests"""
        try:
            if method == "POST" and path == "/api/alerts/rules":
                return self.create_alert_rule(data or {})
            elif method == "GET" and path == "/api/alerts/rules":
                return self.get_alert_rules(data or {})
            elif method == "POST" and path == "/api/alerts/check":
                return self.check_alerts(data or {})
            elif method == "GET" and path == "/api/alerts":
                return self.get_user_alerts(data or {})
            elif method == "PUT" and path.startswith("/api/alerts/") and path.endswith("/acknowledge"):
                alert_id = path.split("/")[-2]
                return self.acknowledge_alert(alert_id, data or {})
            elif method == "PUT" and path.startswith("/api/alerts/") and path.endswith("/resolve"):
                alert_id = path.split("/")[-2]
                return self.resolve_alert(alert_id, data or {})
            elif method == "GET" and path == "/api/alerts/health":
                return self.health_check()
            else:
                return {"error": "Endpoint not found", "status": 404}
                
        except Exception as e:
            logger.error(f"Alerts request error: {e}")
            return {"error": f"Request failed: {str(e)}", "status": 500}
    
    def create_alert_rule(self, data: Dict) -> Dict[str, Any]:
        """
        Create a new alert rule
        
        Expected data:
        - alert_type: Type of alert (cash_flow_low, overdue_invoice, etc.)
        - conditions: Alert conditions and thresholds
        - priority: Alert priority (low/medium/high/critical)
        - channels: Notification channels (email/sms/in_app/push)
        - frequency_limit_hours: Minimum hours between alerts (default: 24)
        - user_id: User creating the rule
        """
        try:
            required_fields = ['alert_type', 'user_id']
            for field in required_fields:
                if field not in data:
                    return {'error': f"Missing required field: {field}", 'status': 400}
            
            # Validate alert type
            try:
                AlertType(data['alert_type'])
            except ValueError:
                return {'error': f"Invalid alert type: {data['alert_type']}", 'status': 400}
            
            # Create alert rule
            rule_id = self.alert_service.create_alert_rule(data['user_id'], data)
            
            return {
                'success': True,
                'rule_id': rule_id,
                'message': 'Alert rule created successfully',
                'rule_config': {
                    'alert_type': data['alert_type'],
                    'priority': data.get('priority', 'medium'),
                    'channels': data.get('channels', ['in_app']),
                    'frequency_limit_hours': data.get('frequency_limit_hours', 24)
                }
            }
            
        except Exception as e:
            logger.error(f"Alert rule creation error: {e}")
            return {'error': f"Failed to create alert rule: {str(e)}", 'status': 500}
    
    def get_alert_rules(self, params: Dict) -> Dict[str, Any]:
        """
        Get alert rules for a user
        
        Query parameters:
        - user_id: User ID to get rules for
        """
        try:
            user_id = params.get('user_id')
            if not user_id:
                return {'error': 'Missing user_id parameter', 'status': 400}
            
            rules = self.alert_service.get_user_rules(user_id)
            
            rules_data = []
            for rule in rules:
                rules_data.append({
                    'rule_id': rule.rule_id,
                    'alert_type': rule.alert_type.value,
                    'priority': rule.priority.value,
                    'channels': [ch.value for ch in rule.channels],
                    'conditions': rule.conditions,
                    'is_active': rule.is_active,
                    'frequency_limit_hours': rule.frequency_limit,
                    'created_at': rule.created_at.isoformat(),
                    'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                })
            
            return {
                'success': True,
                'rules': rules_data,
                'total_rules': len(rules_data),
                'active_rules': sum(1 for rule in rules if rule.is_active)
            }
            
        except Exception as e:
            logger.error(f"Get alert rules error: {e}")
            return {'error': f"Failed to get alert rules: {str(e)}", 'status': 500}
    
    def check_alerts(self, data: Dict) -> Dict[str, Any]:
        """
        Check all alert conditions for a user
        
        Expected data:
        - user_id: User ID to check alerts for
        - financial_data: Optional financial data (uses sample if not provided)
        """
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {'error': 'Missing user_id', 'status': 400}
            
            # Use provided financial data or sample data
            financial_data = data.get('financial_data', self.sample_financial_data)
            
            # Check all alerts
            triggered_alerts = self.alert_service.check_all_alerts(user_id, financial_data)
            
            # Format alert response
            alerts_data = []
            for alert in triggered_alerts:
                alerts_data.append({
                    'alert_id': alert.alert_id,
                    'rule_id': alert.rule_id,
                    'alert_type': alert.alert_type.value,
                    'priority': alert.priority.value,
                    'title': alert.title,
                    'message': alert.message,
                    'data': alert.data,
                    'channels': [ch.value for ch in alert.channels],
                    'status': alert.status.value,
                    'created_at': alert.created_at.isoformat()
                })
            
            return {
                'success': True,
                'alerts_triggered': len(triggered_alerts),
                'alerts': alerts_data,
                'check_summary': {
                    'cash_flow_alerts': sum(1 for a in triggered_alerts if a.alert_type == AlertType.CASH_FLOW_LOW),
                    'invoice_alerts': sum(1 for a in triggered_alerts if a.alert_type == AlertType.OVERDUE_INVOICE),
                    'transaction_alerts': sum(1 for a in triggered_alerts if a.alert_type == AlertType.UNUSUAL_TRANSACTION),
                    'critical_alerts': sum(1 for a in triggered_alerts if a.priority == AlertPriority.CRITICAL)
                },
                'checked_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Alert checking error: {e}")
            return {'error': f"Failed to check alerts: {str(e)}", 'status': 500}
    
    def get_user_alerts(self, params: Dict) -> Dict[str, Any]:
        """
        Get alerts for a user
        
        Query parameters:
        - user_id: User ID
        - status: Optional status filter (pending/sent/acknowledged/resolved)
        - limit: Maximum number of alerts to return (default: 50)
        """
        try:
            user_id = params.get('user_id')
            if not user_id:
                return {'error': 'Missing user_id parameter', 'status': 400}
            
            # Parse status filter
            status_filter = None
            if 'status' in params:
                try:
                    status_filter = AlertStatus(params['status'])
                except ValueError:
                    return {'error': f"Invalid status: {params['status']}", 'status': 400}
            
            # Get alerts
            alerts = self.alert_service.get_user_alerts(user_id, status_filter)
            limit = int(params.get('limit', 50))
            alerts = alerts[:limit]
            
            # Format alerts
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    'alert_id': alert.alert_id,
                    'rule_id': alert.rule_id,
                    'alert_type': alert.alert_type.value,
                    'priority': alert.priority.value,
                    'title': alert.title,
                    'message': alert.message,
                    'data': alert.data,
                    'status': alert.status.value,
                    'created_at': alert.created_at.isoformat(),
                    'sent_at': alert.sent_at.isoformat() if alert.sent_at else None,
                    'acknowledged_at': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                    'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
                })
            
            return {
                'success': True,
                'alerts': alerts_data,
                'total_returned': len(alerts_data),
                'status_filter': params.get('status', 'all'),
                'retrieved_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Get user alerts error: {e}")
            return {'error': f"Failed to get alerts: {str(e)}", 'status': 500}
    
    def acknowledge_alert(self, alert_id: str, data: Dict) -> Dict[str, Any]:
        """
        Acknowledge an alert
        
        Expected data:
        - user_id: User acknowledging the alert
        """
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {'error': 'Missing user_id', 'status': 400}
            
            success = self.alert_service.acknowledge_alert(alert_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Alert acknowledged successfully',
                    'alert_id': alert_id,
                    'acknowledged_at': datetime.now().isoformat()
                }
            else:
                return {'error': 'Alert not found or access denied', 'status': 404}
            
        except Exception as e:
            logger.error(f"Alert acknowledgment error: {e}")
            return {'error': f"Failed to acknowledge alert: {str(e)}", 'status': 500}
    
    def resolve_alert(self, alert_id: str, data: Dict) -> Dict[str, Any]:
        """
        Resolve an alert
        
        Expected data:
        - user_id: User resolving the alert
        """
        try:
            user_id = data.get('user_id')
            if not user_id:
                return {'error': 'Missing user_id', 'status': 400}
            
            success = self.alert_service.resolve_alert(alert_id, user_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Alert resolved successfully',
                    'alert_id': alert_id,
                    'resolved_at': datetime.now().isoformat()
                }
            else:
                return {'error': 'Alert not found or access denied', 'status': 404}
            
        except Exception as e:
            logger.error(f"Alert resolution error: {e}")
            return {'error': f"Failed to resolve alert: {str(e)}", 'status': 500}
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for alerts service"""
        try:
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'services': {
                    'alert_service': 'operational',
                    'notification_engine': 'operational',
                    'cash_flow_monitor': 'operational',
                    'invoice_monitor': 'operational',
                    'transaction_monitor': 'operational'
                },
                'supported_alert_types': [at.value for at in AlertType],
                'supported_priorities': [ap.value for ap in AlertPriority],
                'supported_channels': [nc.value for nc in NotificationChannel],
                'available_endpoints': [
                    'POST /api/alerts/rules - Create alert rule',
                    'GET /api/alerts/rules - Get user rules',
                    'POST /api/alerts/check - Check alert conditions',
                    'GET /api/alerts - Get user alerts',
                    'PUT /api/alerts/{id}/acknowledge - Acknowledge alert',
                    'PUT /api/alerts/{id}/resolve - Resolve alert'
                ],
                'stats': {
                    'total_rules': len(self.alert_service.rule_storage),
                    'total_alerts': len(self.alert_service.alert_storage)
                }
            }
            
        except Exception as e:
            logger.error(f"Alerts health check error: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Create global router instance
alerts_router = AlertsRouter()