"""
PDF Generator for Receipts

Generates professional PDF receipts using ReportLab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from datetime import datetime
from typing import Optional, List
import io
import os

from .models import Receipt, LineItem, ReceiptTemplate
from .qr_generator import QRCodeGenerator


class ReceiptPDFGenerator:
    """PDF generator for receipts"""
    
    def __init__(self, template: Optional[ReceiptTemplate] = None):
        """
        Initialize PDF generator
        
        Args:
            template: Optional receipt template for styling
        """
        self.template = template
        self.qr_generator = QRCodeGenerator()
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a56db'),
            spaceAfter=12,
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6,
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#374151'),
        )
    
    def generate_receipt_pdf(
        self,
        receipt: Receipt,
        output_path: Optional[str] = None
    ) -> bytes:
        """
        Generate PDF receipt
        
        Args:
            receipt: Receipt model
            output_path: Optional file path to save PDF
            
        Returns:
            PDF bytes
        """
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Build PDF content
        story = []
        
        # Header
        story.extend(self._create_header(receipt))
        story.append(Spacer(1, 12))
        
        # Customer information
        story.extend(self._create_customer_section(receipt))
        story.append(Spacer(1, 12))
        
        # Receipt details
        story.extend(self._create_receipt_details(receipt))
        story.append(Spacer(1, 12))
        
        # Line items (if any)
        if receipt.line_items:
            story.extend(self._create_line_items_table(receipt.line_items))
            story.append(Spacer(1, 12))
        
        # Tax breakdown
        story.extend(self._create_tax_breakdown(receipt))
        story.append(Spacer(1, 20))
        
        # QR code
        story.extend(self._create_qr_code(receipt))
        story.append(Spacer(1, 12))
        
        # Footer
        story.extend(self._create_footer(receipt))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
        
        return pdf_bytes
    
    def _create_header(self, receipt: Receipt) -> List:
        """Create PDF header"""
        elements = []
        
        # Business name
        business_name = receipt.business_name or "FinGuard Business"
        title = Paragraph(business_name, self.title_style)
        elements.append(title)
        
        # Business details
        business_info = []
        if receipt.business_address:
            business_info.append(receipt.business_address)
        if receipt.business_phone:
            business_info.append(f"Tel: {receipt.business_phone}")
        if receipt.business_email:
            business_info.append(f"Email: {receipt.business_email}")
        if receipt.business_kra_pin:
            business_info.append(f"KRA PIN: {receipt.business_kra_pin}")
        
        if business_info:
            info_text = " | ".join(business_info)
            info_para = Paragraph(info_text, self.body_style)
            elements.append(info_para)
        
        elements.append(Spacer(1, 12))
        
        # Receipt title
        receipt_title = Paragraph(
            f"<b>OFFICIAL RECEIPT</b>",
            self.heading_style
        )
        elements.append(receipt_title)
        
        return elements
    
    def _create_customer_section(self, receipt: Receipt) -> List:
        """Create customer information section"""
        elements = []
        
        # Customer heading
        heading = Paragraph("<b>Customer Information</b>", self.heading_style)
        elements.append(heading)
        
        # Customer details table
        customer_data = [
            ["Name:", receipt.customer.name],
        ]
        
        if receipt.customer.phone:
            customer_data.append(["Phone:", receipt.customer.phone])
        if receipt.customer.email:
            customer_data.append(["Email:", receipt.customer.email])
        if receipt.customer.kra_pin:
            customer_data.append(["KRA PIN:", receipt.customer.kra_pin])
        if receipt.customer.address:
            customer_data.append(["Address:", receipt.customer.address])
        
        customer_table = Table(customer_data, colWidths=[1.5*inch, 4*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(customer_table)
        
        return elements
    
    def _create_receipt_details(self, receipt: Receipt) -> List:
        """Create receipt details section"""
        elements = []
        
        # Receipt details
        details_data = [
            ["Receipt Number:", receipt.receipt_number],
            ["Receipt Type:", receipt.receipt_type.value.replace('_', ' ').title()],
            ["Payment Method:", receipt.payment_method.value.replace('_', ' ').title()],
            ["Payment Date:", receipt.payment_date.strftime("%B %d, %Y %I:%M %p")],
        ]
        
        if receipt.metadata.mpesa_receipt:
            details_data.append(["M-Pesa Receipt:", receipt.metadata.mpesa_receipt])
        if receipt.metadata.invoice_id:
            details_data.append(["Invoice ID:", receipt.metadata.invoice_id])
        if receipt.metadata.reference_number:
            details_data.append(["Reference:", receipt.metadata.reference_number])
        
        details_table = Table(details_data, colWidths=[1.5*inch, 4*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#374151')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(details_table)
        
        return elements
    
    def _create_line_items_table(self, line_items: List[LineItem]) -> List:
        """Create line items table"""
        elements = []
        
        # Heading
        heading = Paragraph("<b>Items</b>", self.heading_style)
        elements.append(heading)
        elements.append(Spacer(1, 6))
        
        # Table data
        table_data = [
            ["Description", "Qty", "Unit Price", "Total"]
        ]
        
        for item in line_items:
            table_data.append([
                item.description,
                str(item.quantity),
                f"KES {item.unit_price:,.2f}",
                f"KES {item.total:,.2f}"
            ])
        
        # Create table
        items_table = Table(
            table_data,
            colWidths=[3*inch, 0.8*inch, 1.2*inch, 1.2*inch]
        )
        
        items_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#374151')),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(items_table)
        
        return elements
    
    def _create_tax_breakdown(self, receipt: Receipt) -> List:
        """Create tax breakdown section"""
        elements = []
        
        tax = receipt.tax_breakdown
        
        # Tax breakdown table
        tax_data = [
            ["Subtotal:", f"KES {tax.subtotal:,.2f}"],
            [f"VAT ({int(tax.vat_rate * 100)}%):", f"KES {tax.vat_amount:,.2f}"],
            ["", ""],  # Empty row for spacing
            ["TOTAL:", f"KES {tax.total:,.2f}"],
        ]
        
        tax_table = Table(tax_data, colWidths=[3.5*inch, 2*inch])
        tax_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 1), 'Helvetica'),
            ('FONTNAME', (0, 3), (0, 3), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 2), 11),
            ('FONTSIZE', (0, 3), (-1, 3), 14),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('LINEABOVE', (0, 3), (-1, 3), 2, colors.HexColor('#1a56db')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        elements.append(tax_table)
        
        return elements
    
    def _create_qr_code(self, receipt: Receipt) -> List:
        """Create QR code section"""
        elements = []
        
        if not receipt.qr_code_data:
            return elements
        
        try:
            # Generate QR code
            qr_bytes = self.qr_generator.generate_qr_code(receipt.qr_code_data)
            
            # Create temporary image
            qr_img = Image(io.BytesIO(qr_bytes), width=1.5*inch, height=1.5*inch)
            
            # QR code text
            qr_text = Paragraph(
                "<i>Scan QR code to verify receipt</i>",
                self.body_style
            )
            
            elements.append(qr_img)
            elements.append(Spacer(1, 6))
            elements.append(qr_text)
            
        except Exception as e:
            print(f"Error generating QR code: {e}")
        
        return elements
    
    def _create_footer(self, receipt: Receipt) -> List:
        """Create PDF footer"""
        elements = []
        
        # Footer text
        footer_text = self.template.footer_text if self.template else "Thank you for your business!"
        footer = Paragraph(
            f"<i>{footer_text}</i>",
            self.body_style
        )
        elements.append(footer)
        
        # Generation timestamp
        timestamp_text = f"Generated on: {datetime.utcnow().strftime('%B %d, %Y %I:%M %p UTC')}"
        timestamp = Paragraph(
            f"<font size=8 color='#6b7280'>{timestamp_text}</font>",
            self.body_style
        )
        elements.append(Spacer(1, 6))
        elements.append(timestamp)
        
        # KRA compliance notice
        if receipt.business_kra_pin:
            kra_notice = Paragraph(
                "<font size=8 color='#6b7280'>This is a KRA-compliant receipt. Please retain for your records.</font>",
                self.body_style
            )
            elements.append(Spacer(1, 4))
            elements.append(kra_notice)
        
        return elements


# Example usage
if __name__ == "__main__":
    from .models import Receipt, CustomerInfo, PaymentMethod, ReceiptType, TaxBreakdown, LineItem
    
    # Create sample receipt
    receipt = Receipt(
        receipt_number="RCP-2025-0001",
        receipt_type=ReceiptType.PAYMENT,
        customer=CustomerInfo(
            name="John Doe",
            email="john@example.com",
            phone="0712345678",
            kra_pin="A123456789X"
        ),
        payment_method=PaymentMethod.MPESA,
        payment_date=datetime.utcnow(),
        tax_breakdown=TaxBreakdown(
            subtotal=10000.00,
            vat_amount=1600.00,
            total=11600.00
        ),
        line_items=[
            LineItem(
                description="Software Development Services",
                quantity=1,
                unit_price=10000.00,
                total=10000.00
            )
        ],
        business_name="FinGuard Business Solutions",
        business_kra_pin="P051234567U",
        business_address="Nairobi, Kenya",
        business_phone="0700123456",
        business_email="info@finguard.com",
        qr_code_data="RECEIPT:RCP-2025-0001\nAMOUNT:11600.00\nCUSTOMER:John Doe\nDATE:2025-01-12"
    )
    
    # Generate PDF
    generator = ReceiptPDFGenerator()
    pdf_bytes = generator.generate_receipt_pdf(receipt, "test_receipt.pdf")
    
    print(f"PDF generated: test_receipt.pdf ({len(pdf_bytes)} bytes)")
