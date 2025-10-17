"""
Seed script to create sample receipts with PDFs
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.mongodb import connect_to_mongodb, close_mongodb_connection, get_database
from receipts.models import (
    ReceiptGenerateRequest, ReceiptType, PaymentMethod,
    CustomerInfo, LineItem
)
from receipts.service import ReceiptService


async def seed_receipts():
    """Create sample receipts"""
    print("🌱 Starting receipt seeding...")
    
    # Connect to database
    await connect_to_mongodb()
    db = get_database()
    
    # Create receipt service
    receipt_service = ReceiptService(db)
    
    # Sample receipts data
    sample_receipts = [
        {
            "receipt_type": ReceiptType.PAYMENT,
            "customer": CustomerInfo(
                name="KCB Bank - Ltd",
                email="finance@kcb.co.ke",
                phone="+254712345678",
                kra_pin="P051234567Z"
            ),
            "payment_method": PaymentMethod.MPESA,
            "amount": 125000.00,
            "description": "Payment for consulting services - January 2025",
            "payment_date": datetime.now() - timedelta(days=5)
        },
        {
            "receipt_type": ReceiptType.PAYMENT,
            "customer": CustomerInfo(
                name="Twiga Foods",
                email="accounts@twiga.com",
                phone="+254722334455",
                kra_pin="P051111111A"
            ),
            "payment_method": PaymentMethod.BANK_TRANSFER,
            "amount": 89500.00,
            "description": "Invoice INV-2025-045 payment",
            "payment_date": datetime.now() - timedelta(days=3)
        },
        {
            "receipt_type": ReceiptType.PARTIAL_PAYMENT,
            "customer": CustomerInfo(
                name="Safaricom PLC",
                email="billing@safaricom.co.ke",
                phone="+254700000000",
                kra_pin="P051999999B"
            ),
            "payment_method": PaymentMethod.MPESA,
            "amount": 45000.00,
            "description": "Partial payment for monthly IT support services",
            "payment_date": datetime.now() - timedelta(days=7)
        },
        {
            "receipt_type": ReceiptType.PAYMENT,
            "customer": CustomerInfo(
                name="Equity Bank",
                email="corporate@equitybank.co.ke",
                phone="+254733445566",
                kra_pin="P051222222C"
            ),
            "payment_method": PaymentMethod.CASH,
            "amount": 67800.00,
            "description": "Software licensing fees Q1 2025",
            "payment_date": datetime.now() - timedelta(days=10)
        },
        {
            "receipt_type": ReceiptType.INVOICE,
            "customer": CustomerInfo(
                name="Nation Media Group",
                email="procurement@nationmedia.com",
                phone="+254799887766",
                kra_pin="P051333333D"
            ),
            "payment_method": PaymentMethod.BANK_TRANSFER,
            "amount": 156000.00,
            "description": "Digital marketing campaign - February 2025",
            "payment_date": datetime.now() - timedelta(days=2)
        },
        {
            "receipt_type": ReceiptType.REFUND,
            "customer": CustomerInfo(
                name="Co-operative Bank",
                email="refunds@co-opbank.co.ke",
                phone="+254711223344",
                kra_pin="P051444444E"
            ),
            "payment_method": PaymentMethod.MPESA,
            "amount": 23400.00,
            "description": "Refund for overpayment - Invoice INV-2025-033",
            "payment_date": datetime.now() - timedelta(days=12)
        },
        {
            "receipt_type": ReceiptType.PAYMENT,
            "customer": CustomerInfo(
                name="Standard Chartered Bank",
                email="payments@sc.com",
                phone="+254788990011",
                kra_pin="P051555555F"
            ),
            "payment_method": PaymentMethod.CARD,
            "amount": 198000.00,
            "description": "Annual software subscription renewal",
            "payment_date": datetime.now() - timedelta(days=1)
        },
        {
            "receipt_type": ReceiptType.EXPENSE,
            "customer": CustomerInfo(
                name="Office Depot Kenya",
                email="sales@officedepot.co.ke",
                phone="+254766554433",
                kra_pin="P051666666G"
            ),
            "payment_method": PaymentMethod.CASH,
            "amount": 12800.00,
            "description": "Office supplies purchase - stationery and equipment",
            "payment_date": datetime.now() - timedelta(days=15)
        },
        {
            "receipt_type": ReceiptType.PAYMENT,
            "customer": CustomerInfo(
                name="NCBA Group",
                email="finance@ncbagroup.com",
                phone="+254744332211",
                kra_pin="P051777777H"
            ),
            "payment_method": PaymentMethod.MPESA,
            "amount": 234500.00,
            "description": "Full payment for website development project",
            "payment_date": datetime.now() - timedelta(days=20)
        },
        {
            "receipt_type": ReceiptType.PARTIAL_PAYMENT,
            "customer": CustomerInfo(
                name="Diamond Trust Bank",
                email="corporate@dtbafrica.com",
                phone="+254722998877",
                kra_pin="P051888888I"
            ),
            "payment_method": PaymentMethod.BANK_TRANSFER,
            "amount": 78900.00,
            "description": "Partial payment (50%) for mobile app development",
            "payment_date": datetime.now() - timedelta(days=8)
        },
    ]
    
    created_receipts = []
    
    for i, receipt_data in enumerate(sample_receipts, 1):
        try:
            print(f"\n📝 Creating receipt {i}/{len(sample_receipts)}: {receipt_data['customer'].name}")
            
            # Create receipt request
            request = ReceiptGenerateRequest(
                receipt_type=receipt_data["receipt_type"],
                customer=receipt_data["customer"],
                payment_method=receipt_data["payment_method"],
                amount=receipt_data["amount"],
                description=receipt_data["description"],
                payment_date=receipt_data["payment_date"],
                include_vat=True,
                send_email=False  # Don't send emails during seeding
            )
            
            # Generate receipt (includes PDF generation)
            receipt = await receipt_service.generate_receipt(request)
            
            created_receipts.append(receipt)
            print(f"   ✅ Created: {receipt.receipt_number}")
            print(f"   💰 Amount: KES {receipt.tax_breakdown.total:,.2f}")
            print(f"   📄 PDF: {receipt.pdf_path}")
            
        except Exception as e:
            print(f"   ❌ Error creating receipt: {str(e)}")
            continue
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"🎉 Seeding Complete!")
    print(f"{'='*60}")
    print(f"✅ Created {len(created_receipts)} receipts")
    print(f"💰 Total Amount: KES {sum(r.tax_breakdown.total for r in created_receipts):,.2f}")
    print(f"\n📊 Receipt Types:")
    
    type_counts = {}
    for receipt in created_receipts:
        receipt_type = receipt.receipt_type.value
        type_counts[receipt_type] = type_counts.get(receipt_type, 0) + 1
    
    for receipt_type, count in type_counts.items():
        print(f"   - {receipt_type.upper()}: {count}")
    
    print(f"\n📁 PDFs stored in: storage/receipts/")
    print(f"\nYou can now view receipts at: http://localhost:3000/receipts")
    
    # Close database connection
    await close_mongodb_connection()


if __name__ == "__main__":
    asyncio.run(seed_receipts())
