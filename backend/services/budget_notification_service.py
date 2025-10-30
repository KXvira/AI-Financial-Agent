"""
Budget Notification Service - Sends email alerts for budget thresholds
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from backend.automation.email_service import EmailDeliveryService, EmailMessage
from backend.models.budget import Budget, AlertLevel

logger = logging.getLogger("financial-agent.budget.notifications")


class BudgetNotificationService:
    """Service for sending budget-related email notifications"""
    
    def __init__(self):
        self.email_service = EmailDeliveryService()
        logger.info("BudgetNotificationService initialized")
    
    async def send_budget_alert(
        self,
        budget: Budget,
        recipient_email: str,
        recipient_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send budget alert email based on current alert level
        
        Args:
            budget: Budget object with current alert level
            recipient_email: Email address to send to
            recipient_name: Optional recipient name
            
        Returns:
            Email sending result
        """
        try:
            # Don't send email if no alert
            if budget.alert_level == AlertLevel.NONE or budget.alert_level == "none":
                logger.info(f"No alert needed for budget {budget.category}")
                return {"status": "skipped", "reason": "no_alert"}
            
            # Calculate utilization
            utilization = (budget.actual_spent / budget.amount) * 100 if budget.amount > 0 else 0
            remaining = budget.amount - budget.actual_spent
            
            # Determine alert type and styling
            alert_config = self._get_alert_config(budget.alert_level, utilization)
            
            # Build email subject
            subject = f"🚨 Budget Alert: {budget.category} - {alert_config['status']}"
            
            # Build HTML email body
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: {alert_config['color']};
                        color: white;
                        padding: 20px;
                        border-radius: 8px 8px 0 0;
                        text-align: center;
                    }}
                    .content {{
                        background-color: #f9f9f9;
                        padding: 30px;
                        border-radius: 0 0 8px 8px;
                    }}
                    .alert-box {{
                        background-color: white;
                        border-left: 4px solid {alert_config['color']};
                        padding: 15px;
                        margin: 20px 0;
                        border-radius: 4px;
                    }}
                    .stats {{
                        display: table;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    .stat-item {{
                        display: table-row;
                    }}
                    .stat-label {{
                        display: table-cell;
                        padding: 8px;
                        font-weight: bold;
                        width: 50%;
                    }}
                    .stat-value {{
                        display: table-cell;
                        padding: 8px;
                        text-align: right;
                    }}
                    .progress-bar {{
                        width: 100%;
                        height: 30px;
                        background-color: #e0e0e0;
                        border-radius: 15px;
                        overflow: hidden;
                        margin: 20px 0;
                    }}
                    .progress-fill {{
                        height: 100%;
                        background-color: {alert_config['color']};
                        width: {min(utilization, 100)}%;
                        transition: width 0.3s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 20px;
                        color: #666;
                        font-size: 14px;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: {alert_config['color']};
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        margin-top: 20px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{alert_config['icon']} Budget Alert</h1>
                        <h2>{budget.category}</h2>
                    </div>
                    <div class="content">
                        <div class="alert-box">
                            <h3 style="margin-top: 0; color: {alert_config['color']};">
                                {alert_config['status']}
                            </h3>
                            <p><strong>{alert_config['message']}</strong></p>
                        </div>
                        
                        <h3>Budget Summary</h3>
                        <div class="stats">
                            <div class="stat-item">
                                <span class="stat-label">Budget Amount:</span>
                                <span class="stat-value">${budget.amount:,.2f}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Actual Spent:</span>
                                <span class="stat-value">${budget.actual_spent:,.2f}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Remaining:</span>
                                <span class="stat-value" style="color: {'red' if remaining < 0 else 'green'};">
                                    ${abs(remaining):,.2f} {'(Over Budget!)' if remaining < 0 else ''}
                                </span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Utilization:</span>
                                <span class="stat-value">{utilization:.1f}%</span>
                            </div>
                        </div>
                        
                        <div class="progress-bar">
                            <div class="progress-fill">
                                {utilization:.0f}%
                            </div>
                        </div>
                        
                        <h3>Budget Details</h3>
                        <div class="stats">
                            <div class="stat-item">
                                <span class="stat-label">Period:</span>
                                <span class="stat-value">{budget.period_type.capitalize()}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Start Date:</span>
                                <span class="stat-value">{budget.start_date}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">End Date:</span>
                                <span class="stat-value">{budget.end_date}</span>
                            </div>
                            <div class="stat-item">
                                <span class="stat-label">Alert Threshold:</span>
                                <span class="stat-value">{budget.alert_threshold}%</span>
                            </div>
                        </div>
                        
                        {f'<p><strong>Description:</strong> {budget.description}</p>' if budget.description else ''}
                        
                        <div style="text-align: center;">
                            <a href="http://localhost:3000/budgets" class="button">
                                View Budget Dashboard
                            </a>
                        </div>
                    </div>
                    <div class="footer">
                        <p>This is an automated budget alert from your Financial Agent System.</p>
                        <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Create plain text version
            text_body = f"""
Budget Alert: {budget.category}

{alert_config['status']}
{alert_config['message']}

Budget Summary:
---------------
Budget Amount: ${budget.amount:,.2f}
Actual Spent: ${budget.actual_spent:,.2f}
Remaining: ${abs(remaining):,.2f} {'(Over Budget!)' if remaining < 0 else ''}
Utilization: {utilization:.1f}%

Budget Details:
--------------
Period: {budget.period_type.capitalize()}
Start Date: {budget.start_date}
End Date: {budget.end_date}
Alert Threshold: {budget.alert_threshold}%
{f'Description: {budget.description}' if budget.description else ''}

View your budget dashboard: http://localhost:3000/budgets

---
This is an automated budget alert from your Financial Agent System.
Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            """
            
            # Send email
            message = EmailMessage(
                to_email=recipient_email,
                to_name=recipient_name or recipient_email,
                subject=subject,
                text_body=text_body,
                html_body=html_body
            )
            
            result = await self.email_service.send_email(message)
            logger.info(f"Budget alert email sent for {budget.category} to {recipient_email}")
            return result
            
        except Exception as e:
            logger.error(f"Error sending budget alert email: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _get_alert_config(self, alert_level: str, utilization: float) -> Dict[str, str]:
        """Get alert configuration based on level"""
        configs = {
            "warning": {
                "status": "Warning - Approaching Limit",
                "message": f"Your budget has reached {utilization:.1f}% utilization. Consider reviewing your spending.",
                "color": "#EAB308",  # yellow
                "icon": "⚠️"
            },
            "critical": {
                "status": "Critical - Near Limit",
                "message": f"Your budget has reached {utilization:.1f}% utilization. Immediate attention required!",
                "color": "#F97316",  # orange
                "icon": "🔴"
            },
            "exceeded": {
                "status": "EXCEEDED - Over Budget!",
                "message": f"Your budget has been exceeded at {utilization:.1f}% utilization. Take action immediately!",
                "color": "#EF4444",  # red
                "icon": "🚨"
            }
        }
        
        return configs.get(alert_level.lower(), {
            "status": "Budget Alert",
            "message": f"Your budget is at {utilization:.1f}% utilization.",
            "color": "#3B82F6",  # blue
            "icon": "📊"
        })
