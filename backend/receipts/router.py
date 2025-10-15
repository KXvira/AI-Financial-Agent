"""
Receipt API Router

FastAPI endpoints for receipt generation and management.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Response, Body
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
from bson import ObjectId

from .models import (
    Receipt, ReceiptGenerateRequest, ReceiptType, ReceiptStatus,
    ReceiptListResponse, ReceiptStatistics, ReceiptTemplate
)
from .service import ReceiptService
from .templates_service import ReceiptTemplateService
from backend.database.mongodb import get_database, Database


router = APIRouter(prefix="/receipts", tags=["receipts"])


def get_receipt_service(db: Database = Depends(get_database)) -> ReceiptService:
    """Dependency to get receipt service"""
    return ReceiptService(db)


def get_template_service(db: Database = Depends(get_database)) -> ReceiptTemplateService:
    """Dependency to get template service"""
    return ReceiptTemplateService(db)


@router.post("/generate", response_model=Receipt, status_code=201)
async def generate_receipt(
    request: ReceiptGenerateRequest,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Generate a new receipt
    
    - **receipt_type**: Type of receipt (payment, invoice, refund, etc.)
    - **customer**: Customer information
    - **payment_method**: Payment method used
    - **amount**: Total amount (including VAT if include_vat=True)
    - **description**: Payment description (optional)
    - **include_vat**: Whether amount includes VAT (default: True)
    - **send_email**: Send receipt via email (default: False)
    """
    try:
        receipt = await service.generate_receipt(request)
        return receipt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating receipt: {str(e)}")


