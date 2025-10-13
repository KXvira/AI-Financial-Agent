"""
MailerSend Email Service Integration
Handles email sending using MailerSend API
"""

import os
import logging
from typing import Optional, List, Dict, Any
from mailersend import emails

logger = logging.getLogger(__name__)


class MailerSendService:
    """Service for sending emails via MailerSend"""
    
    def __init__(self):
        """Initialize MailerSend service"""
        self.api_token = os.getenv("MAILERSEND_API_TOKEN")
        self.from_email = os.getenv("MAILERSEND_FROM_EMAIL", "noreply@yourdomain.com")
        self.from_name = os.getenv("MAILERSEND_FROM_NAME", "AI Financial Agent")
        
        if not self.api_token:
            logger.warning("MAILERSEND_API_TOKEN not set in environment variables")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("MailerSend service initialized successfully")
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Send an email using MailerSend
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (optional)
            reply_to: Reply-to email address (optional)
            attachments: List of attachments (optional)
            
        Returns:
            Dict with success status and message
        """
        if not self.enabled:
            logger.error("MailerSend service is not enabled. Check API token.")
            return {
                "success": False,
                "error": "MailerSend service not configured"
            }
        
        try:
            # Initialize MailerSend client
            mailer = emails.NewEmail(self.api_token)
            
            # Set sender
            mail_from = {
                "name": self.from_name,
                "email": self.from_email,
            }
            
            # Set recipients
            recipients = [
                {
                    "name": to_email.split('@')[0],
                    "email": to_email,
                }
            ]
            
            # Set reply-to if provided
            reply_to_data = None
            if reply_to:
                reply_to_data = {
                    "email": reply_to,
                }
            
            # Configure email
            mailer.set_mail_from(mail_from, {"name": self.from_name, "email": self.from_email})
            mailer.set_mail_to(recipients, {"name": to_email.split('@')[0], "email": to_email})
            mailer.set_subject(subject)
            mailer.set_html_content(html_content)
            
            if text_content:
                mailer.set_plaintext_content(text_content)
            
            if reply_to_data:
                mailer.set_reply_to(reply_to_data)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    mailer.add_attachment(
                        content=attachment.get('content'),
                        filename=attachment.get('filename'),
                        disposition=attachment.get('disposition', 'attachment')
                    )
            
            # Send email
            response = mailer.send()
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "success": True,
                "message": "Email sent successfully",
                "message_id": response.get('message_id'),
                "to": to_email
            }
            
        except Exception as e:
            logger.error(f"Failed to send email via MailerSend: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "to": to_email
            }
    
    def send_receipt_email(
        self,
        to_email: str,
        customer_name: str,
        receipt_number: str,
        amount: float,
        pdf_path: str,
    ) -> Dict[str, Any]:
        """
        Send a receipt email with PDF attachment
        
        Args:
            to_email: Customer email
            customer_name: Customer name
            receipt_number: Receipt number
            amount: Receipt amount
            pdf_path: Path to PDF file
            
        Returns:
            Dict with success status
        """
        subject = f"Receipt {receipt_number} - Payment Confirmation"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Payment Receipt</h2>
                <p>Dear {customer_name},</p>
                <p>Thank you for your payment. Please find your receipt attached.</p>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Receipt Number:</strong> {receipt_number}</p>
                    <p style="margin: 5px 0;"><strong>Amount:</strong> KES {amount:,.2f}</p>
                </div>
                
                <p>If you have any questions about this receipt, please contact us.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>{self.from_name}</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Payment Receipt
        
        Dear {customer_name},
        
        Thank you for your payment. Please find your receipt attached.
        
        Receipt Number: {receipt_number}
        Amount: KES {amount:,.2f}
        
        If you have any questions about this receipt, please contact us.
        
        Best regards,
        {self.from_name}
        """
        
        # Read PDF file and encode as base64
        import base64
        try:
            with open(pdf_path, 'rb') as f:
                pdf_content = base64.b64encode(f.read()).decode('utf-8')
            
            attachments = [{
                'content': pdf_content,
                'filename': f'{receipt_number}.pdf',
                'disposition': 'attachment'
            }]
            
            return self.send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
                attachments=attachments
            )
        except Exception as e:
            logger.error(f"Failed to read PDF file: {str(e)}")
            return {
                "success": False,
                "error": f"Failed to attach PDF: {str(e)}"
            }
    
    def send_invoice_email(
        self,
        to_email: str,
        customer_name: str,
        invoice_number: str,
        amount: float,
        due_date: str,
        pdf_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Send an invoice email
        
        Args:
            to_email: Customer email
            customer_name: Customer name
            invoice_number: Invoice number
            amount: Invoice amount
            due_date: Payment due date
            pdf_path: Path to PDF invoice (optional)
            
        Returns:
            Dict with success status
        """
        subject = f"Invoice {invoice_number} - Payment Due"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">New Invoice</h2>
                <p>Dear {customer_name},</p>
                <p>Please find your invoice details below:</p>
                
                <div style="background: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 5px 0;"><strong>Invoice Number:</strong> {invoice_number}</p>
                    <p style="margin: 5px 0;"><strong>Amount Due:</strong> KES {amount:,.2f}</p>
                    <p style="margin: 5px 0;"><strong>Due Date:</strong> {due_date}</p>
                </div>
                
                <p>Please make payment by the due date to avoid any late fees.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>{self.from_name}</strong>
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        New Invoice
        
        Dear {customer_name},
        
        Please find your invoice details below:
        
        Invoice Number: {invoice_number}
        Amount Due: KES {amount:,.2f}
        Due Date: {due_date}
        
        Please make payment by the due date to avoid any late fees.
        
        Best regards,
        {self.from_name}
        """
        
        attachments = None
        if pdf_path:
            import base64
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_content = base64.b64encode(f.read()).decode('utf-8')
                
                attachments = [{
                    'content': pdf_content,
                    'filename': f'{invoice_number}.pdf',
                    'disposition': 'attachment'
                }]
            except Exception as e:
                logger.error(f"Failed to read invoice PDF: {str(e)}")
        
        return self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            attachments=attachments
        )


# Singleton instance
_mailersend_service = None


def get_mailersend_service() -> MailerSendService:
    """Get or create MailerSend service instance"""
    global _mailersend_service
    if _mailersend_service is None:
        _mailersend_service = MailerSendService()
    return _mailersend_service
