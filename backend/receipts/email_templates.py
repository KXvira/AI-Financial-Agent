"""
Receipt Email Templates

HTML email templates for receipt delivery.
"""

from typing import Dict, Any


def get_receipt_email_template(receipt_data: Dict[str, Any]) -> str:
    """
    Generate HTML email template for receipt
    
    Args:
        receipt_data: Receipt information
        
    Returns:
        HTML email content
    """
    
    customer_name = receipt_data.get('customer_name', 'Valued Customer')
    receipt_number = receipt_data.get('receipt_number', 'N/A')
    amount = receipt_data.get('amount', 0.0)
    payment_date = receipt_data.get('payment_date', '')
    payment_method = receipt_data.get('payment_method', 'N/A')
    business_name = receipt_data.get('business_name', 'FinGuard Business')
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Receipt - {receipt_number}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 14px;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .greeting {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
        }}
        .message {{
            color: #4b5563;
            margin-bottom: 25px;
            line-height: 1.8;
        }}
        .receipt-details {{
            background-color: #f9fafb;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e5e7eb;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            font-weight: 600;
            color: #6b7280;
            font-size: 14px;
        }}
        .detail-value {{
            color: #1f2937;
            font-size: 14px;
        }}
        .amount-highlight {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            text-align: center;
            margin: 20px 0;
            font-size: 24px;
            font-weight: 700;
        }}
        .button {{
            display: inline-block;
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
            text-align: center;
        }}
        .button:hover {{
            opacity: 0.9;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 13px;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .footer a {{
            color: #1a56db;
            text-decoration: none;
        }}
        .divider {{
            height: 1px;
            background-color: #e5e7eb;
            margin: 20px 0;
        }}
        .info-box {{
            background-color: #eff6ff;
            border-left: 4px solid #1a56db;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .info-box p {{
            margin: 5px 0;
            color: #1e40af;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🧾 Payment Receipt</h1>
            <p>Your payment has been confirmed</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hello {customer_name},
            </div>
            
            <div class="message">
                Thank you for your payment. Your transaction has been successfully processed. 
                Please find your official receipt attached to this email.
            </div>
            
            <div class="amount-highlight">
                KES {amount:,.2f}
            </div>
            
            <div class="receipt-details">
                <div class="detail-row">
                    <span class="detail-label">Receipt Number:</span>
                    <span class="detail-value">{receipt_number}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Payment Date:</span>
                    <span class="detail-value">{payment_date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Payment Method:</span>
                    <span class="detail-value">{payment_method}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Amount Paid:</span>
                    <span class="detail-value">KES {amount:,.2f}</span>
                </div>
            </div>
            
            <div class="info-box">
                <p><strong>📎 Receipt Attached</strong></p>
                <p>Your official receipt PDF is attached to this email. Please keep it for your records.</p>
            </div>
            
            <div class="divider"></div>
            
            <p style="color: #6b7280; font-size: 14px;">
                If you have any questions or concerns about this transaction, 
                please don't hesitate to contact us.
            </p>
        </div>
        
        <div class="footer">
            <p><strong>{business_name}</strong></p>
            <p>This is an automated email. Please do not reply to this message.</p>
            <p>For support, contact us at support@finguard.com</p>
            <p style="margin-top: 15px; font-size: 12px;">
                &copy; 2025 {business_name}. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def get_receipt_text_template(receipt_data: Dict[str, Any]) -> str:
    """
    Generate plain text email template for receipt
    
    Args:
        receipt_data: Receipt information
        
    Returns:
        Plain text email content
    """
    
    customer_name = receipt_data.get('customer_name', 'Valued Customer')
    receipt_number = receipt_data.get('receipt_number', 'N/A')
    amount = receipt_data.get('amount', 0.0)
    payment_date = receipt_data.get('payment_date', '')
    payment_method = receipt_data.get('payment_method', 'N/A')
    business_name = receipt_data.get('business_name', 'FinGuard Business')
    
    text = f"""
PAYMENT RECEIPT
===============

Hello {customer_name},

Thank you for your payment. Your transaction has been successfully processed.
Please find your official receipt attached to this email.

RECEIPT DETAILS
---------------
Receipt Number: {receipt_number}
Payment Date:   {payment_date}
Payment Method: {payment_method}
Amount Paid:    KES {amount:,.2f}

TOTAL AMOUNT: KES {amount:,.2f}

Your official receipt PDF is attached to this email. Please keep it for your records.

If you have any questions or concerns about this transaction, please don't hesitate to contact us.

---
{business_name}
This is an automated email. Please do not reply to this message.
For support, contact us at support@finguard.com

© 2025 {business_name}. All rights reserved.
"""
    
    return text


def get_bulk_receipt_email_template(receipts_data: Dict[str, Any]) -> str:
    """
    Generate HTML email template for bulk receipts
    
    Args:
        receipts_data: Information about bulk receipts
        
    Returns:
        HTML email content
    """
    
    customer_name = receipts_data.get('customer_name', 'Valued Customer')
    receipt_count = receipts_data.get('receipt_count', 0)
    total_amount = receipts_data.get('total_amount', 0.0)
    business_name = receipts_data.get('business_name', 'FinGuard Business')
    receipts = receipts_data.get('receipts', [])
    
    receipts_html = ""
    for receipt in receipts:
        receipts_html += f"""
        <div class="detail-row">
            <span class="detail-label">{receipt.get('receipt_number', 'N/A')}</span>
            <span class="detail-value">KES {receipt.get('amount', 0.0):,.2f}</span>
        </div>
        """
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk Receipts</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f4;
        }}
        .email-container {{
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 600;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .greeting {{
            font-size: 18px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 15px;
        }}
        .message {{
            color: #4b5563;
            margin-bottom: 25px;
        }}
        .receipt-details {{
            background-color: #f9fafb;
            border-radius: 6px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e5e7eb;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        .detail-row:last-child {{
            border-bottom: none;
        }}
        .detail-label {{
            font-weight: 600;
            color: #6b7280;
            font-size: 14px;
        }}
        .detail-value {{
            color: #1f2937;
            font-size: 14px;
        }}
        .amount-highlight {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 15px 20px;
            border-radius: 6px;
            text-align: center;
            margin: 20px 0;
            font-size: 24px;
            font-weight: 700;
        }}
        .footer {{
            background-color: #f9fafb;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e5e7eb;
            color: #6b7280;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📦 Multiple Receipts</h1>
            <p>{receipt_count} receipts attached</p>
        </div>
        
        <div class="content">
            <div class="greeting">
                Hello {customer_name},
            </div>
            
            <div class="message">
                Please find {receipt_count} receipts attached to this email for your records.
            </div>
            
            <div class="amount-highlight">
                Total: KES {total_amount:,.2f}
            </div>
            
            <div class="receipt-details">
                <h3 style="margin-top: 0;">Included Receipts:</h3>
                {receipts_html}
            </div>
        </div>
        
        <div class="footer">
            <p><strong>{business_name}</strong></p>
            <p>&copy; 2025 {business_name}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html
