# FinGuard - Comprehensive System Architecture Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Technology Stack](#technology-stack)
4. [Backend Architecture](#backend-architecture)
5. [Frontend Architecture](#frontend-architecture)
6. [Database Architecture](#database-architecture)
7. [API Architecture](#api-architecture)
8. [Security Architecture](#security-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [System Functionalities](#system-functionalities)

---

## 1. System Overview

**FinGuard** is an AI-powered financial management system designed for Kenyan Small and Medium Businesses (SMBs). It provides comprehensive financial management capabilities including invoice management, payment processing, receipt management with OCR, AI-powered insights, and M-Pesa integration.

### Key Characteristics
- **Type**: Full-stack web application
- **Architecture**: Microservices-oriented with RESTful API
- **Deployment**: Docker containerized with Docker Compose orchestration
- **Database**: MongoDB (NoSQL document database)
- **AI Integration**: Google Gemini AI for OCR and financial insights
- **Target Market**: Kenyan SMBs
- **Currency**: Kenyan Shilling (KES)

---

## 2. Architecture Diagrams

### 2.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            Web Browser (Next.js Frontend)                     │  │
│  │  ┌────────────┬────────────┬────────────┬────────────┐      │  │
│  │  │ Dashboard  │ Invoices   │ Payments   │ Receipts   │      │  │
│  │  ├────────────┼────────────┼────────────┼────────────┤      │  │
│  │  │ Customers  │ AI Insights│ Reports    │ Expenses   │      │  │
│  │  └────────────┴────────────┴────────────┴────────────┘      │  │
│  │           React Components + TypeScript + TailwindCSS        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTP/REST API (JSON)
                            │ Port 3000 → Port 8000
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │               Nginx Reverse Proxy (Production)                │  │
│  │   SSL/TLS Termination │ Rate Limiting │ Compression          │  │
│  └────────────────────┬──────────────────────────────────────────┘  │
│                       │                                              │
│                       ▼                                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            FastAPI Backend (Python 3.12)                      │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │              API Router Layer                            │ │  │
│  │  │  ┌───────────────────────────────────────────────────┐  │ │  │
│  │  │  │ Auth │ Dashboard │ Invoices │ Payments │ Receipts │  │ │  │
│  │  │  ├───────────────────────────────────────────────────┤  │ │  │
│  │  │  │ Customers │ AI Insights │ OCR │ M-Pesa │ Reports  │  │ │  │
│  │  │  └───────────────────────────────────────────────────┘  │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │              Service Layer                               │ │  │
│  │  │  • Receipt Service    • Invoice Service                 │ │  │
│  │  │  • Payment Service    • OCR Service                     │ │  │
│  │  │  • AI Insights (RAG)  • Reconciliation Service          │ │  │
│  │  │  • M-Pesa Service     • Email Service                   │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┬──────────────────┐
          │                 │                 │                  │
          ▼                 ▼                 ▼                  ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐  ┌──────────────┐
│   MongoDB       │ │   Redis     │ │ Google      │  │  M-Pesa      │
│   Database      │ │   Cache     │ │ Gemini AI   │  │  Daraja API  │
│                 │ │             │ │             │  │              │
│ • Transactions  │ │ • Sessions  │ │ • OCR       │  │ • Payments   │
│ • Invoices      │ │ • Rate Limit│ │ • Insights  │  │ • Callbacks  │
│ • Customers     │ │ • Task Queue│ │ • Analysis  │  │              │
│ • Receipts      │ │             │ │             │  │              │
└─────────────────┘ └─────────────┘ └─────────────┘  └──────────────┘
```

### 2.2 Request Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. User Action (Browser)                                          │
│    Example: Upload receipt image                                  │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 2. Frontend (Next.js)                                             │
│    • Form validation                                              │
│    • File handling                                                │
│    • API call preparation                                         │
└──────────────────┬───────────────────────────────────────────────┘
                   │ HTTP POST /receipts/upload-ocr
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 3. API Router (FastAPI)                                           │
│    • Request validation (Pydantic)                                │
│    • Authentication check (JWT)                                   │
│    • Rate limiting                                                │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 4. Service Layer                                                  │
│    • Business logic execution                                     │
│    • File storage (uploads/receipts/)                             │
│    • Gemini AI OCR processing                                     │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 5. Database Layer (MongoDB)                                       │
│    • Data persistence                                             │
│    • Receipt document creation                                    │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 6. Response                                                       │
│    • JSON response with receipt data                              │
│    • HTTP 200 OK or error code                                    │
└──────────────────┬───────────────────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│ 7. Frontend Update                                                │
│    • UI refresh with new data                                     │
│    • Success/error notification                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Frontend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 15.3.5 | React framework with App Router |
| **React** | 18.x | UI component library |
| **TypeScript** | 5.x | Type-safe JavaScript |
| **TailwindCSS** | 3.x | Utility-first CSS framework |
| **Lucide React** | Latest | Icon library |
| **React Hook Form** | Latest | Form handling |
| **Zod** | Latest | Schema validation |
| **Axios/Fetch** | Built-in | HTTP client |

### 3.2 Backend Technologies

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Python** | 3.12 | Programming language |
| **FastAPI** | 0.115+ | Web framework |
| **Uvicorn** | Latest | ASGI server |
| **Pydantic** | 2.12+ | Data validation |
| **Motor** | Latest | Async MongoDB driver |
| **PyMongo** | Latest | MongoDB driver |
| **Google Generative AI** | 0.8.5+ | Gemini AI SDK |
| **ReportLab** | Latest | PDF generation |
| **Pillow (PIL)** | Latest | Image processing |
| **QRCode** | 7.4.2 | QR code generation |
| **python-jose** | Latest | JWT handling |
| **passlib** | Latest | Password hashing |
| **bcrypt** | Latest | Password encryption |

### 3.3 Database & Storage

| Technology | Purpose |
|-----------|---------|
| **MongoDB** | Primary database (NoSQL) |
| **Redis** | Cache, session storage, task queue |
| **File System** | Image and PDF storage |

### 3.4 AI & External Services

| Service | Purpose |
|---------|---------|
| **Google Gemini AI** | OCR processing, financial insights |
| **M-Pesa Daraja API** | Mobile payment integration |
| **SendGrid/SES** | Email notifications (optional) |

### 3.5 DevOps & Deployment

| Technology | Purpose |
|-----------|---------|
| **Docker** | Containerization |
| **Docker Compose** | Multi-container orchestration |
| **Nginx** | Reverse proxy, SSL termination |
| **GitHub Actions** | CI/CD pipeline |
| **Prometheus** | Metrics collection |
| **Grafana** | Monitoring dashboards |

---

## 4. Backend Architecture

### 4.1 Directory Structure

```
backend/
├── app.py                          # Main FastAPI application entry point
├── requirements.txt                # Python dependencies
├── requirements_complete.txt       # Full dependency list
│
├── auth/                           # Authentication & Authorization
│   ├── __init__.py
│   ├── router.py                   # Auth API endpoints
│   ├── service.py                  # Auth business logic
│   ├── models.py                   # User models
│   └── jwt_handler.py              # JWT token management
│
├── database/                       # Database layer
│   ├── __init__.py
│   ├── mongodb.py                  # MongoDB connection & operations
│   └── models.py                   # Database models
│
├── receipts/                       # Receipt Management Module
│   ├── __init__.py
│   ├── router.py                   # Receipt API endpoints
│   ├── service.py                  # Receipt business logic
│   ├── models.py                   # Receipt data models
│   ├── adapter.py                  # Backward compatibility adapter
│   ├── pdf_generator.py            # PDF generation logic
│   └── qr_generator.py             # QR code generation
│
├── invoices/                       # Invoice Management Module
│   ├── __init__.py
│   ├── router.py                   # Invoice API endpoints
│   ├── service.py                  # Invoice business logic
│   └── models.py                   # Invoice data models
│
├── payments/                       # Payment Processing Module
│   ├── __init__.py
│   ├── router.py                   # Payment API endpoints
│   ├── service.py                  # Payment business logic
│   └── models.py                   # Payment data models
│
├── customers/                      # Customer Management Module
│   ├── __init__.py
│   ├── router.py                   # Customer API endpoints
│   ├── service.py                  # Customer business logic
│   └── models.py                   # Customer data models
│
├── dashboard/                      # Dashboard Module
│   ├── __init__.py
│   ├── router.py                   # Dashboard API endpoints
│   └── service.py                  # Dashboard analytics
│
├── ai_insights/                    # AI Financial Insights Module
│   ├── __init__.py
│   ├── router.py                   # AI Insights API endpoints
│   └── service.py                  # RAG service with Gemini AI
│
├── ocr/                            # OCR Processing Module
│   ├── __init__.py
│   ├── router.py                   # OCR API endpoints
│   ├── service.py                  # OCR business logic
│   ├── tasks.py                    # Background OCR tasks
│   └── gemini_ocr.py               # Gemini AI OCR integration
│
├── mpesa/                          # M-Pesa Integration Module
│   ├── __init__.py
│   ├── router.py                   # M-Pesa API endpoints
│   ├── service.py                  # M-Pesa business logic
│   └── models.py                   # M-Pesa data models
│
├── reconciliation/                 # Payment Reconciliation Module
│   ├── __init__.py
│   ├── router.py                   # Reconciliation API endpoints
│   └── service.py                  # Reconciliation logic
│
├── reporting/                      # Reporting Module
│   ├── __init__.py
│   ├── router.py                   # Reporting API endpoints
│   └── service.py                  # Report generation
│
├── automation/                     # Automation Module
│   ├── __init__.py
│   └── router.py                   # Automation API endpoints
│
├── expenses/                       # Expense Management Module
│   ├── __init__.py
│   └── router.py                   # Expense API endpoints
│
└── email/                          # Email Service Module
    ├── __init__.py
    ├── router.py                   # Email API endpoints
    └── service.py                  # Email sending logic
```

### 4.2 Backend Design Patterns

#### 4.2.1 Layered Architecture
- **Router Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Database Layer**: Manages data persistence
- **Model Layer**: Defines data structures

#### 4.2.2 Dependency Injection
```python
# Example: Database dependency injection
from fastapi import Depends
from backend.database.mongodb import get_database, Database

@router.get("/receipts/{receipt_id}")
async def get_receipt(
    receipt_id: str,
    db: Database = Depends(get_database)
):
    # Database instance injected automatically
    receipt = await db.find_one("receipts", {"_id": receipt_id})
    return receipt
```

#### 4.2.3 Adapter Pattern (Backward Compatibility)
```python
# backend/receipts/adapter.py
class ReceiptAdapter:
    """Transforms old receipt format to new format"""
    
    @staticmethod
    def adapt_old_receipt(old_receipt: Dict) -> Dict:
        # Transform flat structure to nested structure
        # Ensures compatibility with old data
        pass
```

#### 4.2.4 Service Pattern
```python
# Separation of concerns
class ReceiptService:
    def generate_receipt(self, data): pass
    def generate_pdf(self, receipt): pass
    def send_email(self, receipt): pass
```

---

## 5. Frontend Architecture

### 5.1 Directory Structure

```
finance-app/
├── app/                            # Next.js App Router
│   ├── layout.tsx                  # Root layout
│   ├── page.tsx                    # Home page
│   │
│   ├── auth/                       # Authentication pages
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   │
│   ├── dashboard/                  # Dashboard pages
│   │   └── page.tsx
│   │
│   ├── receipts/                   # Receipt pages
│   │   ├── page.tsx                # Receipt list & creation
│   │   └── [id]/
│   │       └── page.tsx            # Receipt detail & preview
│   │
│   ├── invoices/                   # Invoice pages
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   │
│   ├── payments/                   # Payment pages
│   │   └── page.tsx
│   │
│   ├── customers/                  # Customer pages
│   │   ├── page.tsx
│   │   └── [id]/
│   │       └── page.tsx
│   │
│   ├── ai-insights/                # AI Insights pages
│   │   └── page.tsx
│   │
│   ├── expenses/                   # Expense pages
│   │   └── page.tsx
│   │
│   └── reports/                    # Report pages
│       └── page.tsx
│
├── components/                     # Reusable components
│   ├── ui/                         # UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   └── Table.tsx
│   │
│   ├── layout/                     # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   │
│   ├── forms/                      # Form components
│   │   ├── ReceiptForm.tsx
│   │   ├── InvoiceForm.tsx
│   │   └── CustomerForm.tsx
│   │
│   └── ReceiptUploader.tsx         # OCR upload component
│
├── lib/                            # Utility libraries
│   ├── api.ts                      # API client
│   ├── auth.ts                     # Auth utilities
│   └── utils.ts                    # Helper functions
│
├── types/                          # TypeScript type definitions
│   ├── receipt.ts
│   ├── invoice.ts
│   ├── payment.ts
│   └── customer.ts
│
├── hooks/                          # Custom React hooks
│   ├── useAuth.ts
│   ├── useReceipts.ts
│   └── useInvoices.ts
│
├── styles/                         # Global styles
│   └── globals.css
│
├── public/                         # Static assets
│   ├── images/
│   └── icons/
│
├── package.json                    # Node.js dependencies
├── tsconfig.json                   # TypeScript configuration
├── tailwind.config.js              # TailwindCSS configuration
└── next.config.js                  # Next.js configuration
```

### 5.2 Frontend Design Patterns

#### 5.2.1 Component Composition
```typescript
// Reusable components
<Card>
  <CardHeader>
    <CardTitle>Receipt #{receipt.id}</CardTitle>
  </CardHeader>
  <CardContent>
    <ReceiptDetails data={receipt} />
  </CardContent>
  <CardFooter>
    <Button onClick={downloadPDF}>Download PDF</Button>
  </CardFooter>
</Card>
```

#### 5.2.2 Custom Hooks
```typescript
// useReceipts.ts
export function useReceipts() {
  const [receipts, setReceipts] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const fetchReceipts = async () => {
    setLoading(true);
    const data = await api.get('/receipts');
    setReceipts(data);
    setLoading(false);
  };
  
  return { receipts, loading, fetchReceipts };
}
```

#### 5.2.3 Type Safety
```typescript
// types/receipt.ts
export interface Receipt {
  id: string;
  receipt_number: string;
  customer: Customer;
  line_items: LineItem[];
  tax_breakdown: TaxBreakdown;
  status: ReceiptStatus;
  generated_at: string;
}
```

---

## 6. Database Architecture

### 6.1 MongoDB Database Design

**Database Name**: `financial_agent`

### 6.2 Collections Schema

#### 6.2.1 Transactions Collection

```javascript
{
  _id: ObjectId("..."),
  transaction_id: "TXN-20251018-001",
  type: "credit" | "debit",
  amount: 5000.00,
  currency: "KES",
  gateway: "mpesa" | "bank" | "cash" | "card",
  status: "pending" | "completed" | "failed" | "cancelled",
  customer_id: ObjectId("..."),
  customer_name: "John Doe",
  customer_phone: "+254712345678",
  reference: "MPESA123456",
  description: "Payment for invoice INV-001",
  mpesa_receipt_number: "QAR123ABC",
  request_timestamp: ISODate("2025-10-18T08:00:00Z"),
  completion_timestamp: ISODate("2025-10-18T08:00:05Z"),
  metadata: {
    source: "mobile_app",
    ip_address: "192.168.1.1"
  },
  created_at: ISODate("2025-10-18T08:00:00Z"),
  updated_at: ISODate("2025-10-18T08:00:05Z")
}
```

**Indexes**:
- `transaction_id` (unique)
- `customer_id`
- `status`
- `gateway`
- `request_timestamp` (descending)
- Compound: `{customer_id: 1, status: 1}`

#### 6.2.2 Invoices Collection

```javascript
{
  _id: ObjectId("..."),
  invoice_id: "INV-20251018-001",
  invoice_number: "INV-001",
  customer_id: ObjectId("..."),
  customer: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+254712345678",
    address: "123 Main St, Nairobi"
  },
  line_items: [
    {
      description: "Web Development Service",
      quantity: 10,
      unit_price: 5000.00,
      total: 50000.00
    }
  ],
  subtotal: 50000.00,
  tax_rate: 16,
  tax_amount: 8000.00,
  total_amount: 58000.00,
  currency: "KES",
  status: "draft" | "sent" | "paid" | "overdue" | "cancelled",
  date_issued: ISODate("2025-10-18T00:00:00Z"),
  due_date: ISODate("2025-11-18T00:00:00Z"),
  paid_date: ISODate("2025-10-20T00:00:00Z"),
  payment_terms: "Net 30",
  notes: "Thank you for your business",
  pdf_path: "/uploads/invoices/INV-001.pdf",
  created_at: ISODate("2025-10-18T08:00:00Z"),
  updated_at: ISODate("2025-10-18T08:00:00Z")
}
```

**Indexes**:
- `invoice_id` (unique)
- `invoice_number` (unique)
- `customer_id`
- `status`
- `date_issued` (descending)
- `due_date`
- Compound: `{customer_id: 1, status: 1}`

#### 6.2.3 Receipts Collection

```javascript
{
  _id: ObjectId("..."),
  receipt_id: "RCP-20251018-001",
  receipt_number: "RCP-001",
  receipt_type: "payment" | "refund" | "purchase",
  customer: {
    name: "John Doe",
    email: "john@example.com",
    phone: "+254712345678"
  },
  line_items: [
    {
      description: "Service Payment",
      quantity: 1,
      unit_price: 5000.00,
      total: 5000.00
    }
  ],
  tax_breakdown: {
    subtotal: 4310.34,
    vat_rate: 16,
    vat_amount: 689.66,
    total: 5000.00
  },
  payment_method: "mpesa" | "cash" | "bank" | "card",
  transaction_id: "TXN-20251018-001",
  status: "generated" | "sent" | "cancelled",
  generated_at: ISODate("2025-10-18T08:00:00Z"),
  pdf_path: "/uploads/receipts/pdfs/RCP-001.pdf",
  qr_code: "data:image/png;base64,...",
  notes: "Payment received. Thank you!",
  ocr_data: {
    uploaded: true,
    image_path: "/uploads/receipts/images/receipt-123.jpg",
    extracted_data: {
      merchant_name: "ABC Store",
      date: "2025-10-18",
      items: [...],
      total: 5000.00
    },
    confidence_score: 0.95
  },
  created_at: ISODate("2025-10-18T08:00:00Z"),
  updated_at: ISODate("2025-10-18T08:00:00Z")
}
```

**Indexes**:
- `receipt_id` (unique)
- `receipt_number` (unique)
- `receipt_type`
- `status`
- `generated_at` (descending)
- `customer.email`

#### 6.2.4 Customers Collection

```javascript
{
  _id: ObjectId("..."),
  customer_id: "CUST-20251018-001",
  name: "John Doe",
  email: "john@example.com",
  phone: "+254712345678",
  address: {
    street: "123 Main St",
    city: "Nairobi",
    county: "Nairobi",
    postal_code: "00100",
    country: "Kenya"
  },
  business_info: {
    business_name: "John's Enterprise",
    kra_pin: "A123456789X",
    registration_number: "REG123456"
  },
  financials: {
    total_invoices: 50,
    total_amount_invoiced: 2500000.00,
    total_paid: 2000000.00,
    outstanding_balance: 500000.00,
    last_payment_date: ISODate("2025-10-15T00:00:00Z")
  },
  status: "active" | "inactive" | "blocked",
  tags: ["vip", "wholesale"],
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-10-18T08:00:00Z")
}
```

**Indexes**:
- `customer_id` (unique)
- `email` (unique)
- `phone` (unique)
- `status`
- `created_at` (descending)
- Text index on `name` and `business_info.business_name`

#### 6.2.5 Users Collection (Authentication)

```javascript
{
  _id: ObjectId("..."),
  user_id: "USER-20251018-001",
  username: "admin",
  email: "admin@example.com",
  hashed_password: "$2b$12$...",
  full_name: "Admin User",
  role: "admin" | "user" | "accountant" | "viewer",
  permissions: ["read", "write", "delete"],
  is_active: true,
  is_verified: true,
  phone: "+254712345678",
  profile_picture: "/uploads/profiles/admin.jpg",
  last_login: ISODate("2025-10-18T08:00:00Z"),
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-10-18T08:00:00Z")
}
```

**Indexes**:
- `user_id` (unique)
- `email` (unique)
- `username` (unique)
- `role`
- `is_active`

#### 6.2.6 Analytics Cache Collection

```javascript
{
  _id: ObjectId("..."),
  metric_type: "revenue_monthly" | "expense_categories" | "customer_stats",
  period: "2025-10",
  value: 48908755.00,
  breakdown: {
    mpesa: 30000000.00,
    bank: 15000000.00,
    cash: 3908755.00
  },
  calculated_at: ISODate("2025-10-18T08:00:00Z"),
  expires_at: ISODate("2025-10-19T08:00:00Z")
}
```

**Indexes**:
- Compound: `{metric_type: 1, period: 1}` (unique)
- `expires_at` (TTL index for auto-deletion)

### 6.3 Database Relationships

```
Users ──┐
        │
        ├──> Transactions ──┐
        │                   │
        ├──> Invoices ──────┼──> Customers
        │                   │
        ├──> Receipts ──────┘
        │
        └──> Payments
```

### 6.4 Data Access Patterns

#### 6.4.1 Common Queries

**Get Dashboard Statistics**:
```javascript
// Aggregate transactions by status
db.transactions.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$gateway", total: { $sum: "$amount" } } }
])
```

**Get Customer Invoice History**:
```javascript
db.invoices.find({ 
  customer_id: ObjectId("..."),
  status: { $in: ["sent", "paid", "overdue"] }
}).sort({ date_issued: -1 })
```

**Search Receipts**:
```javascript
db.receipts.find({
  $or: [
    { receipt_number: /RCP-001/i },
    { "customer.name": /John/i }
  ],
  status: "generated"
})
```

#### 6.4.2 Optimization Strategies

1. **Compound Indexes**: For common query patterns
2. **Text Indexes**: For search functionality
3. **TTL Indexes**: For automatic cache expiration
4. **Projection**: Select only needed fields
5. **Connection Pooling**: Reuse database connections
6. **Async Operations**: Use Motor for non-blocking I/O

---

## 7. API Architecture

### 7.1 API Endpoint Structure

**Base URL**: `http://localhost:8000`

### 7.2 API Routes Overview

```
/                           # Root (health check)
├── /docs                   # Swagger UI documentation
├── /redoc                  # ReDoc documentation
├── /openapi.json           # OpenAPI schema
│
├── /auth                   # Authentication
│   ├── POST /register
│   ├── POST /login
│   ├── POST /logout
│   ├── POST /refresh
│   └── GET /me
│
├── /api
│   ├── /dashboard          # Dashboard
│   │   ├── GET /stats
│   │   ├── GET /stats/summary
│   │   └── GET /health
│   │
│   ├── /invoices           # Invoice Management
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── GET /{id}
│   │   ├── PUT /{id}
│   │   ├── DELETE /{id}
│   │   ├── GET /{id}/download
│   │   └── POST /{id}/send
│   │
│   ├── /payments           # Payment Processing
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── GET /{id}
│   │   └── POST /verify
│   │
│   ├── /customers          # Customer Management
│   │   ├── GET /
│   │   ├── POST /
│   │   ├── GET /{id}
│   │   ├── PUT /{id}
│   │   └── DELETE /{id}
│   │
│   ├── /ai-insights        # AI Financial Insights
│   │   ├── POST /query
│   │   ├── GET /health
│   │   └── POST /analyze
│   │
│   ├── /mpesa              # M-Pesa Integration
│   │   ├── POST /stk-push
│   │   ├── POST /callback
│   │   └── GET /transactions
│   │
│   └── /reports            # Reporting
│       ├── GET /income-statement
│       ├── GET /balance-sheet
│       └── GET /cash-flow
│
├── /receipts               # Receipt Management
│   ├── GET /
│   ├── POST /generate
│   ├── POST /upload-ocr
│   ├── GET /{id}
│   ├── GET /{id}/download
│   └── GET /statistics/summary
│
├── /ocr                    # OCR Processing
│   ├── POST /upload
│   ├── POST /process
│   └── GET /task/{id}
│
└── /reconciliation         # Payment Reconciliation
    ├── POST /auto
    ├── POST /manual
    └── GET /logs
```

### 7.3 API Request/Response Examples

#### 7.3.1 Receipt OCR Upload

**Request**:
```http
POST /receipts/upload-ocr
Content-Type: multipart/form-data

file: [receipt-image.jpg]
```

**Response**:
```json
{
  "receipt_id": "RCP-20251018-001",
  "receipt_number": "RCP-001",
  "customer": {
    "name": "ABC Store",
    "email": "contact@abcstore.com",
    "phone": "+254700000000"
  },
  "line_items": [
    {
      "description": "Product A",
      "quantity": 2,
      "unit_price": 1500.00,
      "total": 3000.00
    }
  ],
  "tax_breakdown": {
    "subtotal": 2586.21,
    "vat_rate": 16,
    "vat_amount": 413.79,
    "total": 3000.00
  },
  "status": "generated",
  "pdf_path": "/uploads/receipts/pdfs/RCP-001.pdf"
}
```

#### 7.3.2 AI Insights Query

**Request**:
```http
POST /api/ai-insights/query
Content-Type: application/json

{
  "query": "What are my spending patterns this month?"
}
```

**Response**:
```json
{
  "answer": "## Spending Analysis for October 2025\n\n### Overview\n...",
  "confidence": 0.92,
  "data_sources": ["transactions", "invoices", "receipts"],
  "timestamp": "2025-10-18T08:00:00Z",
  "suggestions": [
    "Consider negotiating bulk discounts with top suppliers",
    "Review recurring expenses for optimization opportunities"
  ]
}
```

### 7.4 Authentication Flow

```
1. User Login
   POST /auth/login
   { "email": "user@example.com", "password": "***" }
   ↓
2. Server Validates Credentials
   • Check email exists
   • Verify password hash
   ↓
3. Generate JWT Token
   {
     "access_token": "eyJ...",
     "token_type": "bearer",
     "expires_in": 1800
   }
   ↓
4. Client Stores Token
   localStorage.setItem('token', accessToken)
   ↓
5. Subsequent Requests
   Headers: { "Authorization": "Bearer eyJ..." }
   ↓
6. Server Validates Token
   • Decode JWT
   • Check expiration
   • Verify signature
   ↓
7. Process Request
```

---

## 8. Security Architecture

### 8.1 Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Network Security                                    │
│ • SSL/TLS encryption                                         │
│ • HTTPS only                                                 │
│ • Firewall rules                                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Application Security                               │
│ • CORS configuration                                         │
│ • Rate limiting                                              │
│ • Request validation                                         │
│ • Security headers                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Authentication & Authorization                      │
│ • JWT tokens                                                 │
│ • Role-based access control (RBAC)                           │
│ • Password hashing (bcrypt)                                  │
│ • Session management                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: Data Security                                       │
│ • Input sanitization                                         │
│ • SQL injection prevention                                   │
│ • XSS protection                                             │
│ • File upload validation                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 5: Database Security                                   │
│ • MongoDB authentication                                     │
│ • Connection encryption                                      │
│ • Access control lists                                       │
│ • Audit logging                                              │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Security Implementations

#### 8.2.1 Password Security
```python
# Password hashing with bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash("user_password")

# Verify password
is_valid = pwd_context.verify("user_password", hashed)
```

#### 8.2.2 JWT Authentication
```python
# JWT token generation
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt
```

#### 8.2.3 Rate Limiting
```python
# Rate limiting middleware
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/endpoint")
@limiter.limit("10/minute")
async def endpoint(request: Request):
    pass
```

### 8.3 Security Best Practices Implemented

1. **Input Validation**: Pydantic models validate all inputs
2. **SQL Injection Prevention**: MongoDB's parameterized queries
3. **XSS Protection**: Content Security Policy headers
4. **CSRF Protection**: Token-based authentication
5. **File Upload Security**: File type and size validation
6. **Error Handling**: Generic error messages to prevent information leakage
7. **Logging**: Comprehensive audit trails
8. **Environment Variables**: Sensitive data not in code

---

## 9. Deployment Architecture

### 9.1 Docker Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │   Nginx        │  │   Backend      │  │   Frontend    │ │
│  │   Container    │  │   Container    │  │   Container   │ │
│  │   Port: 80/443 │  │   Port: 8000   │  │   Port: 3000  │ │
│  └───────┬────────┘  └───────┬────────┘  └───────┬───────┘ │
│          │                   │                    │          │
│          └───────────────────┴────────────────────┘          │
│                              │                               │
│  ┌──────────────────────────┴────────────────────────────┐  │
│  │                                                        │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │ MongoDB  │  │  Redis   │  │Prometheus│           │  │
│  │  │Container │  │Container │  │Container │           │  │
│  │  │Port:27017│  │Port:6379 │  │Port:9090 │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  │                                                        │  │
│  │  ┌──────────┐  ┌──────────┐                          │  │
│  │  │ Grafana  │  │  Celery  │                          │  │
│  │  │Container │  │  Worker  │                          │  │
│  │  │Port:3000 │  │Container │                          │  │
│  │  └──────────┘  └──────────┘                          │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Shared Docker Volumes                      │  │
│  │  • mongodb-data                                        │  │
│  │  • redis-data                                          │  │
│  │  • uploads (receipts, invoices)                       │  │
│  │  • logs                                                │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 9.2 Deployment Environments

#### 9.2.1 Development
- **Environment**: Local machine
- **Database**: MongoDB (local or Atlas)
- **Ports**: Backend 8000, Frontend 3000
- **Hot Reload**: Enabled
- **Debug Mode**: Enabled

#### 9.2.2 Production
- **Environment**: Cloud server (AWS, DigitalOcean, etc.)
- **Database**: MongoDB Atlas (managed)
- **Ports**: HTTP 80, HTTPS 443
- **Hot Reload**: Disabled
- **Debug Mode**: Disabled
- **SSL/TLS**: Enabled with Let's Encrypt
- **Monitoring**: Prometheus + Grafana

### 9.3 CI/CD Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Developer pushes code to GitHub                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. GitHub Actions Triggered                                 │
│    • Run tests (pytest)                                     │
│    • Code linting (black, flake8)                           │
│    • Type checking (mypy)                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Build Docker Images                                      │
│    • Backend image                                          │
│    • Frontend image                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Push to Container Registry                               │
│    • GitHub Container Registry (GHCR)                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Deploy to Production                                     │
│    • SSH to production server                               │
│    • Pull latest images                                     │
│    • Run docker-compose up                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Health Check                                             │
│    • Verify services are running                            │
│    • Run smoke tests                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Notify Team                                              │
│    • Slack notification                                     │
│    • Email notification                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 10. System Functionalities

### 10.1 Core Features

#### 10.1.1 Dashboard
**Purpose**: Real-time financial overview

**Features**:
- Total revenue display (KES format)
- Total transactions count
- Total invoices count
- Payment status breakdown
- Recent transactions list
- Recent payments list
- Revenue trends chart
- Payment methods distribution

**Technical Implementation**:
- Real-time data aggregation from MongoDB
- Caching with Redis for performance
- Chart.js for data visualization
- Auto-refresh every 30 seconds

#### 10.1.2 Receipt Management
**Purpose**: Generate and manage receipts with OCR capability

**Features**:
- **Manual Receipt Creation**: 
  - Line item management
  - Tax calculation (16% VAT)
  - Customer information
  - Payment method selection
  - PDF generation with QR code

- **OCR Upload**:
  - Image upload (JPG, PNG, WEBP, PDF)
  - Google Gemini AI extraction
  - Automatic data parsing
  - Customer detection
  - Line items extraction
  - Amount calculation

- **Receipt Management**:
  - List all receipts with pagination
  - Filter by type, status, date
  - Search by receipt number or customer
  - Download PDF
  - View receipt details
  - Receipt statistics

- **Backward Compatibility**:
  - Adapter pattern for old receipts
  - Automatic format transformation
  - No data migration required

**Technical Implementation**:
```python
# OCR Processing Flow
1. Upload Image → Save to /uploads/receipts/images/
2. Send to Gemini AI → Extract text data
3. Parse JSON Response → Extract customer, items, amounts
4. Create Receipt Object → Save to MongoDB
5. Generate PDF → Save to /uploads/receipts/pdfs/
6. Return Receipt → With PDF path
```

#### 10.1.3 Invoice Management
**Purpose**: Create, send, and track invoices

**Features**:
- Invoice creation with line items
- Customer selection
- Tax calculation
- Due date tracking
- Status management (draft, sent, paid, overdue)
- PDF generation
- Email sending
- Payment tracking
- Invoice history

**Business Logic**:
- Automatic overdue detection
- Payment reminders
- Aging reports (30/60/90 days)
- Revenue recognition

#### 10.1.4 Payment Processing
**Purpose**: Record and track payments

**Features**:
- Payment recording
- M-Pesa integration
- Bank transfer tracking
- Cash payment recording
- Payment verification
- Receipt generation
- Payment reconciliation
- Refund processing

**M-Pesa Integration**:
- STK Push for customer payments
- Callback handling
- Transaction verification
- Automatic invoice updating

#### 10.1.5 Customer Management
**Purpose**: Manage customer database

**Features**:
- Customer profiles
- Contact information
- Business details (KRA PIN)
- Transaction history
- Invoice history
- Payment history
- Outstanding balance tracking
- Customer segmentation
- Customer search

#### 10.1.6 AI Financial Insights
**Purpose**: AI-powered financial analysis using RAG

**Features**:
- **Conversational AI**:
  - Natural language queries
  - Context-aware responses
  - Financial recommendations

- **Analysis Types**:
  - Transaction pattern analysis
  - Cash flow forecasting
  - Expense categorization
  - Revenue trends
  - Customer analytics
  - Profitability analysis

- **Data Sources**:
  - Transactions (707 records)
  - Invoices (999 records)
  - Receipts
  - Customers
  - Payments

**Technical Implementation**:
- **RAG Architecture**:
  - Retrieval: MongoDB queries
  - Augmentation: Context building
  - Generation: Google Gemini AI

- **Context Building**:
  ```python
  1. Query Database → Get relevant data
  2. Aggregate Data → Calculate statistics
  3. Format Context → Markdown structure
  4. Send to Gemini → With user query
  5. Generate Response → AI analysis
  6. Return to User → Formatted answer
  ```

#### 10.1.7 OCR Processing
**Purpose**: Extract data from images

**Features**:
- Multi-format support (JPG, PNG, WEBP, PDF)
- Google Gemini Vision AI
- High accuracy (95%+ confidence)
- Structured data extraction
- Background processing with Celery
- Progress tracking
- Error handling

**Extraction Capabilities**:
- Merchant information
- Transaction date
- Line items with prices
- Total amounts
- Tax amounts
- Payment methods

#### 10.1.8 M-Pesa Integration
**Purpose**: Mobile money payment processing

**Features**:
- STK Push initiation
- Customer phone validation
- Payment confirmation
- Callback handling
- Transaction logging
- Balance inquiry
- Transaction status checking

**Daraja API Integration**:
- OAuth authentication
- Request signing
- Callback URL management
- Error handling

#### 10.1.9 Reconciliation
**Purpose**: Match payments to invoices

**Features**:
- Automatic reconciliation
- Manual reconciliation
- Bulk reconciliation
- Reconciliation rules
- Exception handling
- Audit trail

**Reconciliation Logic**:
```python
1. Get Unreconciled Payments
2. Match by Amount + Customer
3. Match by Reference Number
4. Match by Date Range
5. Manual Review for Exceptions
6. Update Invoice Status
7. Generate Reconciliation Report
```

#### 10.1.10 Reporting
**Purpose**: Financial reports and analytics

**Features**:
- **Financial Statements**:
  - Income Statement
  - Balance Sheet
  - Cash Flow Statement
  - Profit & Loss

- **Management Reports**:
  - Sales reports
  - Expense reports
  - Customer reports
  - Aging reports

- **Analytics**:
  - Revenue trends
  - Expense trends
  - Customer lifetime value
  - Payment patterns

- **Export Formats**:
  - PDF
  - Excel (CSV)
  - JSON

#### 10.1.11 Expense Management
**Purpose**: Track business expenses

**Features**:
- Expense recording
- Receipt attachment
- Category management
- Expense approval workflow
- Budget tracking
- Expense reports
- Tax deduction tracking

#### 10.1.12 Automation
**Purpose**: Automate repetitive tasks

**Features**:
- Scheduled reports
- Automatic payment reminders
- Recurring invoices
- Auto-reconciliation
- Email automation
- Background tasks with Celery

### 10.2 User Roles & Permissions

```
┌──────────────────────────────────────────────────────────────┐
│ Role: Admin                                                   │
├──────────────────────────────────────────────────────────────┤
│ • Full system access                                         │
│ • User management                                            │
│ • System configuration                                       │
│ • All CRUD operations                                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Role: Accountant                                             │
├──────────────────────────────────────────────────────────────┤
│ • Invoice management                                         │
│ • Payment recording                                          │
│ • Reconciliation                                             │
│ • Financial reports                                          │
│ • Customer management                                        │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Role: User                                                    │
├──────────────────────────────────────────────────────────────┤
│ • View dashboard                                             │
│ • Create receipts                                            │
│ • View invoices                                              │
│ • Limited customer access                                    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Role: Viewer                                                  │
├──────────────────────────────────────────────────────────────┤
│ • Read-only access                                           │
│ • View reports                                               │
│ • Export data                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## 11. Performance Optimization

### 11.1 Backend Optimization
- **Database Indexing**: Strategic indexes on frequently queried fields
- **Connection Pooling**: Reuse database connections
- **Async Operations**: Non-blocking I/O with Motor
- **Caching**: Redis for frequently accessed data
- **Query Optimization**: Projection to select only needed fields
- **Background Tasks**: Celery for heavy operations

### 11.2 Frontend Optimization
- **Code Splitting**: Next.js automatic code splitting
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Load components on demand
- **Memoization**: React.memo for expensive components
- **Debouncing**: For search and input fields
- **CDN**: Static assets served from CDN

### 11.3 Database Optimization
- **Compound Indexes**: For common query patterns
- **Text Indexes**: For search functionality
- **TTL Indexes**: Automatic cache cleanup
- **Aggregation Pipeline**: Efficient data processing
- **Read/Write Concern**: Balance consistency and performance

---

## 12. Monitoring & Observability

### 12.1 Monitoring Stack
- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Application Logs**: Structured logging with Python logging
- **Error Tracking**: Exception logging
- **Performance Metrics**: Response times, throughput

### 12.2 Key Metrics
- API response times
- Database query times
- Error rates
- Request rates
- CPU/Memory usage
- Active users
- Transaction volumes

---

## 13. Backup & Disaster Recovery

### 13.1 Backup Strategy
- **MongoDB Backups**: Daily automated backups
- **File System Backups**: Weekly backups of uploads
- **Database Replication**: MongoDB replica sets
- **Point-in-Time Recovery**: Transaction log backups

### 13.2 Disaster Recovery
- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 24 hours
- **Backup Location**: Off-site cloud storage
- **Recovery Testing**: Monthly DR drills

---

## 14. Future Enhancements

### 14.1 Planned Features
- [ ] Mobile app (React Native)
- [ ] Advanced analytics with ML predictions
- [ ] Multi-currency support
- [ ] Multiple business/branch support
- [ ] Inventory management
- [ ] Payroll integration
- [ ] Tax filing automation
- [ ] Bank account integration
- [ ] E-commerce integration
- [ ] WhatsApp integration for notifications

### 14.2 Scalability Roadmap
- [ ] Microservices architecture
- [ ] Kubernetes orchestration
- [ ] Horizontal scaling
- [ ] Database sharding
- [ ] CDN integration
- [ ] Load balancing
- [ ] Multi-region deployment

---

## 15. Conclusion

FinGuard is a comprehensive, production-ready financial management system specifically designed for Kenyan SMBs. With its modern tech stack, robust architecture, and AI-powered features, it provides businesses with the tools they need to manage their finances effectively.

### Key Strengths
✅ Modern full-stack architecture
✅ AI-powered insights with Gemini AI
✅ OCR receipt processing
✅ M-Pesa integration for local payments
✅ Comprehensive invoice management
✅ Production-ready with Docker
✅ Security-first approach
✅ Scalable and maintainable

### System Status
- **Production Ready**: ✅ Yes
- **Documentation**: ✅ Complete
- **Testing**: ✅ Comprehensive test suite
- **Deployment**: ✅ Docker-based deployment
- **Monitoring**: ✅ Prometheus + Grafana
- **Security**: ✅ JWT auth, RBAC, encryption

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Maintained By**: FinGuard Development Team
