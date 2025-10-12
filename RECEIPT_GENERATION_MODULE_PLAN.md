# Receipt Generation Module - Implementation Plan 🧾

**Created**: January 12, 2025  
**Module Type**: Document Generation & Management  
**Priority**: High  
**Estimated Timeline**: 2-3 weeks

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Objectives](#objectives)
3. [Technical Architecture](#technical-architecture)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Frontend Components](#frontend-components)
7. [Implementation Phases](#implementation-phases)
8. [Integration Points](#integration-points)
9. [Testing Strategy](#testing-strategy)
10. [Security & Compliance](#security--compliance)

---

## 🎯 Overview

### What is the Receipt Generation Module?

A comprehensive system that automatically generates, manages, and delivers professional receipts for:
- **Payment Confirmations** - When customers make payments (M-Pesa, Bank, Cash)
- **Invoice Payments** - When invoices are marked as paid
- **Refunds** - When refunds are processed
- **Partial Payments** - For installment payments
- **Expense Documentation** - For internal expense tracking

### Why is it Important?

1. **Legal Compliance**: Kenyan tax law requires proper receipt documentation (KRA compliance)
2. **Customer Trust**: Professional receipts build credibility
3. **Record Keeping**: Audit trail for all financial transactions
4. **Automation**: Reduces manual work and errors
5. **Integration**: Works with existing payment, invoice, and customer systems

---

## 🎯 Objectives

### Primary Goals
- ✅ Generate professional, KRA-compliant receipts automatically
- ✅ Support multiple receipt types (payment, refund, invoice, expense)
- ✅ Provide PDF download and email delivery
- ✅ Include QR codes for verification
- ✅ Maintain audit trail and version history
- ✅ Support template customization (letterhead, colors, branding)

### Secondary Goals
- ✅ Bulk receipt generation for multiple transactions
- ✅ Receipt preview before generation
- ✅ Receipt search and filtering
- ✅ Analytics and reporting on receipts
- ✅ Integration with email service for automatic sending
- ✅ Receipt numbering with custom prefixes

---

## 🏗️ Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Receipt Generation Flow                   │
└─────────────────────────────────────────────────────────────┘

1. TRIGGER EVENT
   ├── Payment Completed (M-Pesa, Bank, Cash)
   ├── Invoice Marked as Paid
   ├── Refund Processed
   └── Manual Receipt Request

2. RECEIPT SERVICE
   ├── Validate Transaction Data
   ├── Generate Receipt Number
   ├── Apply Template
   ├── Calculate Totals & Tax
   └── Generate QR Code

3. PDF GENERATION
   ├── Use ReportLab or WeasyPrint
   ├── Apply Branding (Logo, Colors)
   ├── Include QR Code for Verification
   └── Add Watermark (if needed)

4. STORAGE & DELIVERY
   ├── Save to MongoDB (metadata)
   ├── Store PDF in filesystem/S3
   ├── Send Email (optional)
   └── Provide Download Link

5. AUDIT & COMPLIANCE
   ├── Log Generation Event
   ├── Track View/Download History
   └── Maintain Version History
```

### Technology Stack

**Backend:**
- **Python 3.10+** - Core language
- **FastAPI** - REST API framework
- **ReportLab** or **WeasyPrint** - PDF generation
- **Pillow (PIL)** - Image processing
- **qrcode** - QR code generation
- **Motor** - Async MongoDB driver
- **Jinja2** - HTML templating

**Frontend:**
- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React-PDF** - PDF preview
- **Lucide Icons** - Icons

**Storage:**
- **MongoDB** - Receipt metadata and audit logs
- **Local Filesystem / AWS S3** - PDF storage

---

## 🗄️ Database Schema

### 1. Receipts Collection

```javascript
{
  _id: ObjectId,
  receipt_id: "RCP-2025-0001",      // Unique receipt number
  receipt_number: "RCP-2025-0001",   // Same as receipt_id
  
  // Receipt Type
  type: "payment",                    // payment, refund, invoice, expense
  category: "customer_payment",       // customer_payment, supplier_payment, refund, etc.
  
  // Transaction Reference
  transaction_id: String,             // Reference to transaction
  invoice_id: String,                 // Reference to invoice (if applicable)
  payment_id: String,                 // Reference to payment
  
  // Financial Details
  amount: 50000.00,
  currency: "KES",
  payment_method: "mpesa",            // mpesa, bank, cash, card
  mpesa_code: "RK12ABC345",          // M-Pesa confirmation code
  
  // Tax Information (KRA Compliance)
  subtotal: 43103.45,
  vat_rate: 0.16,                    // 16% VAT
  vat_amount: 6896.55,
  total: 50000.00,
  
  // Parties
  from: {                             // Payer
    type: "customer",                 // customer, supplier, internal
    id: "CUST-0001",
    name: "Tech Solutions Ltd",
    email: "info@techsolutions.com",
    phone: "254712345678",
    address: "Westlands, Nairobi",
    tax_id: "P051234567A"            // KRA PIN
  },
  
  to: {                               // Recipient (Your Business)
    business_name: "Fin Guard Systems",
    email: "accounts@finguard.com",
    phone: "254700000000",
    address: "CBD, Nairobi, Kenya",
    tax_id: "P051234567B",           // Your KRA PIN
    postal_address: "P.O. Box 12345, Nairobi"
  },
  
  // Receipt Details
  issue_date: ISODate("2025-01-12"),
  issue_time: "14:30:00",
  description: "Payment for Invoice INV-2025-0045",
  items: [                            // Optional: Itemized breakdown
    {
      description: "Web Development Service",
      quantity: 1,
      unit_price: 43103.45,
      vat: 6896.55,
      total: 50000.00
    }
  ],
  notes: "Thank you for your payment",
  
  // Template & Branding
  template_id: "TMPL-DEFAULT",
  template_name: "Standard Receipt",
  include_logo: true,
  include_qr_code: true,
  include_watermark: false,
  
  // PDF Information
  pdf_path: "/receipts/2025/01/RCP-2025-0001.pdf",
  pdf_url: "https://storage.finguard.com/receipts/RCP-2025-0001.pdf",
  pdf_size: 145678,                   // bytes
  pdf_generated_at: ISODate("2025-01-12T14:30:05"),
  
  // QR Code (for verification)
  qr_code_data: "https://verify.finguard.com/receipt/RCP-2025-0001",
  qr_code_path: "/qr_codes/RCP-2025-0001.png",
  
  // Status & Workflow
  status: "generated",                // draft, generated, sent, viewed, printed
  is_void: false,
  void_reason: null,
  void_date: null,
  
  // Delivery
  sent_via_email: true,
  email_sent_at: ISODate("2025-01-12T14:30:10"),
  email_status: "delivered",
  download_count: 3,
  view_count: 5,
  print_count: 1,
  
  // Compliance & Audit
  generated_by: "system",             // system, user_id
  generated_method: "automatic",      // automatic, manual
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  
  // Version Control
  version: 1,
  previous_version_id: null,
  is_latest: true,
  
  // Metadata
  created_at: ISODate("2025-01-12T14:30:00"),
  updated_at: ISODate("2025-01-12T14:30:00"),
  created_by: "user_id_or_system",
  
  // Search & Filtering
  tags: ["payment", "mpesa", "customer"],
  fiscal_year: 2025,
  fiscal_quarter: "Q1",
  fiscal_month: "January"
}
```

### 2. Receipt Templates Collection

```javascript
{
  _id: ObjectId,
  template_id: "TMPL-DEFAULT",
  name: "Standard Receipt",
  description: "Default receipt template for all transactions",
  
  // Template Type
  type: "receipt",                    // receipt, invoice, quotation
  category: "payment",                // payment, refund, expense
  
  // Layout Configuration
  layout: {
    page_size: "A4",                  // A4, Letter
    orientation: "portrait",          // portrait, landscape
    margins: {
      top: 20,
      bottom: 20,
      left: 15,
      right: 15
    }
  },
  
  // Header Configuration
  header: {
    include_logo: true,
    logo_position: "left",            // left, center, right
    logo_width: 150,                  // pixels
    include_company_details: true,
    title: "RECEIPT",
    title_font_size: 24,
    title_color: "#2563eb",
    background_color: "#f3f4f6"
  },
  
  // Body Configuration
  body: {
    sections: [
      "receipt_details",              // Receipt number, date, etc.
      "parties",                      // From/To information
      "transaction_details",          // Amount, payment method
      "itemized_breakdown",           // Optional items list
      "tax_summary",                  // VAT breakdown
      "notes"                         // Additional notes
    ],
    show_qr_code: true,
    qr_code_position: "top-right",
    show_watermark: false,
    watermark_text: "PAID"
  },
  
  // Footer Configuration
  footer: {
    include_footer: true,
    text: "This is a computer-generated receipt and does not require a signature.",
    include_terms: true,
    terms_text: "All payments are non-refundable unless otherwise stated.",
    include_contact: true,
    show_page_numbers: true
  },
  
  // Styling
  styles: {
    primary_color: "#2563eb",
    secondary_color: "#64748b",
    accent_color: "#f59e0b",
    font_family: "Helvetica",
    font_size: 10,
    line_height: 1.5,
    border_color: "#e5e7eb"
  },
  
  // Status
  is_default: true,
  is_active: true,
  is_public: true,
  
  // Usage Statistics
  usage_count: 1245,
  last_used: ISODate("2025-01-12"),
  
  // Metadata
  created_at: ISODate("2025-01-01"),
  updated_at: ISODate("2025-01-12"),
  created_by: "admin_user_id"
}
```

### 3. Receipt Audit Log Collection

```javascript
{
  _id: ObjectId,
  receipt_id: "RCP-2025-0001",
  
  // Event Information
  event_type: "viewed",               // generated, viewed, downloaded, printed, emailed, voided
  event_timestamp: ISODate("2025-01-12T15:30:00"),
  
  // User Information
  user_id: "user_id",
  user_name: "John Doe",
  user_email: "john@example.com",
  user_role: "customer",
  
  // Technical Details
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  device_type: "desktop",             // desktop, mobile, tablet
  browser: "Chrome",
  
  // Event-Specific Data
  event_data: {
    download_format: "pdf",           // For download events
    email_recipient: "customer@example.com",  // For email events
    void_reason: "Duplicate payment"  // For void events
  },
  
  // Metadata
  created_at: ISODate("2025-01-12T15:30:00")
}
```

### 4. Receipt Sequences Collection

```javascript
{
  _id: ObjectId,
  year: 2025,
  prefix: "RCP",
  last_number: 1234,
  format: "RCP-YYYY-####",           // Format pattern
  
  created_at: ISODate("2025-01-01"),
  updated_at: ISODate("2025-01-12")
}
```

---

## 🔌 API Endpoints

### Receipt Generation Endpoints

#### 1. Generate Receipt
```http
POST /receipts/generate
Content-Type: application/json

{
  "transaction_id": "txn_12345",
  "type": "payment",
  "amount": 50000.00,
  "currency": "KES",
  "payment_method": "mpesa",
  "mpesa_code": "RK12ABC345",
  "customer_id": "CUST-0001",
  "invoice_id": "INV-2025-0045",
  "send_email": true,
  "template_id": "TMPL-DEFAULT"
}

Response: 201 Created
{
  "success": true,
  "receipt_id": "RCP-2025-0001",
  "pdf_url": "https://api.finguard.com/receipts/RCP-2025-0001/download",
  "qr_code_url": "https://verify.finguard.com/receipt/RCP-2025-0001",
  "email_sent": true,
  "message": "Receipt generated and sent successfully"
}
```

#### 2. Get Receipt Details
```http
GET /receipts/{receipt_id}

Response: 200 OK
{
  "receipt_id": "RCP-2025-0001",
  "type": "payment",
  "amount": 50000.00,
  "currency": "KES",
  "customer": {
    "name": "Tech Solutions Ltd",
    "email": "info@techsolutions.com"
  },
  "issue_date": "2025-01-12",
  "status": "generated",
  "pdf_url": "https://api.finguard.com/receipts/RCP-2025-0001/download",
  "view_count": 5,
  "download_count": 3
}
```

#### 3. Download Receipt PDF
```http
GET /receipts/{receipt_id}/download

Response: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="RCP-2025-0001.pdf"

[PDF Binary Data]
```

#### 4. Email Receipt
```http
POST /receipts/{receipt_id}/email
Content-Type: application/json

{
  "recipient_email": "customer@example.com",
  "cc_emails": ["manager@company.com"],
  "subject": "Payment Receipt - RCP-2025-0001",
  "message": "Thank you for your payment"
}

Response: 200 OK
{
  "success": true,
  "email_sent": true,
  "recipient": "customer@example.com",
  "message": "Receipt emailed successfully"
}
```

#### 5. List Receipts
```http
GET /receipts?page=1&limit=20&type=payment&status=generated&start_date=2025-01-01&end_date=2025-01-31

Response: 200 OK
{
  "receipts": [
    {
      "receipt_id": "RCP-2025-0001",
      "type": "payment",
      "amount": 50000.00,
      "customer_name": "Tech Solutions Ltd",
      "issue_date": "2025-01-12",
      "status": "generated"
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

#### 6. Void Receipt
```http
POST /receipts/{receipt_id}/void
Content-Type: application/json

{
  "reason": "Duplicate payment - corrected",
  "notes": "New receipt RCP-2025-0002 issued"
}

Response: 200 OK
{
  "success": true,
  "receipt_id": "RCP-2025-0001",
  "status": "voided",
  "void_date": "2025-01-12T16:00:00Z",
  "message": "Receipt voided successfully"
}
```

#### 7. Bulk Generate Receipts
```http
POST /receipts/bulk-generate
Content-Type: application/json

{
  "transaction_ids": ["txn_001", "txn_002", "txn_003"],
  "send_email": true,
  "template_id": "TMPL-DEFAULT"
}

Response: 202 Accepted
{
  "success": true,
  "job_id": "bulk_job_12345",
  "total_receipts": 3,
  "status": "processing",
  "message": "Bulk receipt generation started"
}
```

#### 8. Get Receipt Statistics
```http
GET /receipts/statistics?start_date=2025-01-01&end_date=2025-01-31

Response: 200 OK
{
  "total_receipts": 1245,
  "total_amount": 62500000.00,
  "by_type": {
    "payment": 1100,
    "refund": 45,
    "expense": 100
  },
  "by_status": {
    "generated": 1200,
    "voided": 45
  },
  "by_payment_method": {
    "mpesa": 900,
    "bank": 200,
    "cash": 100,
    "card": 45
  }
}
```

### Receipt Template Endpoints

#### 9. List Templates
```http
GET /receipts/templates

Response: 200 OK
{
  "templates": [
    {
      "template_id": "TMPL-DEFAULT",
      "name": "Standard Receipt",
      "is_default": true,
      "usage_count": 1245
    }
  ]
}
```

#### 10. Create Custom Template
```http
POST /receipts/templates
Content-Type: application/json

{
  "name": "Custom Receipt - Blue",
  "layout": {...},
  "header": {...},
  "styles": {
    "primary_color": "#1e40af"
  }
}

Response: 201 Created
{
  "success": true,
  "template_id": "TMPL-CUSTOM-001",
  "message": "Template created successfully"
}
```

---

## 🎨 Frontend Components

### 1. Receipt List Page (`/receipts`)

**Features:**
- Searchable table with filters (date range, type, customer)
- Quick actions (view, download, email, void)
- Bulk selection for batch operations
- Export to CSV/Excel
- Receipt statistics cards

**Components:**
```tsx
- ReceiptListPage
  ├── ReceiptFilters (date, type, status, customer)
  ├── ReceiptStatsCards (total, amount, by type)
  ├── ReceiptTable
  │   ├── ReceiptRow
  │   │   ├── ReceiptActions (view, download, email, void)
  │   │   └── StatusBadge
  │   └── BulkActions
  └── Pagination
```

### 2. Receipt Detail Page (`/receipts/[id]`)

**Features:**
- Full receipt preview (embedded PDF)
- Receipt information (customer, amount, date)
- Action buttons (download, email, print, void)
- Audit log (views, downloads, emails)
- Related transactions/invoices

**Components:**
```tsx
- ReceiptDetailPage
  ├── ReceiptHeader (receipt number, status)
  ├── ReceiptPDFViewer
  ├── ReceiptInfo
  │   ├── CustomerInfo
  │   ├── TransactionInfo
  │   └── AmountBreakdown
  ├── ReceiptActions (download, email, print, void)
  └── ReceiptAuditLog
```

### 3. Receipt Generation Modal

**Features:**
- Form to generate receipt manually
- Customer selection
- Amount and payment method
- Template selection
- Preview before generation
- Email delivery option

**Components:**
```tsx
- GenerateReceiptModal
  ├── CustomerSelector
  ├── AmountInput
  ├── PaymentMethodSelector
  ├── TemplateSelector
  ├── ReceiptPreview
  └── GenerateButton
```

### 4. Receipt Template Manager (`/settings/receipt-templates`)

**Features:**
- List of available templates
- Create/edit/delete templates
- Template preview
- Set default template
- Usage statistics

**Components:**
```tsx
- TemplateManagerPage
  ├── TemplateList
  │   └── TemplateCard (preview, edit, delete)
  ├── TemplateEditor
  │   ├── LayoutConfig
  │   ├── HeaderConfig
  │   ├── StyleConfig
  │   └── PreviewPane
  └── CreateTemplateButton
```

---

## 🚀 Implementation Phases

### Phase 1: Core Receipt Generation (Week 1)
**Priority: High**

**Backend Tasks:**
1. ✅ Create database models and schemas
2. ✅ Set up PDF generation service (ReportLab)
3. ✅ Implement receipt number generation
4. ✅ Create basic receipt template
5. ✅ Build receipt generation endpoint
6. ✅ Add file storage (filesystem/S3)
7. ✅ Implement QR code generation

**Frontend Tasks:**
1. ✅ Create receipt list page
2. ✅ Build receipt detail page with PDF viewer
3. ✅ Add download functionality
4. ✅ Create basic filters

**Testing:**
- Unit tests for receipt generation
- PDF generation tests
- API endpoint tests

**Deliverables:**
- Working receipt generation API
- Basic PDF receipts with QR codes
- Receipt list and detail pages

---

### Phase 2: Email Integration & Templates (Week 2)
**Priority: High**

**Backend Tasks:**
1. ✅ Integrate with email service
2. ✅ Create email templates for receipts
3. ✅ Build template management system
4. ✅ Add template customization options
5. ✅ Implement bulk receipt generation
6. ✅ Add receipt audit logging

**Frontend Tasks:**
1. ✅ Create receipt generation modal
2. ✅ Build template manager page
3. ✅ Add email receipt functionality
4. ✅ Implement template preview

**Testing:**
- Email delivery tests
- Template rendering tests
- Bulk generation tests

**Deliverables:**
- Email delivery working
- Customizable templates
- Template manager UI
- Bulk generation feature

---

### Phase 3: Automation & Integration (Week 3)
**Priority: Medium**

**Backend Tasks:**
1. ✅ Auto-generate receipts on payment completion
2. ✅ Integrate with M-Pesa webhook
3. ✅ Integrate with invoice payment flow
4. ✅ Add receipt void functionality
5. ✅ Implement receipt statistics
6. ✅ Add receipt search and filtering

**Frontend Tasks:**
1. ✅ Add receipt statistics dashboard
2. ✅ Implement advanced filters
3. ✅ Create receipt void interface
4. ✅ Add audit log viewer
5. ✅ Build receipt analytics

**Testing:**
- Integration tests with payment flow
- Webhook tests
- End-to-end tests

**Deliverables:**
- Automatic receipt generation
- Receipt void functionality
- Analytics and reporting
- Full integration with existing systems

---

## 🔗 Integration Points

### 1. Payment System Integration

**M-Pesa Webhook:**
```python
# After successful M-Pesa payment
async def mpesa_callback(payment_data):
    # Process payment
    payment = await process_mpesa_payment(payment_data)
    
    # Generate receipt automatically
    if payment.status == "completed":
        receipt = await generate_receipt(
            transaction_id=payment.id,
            type="payment",
            payment_method="mpesa",
            mpesa_code=payment.mpesa_code,
            amount=payment.amount,
            customer_id=payment.customer_id,
            send_email=True
        )
```

### 2. Invoice System Integration

**When Invoice is Marked as Paid:**
```python
async def mark_invoice_paid(invoice_id, payment_id):
    # Update invoice status
    invoice = await update_invoice_status(invoice_id, "paid")
    
    # Generate receipt
    receipt = await generate_receipt(
        invoice_id=invoice_id,
        transaction_id=payment_id,
        type="invoice_payment",
        amount=invoice.total,
        customer_id=invoice.customer_id,
        send_email=True
    )
```

### 3. Email Service Integration

**Automatic Email Delivery:**
```python
async def send_receipt_email(receipt_id, recipient_email):
    receipt = await get_receipt(receipt_id)
    
    # Attach PDF
    pdf_path = receipt.pdf_path
    
    # Send via email service
    await email_service.send_email(
        to=recipient_email,
        subject=f"Receipt {receipt.receipt_number}",
        template="receipt_email",
        attachments=[pdf_path],
        data={
            "receipt": receipt,
            "company": company_info
        }
    )
```

### 4. Automation System Integration

**Scheduled Receipt Delivery:**
```python
# Monthly receipt summary
async def send_monthly_receipt_summary(customer_id):
    receipts = await get_customer_receipts(
        customer_id=customer_id,
        start_date=first_day_of_month,
        end_date=last_day_of_month
    )
    
    # Generate summary PDF
    summary_pdf = await generate_receipt_summary(receipts)
    
    # Send via email
    await email_service.send_summary(customer_id, summary_pdf)
```

---

## 🧪 Testing Strategy

### Unit Tests

```python
# test_receipt_generation.py

def test_generate_receipt_number():
    """Test receipt number generation"""
    receipt_number = generate_receipt_number(year=2025, prefix="RCP")
    assert receipt_number.startswith("RCP-2025-")
    assert len(receipt_number) == 13

def test_calculate_vat():
    """Test VAT calculation"""
    amount = 50000.00
    vat_rate = 0.16
    vat = calculate_vat(amount, vat_rate)
    assert vat == 6896.55

def test_generate_receipt_pdf():
    """Test PDF generation"""
    receipt_data = {...}
    pdf_path = generate_receipt_pdf(receipt_data)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0
```

### Integration Tests

```python
# test_receipt_integration.py

async def test_auto_receipt_generation_on_payment():
    """Test automatic receipt generation after payment"""
    # Create payment
    payment = await create_payment(...)
    
    # Check receipt was generated
    receipt = await get_receipt_by_transaction_id(payment.id)
    assert receipt is not None
    assert receipt.amount == payment.amount

async def test_email_receipt_delivery():
    """Test receipt email delivery"""
    receipt = await generate_receipt(...)
    
    # Send email
    result = await send_receipt_email(receipt.receipt_id)
    assert result.success is True
    assert result.email_sent is True
```

### End-to-End Tests

```python
# test_receipt_e2e.py

async def test_full_receipt_workflow():
    """Test complete receipt workflow"""
    # 1. Customer makes M-Pesa payment
    payment = await make_mpesa_payment(...)
    
    # 2. Receipt is auto-generated
    receipt = await wait_for_receipt(payment.id)
    assert receipt is not None
    
    # 3. Receipt is emailed
    assert receipt.email_sent is True
    
    # 4. Customer downloads receipt
    pdf = await download_receipt(receipt.receipt_id)
    assert pdf is not None
```

---

## 🔐 Security & Compliance

### KRA Compliance (Kenya Revenue Authority)

**Requirements:**
1. ✅ Include KRA PIN for both parties
2. ✅ Show VAT breakdown clearly
3. ✅ Sequential receipt numbering
4. ✅ Cannot delete receipts (only void)
5. ✅ Maintain audit trail
6. ✅ Store receipts for 7+ years

**Implementation:**
```python
# Receipt must include:
- Business KRA PIN
- Customer KRA PIN (if available)
- VAT amount (16%)
- Receipt number (sequential)
- Date and time of issue
- Payment method
```

### Data Security

**Measures:**
1. ✅ Encrypt sensitive data (KRA PINs, amounts)
2. ✅ Role-based access control
3. ✅ Audit logging for all actions
4. ✅ Secure PDF storage
5. ✅ SSL/TLS for transmission
6. ✅ Watermark for printed receipts

**Implementation:**
```python
# Encrypt sensitive fields
from cryptography.fernet import Fernet

def encrypt_kra_pin(pin: str) -> str:
    cipher_suite = Fernet(encryption_key)
    encrypted = cipher_suite.encrypt(pin.encode())
    return encrypted.decode()
```

### Audit Trail

**Log All Actions:**
- Receipt generation (who, when, what)
- Receipt views (IP, device, timestamp)
- Receipt downloads (format, user)
- Receipt emails (recipient, status)
- Receipt voids (reason, who, when)

---

## 📊 Analytics & Reporting

### Receipt Dashboard

**Metrics:**
- Total receipts generated
- Total amount on receipts
- Receipts by type (payment, refund)
- Receipts by payment method
- Average receipt amount
- Void rate

**Charts:**
- Receipts over time (line chart)
- Receipts by type (pie chart)
- Receipts by payment method (bar chart)
- Top customers by receipt count

---

## 📦 Dependencies

### Python Packages

```bash
# PDF Generation
reportlab==4.0.7           # or weasyprint==60.1
pillow==10.1.0             # Image processing
qrcode[pil]==7.4.2        # QR code generation

# Optional: Advanced PDF
pypdf==3.17.1              # PDF manipulation
pdfkit==1.0.0              # HTML to PDF (requires wkhtmltopdf)

# Async
motor==3.3.2               # MongoDB async driver
aiofiles==23.2.1           # Async file operations
```

### System Requirements

```bash
# For wkhtmltopdf (if using pdfkit)
sudo apt-get install wkhtmltopdf

# For WeasyPrint
sudo apt-get install python3-dev python3-pip python3-cffi \
     libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
     libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Generate receipts in < 2 seconds
- ✅ Support 1000+ receipts per day
- ✅ 99.9% email delivery rate
- ✅ PDF size < 200KB
- ✅ QR code verification working
- ✅ Sequential numbering with no gaps

### Non-Functional Requirements
- ✅ API response time < 500ms
- ✅ PDF generation < 2 seconds
- ✅ Storage: 1MB per 10 receipts
- ✅ Uptime: 99.9%
- ✅ KRA compliance: 100%

---

## 📅 Timeline Summary

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 1: Core Generation | Week 1 | Receipt API, PDF generation, Basic UI |
| Phase 2: Email & Templates | Week 2 | Email integration, Templates, Bulk generation |
| Phase 3: Automation | Week 3 | Auto-generation, Analytics, Full integration |

**Total Duration**: 3 weeks  
**Team Size**: 2-3 developers (1 backend, 1-2 frontend)

---

## 🔮 Future Enhancements

### Phase 4 (Future)
- [ ] Multi-currency support
- [ ] Multiple languages (English, Swahili)
- [ ] SMS receipt delivery
- [ ] WhatsApp integration
- [ ] Receipt verification portal
- [ ] Mobile app for receipt viewing
- [ ] Blockchain verification
- [ ] AI-powered fraud detection
- [ ] Receipt OCR for expense matching

---

## 📝 Notes

### Design Decisions

**Why ReportLab over WeasyPrint?**
- Better performance for simple layouts
- No system dependencies
- Easier to deploy
- Better for programmatic PDF generation

**Why Sequential Numbering?**
- KRA compliance requirement
- Audit trail
- Easy tracking
- Cannot skip numbers

**Why QR Codes?**
- Easy verification
- Modern and professional
- Small file size
- Mobile-friendly

---

## 📚 References

- [Kenya Revenue Authority - VAT Guidelines](https://www.kra.go.ke/tax-professional/vat)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PDF/A Standard (Archival)](https://en.wikipedia.org/wiki/PDF/A)
- [QR Code Specification](https://www.qrcode.com/en/about/standards.html)

---

**Document Status**: ✅ Complete  
**Ready for Implementation**: Yes  
**Reviewed By**: Development Team  
**Approved Date**: January 12, 2025

---

*This plan provides a complete roadmap for implementing the Receipt Generation Module. Follow the phases sequentially for best results.*
