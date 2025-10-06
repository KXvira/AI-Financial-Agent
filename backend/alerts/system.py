"""
Intelligent Alert System
Predictive alerts and notification engine for financial events
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class AlertType(str, Enum):
    """Types of financial alerts"""
    CASH_FLOW_LOW = "cash_flow_low"
    OVERDUE_INVOICE = "overdue_invoice"
    UNUSUAL_TRANSACTION = "unusual_transaction"
    PAYMENT_FAILURE = "payment_failure"
    BUDGET_VARIANCE = "budget_variance"
    PREDICTION_WARNING = "prediction_warning"
    SYSTEM_ALERT = "system_alert"

class AlertPriority(str, Enum):
    """Alert priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status"""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"

class NotificationChannel(str, Enum):
    """Notification channels"""
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"

class AlertRule:
    """Alert rule configuration"""
    
    def __init__(self, rule_id: str, rule_config: Dict[str, Any]):
        self.rule_id = rule_id
        self.alert_type = AlertType(rule_config['alert_type'])
        self.conditions = rule_config.get('conditions', {})
        self.priority = AlertPriority(rule_config.get('priority', AlertPriority.MEDIUM))
        self.channels = [NotificationChannel(ch) for ch in rule_config.get('channels', ['in_app'])]
        self.frequency_limit = rule_config.get('frequency_limit_hours', 24)
        self.is_active = rule_config.get('is_active', True)
        self.user_id = rule_config.get('user_id')
        self.created_at = datetime.now()
        self.last_triggered = None

class Alert:
    """Individual alert instance"""
    
    def __init__(self, alert_data: Dict[str, Any]):
        self.alert_id = alert_data.get('alert_id', f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.rule_id = alert_data['rule_id']
        self.user_id = alert_data['user_id']
        self.alert_type = AlertType(alert_data['alert_type'])
        self.priority = AlertPriority(alert_data.get('priority', AlertPriority.MEDIUM))
        self.title = alert_data['title']
        self.message = alert_data['message']
        self.data = alert_data.get('data', {})
        self.channels = [NotificationChannel(ch) for ch in alert_data.get('channels', ['in_app'])]
        self.status = AlertStatus.PENDING
        self.created_at = datetime.now()
        self.sent_at = None
        self.acknowledged_at = None
        self.resolved_at = None

class CashFlowMonitor:
    """Monitor cash flow and generate low balance alerts"""
    
    def __init__(self):
        self.default_thresholds = {
            'critical_balance': 10000,  # KES
            'warning_balance': 50000,   # KES
            'prediction_days': 30
        }
    
    def check_cash_flow_alerts(self, cash_data: Dict[str, Any], user_rules: List[AlertRule]) -> List[Alert]:
        """Check for cash flow related alerts"""
        alerts = []
        
        try:
            current_balance = cash_data.get('current_balance', 0)
            predicted_balance = cash_data.get('predicted_balance_30d', current_balance)
            
            for rule in user_rules:
                if rule.alert_type != AlertType.CASH_FLOW_LOW or not rule.is_active:
                    continue
                
                # Check if rule was recently triggered
                if self._is_recently_triggered(rule):
                    continue
                
                thresholds = {**self.default_thresholds, **rule.conditions}
                
                # Critical low balance
                if current_balance <= thresholds['critical_balance']:
                    alert = Alert({
                        'rule_id': rule.rule_id,
                        'user_id': rule.user_id,
                        'alert_type': AlertType.CASH_FLOW_LOW,
                        'priority': AlertPriority.CRITICAL,
                        'title': 'Critical: Low Cash Balance',
                        'message': f'Your current balance of KES {current_balance:,.2f} is critically low.',
                        'data': {
                            'current_balance': current_balance,
                            'threshold': thresholds['critical_balance'],
                            'recommended_action': 'Immediate cash injection required'
                        },
                        'channels': rule.channels
                    })
                    alerts.append(alert)
                
                # Warning low balance
                elif current_balance <= thresholds['warning_balance']:
                    alert = Alert({
                        'rule_id': rule.rule_id,
                        'user_id': rule.user_id,
                        'alert_type': AlertType.CASH_FLOW_LOW,
                        'priority': AlertPriority.HIGH,
                        'title': 'Warning: Low Cash Balance',
                        'message': f'Your current balance of KES {current_balance:,.2f} is below the warning threshold.',
                        'data': {
                            'current_balance': current_balance,
                            'threshold': thresholds['warning_balance'],
                            'recommended_action': 'Monitor cash flow closely'
                        },
                        'channels': rule.channels
                    })
                    alerts.append(alert)
                
                # Predicted low balance
                elif predicted_balance <= thresholds['critical_balance']:
                    alert = Alert({
                        'rule_id': rule.rule_id,
                        'user_id': rule.user_id,
                        'alert_type': AlertType.PREDICTION_WARNING,
                        'priority': AlertPriority.HIGH,
                        'title': 'Forecast: Predicted Low Balance',
                        'message': f'Your balance is predicted to drop to KES {predicted_balance:,.2f} within 30 days.',
                        'data': {
                            'current_balance': current_balance,
                            'predicted_balance': predicted_balance,
                            'prediction_days': thresholds['prediction_days'],
                            'recommended_action': 'Plan cash flow management'
                        },
                        'channels': rule.channels
                    })
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Cash flow alert check error: {e}")
            return []
    
    def _is_recently_triggered(self, rule: AlertRule) -> bool:
        """Check if rule was triggered recently based on frequency limit"""
        if rule.last_triggered is None:
            return False
        
        time_since_last = datetime.now() - rule.last_triggered
        return time_since_last.total_seconds() < (rule.frequency_limit * 3600)

class InvoiceMonitor:
    """Monitor invoices and generate overdue alerts"""
    
    def check_overdue_invoices(self, invoices: List[Dict[str, Any]], user_rules: List[AlertRule]) -> List[Alert]:
        """Check for overdue invoice alerts"""
        alerts = []
        
        try:
            current_date = datetime.now()
            
            for rule in user_rules:
                if rule.alert_type != AlertType.OVERDUE_INVOICE or not rule.is_active:
                    continue
                
                if self._is_recently_triggered(rule):
                    continue
                
                grace_period = rule.conditions.get('grace_period_days', 7)
                
                overdue_invoices = []
                for invoice in invoices:
                    due_date = datetime.fromisoformat(invoice.get('due_date', current_date.isoformat()))
                    days_overdue = (current_date - due_date).days
                    
                    if days_overdue > grace_period and invoice.get('status') != 'paid':
                        overdue_invoices.append({
                            'invoice_id': invoice.get('id'),
                            'amount': invoice.get('amount', 0),
                            'days_overdue': days_overdue,
                            'customer': invoice.get('customer_name', 'Unknown')
                        })
                
                if overdue_invoices:
                    total_overdue = sum(inv['amount'] for inv in overdue_invoices)
                    
                    priority = AlertPriority.CRITICAL if len(overdue_invoices) > 5 else AlertPriority.HIGH
                    
                    alert = Alert({
                        'rule_id': rule.rule_id,
                        'user_id': rule.user_id,
                        'alert_type': AlertType.OVERDUE_INVOICE,
                        'priority': priority,
                        'title': f'{len(overdue_invoices)} Overdue Invoices',
                        'message': f'You have {len(overdue_invoices)} overdue invoices totaling KES {total_overdue:,.2f}',
                        'data': {
                            'overdue_count': len(overdue_invoices),
                            'total_amount': total_overdue,
                            'invoices': overdue_invoices[:5],  # Limit to 5 for display
                            'recommended_action': 'Follow up with customers immediately'
                        },
                        'channels': rule.channels
                    })
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Invoice alert check error: {e}")
            return []
    
    def _is_recently_triggered(self, rule: AlertRule) -> bool:
        """Check if rule was triggered recently"""
        if rule.last_triggered is None:
            return False
        
        time_since_last = datetime.now() - rule.last_triggered
        return time_since_last.total_seconds() < (rule.frequency_limit * 3600)

class TransactionMonitor:
    """Monitor transactions for unusual patterns"""
    
    def __init__(self):
        self.anomaly_thresholds = {
            'amount_multiplier': 3.0,  # 3x average is unusual
            'frequency_multiplier': 2.0,  # 2x normal frequency
            'time_window_hours': 24
        }
    
    def check_unusual_transactions(self, recent_transactions: List[Dict[str, Any]], 
                                 historical_stats: Dict[str, float], 
                                 user_rules: List[AlertRule]) -> List[Alert]:
        """Check for unusual transaction patterns"""
        alerts = []
        
        try:
            avg_amount = historical_stats.get('avg_amount', 1000)
            avg_frequency = historical_stats.get('daily_frequency', 5)
            
            for rule in user_rules:
                if rule.alert_type != AlertType.UNUSUAL_TRANSACTION or not rule.is_active:
                    continue
                
                if self._is_recently_triggered(rule):
                    continue
                
                thresholds = {**self.anomaly_thresholds, **rule.conditions}
                unusual_transactions = []
                
                # Check for unusually large amounts
                for transaction in recent_transactions:
                    amount = transaction.get('amount', 0)
                    if amount > (avg_amount * thresholds['amount_multiplier']):
                        unusual_transactions.append({
                            'transaction_id': transaction.get('id'),
                            'amount': amount,
                            'type': 'large_amount',
                            'description': transaction.get('description', ''),
                            'timestamp': transaction.get('created_at')
                        })
                
                # Check transaction frequency
                current_time = datetime.now()
                recent_count = len([
                    t for t in recent_transactions 
                    if (current_time - datetime.fromisoformat(t.get('created_at', current_time.isoformat()))).total_seconds() 
                    < (thresholds['time_window_hours'] * 3600)
                ])
                
                if recent_count > (avg_frequency * thresholds['frequency_multiplier']):
                    unusual_transactions.append({
                        'type': 'high_frequency',
                        'count': recent_count,
                        'normal_count': avg_frequency,
                        'time_window': thresholds['time_window_hours']
                    })
                
                if unusual_transactions:
                    alert = Alert({
                        'rule_id': rule.rule_id,
                        'user_id': rule.user_id,
                        'alert_type': AlertType.UNUSUAL_TRANSACTION,
                        'priority': AlertPriority.MEDIUM,
                        'title': 'Unusual Transaction Activity Detected',
                        'message': f'Detected {len(unusual_transactions)} unusual transaction patterns.',
                        'data': {
                            'unusual_transactions': unusual_transactions,
                            'recommended_action': 'Review transactions for accuracy'
                        },
                        'channels': rule.channels
                    })
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Transaction alert check error: {e}")
            return []
    
    def _is_recently_triggered(self, rule: AlertRule) -> bool:
        """Check if rule was triggered recently"""
        if rule.last_triggered is None:
            return False
        
        time_since_last = datetime.now() - rule.last_triggered
        return time_since_last.total_seconds() < (rule.frequency_limit * 3600)

class NotificationEngine:
    """Handle alert notifications across multiple channels"""
    
    def __init__(self):
        self.notification_providers = {
            NotificationChannel.EMAIL: self._send_email,
            NotificationChannel.SMS: self._send_sms,
            NotificationChannel.IN_APP: self._send_in_app,
            NotificationChannel.PUSH: self._send_push
        }
    
    def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """Send alert through specified channels"""
        results = {}
        
        try:
            for channel in alert.channels:
                try:
                    success = self.notification_providers[channel](alert)
                    results[channel.value] = success
                except Exception as e:
                    logger.error(f"Failed to send {channel.value} notification: {e}")
                    results[channel.value] = False
            
            # Update alert status
            if any(results.values()):
                alert.status = AlertStatus.SENT
                alert.sent_at = datetime.now()
            
            return results
            
        except Exception as e:
            logger.error(f"Alert sending error: {e}")
            return {channel.value: False for channel in alert.channels}
    
    def _send_email(self, alert: Alert) -> bool:
        """Send email notification (mock implementation)"""
        try:
            # Mock email sending
            email_content = {
                'to': 'user@company.com',  # Would get from user profile
                'subject': alert.title,
                'body': f"{alert.message}\n\nPriority: {alert.priority.value}\nTime: {alert.created_at}",
                'priority': alert.priority.value
            }
            
            logger.info(f"Email sent: {alert.title} to user {alert.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False
    
    def _send_sms(self, alert: Alert) -> bool:
        """Send SMS notification (mock implementation)"""
        try:
            # Mock SMS using Africa's Talking API
            sms_content = {
                'to': '+254712345678',  # Would get from user profile
                'message': f"{alert.title}: {alert.message}",
                'priority': alert.priority.value
            }
            
            logger.info(f"SMS sent: {alert.title} to user {alert.user_id}")
            return True
            
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False
    
    def _send_in_app(self, alert: Alert) -> bool:
        """Send in-app notification"""
        try:
            # Store in database for in-app display
            notification_data = {
                'user_id': alert.user_id,
                'title': alert.title,
                'message': alert.message,
                'priority': alert.priority.value,
                'data': alert.data,
                'created_at': alert.created_at.isoformat()
            }
            
            logger.info(f"In-app notification created: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"In-app notification failed: {e}")
            return False
    
    def _send_push(self, alert: Alert) -> bool:
        """Send push notification (mock implementation)"""
        try:
            # Mock push notification
            push_content = {
                'user_id': alert.user_id,
                'title': alert.title,
                'body': alert.message,
                'priority': alert.priority.value,
                'data': alert.data
            }
            
            logger.info(f"Push notification sent: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            return False

class AlertService:
    """Main alert orchestration service"""
    
    def __init__(self):
        self.cash_flow_monitor = CashFlowMonitor()
        self.invoice_monitor = InvoiceMonitor()
        self.transaction_monitor = TransactionMonitor()
        self.notification_engine = NotificationEngine()
        self.alert_storage = {}  # Would be database in production
        self.rule_storage = {}   # Would be database in production
    
    def create_alert_rule(self, user_id: str, rule_config: Dict[str, Any]) -> str:
        """Create a new alert rule"""
        try:
            rule_id = f"rule_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            rule_config['user_id'] = user_id
            
            rule = AlertRule(rule_id, rule_config)
            self.rule_storage[rule_id] = rule
            
            logger.info(f"Alert rule created: {rule_id} for user {user_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Alert rule creation error: {e}")
            raise ValueError(f"Failed to create alert rule: {e}")
    
    def get_user_rules(self, user_id: str) -> List[AlertRule]:
        """Get all alert rules for a user"""
        return [rule for rule in self.rule_storage.values() if rule.user_id == user_id]
    
    def check_all_alerts(self, user_id: str, financial_data: Dict[str, Any]) -> List[Alert]:
        """Check all alert conditions for a user"""
        try:
            user_rules = self.get_user_rules(user_id)
            all_alerts = []
            
            # Cash flow alerts
            if 'cash_flow' in financial_data:
                cash_alerts = self.cash_flow_monitor.check_cash_flow_alerts(
                    financial_data['cash_flow'], user_rules
                )
                all_alerts.extend(cash_alerts)
            
            # Invoice alerts
            if 'invoices' in financial_data:
                invoice_alerts = self.invoice_monitor.check_overdue_invoices(
                    financial_data['invoices'], user_rules
                )
                all_alerts.extend(invoice_alerts)
            
            # Transaction alerts
            if 'transactions' in financial_data and 'transaction_stats' in financial_data:
                transaction_alerts = self.transaction_monitor.check_unusual_transactions(
                    financial_data['transactions'], 
                    financial_data['transaction_stats'], 
                    user_rules
                )
                all_alerts.extend(transaction_alerts)
            
            # Store and send alerts
            for alert in all_alerts:
                self.alert_storage[alert.alert_id] = alert
                self.notification_engine.send_alert(alert)
                
                # Update rule last triggered time
                rule = self.rule_storage.get(alert.rule_id)
                if rule:
                    rule.last_triggered = datetime.now()
            
            return all_alerts
            
        except Exception as e:
            logger.error(f"Alert checking error: {e}")
            raise ValueError(f"Failed to check alerts: {e}")
    
    def get_user_alerts(self, user_id: str, status: Optional[AlertStatus] = None) -> List[Alert]:
        """Get alerts for a user, optionally filtered by status"""
        user_alerts = [alert for alert in self.alert_storage.values() if alert.user_id == user_id]
        
        if status:
            user_alerts = [alert for alert in user_alerts if alert.status == status]
        
        return sorted(user_alerts, key=lambda x: x.created_at, reverse=True)
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Mark alert as acknowledged"""
        try:
            alert = self.alert_storage.get(alert_id)
            if alert and alert.user_id == user_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Alert acknowledgment error: {e}")
            return False
    
    def resolve_alert(self, alert_id: str, user_id: str) -> bool:
        """Mark alert as resolved"""
        try:
            alert = self.alert_storage.get(alert_id)
            if alert and alert.user_id == user_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Alert resolution error: {e}")
            return False