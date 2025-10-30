"""
Email Delivery Service
Handles sending reports via email with SMTP
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailConfig(BaseModel):
    """Email configuration"""
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server host")
    smtp_port: int = Field(default=587, description="SMTP server port")
    smtp_user: str = Field(..., description="SMTP username/email")
    smtp_password: str = Field(..., description="SMTP password")
    from_email: str = Field(..., description="From email address")
    from_name: str = Field(default="Fin Guard", description="From name")
    use_tls: bool = Field(default=True, description="Use TLS encryption")


class EmailMessage(BaseModel):
    """Email message"""
    to: List[EmailStr] = Field(..., description="Recipient email addresses")
    subject: str = Field(..., description="Email subject")
    body_html: str = Field(..., description="Email body (HTML)")
    body_text: Optional[str] = Field(None, description="Email body (plain text)")
    cc: Optional[List[EmailStr]] = Field(None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(None, description="BCC recipients")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="File attachments")


class EmailDeliveryService:
    """Service for sending emails with reports"""
    
    def __init__(self):
        # Get email configuration from environment variables
        self.config = EmailConfig(
            smtp_host=os.getenv('SMTP_HOST', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            smtp_user=os.getenv('SMTP_USER', ''),
            smtp_password=os.getenv('SMTP_PASSWORD', ''),
            from_email=os.getenv('FROM_EMAIL', 'noreply@finguard.com'),
            from_name=os.getenv('FROM_NAME', 'Fin Guard Reports'),
            use_tls=os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
        )
        
    async def send_email(self, message: EmailMessage) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            message: Email message to send
            
        Returns:
            Success status and details
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config.from_name} <{self.config.from_email}>"
            msg['To'] = ', '.join(message.to)
            msg['Subject'] = message.subject
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            if message.cc:
                msg['Cc'] = ', '.join(message.cc)
            
            # Add body
            if message.body_text:
                part1 = MIMEText(message.body_text, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(message.body_html, 'html')
            msg.attach(part2)
            
            # Add attachments
            if message.attachments:
                for attachment in message.attachments:
                    part = MIMEApplication(attachment['data'], Name=attachment['filename'])
                    part['Content-Disposition'] = f'attachment; filename="{attachment["filename"]}"'
                    msg.attach(part)
            
            # Send email
            recipients = message.to.copy()
            if message.cc:
                recipients.extend(message.cc)
            if message.bcc:
                recipients.extend(message.bcc)
            
            with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                
                server.send_message(msg, self.config.from_email, recipients)
            
            logger.info(f"Email sent successfully to {', '.join(message.to)}")
            
            return {
                "success": True,
                "message": "Email sent successfully",
                "recipients": len(recipients),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_report_email(
        self,
        recipients: List[str],
        report_type: str,
        report_data: Dict[str, Any],
        report_file: Optional[bytes] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a report via email
        
        Args:
            recipients: List of recipient email addresses
            report_type: Type of report
            report_data: Report data for email body
            report_file: Optional report file (PDF/Excel) as bytes
            filename: Filename for attachment
            
        Returns:
            Success status
        """
        try:
            # Generate email content
            subject = f"Fin Guard Report: {report_type.replace('_', ' ').title()}"
            
            # Create HTML body
            html_body = self._create_report_email_html(report_type, report_data)
            
            # Create text body
            text_body = self._create_report_email_text(report_type, report_data)
            
            # Prepare attachments
            attachments = []
            if report_file and filename:
                attachments.append({
                    'data': report_file,
                    'filename': filename
                })
            
            # Send email
            message = EmailMessage(
                to=recipients,
                subject=subject,
                body_html=html_body,
                body_text=text_body,
                attachments=attachments if attachments else None
            )
            
            return await self.send_email(message)
            
        except Exception as e:
            logger.error(f"Error sending report email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_report_email_html(self, report_type: str, data: Dict[str, Any]) -> str:
        """Create HTML email body for report"""
        report_name = report_type.replace('_', ' ').title()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .content {{
                    background: white;
                    padding: 30px;
                    border: 1px solid #e0e0e0;
                }}
                .metric {{
                    background: #f5f5f5;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 5px;
                    border-left: 4px solid #667eea;
                }}
                .metric-label {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 5px;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-radius: 0 0 10px 10px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 {report_name}</h1>
                <p>Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}</p>
            </div>
            
            <div class="content">
                <p>Hello,</p>
                <p>Your scheduled <strong>{report_name}</strong> report is ready.</p>
                
                <h3>📈 Key Highlights:</h3>
        """
        
        # Add metrics from data
        if 'summary' in data:
            for key, value in data['summary'].items():
                html += f"""
                <div class="metric">
                    <div class="metric-label">{key.replace('_', ' ').title()}</div>
                    <div class="metric-value">{value}</div>
                </div>
                """
        
        html += """
                <p style="margin-top: 20px;">
                    The full report is attached to this email. You can also view it in your Fin Guard dashboard.
                </p>
                
                <a href="http://localhost:3001/reports" class="button">View Dashboard</a>
            </div>
            
            <div class="footer">
                <p>This is an automated email from Fin Guard.</p>
                <p>To manage your report subscriptions, visit your dashboard settings.</p>
                <p>&copy; 2025 Fin Guard. All rights reserved.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _create_report_email_text(self, report_type: str, data: Dict[str, Any]) -> str:
        """Create plain text email body for report"""
        report_name = report_type.replace('_', ' ').title()
        
        text = f"""
Fin Guard Report: {report_name}
Generated on {datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')}

Hello,

Your scheduled {report_name} report is ready.

Key Highlights:
"""
        
        if 'summary' in data:
            for key, value in data['summary'].items():
                text += f"- {key.replace('_', ' ').title()}: {value}\n"
        
        text += """

The full report is attached to this email.

View your dashboard: http://localhost:3001/reports

---
This is an automated email from Fin Guard.
To manage your report subscriptions, visit your dashboard settings.

© 2025 Fin Guard. All rights reserved.
"""
        
        return text
    
    async def send_test_email(self, recipient: str) -> Dict[str, Any]:
        """Send a test email to verify configuration"""
        try:
            message = EmailMessage(
                to=[recipient],
                subject="Fin Guard - Test Email",
                body_html="""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2 style="color: #667eea;">✅ Email Configuration Test</h2>
                    <p>Your email configuration is working correctly!</p>
                    <p>This is a test email from Fin Guard.</p>
                    <hr style="border: 1px solid #e0e0e0; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Sent from Fin Guard Financial Management System
                    </p>
                </body>
                </html>
                """,
                body_text="Email Configuration Test\n\nYour email configuration is working correctly!"
            )
            
            return await self.send_email(message)
            
        except Exception as e:
            logger.error(f"Error sending test email: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured"""
        return bool(self.config.smtp_user and self.config.smtp_password)
