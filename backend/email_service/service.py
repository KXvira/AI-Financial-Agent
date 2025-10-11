"""
Email Service for Invoice Delivery
Handles email sending via SendGrid and PDF generation
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
from io import BytesIO

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False
    logging.warning("SendGrid not available. Email features will be disabled.")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("ReportLab not available. PDF generation will be disabled.")

from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending invoices via email with PDF attachments"""
    
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.logger = logger
        self.sendgrid_client = None
        self.from_email = os.getenv('SENDGRID_FROM_EMAIL', 'invoices@yourdomain.com')
        self.from_name = os.getenv('SENDGRID_FROM_NAME', 'Financial Agent')
        
        if SENDGRID_AVAILABLE:
            self._initialize_sendgrid()
    
    def _initialize_sendgrid(self):
        """Initialize SendGrid API client"""
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            self.logger.warning("SENDGRID_API_KEY not set. Email features will be limited.")
            return
        
        try:
            self.sendgrid_client = SendGridAPIClient(api_key)
            self.logger.info("SendGrid initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize SendGrid: {str(e)}")
            self.sendgrid_client = None
    
    def generate_invoice_pdf(self, invoice: Dict[str, Any]) -> bytes:
        """
        Generate PDF for an invoice
        
        Args:
            invoice: Invoice document from database
        
        Returns:
            PDF content as bytes
        """
        if not PDF_AVAILABLE:
            raise RuntimeError("PDF generation not available. Install reportlab.")
        
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
            
            # Container for the 'Flowable' objects
            elements = []
            
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1e3a8a'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#1e3a8a'),
                spaceAfter=12,
            )
            
            # Title
            title = Paragraph("INVOICE", title_style)
            elements.append(title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Invoice details header
            invoice_id = invoice.get('invoice_id', 'N/A')
            issue_date = invoice.get('issue_date', 'N/A')
            due_date = invoice.get('due_date', 'N/A')
            status = invoice.get('status', 'pending').upper()
            
            header_data = [
                ['Invoice Number:', invoice_id, 'Issue Date:', issue_date],
                ['Customer:', invoice.get('customer_name', 'N/A'), 'Due Date:', due_date],
                ['Status:', status, '', '']
            ]
            
            header_table = Table(header_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.5*inch])
            header_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            elements.append(header_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Invoice items
            items_heading = Paragraph("Invoice Items", heading_style)
            elements.append(items_heading)
            
            # Items table
            items = invoice.get('items', [])
            if items:
                # Table header
                items_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
                
                # Table rows
                for item in items:
                    desc = item.get('description', 'N/A')
                    qty = item.get('quantity', 0)
                    unit_price = item.get('unit_price', 0)
                    total = item.get('total', 0)
                    
                    items_data.append([
                        desc,
                        f"{qty:,.2f}",
                        f"KES {unit_price:,.2f}",
                        f"KES {total:,.2f}"
                    ])
                
                items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
                items_table.setStyle(TableStyle([
                    # Header
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('ALIGN', (1, 0), (-1, 0), 'RIGHT'),
                    
                    # Body
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    
                    # Grid
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                elements.append(items_table)
            else:
                # Fallback if no items
                amount = invoice.get('amount', 0)
                items_data = [
                    ['Description', 'Amount'],
                    ['Invoice Amount', f"KES {amount:,.2f}"]
                ]
                
                items_table = Table(items_data, colWidths=[5*inch, 2*inch])
                items_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                
                elements.append(items_table)
            
            elements.append(Spacer(1, 0.3*inch))
            
            # Totals section
            subtotal = sum(item.get('total', 0) for item in items) if items else invoice.get('amount', 0)
            tax_rate = 0.16
            tax_amount = subtotal * tax_rate
            total_amount = subtotal + tax_amount
            
            totals_data = [
                ['', '', 'Subtotal:', f"KES {subtotal:,.2f}"],
                ['', '', 'Tax (16%):', f"KES {tax_amount:,.2f}"],
                ['', '', 'Total Amount:', f"KES {total_amount:,.2f}"],
            ]
            
            totals_table = Table(totals_data, colWidths=[2.5*inch, 2*inch, 1.5*inch, 1.5*inch])
            totals_table.setStyle(TableStyle([
                ('FONTNAME', (2, 0), (2, 1), 'Helvetica'),
                ('FONTNAME', (2, 2), (2, 2), 'Helvetica-Bold'),
                ('FONTNAME', (3, 0), (3, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (2, 2), (3, 2), 2, colors.black),
                ('TEXTCOLOR', (2, 2), (3, 2), colors.HexColor('#1e3a8a')),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            elements.append(totals_table)
            elements.append(Spacer(1, 0.4*inch))
            
            # Notes
            notes = invoice.get('notes', '')
            if notes:
                notes_heading = Paragraph("Notes", heading_style)
                elements.append(notes_heading)
                notes_para = Paragraph(notes, styles['Normal'])
                elements.append(notes_para)
                elements.append(Spacer(1, 0.2*inch))
            
            # Footer
            footer_text = "Thank you for your business!"
            footer = Paragraph(f"<para align=center><i>{footer_text}</i></para>", styles['Normal'])
            elements.append(Spacer(1, 0.3*inch))
            elements.append(footer)
            
            # Build PDF
            doc.build(elements)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    async def send_invoice_email(
        self,
        invoice_id: str,
        recipient_email: str,
        recipient_name: Optional[str] = None,
        cc_emails: Optional[List[str]] = None,
        custom_message: Optional[str] = None,
        attach_pdf: bool = True
    ) -> Dict[str, Any]:
        """
        Send invoice via email with optional PDF attachment
        
        Args:
            invoice_id: Invoice ID to send
            recipient_email: Primary recipient email
            recipient_name: Recipient name (optional)
            cc_emails: List of CC email addresses
            custom_message: Custom message to include in email
            attach_pdf: Whether to attach PDF (default True)
        
        Returns:
            Dict with send status and details
        """
        try:
            # Get invoice from database
            invoice = await self.db.invoices.find_one({"invoice_id": invoice_id})
            if not invoice:
                raise ValueError(f"Invoice {invoice_id} not found")
            
            # Get customer details
            customer_id = invoice.get('customer_id')
            customer = None
            if customer_id:
                customer = await self.db.customers.find_one({"customer_id": customer_id})
            
            # Prepare email content
            subject = f"Invoice {invoice_id} from {self.from_name}"
            
            # Build email body
            customer_name = recipient_name or invoice.get('customer_name', 'Valued Customer')
            issue_date = invoice.get('issue_date', 'N/A')
            due_date = invoice.get('due_date', 'N/A')
            amount = invoice.get('amount', 0)
            
            # Calculate total with tax
            items = invoice.get('items', [])
            if items:
                subtotal = sum(item.get('total', 0) for item in items)
                tax_amount = subtotal * 0.16
                total_amount = subtotal + tax_amount
            else:
                total_amount = amount
            
            html_body = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                    .content {{ background-color: #f9fafb; padding: 30px; margin: 20px 0; }}
                    .invoice-details {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                    .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
                    .label {{ font-weight: bold; color: #6b7280; }}
                    .value {{ color: #1f2937; }}
                    .amount {{ font-size: 24px; font-weight: bold; color: #1e3a8a; text-align: center; margin: 20px 0; }}
                    .footer {{ text-align: center; color: #6b7280; font-size: 12px; margin-top: 30px; }}
                    .button {{ display: inline-block; background-color: #1e3a8a; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Invoice from {self.from_name}</h1>
                    </div>
                    
                    <div class="content">
                        <p>Dear {customer_name},</p>
                        
                        <p>Thank you for your business! Please find your invoice details below.</p>
                        
                        {f'<p style="background-color: #fef3c7; padding: 15px; border-left: 4px solid #f59e0b; margin: 20px 0;">{custom_message}</p>' if custom_message else ''}
                        
                        <div class="invoice-details">
                            <div class="detail-row">
                                <span class="label">Invoice Number:</span>
                                <span class="value">{invoice_id}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Issue Date:</span>
                                <span class="value">{issue_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Due Date:</span>
                                <span class="value">{due_date}</span>
                            </div>
                        </div>
                        
                        <div class="amount">
                            Total Amount: KES {total_amount:,.2f}
                        </div>
                        
                        <p style="text-align: center;">
                            {f'<strong>Payment is due by {due_date}.</strong>' if due_date != 'N/A' else ''}
                        </p>
                        
                        {f'<p style="text-align: center;"><a href="#" class="button">View Invoice Online</a></p>' if False else ''}
                    </div>
                    
                    <div class="footer">
                        <p>If you have any questions about this invoice, please contact us.</p>
                        <p>&copy; 2025 {self.from_name}. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_body = f"""
            Invoice from {self.from_name}
            
            Dear {customer_name},
            
            Thank you for your business! Please find your invoice details below.
            
            {custom_message if custom_message else ''}
            
            Invoice Number: {invoice_id}
            Issue Date: {issue_date}
            Due Date: {due_date}
            Total Amount: KES {total_amount:,.2f}
            
            Payment is due by {due_date}.
            
            If you have any questions about this invoice, please contact us.
            
            {self.from_name}
            """
            
            # Send via SendGrid or mock
            if self.sendgrid_client and SENDGRID_AVAILABLE:
                result = await self._send_via_sendgrid(
                    to_email=recipient_email,
                    to_name=recipient_name,
                    cc_emails=cc_emails,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                    invoice=invoice,
                    attach_pdf=attach_pdf
                )
            else:
                result = await self._mock_send_email(
                    invoice_id=invoice_id,
                    recipient_email=recipient_email,
                    subject=subject
                )
            
            # Log email in database
            await self._log_email(invoice_id, recipient_email, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending invoice email: {str(e)}")
            raise
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        to_name: Optional[str],
        cc_emails: Optional[List[str]],
        subject: str,
        html_body: str,
        text_body: str,
        invoice: Dict[str, Any],
        attach_pdf: bool
    ) -> Dict[str, Any]:
        """Send email via SendGrid API"""
        try:
            from_email = Email(self.from_email, self.from_name)
            to_email_obj = To(to_email, to_name)
            
            # Create mail object
            message = Mail(
                from_email=from_email,
                to_emails=to_email_obj,
                subject=subject,
                plain_text_content=text_body,
                html_content=html_body
            )
            
            # Add CC if provided
            if cc_emails:
                for cc_email in cc_emails:
                    message.add_cc(cc_email)
            
            # Attach PDF if requested
            if attach_pdf and PDF_AVAILABLE:
                try:
                    pdf_content = self.generate_invoice_pdf(invoice)
                    encoded_pdf = base64.b64encode(pdf_content).decode()
                    
                    attachment = Attachment()
                    attachment.file_content = FileContent(encoded_pdf)
                    attachment.file_type = FileType('application/pdf')
                    attachment.file_name = FileName(f"invoice_{invoice.get('invoice_id', 'unknown')}.pdf")
                    attachment.disposition = Disposition('attachment')
                    
                    message.add_attachment(attachment)
                except Exception as e:
                    self.logger.warning(f"Failed to attach PDF: {str(e)}")
            
            # Send email
            response = self.sendgrid_client.send(message)
            
            return {
                "success": True,
                "status_code": response.status_code,
                "message": "Email sent successfully via SendGrid",
                "method": "sendgrid",
                "recipient": to_email,
                "sent_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"SendGrid error: {str(e)}")
            raise
    
    async def _mock_send_email(
        self,
        invoice_id: str,
        recipient_email: str,
        subject: str
    ) -> Dict[str, Any]:
        """Mock email sending when SendGrid is not configured"""
        self.logger.info(f"MOCK EMAIL: Would send '{subject}' to {recipient_email}")
        
        return {
            "success": True,
            "status_code": 200,
            "message": "Email sent successfully (MOCK MODE)",
            "method": "mock",
            "recipient": recipient_email,
            "sent_at": datetime.now().isoformat(),
            "note": "SendGrid not configured. This is a simulated send."
        }
    
    async def _log_email(self, invoice_id: str, recipient: str, result: Dict[str, Any]):
        """Log email send attempt in database"""
        try:
            log_entry = {
                "invoice_id": invoice_id,
                "recipient": recipient,
                "success": result.get("success", False),
                "method": result.get("method", "unknown"),
                "status_code": result.get("status_code"),
                "sent_at": datetime.now(),
                "details": result
            }
            
            await self.db.email_logs.insert_one(log_entry)
            
        except Exception as e:
            self.logger.error(f"Error logging email: {str(e)}")
    
    async def get_email_history(
        self,
        invoice_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get email send history"""
        try:
            query = {}
            if invoice_id:
                query["invoice_id"] = invoice_id
            
            logs = await self.db.email_logs.find(query).sort(
                "sent_at", -1
            ).limit(limit).to_list(limit)
            
            # Convert ObjectId to string
            for log in logs:
                log["_id"] = str(log["_id"])
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Error getting email history: {str(e)}")
            return []
