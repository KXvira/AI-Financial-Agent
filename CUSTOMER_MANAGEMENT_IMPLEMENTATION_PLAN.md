# Customer Management System - Implementation Plan

## Overview
Transform the existing hardcoded customers section into a comprehensive Customer Management System with real-time data, AI-powered invoice drafting, and automated sending capabilities.

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Database Schema](#database-schema)
3. [Backend API Endpoints](#backend-api-endpoints)
4. [Frontend Components](#frontend-components)
5. [AI Invoice Drafting](#ai-invoice-drafting)
6. [Email/SMS Integration](#emailsms-integration)
7. [Implementation Phases](#implementation-phases)
8. [File Structure](#file-structure)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Customer Management System                │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Customer   │───▶│  AI Invoice  │───▶│    Send       │  │
│  │    List     │    │   Drafting   │    │  Invoice      │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                   │                     │          │
│         ▼                   ▼                     ▼          │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │  Customer   │    │   Preview    │    │   Email/SMS   │  │
│  │   Details   │    │  & Edit      │    │   Service     │  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                                        │          │
│         ▼                                        ▼          │
│  ┌─────────────┐                        ┌───────────────┐  │
│  │  Invoices   │                        │  Notification │  │
│  │  & History  │                        │    Logs       │  │
│  └─────────────┘                        └───────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

### 1. Customers Collection (Enhanced)
```javascript
{
  _id: ObjectId,
  customer_id: "CUST-0001",           // Unique customer identifier
  name: "Tech Solutions Ltd",         // Company/Person name
  email: "info@techsolutions.com",    // Primary email
  phone: "254722123456",              // Primary phone (M-Pesa format)
  secondary_email: "billing@tech.com",// Optional secondary email
  secondary_phone: "254733456789",    // Optional secondary phone
  
  // Address Information
  address: {
    street: "123 Kimathi Street",
    city: "Nairobi",
    postal_code: "00100",
    country: "Kenya"
  },
  
  // Business Information
  business_type: "technology",         // Category
  tax_id: "P051234567X",              // KRA PIN or Tax ID
  
  // Financial Summary (computed/cached)
  total_invoices: 45,
  total_billed: 2500000.00,
  total_paid: 2100000.00,
  outstanding_balance: 400000.00,
  
  // Payment Information
  preferred_payment_method: "mpesa",   // mpesa, bank, cash
  payment_terms: "net_30",             // net_15, net_30, net_60
  credit_limit: 1000000.00,
  
  // Status & Settings
  status: "active",                    // active, inactive, suspended
  payment_status: "good",              // good, warning, overdue
  auto_send_invoices: true,           // Auto-send generated invoices
  send_reminders: true,                // Send payment reminders
  
  // Metadata
  created_at: ISODate("2024-01-15"),
  updated_at: ISODate("2025-10-11"),
  created_by: "user_id",
  last_invoice_date: ISODate("2025-10-10"),
  
  // AI Settings
  ai_preferences: {
    invoice_template: "professional",  // professional, simple, detailed
    language: "english",               // english, swahili
    include_tax: true,
    default_currency: "KES"
  },
  
  // Notes & Tags
  notes: "VIP customer, prefers monthly billing",
  tags: ["vip", "technology", "recurring"]
}
```

### 2. Invoice Templates Collection (New)
```javascript
{
  _id: ObjectId,
  template_id: "TMPL-001",
  name: "Standard Service Invoice",
  description: "Default template for service-based invoices",
  
  // Template Structure
  header: {
    include_logo: true,
    include_company_details: true,
    title: "INVOICE"
  },
  
  body: {
    columns: ["Item", "Description", "Quantity", "Rate", "Amount"],
    show_subtotal: true,
    show_tax: true,
    tax_rate: 16,  // VAT 16%
    show_discount: false
  },
  
  footer: {
    payment_terms: "Payment due within 30 days",
    bank_details: true,
    mpesa_details: true,
    notes_section: true
  },
  
  // AI Prompts for this template
  ai_prompt: "Generate a professional service invoice...",
  
  created_at: ISODate("2025-01-01"),
  is_default: true,
  status: "active"
}
```

### 3. Invoice Drafts Collection (New)
```javascript
{
  _id: ObjectId,
  draft_id: "DRAFT-001",
  customer_id: "CUST-0001",
  
  // Draft Status
  status: "draft",  // draft, reviewed, sent, converted_to_invoice
  
  // AI Generation Info
  generated_by: "ai",  // ai, manual
  ai_model: "gemini-pro",
  generation_prompt: "Create invoice for 3 months web hosting...",
  
  // Invoice Details (similar to invoice schema)
  invoice_number: null,  // Will be assigned when sent
  customer_name: "Tech Solutions Ltd",
  customer_email: "info@techsolutions.com",
  
  items: [
    {
      description: "Web Hosting Service",
      quantity: 3,
      unit: "months",
      rate: 15000.00,
      amount: 45000.00
    }
  ],
  
  subtotal: 45000.00,
  tax: 7200.00,      // 16% VAT
  total: 52200.00,
  
  // Metadata
  created_at: ISODate("2025-10-11"),
  reviewed_at: null,
  sent_at: null,
  converted_to_invoice_id: null,
  
  // Version Control
  version: 1,
  previous_version_id: null,
  
  notes: "AI generated based on previous invoices pattern"
}
```

### 4. Notification Logs Collection (New)
```javascript
{
  _id: ObjectId,
  notification_id: "NOTIF-001",
  
  // Reference
  customer_id: "CUST-0001",
  invoice_id: "INV-1001",
  
  // Notification Details
  type: "invoice_sent",  // invoice_sent, reminder, payment_received, overdue
  channel: "email",      // email, sms, both
  
  // Recipients
  recipients: {
    email: ["info@techsolutions.com"],
    phone: ["254722123456"]
  },
  
  // Content
  subject: "Invoice INV-1001 from Your Company",
  message: "Please find attached your invoice...",
  
  // Status
  status: "sent",  // pending, sent, failed, bounced
  sent_at: ISODate("2025-10-11T10:30:00"),
  delivered_at: ISODate("2025-10-11T10:30:15"),
  opened_at: ISODate("2025-10-11T11:45:00"),
  
  // Tracking
  tracking_id: "msg_abc123xyz",
  error_message: null,
  retry_count: 0,
  
  created_at: ISODate("2025-10-11T10:30:00")
}
```

---

## 🔌 Backend API Endpoints

### Customer Management Endpoints

#### 1. List All Customers
```http
GET /api/customers?limit=50&skip=0&status=active&search=tech&sort=name
```
**Response:**
```json
{
  "customers": [
    {
      "customer_id": "CUST-0001",
      "name": "Tech Solutions Ltd",
      "email": "info@techsolutions.com",
      "phone": "254722123456",
      "total_invoices": 45,
      "outstanding_balance": 400000.00,
      "payment_status": "good",
      "status": "active",
      "last_invoice_date": "2025-10-10"
    }
  ],
  "total": 8,
  "limit": 50,
  "skip": 0
}
```

#### 2. Get Customer Details
```http
GET /api/customers/{customer_id}
```
**Response:**
```json
{
  "customer_id": "CUST-0001",
  "name": "Tech Solutions Ltd",
  "email": "info@techsolutions.com",
  "phone": "254722123456",
  "address": {...},
  "financial_summary": {
    "total_invoices": 45,
    "total_billed": 2500000.00,
    "total_paid": 2100000.00,
    "outstanding_balance": 400000.00,
    "average_payment_days": 25,
    "payment_history": [...]
  },
  "recent_invoices": [...],
  "recent_payments": [...],
  "status": "active"
}
```

#### 3. Create Customer
```http
POST /api/customers
Content-Type: application/json

{
  "name": "New Company Ltd",
  "email": "contact@newcompany.com",
  "phone": "254722123456",
  "address": {...},
  "payment_terms": "net_30"
}
```

#### 4. Update Customer
```http
PUT /api/customers/{customer_id}
Content-Type: application/json

{
  "email": "newemail@company.com",
  "phone": "254733456789",
  "status": "active"
}
```

#### 5. Get Customer Statistics
```http
GET /api/customers/stats/summary
```
**Response:**
```json
{
  "total_customers": 8,
  "active_customers": 7,
  "inactive_customers": 1,
  "total_outstanding": 1200000.00,
  "customers_with_overdue": 2,
  "top_customers": [
    {
      "customer_id": "CUST-0001",
      "name": "Tech Solutions Ltd",
      "total_billed": 2500000.00
    }
  ]
}
```

### AI Invoice Drafting Endpoints

#### 6. Generate Invoice Draft (AI)
```http
POST /api/customers/{customer_id}/invoices/generate
Content-Type: application/json

{
  "prompt": "Create an invoice for 3 months of web hosting service at KES 15,000 per month",
  "template": "standard",
  "auto_calculate_tax": true,
  "include_previous_context": true
}
```
**Response:**
```json
{
  "draft_id": "DRAFT-001",
  "status": "draft",
  "invoice_data": {
    "customer_name": "Tech Solutions Ltd",
    "items": [
      {
        "description": "Web Hosting Service",
        "quantity": 3,
        "unit": "months",
        "rate": 15000.00,
        "amount": 45000.00
      }
    ],
    "subtotal": 45000.00,
    "tax": 7200.00,
    "total": 52200.00,
    "due_date": "2025-11-10"
  },
  "ai_confidence": 0.95,
  "suggestions": [
    "Consider adding service period dates",
    "Review tax calculation"
  ]
}
```

#### 7. Update Invoice Draft
```http
PUT /api/customers/{customer_id}/invoices/drafts/{draft_id}
Content-Type: application/json

{
  "items": [...],
  "notes": "Updated payment terms"
}
```

#### 8. Preview Invoice Draft
```http
GET /api/customers/{customer_id}/invoices/drafts/{draft_id}/preview
```
**Response:** PDF or HTML preview

#### 9. Convert Draft to Invoice & Send
```http
POST /api/customers/{customer_id}/invoices/drafts/{draft_id}/send
Content-Type: application/json

{
  "send_via": "both",  // email, sms, both
  "include_pdf": true,
  "custom_message": "Thank you for your business...",
  "schedule_send": null  // null for immediate, or ISO date for scheduled
}
```
**Response:**
```json
{
  "invoice_id": "INV-1258",
  "status": "sent",
  "sent_via": {
    "email": {
      "status": "sent",
      "sent_to": "info@techsolutions.com",
      "sent_at": "2025-10-11T10:30:00Z"
    },
    "sms": {
      "status": "sent",
      "sent_to": "254722123456",
      "sent_at": "2025-10-11T10:30:05Z"
    }
  },
  "tracking": {
    "email_tracking_id": "msg_abc123",
    "sms_tracking_id": "sms_xyz789"
  }
}
```

#### 10. Get Customer Invoice Drafts
```http
GET /api/customers/{customer_id}/invoices/drafts
```

#### 11. Smart Invoice Suggestions (AI)
```http
POST /api/customers/{customer_id}/invoices/suggest
Content-Type: application/json

{
  "context": "monthly",  // monthly, quarterly, one-time
  "based_on": "previous_invoices"  // previous_invoices, services, custom
}
```
**Response:**
```json
{
  "suggestions": [
    {
      "confidence": 0.92,
      "description": "Monthly Web Hosting - Based on 6-month pattern",
      "items": [...],
      "estimated_total": 52200.00,
      "reasoning": "Customer has been billed monthly for web hosting..."
    }
  ]
}
```

### Invoice Sending Endpoints

#### 12. Send Existing Invoice
```http
POST /api/invoices/{invoice_id}/send
Content-Type: application/json

{
  "send_via": "email",
  "recipients": {
    "email": ["custom@email.com"],
    "phone": ["254722123456"]
  },
  "include_pdf": true,
  "custom_message": "Reminder: Payment due soon"
}
```

#### 13. Get Notification History
```http
GET /api/customers/{customer_id}/notifications?type=invoice_sent&limit=20
```

#### 14. Track Invoice Delivery
```http
GET /api/invoices/{invoice_id}/delivery-status
```
**Response:**
```json
{
  "invoice_id": "INV-1258",
  "sent_at": "2025-10-11T10:30:00Z",
  "email": {
    "sent": true,
    "delivered": true,
    "opened": true,
    "opened_at": "2025-10-11T11:45:00Z",
    "clicks": 2
  },
  "sms": {
    "sent": true,
    "delivered": true,
    "delivery_status": "delivered"
  }
}
```

---

## 🎨 Frontend Components

### Page Structure

```
/customers
  ├── page.tsx                          # Customer list with stats
  ├── new/page.tsx                      # Create new customer form
  ├── [id]/
  │   ├── page.tsx                      # Customer detail dashboard
  │   ├── edit/page.tsx                 # Edit customer info
  │   ├── invoices/
  │   │   ├── page.tsx                  # Customer's invoices list
  │   │   ├── new/page.tsx              # Manual invoice creation
  │   │   └── generate/page.tsx         # AI invoice generation
  │   ├── payments/page.tsx             # Customer's payment history
  │   └── activity/page.tsx             # Customer activity log
  └── stats/page.tsx                    # Customer analytics
```

### Component Breakdown

#### 1. Customer List Page (`/customers/page.tsx`)
**Features:**
- Table with customer list
- Search by name, email, phone
- Filter by status, payment status
- Sort by name, outstanding balance, last invoice
- Quick stats cards (total customers, outstanding, overdue)
- "Add New Customer" button
- Export to CSV/Excel

**Columns:**
- Customer Name
- Contact (email/phone)
- Total Invoices
- Outstanding Balance
- Payment Status (Good/Warning/Overdue)
- Last Invoice Date
- Actions (View, Edit, Create Invoice)

#### 2. Customer Detail Dashboard (`/customers/[id]/page.tsx`)
**Sections:**
- **Header:** Customer name, contact, edit button
- **Financial Summary Cards:**
  - Total Billed
  - Total Paid
  - Outstanding Balance
  - Payment Score
- **Quick Actions:**
  - 🤖 Generate Invoice with AI
  - ✍️ Create Invoice Manually
  - 📧 Send Message
  - 💰 Record Payment
- **Tabs:**
  - Overview (summary)
  - Invoices (list with status)
  - Payments (payment history)
  - Activity (timeline of actions)
  - Notes (internal notes)

#### 3. AI Invoice Generation (`/customers/[id]/invoices/generate/page.tsx`)
**Features:**
- **Input Section:**
  - Text area for natural language prompt
  - Template selector
  - Quick prompts (Monthly Service, Project, Product Sale)
  - "Use Previous Invoice as Template" checkbox
  
- **AI Generation:**
  - Loading spinner with AI processing message
  - Confidence score display
  
- **Preview & Edit:**
  - Live preview of generated invoice
  - Editable fields (items, amounts, dates)
  - Add/remove line items
  - Tax calculation
  - Notes section
  
- **Actions:**
  - Save as Draft
  - Preview PDF
  - Send Invoice (opens modal)
  - Discard

#### 4. Send Invoice Modal
**Features:**
- Delivery method selection (Email, SMS, Both)
- Recipient confirmation (pre-filled from customer)
- Custom message textarea
- Include PDF attachment toggle
- Schedule send (optional date picker)
- Preview message
- "Send Now" button

#### 5. Customer Statistics Page (`/customers/stats/page.tsx`)
**Features:**
- Charts:
  - Revenue by customer (pie chart)
  - Payment trends (line chart)
  - Customer acquisition (bar chart)
  - Outstanding balance aging (stacked bar)
- Top 10 customers by revenue
- Customers needing attention (overdue payments)
- Payment behavior analysis

---

## 🤖 AI Invoice Drafting

### AI Integration Strategy

#### Gemini API Integration
**File:** `backend/ai_agent/invoice_generator.py`

```python
class InvoiceGenerator:
    """AI-powered invoice generation using Gemini"""
    
    async def generate_invoice_draft(
        self,
        customer_data: dict,
        prompt: str,
        previous_invoices: list = None,
        template: str = "standard"
    ) -> dict:
        """
        Generate invoice draft using AI
        
        Args:
            customer_data: Customer information
            prompt: Natural language description
            previous_invoices: Historical invoices for context
            template: Invoice template to use
            
        Returns:
            dict: Generated invoice data with items, amounts, etc.
        """
```

### AI Prompt Engineering

#### Context Building
```python
system_prompt = f"""
You are an expert invoice generator for a financial management system.

CUSTOMER INFORMATION:
- Name: {customer.name}
- Business Type: {customer.business_type}
- Payment Terms: {customer.payment_terms}
- Currency: KES (Kenyan Shillings)

HISTORICAL CONTEXT:
{previous_invoice_summary}

TAX RULES:
- Standard VAT: 16%
- Apply to services and products
- Show tax separately

TASK:
Generate a professional invoice based on the following request:
"{user_prompt}"

OUTPUT FORMAT (JSON):
{{
  "items": [
    {{
      "description": "Service/Product name",
      "quantity": number,
      "unit": "unit type",
      "rate": amount,
      "amount": total
    }}
  ],
  "subtotal": amount,
  "tax": amount,
  "total": amount,
  "due_date": "YYYY-MM-DD",
  "notes": "any relevant notes",
  "confidence": 0.0-1.0
}}
"""
```

#### AI Features
1. **Smart Item Recognition**
   - Recognize services from description
   - Suggest appropriate rates based on history
   - Calculate quantities automatically

2. **Context Awareness**
   - Learn from previous invoices
   - Detect recurring patterns
   - Suggest next invoice date

3. **Validation**
   - Check for missing information
   - Verify calculations
   - Flag unusual amounts

4. **Suggestions**
   - Payment terms recommendations
   - Discount suggestions
   - Notes and reminders

---

## 📧 Email/SMS Integration

### Email Service
**Provider Options:**
1. **SendGrid** (Recommended)
2. **AWS SES**
3. **Mailgun**

**Implementation:**
```python
# backend/services/email_service.py

class EmailService:
    async def send_invoice_email(
        self,
        to_email: str,
        invoice_data: dict,
        pdf_attachment: bytes,
        custom_message: str = None
    ) -> dict:
        """Send invoice via email with tracking"""
```

**Email Template:**
```html
Subject: Invoice {invoice_number} from {company_name}

Dear {customer_name},

{custom_message or default_message}

Invoice Details:
- Invoice Number: {invoice_number}
- Amount: {currency} {total}
- Due Date: {due_date}

Please find your invoice attached.

Payment Options:
- M-Pesa Paybill: {paybill_number}
- Bank Transfer: {bank_details}

View Invoice Online: {invoice_link}

Thank you for your business!
```

### SMS Service
**Provider:** Africa's Talking / Twilio

**Implementation:**
```python
# backend/services/sms_service.py

class SMSService:
    async def send_invoice_sms(
        self,
        phone_number: str,
        invoice_data: dict
    ) -> dict:
        """Send invoice notification via SMS"""
```

**SMS Template:**
```
Invoice {invoice_number}
Amount: KES {total}
Due: {due_date}
Pay via M-Pesa Paybill {paybill}
Acc: {invoice_number}
View: {short_link}
```

### Tracking System
```python
# backend/services/notification_tracker.py

class NotificationTracker:
    async def track_email_open(self, tracking_id: str)
    async def track_link_click(self, tracking_id: str, link: str)
    async def get_delivery_status(self, notification_id: str)
```

---

## 📅 Implementation Phases

### Phase 1: Foundation (Week 1)
**Backend:**
- [ ] Create customers database schema
- [ ] Implement customer CRUD endpoints
- [ ] Create customer statistics endpoint
- [ ] Set up data migration (extract customers from invoices)

**Frontend:**
- [ ] Customer list page with real data
- [ ] Customer detail page layout
- [ ] Create/Edit customer forms
- [ ] Customer statistics dashboard

**Deliverable:** Functional customer management with real data

---

### Phase 2: AI Invoice Generation (Week 2)
**Backend:**
- [ ] Implement Gemini AI invoice generator
- [ ] Create invoice drafts endpoints
- [ ] Build context analyzer (previous invoices)
- [ ] Implement draft CRUD operations

**Frontend:**
- [ ] AI invoice generation interface
- [ ] Natural language prompt input
- [ ] Invoice preview component
- [ ] Draft editing interface
- [ ] Template selector

**Deliverable:** AI-powered invoice drafting system

---

### Phase 3: Invoice Sending (Week 3)
**Backend:**
- [ ] Integrate SendGrid for email
- [ ] Integrate Africa's Talking for SMS
- [ ] Build PDF generation service
- [ ] Implement notification tracking
- [ ] Create delivery status endpoints

**Frontend:**
- [ ] Send invoice modal
- [ ] Delivery method selector
- [ ] Custom message composer
- [ ] Schedule send feature
- [ ] Delivery tracking display

**Deliverable:** Complete invoice sending workflow

---

### Phase 4: Polish & Features (Week 4)
**Backend:**
- [ ] Batch invoice generation
- [ ] Automated reminders
- [ ] Payment links generation
- [ ] Analytics and reporting
- [ ] Performance optimization

**Frontend:**
- [ ] Customer activity timeline
- [ ] Advanced search and filters
- [ ] Export functionality
- [ ] Mobile responsiveness
- [ ] Keyboard shortcuts

**Deliverable:** Production-ready system

---

## 📁 File Structure

```
backend/
├── customers/
│   ├── __init__.py
│   ├── models.py          # Customer, InvoiceDraft models
│   ├── router.py          # Customer API endpoints
│   ├── service.py         # Customer business logic
│   └── schemas.py         # Pydantic schemas
│
├── ai_agent/
│   ├── invoice_generator.py    # AI invoice generation
│   ├── context_analyzer.py     # Historical analysis
│   └── validators.py           # Invoice validation
│
├── services/
│   ├── email_service.py        # Email sending
│   ├── sms_service.py          # SMS sending
│   ├── pdf_generator.py        # PDF creation
│   └── notification_tracker.py  # Delivery tracking
│
└── templates/
    ├── invoice_email.html      # Email template
    └── invoice_pdf.html        # PDF template

finance-app/app/customers/
├── page.tsx                    # Customer list
├── new/page.tsx                # Create customer
├── stats/page.tsx              # Statistics
├── [id]/
│   ├── page.tsx                # Customer dashboard
│   ├── edit/page.tsx           # Edit customer
│   ├── invoices/
│   │   ├── page.tsx            # Invoice list
│   │   ├── new/page.tsx        # Manual invoice
│   │   └── generate/page.tsx   # AI generation
│   ├── payments/page.tsx       # Payment history
│   └── activity/page.tsx       # Activity log
│
└── components/
    ├── CustomerCard.tsx
    ├── CustomerForm.tsx
    ├── AIInvoiceGenerator.tsx
    ├── InvoicePreview.tsx
    ├── SendInvoiceModal.tsx
    └── ActivityTimeline.tsx
```

---

## 🔐 Security Considerations

1. **API Authentication**
   - Require auth tokens for all customer operations
   - Implement rate limiting for AI generation
   - Validate all customer data inputs

2. **Data Privacy**
   - Encrypt sensitive customer data
   - Implement access controls
   - Audit log all operations

3. **Email/SMS Security**
   - Use API keys securely
   - Implement sending limits
   - Monitor for abuse

---

## 🧪 Testing Strategy

### Unit Tests
- Customer CRUD operations
- AI invoice generation
- Email/SMS sending
- PDF generation

### Integration Tests
- End-to-end invoice workflow
- Customer-invoice relationships
- Notification delivery

### User Acceptance Tests
- Generate invoice from scratch
- Edit and send draft
- Track delivery status
- View customer analytics

---

## 📊 Success Metrics

1. **Adoption Metrics**
   - Number of customers created
   - AI invoices generated per day
   - Invoices sent via system

2. **Efficiency Metrics**
   - Time to create invoice (manual vs AI)
   - Email delivery success rate
   - SMS delivery success rate

3. **Quality Metrics**
   - AI generation accuracy
   - Invoice edit rate after AI generation
   - Customer satisfaction

---

## 🚀 Future Enhancements

1. **Advanced AI Features**
   - Multi-language invoice generation
   - Voice-to-invoice (speak your invoice)
   - Smart payment predictions

2. **Automation**
   - Recurring invoice automation
   - Auto-send on due dates
   - Payment reminder automation

3. **Integration**
   - Accounting software integration (QuickBooks, Xero)
   - Payment gateway integration
   - WhatsApp Business API

4. **Analytics**
   - Customer lifetime value
   - Churn prediction
   - Revenue forecasting

---

## 💰 Cost Estimates

### Third-Party Services
- **SendGrid:** Free tier (100 emails/day), $15/mo (40,000 emails)
- **Africa's Talking SMS:** ~KES 0.80 per SMS
- **Gemini API:** Free tier available, pay-as-you-go
- **Storage:** MongoDB Atlas current plan (sufficient)

### Development Time
- Phase 1: 5-7 days
- Phase 2: 7-10 days
- Phase 3: 5-7 days
- Phase 4: 5-7 days

**Total:** 3-4 weeks for complete implementation

---

## ✅ Checklist Before Implementation

- [ ] Review and approve this plan
- [ ] Set up SendGrid account
- [ ] Set up Africa's Talking account
- [ ] Create test customer data
- [ ] Design invoice PDF template
- [ ] Prepare AI training examples
- [ ] Set up staging environment

---

**Document Version:** 1.0  
**Created:** October 11, 2025  
**Status:** Draft - Awaiting Approval  
**Next Step:** Review and approve to begin Phase 1