@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(
    receipt_id: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Get receipt by ID
    
    Returns receipt details including PDF path and QR code data.
    """
    receipt = await service.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    # Log audit event (viewed)
    await service._log_audit(
        receipt_id=receipt.id,
        receipt_number=receipt.receipt_number,
        action="viewed"
    )
    
    return receipt


@router.get("/number/{receipt_number}", response_model=Receipt)
async def get_receipt_by_number(
    receipt_number: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Get receipt by receipt number
    
    Returns receipt details by receipt number (e.g., RCP-2025-0001).
    """
    receipt = await service.get_receipt_by_number(receipt_number)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt


@router.get("/")
async def list_receipts(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    receipt_type: Optional[str] = Query(None, description="Filter by receipt type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    customer_id: Optional[str] = Query(None, description="Filter by customer ID"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    db: Database = Depends(get_database)
):
    """
    List receipts with filters
    
    Supports pagination and filtering by:
    - Receipt type (payment, invoice, refund, etc.)
    - Status (draft, generated, sent, viewed, downloaded, voided, issued)
    - Customer ID
    - Date range
    """
    try:
        # Build query
        query = {}
        if receipt_type:
            query["receipt_type"] = receipt_type
        if status:
            query["status"] = status
        if customer_id:
            query["customer_id"] = customer_id
        if start_date or end_date:
            query["issued_date"] = {}
            if start_date:
                query["issued_date"]["$gte"] = start_date
            if end_date:
                query["issued_date"]["$lte"] = end_date
        
        # Get total count
        total = await db.db.receipts.count_documents(query)
        
        # Calculate skip
        skip = (page - 1) * page_size
        
        # Get receipts
        cursor = db.db.receipts.find(query).sort("issued_date", -1).skip(skip).limit(page_size)
        
        receipts = []
        async for doc in cursor:
            # Convert ObjectId to string
            doc["_id"] = str(doc["_id"])
            # Convert dates to ISO format
            for date_field in ["issued_date", "created_at", "updated_at"]:
                if date_field in doc and doc[date_field]:
                    if isinstance(doc[date_field], datetime):
                        doc[date_field] = doc[date_field].isoformat()
            receipts.append(doc)
        
        return {
            "receipts": receipts,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listing receipts: {str(e)}")


@router.get("/{receipt_id}/download")
async def download_receipt(
    receipt_id: str,
    db: Database = Depends(get_database)
):
    """
    Download receipt PDF with professional formatting
    
    Generates a comprehensive receipt PDF with:
    - Company branding and logo
    - Professional layout with boxes and colors
    - Detailed payment breakdown
    - Terms and conditions
    - Multi-page support
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch, cm
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
        from reportlab.platypus import Frame, PageTemplate
        from io import BytesIO
        from datetime import datetime
        import qrcode
        from PIL import Image as PILImage
        
        # Get receipt from database
        receipt = await db.db.receipts.find_one({"_id": ObjectId(receipt_id)})
        if not receipt:
            raise HTTPException(status_code=404, detail="Receipt not found")
        
        # Create PDF in memory with better settings
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
            title=f"Receipt {receipt.get('receipt_number', 'N/A')}",
            author="FinGuard Financial Management System"
        )
        
        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a365d'),
            spaceAfter=30,
            alignment=1,  # Center
            fontName='Helvetica-Bold'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2d3748'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=6
        )
        
        # ==================== HEADER SECTION ====================
        # Company Logo/Branding (placeholder - you can add actual logo later)
        header_data = [
            [Paragraph("<b>FinGuard</b>", ParagraphStyle('LogoStyle', fontSize=28, textColor=colors.HexColor('#1a365d'), fontName='Helvetica-Bold'))],
            [Paragraph("<i>Financial Management System</i>", ParagraphStyle('TaglineStyle', fontSize=10, textColor=colors.HexColor('#718096'), fontName='Helvetica-Oblique'))]
        ]
        header_table = Table(header_data, colWidths=[6.5*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Main Title with border
        title_data = [[Paragraph("RECEIPT", title_style)]]
        title_table = Table(title_data, colWidths=[6.5*inch])
        title_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#1a365d')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#edf2f7')),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(title_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== QR CODE FOR VALIDATION ====================
        # Generate QR code with receipt information (not URL)
        receipt_number = receipt.get('receipt_number', 'N/A')
        receipt_date = receipt.get('issued_date', receipt.get('created_at', 'N/A'))
        if isinstance(receipt_date, str) and len(receipt_date) > 10:
            try:
                receipt_date = datetime.fromisoformat(receipt_date.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        customer_name = receipt.get('customer_name', 'N/A')
        amount = receipt.get('amount', 0)
        payment_method = receipt.get('payment_method', 'N/A')
        status = receipt.get('status', 'N/A')
        transaction_ref = receipt.get('transaction_reference', 'N/A')
        
        # Create QR code data with receipt details
        qr_data_text = f"""RECEIPT: {receipt_number}
DATE: {receipt_date}
CUSTOMER: {customer_name}
AMOUNT: KES {amount:,.2f}
PAYMENT METHOD: {payment_method.upper()}
STATUS: {status.upper()}
TRANSACTION REF: {transaction_ref}
VERIFY AT: https://finguard.com/verify/{receipt_number}"""
        
        # Create QR code
        qr = qrcode.QRCode(
            version=2,  # Increased version for more data
            error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium error correction for more data
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data_text)
        qr.make(fit=True)
        
        # Generate QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to ReportLab Image
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_image = Image(qr_buffer, width=1.2*inch, height=1.2*inch)
        
        # Create QR code section with text
        qr_text_style = ParagraphStyle(
            'QRTextStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#4a5568'),
            alignment=1  # Center
        )
        
        qr_data = [
            [qr_image, 
             [Paragraph("<b>Scan to View Details</b>", ParagraphStyle('QRTitle', fontSize=10, fontName='Helvetica-Bold', alignment=1)),
              Paragraph(f"Receipt: {receipt_number}", qr_text_style),
              Paragraph("Scan this QR code to view", qr_text_style),
              Paragraph("complete receipt information", qr_text_style),
              Paragraph("(customer, amount, date, etc.)", qr_text_style)]
            ]
        ]
        qr_table = Table(qr_data, colWidths=[1.5*inch, 5*inch])
        qr_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(qr_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== RECEIPT INFO SECTION ====================
        receipt_date = receipt.get('issued_date', receipt.get('created_at', 'N/A'))
        if isinstance(receipt_date, str) and len(receipt_date) > 10:
            try:
                receipt_date = datetime.fromisoformat(receipt_date.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        receipt_info_data = [
            [Paragraph("<b>Receipt Number:</b>", normal_style), Paragraph(str(receipt.get('receipt_number', 'N/A')), normal_style)],
            [Paragraph("<b>Date:</b>", normal_style), Paragraph(str(receipt_date), normal_style)],
            [Paragraph("<b>Status:</b>", normal_style), Paragraph(f"<b>{receipt.get('status', 'N/A').upper()}</b>", normal_style)],
        ]
        receipt_info_table = Table(receipt_info_data, colWidths=[2*inch, 4.5*inch])
        receipt_info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(receipt_info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== CUSTOMER INFORMATION ====================
        elements.append(Paragraph("Customer Information:", heading_style))
        customer_data = [
            [Paragraph("<b>Name:</b>", normal_style), Paragraph(str(receipt.get('customer_name', 'N/A')), normal_style)],
            [Paragraph("<b>Phone:</b>", normal_style), Paragraph(str(receipt.get('customer_phone', 'N/A')), normal_style)],
            [Paragraph("<b>Email:</b>", normal_style), Paragraph(str(receipt.get('customer_email', 'N/A')), normal_style)],
        ]
        customer_table = Table(customer_data, colWidths=[2*inch, 4.5*inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== PAYMENT DETAILS ====================
        elements.append(Paragraph("Payment Details:", heading_style))
        
        amount = receipt.get('amount', 0)
        payment_data = [
            [Paragraph("<b>Amount:</b>", normal_style), Paragraph(f"<b>KES {amount:,.2f}</b>", ParagraphStyle('AmountStyle', fontSize=14, textColor=colors.HexColor('#2f855a'), fontName='Helvetica-Bold'))],
            [Paragraph("<b>Payment Method:</b>", normal_style), Paragraph(str(receipt.get('payment_method', 'N/A')).upper(), normal_style)],
            [Paragraph("<b>Transaction Reference:</b>", normal_style), Paragraph(str(receipt.get('transaction_reference', 'N/A')), normal_style)],
            [Paragraph("<b>Description:</b>", normal_style), Paragraph(str(receipt.get('description', 'Payment received')), normal_style)],
        ]
        payment_table = Table(payment_data, colWidths=[2*inch, 4.5*inch])
        payment_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f7fafc')),
            ('BACKGROUND', (1, 0), (1, 0), colors.HexColor('#c6f6d5')),  # Highlight amount
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(payment_table)
        elements.append(Spacer(1, 0.4*inch))
        
        # ==================== PAYMENT BREAKDOWN (if available) ====================
        if receipt.get('tax_breakdown'):
            elements.append(Paragraph("Payment Breakdown:", heading_style))
            tax_breakdown = receipt.get('tax_breakdown', {})
            
            breakdown_data = [
                [Paragraph("<b>Description</b>", normal_style), Paragraph("<b>Amount (KES)</b>", normal_style)],
                [Paragraph("Subtotal", normal_style), Paragraph(f"{tax_breakdown.get('subtotal', 0):,.2f}", normal_style)],
                [Paragraph(f"Tax ({tax_breakdown.get('tax_rate', 0)}%)", normal_style), Paragraph(f"{tax_breakdown.get('tax_amount', 0):,.2f}", normal_style)],
                [Paragraph("<b>Total</b>", ParagraphStyle('TotalStyle', fontSize=12, fontName='Helvetica-Bold')), Paragraph(f"<b>{tax_breakdown.get('total', 0):,.2f}</b>", ParagraphStyle('TotalStyle', fontSize=12, fontName='Helvetica-Bold'))],
            ]
            breakdown_table = Table(breakdown_data, colWidths=[4*inch, 2.5*inch])
            breakdown_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))
            elements.append(breakdown_table)
            elements.append(Spacer(1, 0.4*inch))
        
        # ==================== PAGE BREAK IF NEEDED ====================
        # Add page break for terms and conditions on second page
        elements.append(PageBreak())
        
        # ==================== TERMS & CONDITIONS (Page 2) ====================
        elements.append(Paragraph("Terms and Conditions:", heading_style))
        
        terms_text = """
        <b>1. Payment Confirmation:</b><br/>
        This receipt confirms that payment has been received and processed. Please retain this receipt for your records.<br/><br/>
        
        <b>2. Refund Policy:</b><br/>
        Refunds may be requested within 30 days of payment. Please contact our support team with your receipt number for refund processing.<br/><br/>
        
        <b>3. Validity:</b><br/>
        This receipt is valid and serves as proof of payment. It may be required for accounting, tax, or audit purposes.<br/><br/>
        
        <b>4. Contact Information:</b><br/>
        For any queries regarding this receipt, please contact:<br/>
        • Email: support@finguard.com<br/>
        • Phone: +254 700 000 000<br/>
        • Website: www.finguard.com<br/><br/>
        
        <b>5. Data Privacy:</b><br/>
        Your information is protected under our privacy policy. We do not share your data with third parties without consent.<br/><br/>
        
        <b>6. Authenticity & QR Code Verification:</b><br/>
        This is a computer-generated receipt and does not require a physical signature. You can verify its authenticity by:<br/>
        • Scanning the QR code on page 1 with your smartphone - it contains all receipt details including customer name, amount, date, payment method, and transaction reference<br/>
        • Visiting www.finguard.com/verify/{receipt_number} for online verification<br/>
        • Contacting our support team with the receipt number<br/>
        The QR code contains embedded receipt information that can be read by any QR scanner without internet connection.
        """
        
        terms_style = ParagraphStyle(
            'TermsStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=6,
            leading=12
        )
        elements.append(Paragraph(terms_text, terms_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # ==================== FOOTER ====================
        footer_data = [
            [Paragraph("<b>Thank you for your business!</b>", ParagraphStyle('FooterBold', fontSize=12, textColor=colors.HexColor('#1a365d'), fontName='Helvetica-Bold', alignment=1))],
            [Paragraph("FinGuard - Financial Management System", ParagraphStyle('FooterNormal', fontSize=9, textColor=colors.HexColor('#718096'), fontName='Helvetica-Oblique', alignment=1))],
            [Paragraph("Empowering Your Financial Success", ParagraphStyle('FooterTagline', fontSize=8, textColor=colors.HexColor('#a0aec0'), fontName='Helvetica-Oblique', alignment=1))],
        ]
        footer_table = Table(footer_data, colWidths=[6.5*inch])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LINEABOVE', (0, 0), (-1, 0), 1, colors.HexColor('#cbd5e0')),
        ]))
        elements.append(footer_table)
        
        # Build PDF
        doc.build(elements)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Return PDF
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={receipt.get('receipt_number', 'receipt')}.pdf"
            }
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.post("/{receipt_id}/void", response_model=Receipt)
async def void_receipt(
    receipt_id: str,
    reason: str = Query(..., description="Reason for voiding receipt"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Void a receipt
    
    Marks a receipt as voided. Receipts cannot be deleted for KRA compliance,
    but can be voided with a reason.
    
    - **reason**: Reason for voiding the receipt (required)
    """
    receipt = await service.void_receipt(receipt_id, reason)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    
    return receipt


@router.post("/{receipt_id}/email")
async def email_receipt(
    receipt_id: str,
    email: Optional[str] = Query(None, description="Override email address"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Send receipt via email
    
    Sends the receipt PDF to the customer's email address.
    Optionally override the email address.
    
    - **email**: Optional email override (uses customer email if not provided)
    """
    try:
        result = await service.send_receipt_email(receipt_id, email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


@router.get("/statistics/summary")
async def get_statistics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Database = Depends(get_database)
):
    """
    Get receipt statistics
    
    Returns statistical analysis of receipts including:
    - Total receipts
    - Breakdown by type and status
    - Financial totals
    
    - **days**: Number of days to analyze (default: 30)
    """
    try:
        # Get statistics from our generated data
        total_receipts = await db.db.receipts.count_documents({})
        payment_receipts = await db.db.receipts.count_documents({"receipt_type": "payment"})
        invoice_receipts = await db.db.receipts.count_documents({"receipt_type": "invoice"})
        
        # Calculate total amount
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = await db.db.receipts.aggregate(pipeline).to_list(None)
        total_amount = result[0]['total'] if result else 0.0
        
        return {
            "total_receipts": total_receipts,
            "payment_receipts": payment_receipts,
            "invoice_receipts": invoice_receipts,
            "total_amount": total_amount,
            "average_amount": total_amount / total_receipts if total_receipts > 0 else 0.0,
            "receipts_by_type": {
                "payment": payment_receipts,
                "invoice": invoice_receipts
            },
            "receipts_by_status": {}  # Can be populated later if needed
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return default statistics if there's an error
        return {
            "total_receipts": 0,
            "payment_receipts": 0,
            "invoice_receipts": 0,
            "total_amount": 0.0,
            "average_amount": 0.0,
            "receipts_by_type": {
                "payment": 0,
                "invoice": 0
            },
            "receipts_by_status": {}
        }


@router.post("/bulk-generate")
async def bulk_generate_receipts(
    requests: List[ReceiptGenerateRequest],
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Generate multiple receipts in bulk
    
    Accepts a list of receipt generation requests and creates all receipts.
    Returns list of generated receipt IDs and any errors.
    
    - **requests**: List of receipt generation requests
    """
    results = {
        "success": [],
        "errors": []
    }
    
    for idx, request in enumerate(requests):
        try:
            receipt = await service.generate_receipt(request)
            results["success"].append({
                "index": idx,
                "receipt_id": receipt.id,
                "receipt_number": receipt.receipt_number
            })
        except Exception as e:
            results["errors"].append({
                "index": idx,
                "error": str(e)
            })
    
    return {
        "total_requested": len(requests),
        "total_success": len(results["success"]),
        "total_errors": len(results["errors"]),
        "results": results
    }


@router.post("/bulk-email")
async def bulk_email_receipts(
    receipt_ids: List[str] = Body(..., description="List of receipt IDs to email"),
    email: str = Body(..., description="Recipient email address"),
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Send multiple receipts in one email
    
    Sends multiple receipt PDFs attached to a single email.
    Useful for sending monthly statements or multiple transactions.
    
    - **receipt_ids**: List of receipt IDs to include
    - **email**: Recipient email address
    """
    try:
        result = await service.send_bulk_receipts_email(receipt_ids, email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending bulk email: {str(e)}")


@router.get("/verify/{receipt_number}")
async def verify_receipt(
    receipt_number: str,
    service: ReceiptService = Depends(get_receipt_service)
):
    """
    Verify receipt authenticity
    
    Verifies that a receipt number exists and returns basic details.
    Used for QR code verification.
    
    - **receipt_number**: Receipt number to verify (e.g., RCP-2025-0001)
    """
    receipt = await service.get_receipt_by_number(receipt_number)
    if not receipt:
        return {
            "valid": False,
            "message": "Receipt not found"
        }
    
    if receipt.status == ReceiptStatus.VOIDED:
        return {
            "valid": False,
            "message": "Receipt has been voided",
            "voided_at": receipt.voided_at,
            "void_reason": receipt.void_reason
        }
    
    return {
        "valid": True,
        "receipt_number": receipt.receipt_number,
        "customer_name": receipt.customer.name,
        "amount": receipt.tax_breakdown.total,
        "payment_date": receipt.payment_date,
        "status": receipt.status
    }


# =============================================================================
# RECEIPT TEMPLATE ENDPOINTS
# =============================================================================

@router.get("/templates/", tags=["templates"])
async def list_templates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    List all receipt templates
    
    Returns available templates for receipt customization.
    """
    result = await service.list_templates(
        page=page,
        page_size=page_size,
        is_active=is_active
    )
    return result


@router.post("/templates/", response_model=ReceiptTemplate, status_code=201, tags=["templates"])
async def create_template(
    template: ReceiptTemplate,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Create a new receipt template
    
    Creates a custom receipt template with branding and styling options.
    """
    try:
        created = await service.create_template(template)
        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")


@router.get("/templates/{template_id}", response_model=ReceiptTemplate, tags=["templates"])
async def get_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Get template by ID
    
    Returns template details for customization.
    """
    template = await service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.put("/templates/{template_id}", response_model=ReceiptTemplate, tags=["templates"])
async def update_template(
    template_id: str,
    updates: Dict[str, Any] = Body(..., description="Fields to update"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Update a receipt template
    
    Updates template settings and styling options.
    """
    template = await service.update_template(template_id, updates)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/templates/{template_id}", tags=["templates"])
async def delete_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Delete a receipt template
    
    Soft deletes a template by marking it as inactive.
    """
    success = await service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"success": True, "message": "Template deleted successfully"}


@router.get("/templates/default/get", response_model=ReceiptTemplate, tags=["templates"])
async def get_default_template(
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Get the default receipt template
    
    Returns the currently active default template.
    """
    template = await service.get_default_template()
    if not template:
        raise HTTPException(status_code=404, detail="No default template found")
    return template


@router.post("/templates/{template_id}/set-default", response_model=ReceiptTemplate, tags=["templates"])
async def set_default_template(
    template_id: str,
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Set a template as default
    
    Makes this template the default for all new receipts.
    """
    template = await service.set_default_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/templates/seed/defaults", tags=["templates"])
async def seed_default_templates(
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Seed default receipt templates
    
    Creates default templates if none exist.
    """
    templates = await service.seed_default_templates()
    return {
        "success": True,
        "message": f"Created {len(templates)} default templates" if templates else "Templates already exist",
        "templates_created": len(templates)
    }


@router.post("/templates/{template_id}/duplicate", response_model=ReceiptTemplate, tags=["templates"])
async def duplicate_template(
    template_id: str,
    new_name: str = Query(..., description="Name for the duplicated template"),
    service: ReceiptTemplateService = Depends(get_template_service)
):
    """
    Duplicate an existing template
    
    Creates a copy of a template with a new name.
    """
    template = await service.duplicate_template(template_id, new_name)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


# Simple list endpoint for generated receipts
@router.get("/simple/list")
async def list_simple_receipts(
    limit: int = Query(20, ge=1, le=100),
    page: int = Query(1, ge=1),
    receipt_type: Optional[str] = Query(None),
    db: Database = Depends(get_database)
):
    """
    Simple endpoint to list generated receipts
    Works with our generated receipt data structure
    """
    try:
        # Build query
        query = {}
        if receipt_type:
            query["receipt_type"] = receipt_type
        
        # Get total count
        total = await db.db.receipts.count_documents(query)
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Get receipts
        cursor = db.db.receipts.find(query).sort("issued_date", -1).skip(skip).limit(limit)
        
        receipts = []
        async for doc in cursor:
            # Convert ObjectId to string
            doc["_id"] = str(doc["_id"])
            # Convert dates to ISO format
            for date_field in ["issued_date", "created_at", "updated_at"]:
                if date_field in doc and doc[date_field]:
                    if isinstance(doc[date_field], datetime):
                        doc[date_field] = doc[date_field].isoformat()
            receipts.append(doc)
        
        return {
            "receipts": receipts,
            "total": total,
            "page": page,
            "page_size": limit
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error listing receipts: {str(e)}")
