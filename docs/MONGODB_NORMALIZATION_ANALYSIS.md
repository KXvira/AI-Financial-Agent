# MongoDB Database Normalization Analysis & Recommendations

## Executive Summary

This document provides a comprehensive analysis of the current MongoDB schema for the FinGuard-Lite-Enhanced application and proposes a fully normalized database design to improve data integrity, reduce redundancy, and enforce better relationships between collections.

**Date:** October 14, 2025  
**Database:** MongoDB (Document-based NoSQL)  
**Current Collections:** 7 main collections  
**Target Normalization Level:** 3NF with MongoDB best practices

---

## 1. Current MongoDB Collection Structure Analysis

### 1.1 Existing Collections

Based on the codebase analysis, the following collections are currently in use:

1. **users** - User authentication and authorization
2. **customers** - Customer information and financial summaries
3. **invoices** - Invoice records with embedded customer and items
4. **transactions** - Financial transactions (payments, expenses)
5. **mpesa_payments** - M-Pesa payment gateway records
6. **receipts** - Receipt/payment records
7. **ocr_results** - OCR processing results

### 1.2 Current Schema Issues & Redundancies

#### ❌ **Issue 1: Customer Data Duplication**

**Current State:**
```javascript
// In invoices collection
{
  invoice_number: "INV-2025-10-0001",
  customer: {
    id: "CUST-0001",
    name: "Acme Corp Kenya Ltd",
    phone_number: "254712345678",
    email: "acme@example.com",
    address: "123 Main St",
    city: "Nairobi",
    country: "Kenya"
  },
  // ... other fields
}
```

**Problems:**
- Customer data is **fully embedded** in every invoice
- If customer email/phone changes, all invoices remain outdated
- Customer information is duplicated across thousands of invoices
- No single source of truth for customer data
- Inconsistent customer data across invoices

#### ❌ **Issue 2: Invoice Items Not Separated**

**Current State:**
```javascript
{
  invoice_number: "INV-2025-10-0001",
  items: [
    {
      id: "item1",
      description: "Office Supplies",
      quantity: 5,
      unit_price: 1000,
      amount: 5000,
      tax_rate: 0.16,
      tax_amount: 800
    }
  ],
  // ... other fields
}
```

**Problems:**
- Items are embedded arrays, making it difficult to:
  - Query all invoices containing a specific product/service
  - Track product/service sales history
  - Generate product-wise revenue reports
  - Maintain a product catalog with consistent pricing

#### ❌ **Issue 3: Transaction & Payment Duplication**

**Current State:**
```javascript
// In transactions collection
{
  reference: "QW12345678XY",
  gateway: "mpesa",
  amount: 5800,
  phone_number: "254712345678",
  matched_invoice_id: "INV-2025-10-0001"
}

// In mpesa_payments collection (DUPLICATE!)
{
  TransID: "QW12345678XY",
  TransAmount: 5800,
  MSISDN: "254712345678",
  InvoiceNumber: "INV-2025-10-0001"
}

// In invoices collection (DUPLICATE!)
{
  invoice_number: "INV-2025-10-0001",
  payment_transactions: ["trans_id_1", "trans_id_2"],
  payment_gateway: "mpesa",
  gateway_reference: "QW12345678XY"
}
```

**Problems:**
- Same payment information stored in 3 different collections
- M-Pesa specific data should be in a separate `payment_gateway_data` collection
- No clear relationship model between payments and invoices
- Reconciliation data scattered across collections

#### ❌ **Issue 4: User Activity Not Tracked**

**Current State:**
```javascript
// In users collection
{
  email: "admin@example.com",
  last_login: "2025-10-14T10:30:00Z",
  failed_login_attempts: 2
}
```

**Problems:**
- No audit trail of user actions
- Login history limited to single timestamp
- Cannot track who created/modified invoices, customers, etc.
- No session management collection

#### ❌ **Issue 5: Customer Financial Summaries Denormalized**

**Current State:**
```javascript
// In customers collection
{
  customer_id: "CUST-0001",
  name: "Acme Corp",
  total_invoices: 45,
  total_billed: 2500000.00,
  total_paid: 2100000.00,
  outstanding_balance: 400000.00,
  payment_status: "good"
}
```

**Problems:**
- Financial summaries are **calculated data** stored in customer records
- Risk of data inconsistency if not properly updated
- Should be computed dynamically or cached separately
- Violates normalization principles (derived attributes)

#### ❌ **Issue 6: No Product/Service Catalog**

**Current State:**
- Products/services exist only as strings in invoice items
- No way to track:
  - Standard pricing
  - Service/product descriptions
  - Tax rates per product
  - Product categories

---

## 2. Proposed Normalized Schema Design (3NF)

### 2.1 Core Principles

1. **Eliminate Redundancy**: Remove duplicate data
2. **Establish Clear References**: Use ObjectId references between collections
3. **Single Source of Truth**: Each piece of data stored in one place
4. **Historical Accuracy**: Snapshot data where needed (e.g., item prices at invoice time)
5. **MongoDB Best Practices**: Balance normalization with query performance

### 2.2 Normalized Collection Structure

```
📦 Normalized Collections (11 total)
├── 👥 users                    # User accounts
├── 👥 user_sessions             # Active user sessions (NEW)
├── 📝 audit_logs               # User activity tracking (NEW)
├── 🏢 customers                # Customer master data (normalized)
├── 📦 products                 # Product/service catalog (NEW)
├── 🧾 invoices                 # Invoice headers (normalized)
├── 🧾 invoice_items            # Invoice line items (NEW - separated)
├── 💰 payments                 # Unified payment records (normalized)
├── 🔌 payment_gateway_data     # Gateway-specific data (NEW)
├── 🧾 receipts                 # Receipt records
└── 📸 ocr_results              # OCR processing results
```

---

## 3. Detailed Normalized Schema Definitions

### 3.1 Users Collection (Normalized)

```javascript
// Collection: users
{
  _id: ObjectId("..."),
  email: "admin@example.com",
  password_hash: "$2b$12$...",
  full_name: "John Doe",
  role: "admin",  // admin, manager, accountant, viewer
  status: "active",  // active, inactive, suspended, pending
  department: "Finance",
  phone: "+254712345678",
  avatar_url: "https://...",
  
  // Permissions
  custom_permissions: ["invoices.delete", "reports.export"],
  
  // Security
  failed_login_attempts: 0,
  locked_until: null,
  password_changed_at: ISODate("2025-10-01T00:00:00Z"),
  
  // Metadata (NO last_login here - moved to sessions)
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-10-14T00:00:00Z"),
  created_by: ObjectId("..."),  // Reference to another user
}

// Indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ status: 1 })
db.users.createIndex({ role: 1 })
```

**Changes:**
- ✅ Removed `last_login` (moved to `user_sessions`)
- ✅ Added `created_by` reference
- ✅ Added `password_changed_at` for security

---

### 3.2 User Sessions Collection (NEW)

```javascript
// Collection: user_sessions
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),  // Reference to users
  token_hash: "...",  // Hashed JWT token for revocation
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  device_type: "desktop",  // desktop, mobile, tablet
  
  // Session lifecycle
  created_at: ISODate("2025-10-14T10:00:00Z"),
  expires_at: ISODate("2025-10-15T10:00:00Z"),
  last_activity: ISODate("2025-10-14T12:30:00Z"),
  revoked_at: null,
  revoked_reason: null,  // "logout", "security", "expired"
}

// Indexes
db.user_sessions.createIndex({ user_id: 1, revoked_at: 1 })
db.user_sessions.createIndex({ token_hash: 1 }, { unique: true })
db.user_sessions.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 })  // TTL index
```

**Purpose:**
- Track active user sessions
- Enable token revocation
- Session analytics
- Multi-device login management

---

### 3.3 Audit Logs Collection (NEW)

```javascript
// Collection: audit_logs
{
  _id: ObjectId("..."),
  user_id: ObjectId("..."),  // Reference to users
  action: "invoice.create",  // Namespaced action
  resource_type: "invoice",  // invoice, customer, payment, etc.
  resource_id: ObjectId("..."),  // Reference to the resource
  
  // Change tracking
  changes: {
    before: { status: "draft", total: 5000 },
    after: { status: "sent", total: 5800 }
  },
  
  // Context
  ip_address: "192.168.1.100",
  user_agent: "Mozilla/5.0...",
  session_id: ObjectId("..."),  // Reference to user_sessions
  
  // Metadata
  timestamp: ISODate("2025-10-14T10:00:00Z"),
  success: true,
  error_message: null
}

// Indexes
db.audit_logs.createIndex({ user_id: 1, timestamp: -1 })
db.audit_logs.createIndex({ resource_type: 1, resource_id: 1 })
db.audit_logs.createIndex({ action: 1, timestamp: -1 })
db.audit_logs.createIndex({ timestamp: -1 })  // For recent activity
```

**Purpose:**
- Complete audit trail
- Track who changed what and when
- Compliance and security
- Debugging and troubleshooting

---

### 3.4 Customers Collection (Normalized)

```javascript
// Collection: customers
{
  _id: ObjectId("..."),
  customer_id: "CUST-0001",  // Business ID (for display)
  
  // Basic information
  name: "Acme Corp Kenya Ltd",
  email: "info@acmecorp.com",
  phone: "254712345678",
  secondary_email: "billing@acmecorp.com",
  secondary_phone: "254722345678",
  
  // Address (embedded - changes infrequently)
  address: {
    street: "123 Kimathi Street",
    city: "Nairobi",
    postal_code: "00100",
    country: "Kenya"
  },
  
  // Business details
  business_type: "technology",
  tax_id: "P051234567X",
  
  // Payment preferences
  preferred_payment_method: "mpesa",
  payment_terms: "net_30",
  credit_limit: 500000.00,
  
  // Automation settings
  auto_send_invoices: false,
  send_reminders: true,
  
  // AI preferences (embedded - specific to this customer)
  ai_preferences: {
    invoice_template: "professional",
    language: "english",
    include_tax: true,
    default_currency: "KES"
  },
  
  // Status
  status: "active",  // active, inactive, suspended
  
  // Metadata
  notes: "VIP customer - priority support",
  tags: ["vip", "technology", "enterprise"],
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-10-14T00:00:00Z"),
  created_by: ObjectId("...")  // Reference to users
  
  // ❌ REMOVED: total_invoices, total_billed, total_paid, outstanding_balance
  // ✅ These are now computed via aggregation or cached separately
}

// Indexes
db.customers.createIndex({ customer_id: 1 }, { unique: true })
db.customers.createIndex({ email: 1 }, { unique: true })
db.customers.createIndex({ phone: 1 })
db.customers.createIndex({ status: 1 })
db.customers.createIndex({ name: "text", email: "text" })  // Text search
```

**Changes:**
- ❌ Removed computed fields (total_invoices, total_billed, etc.)
- ✅ Keep address embedded (doesn't change often, always accessed together)
- ✅ Keep ai_preferences embedded (customer-specific, not reusable)
- ✅ Added created_by for audit trail

---

### 3.5 Products/Services Collection (NEW)

```javascript
// Collection: products
{
  _id: ObjectId("..."),
  product_id: "PROD-0001",  // Business ID
  
  // Product details
  name: "Office Supplies",
  description: "General office supplies and stationery",
  sku: "OFF-SUPP-001",
  category: "office_supplies",  // office_supplies, it_services, consulting, etc.
  
  // Pricing
  unit_price: 1000.00,
  currency: "KES",
  tax_rate: 0.16,  // 16% VAT
  
  // Inventory (if applicable)
  is_service: false,
  track_inventory: true,
  current_stock: 100,
  reorder_level: 20,
  
  // Status
  status: "active",  // active, discontinued
  
  // Metadata
  created_at: ISODate("2025-01-01T00:00:00Z"),
  updated_at: ISODate("2025-10-14T00:00:00Z"),
  created_by: ObjectId("...")
}

// Indexes
db.products.createIndex({ product_id: 1 }, { unique: true })
db.products.createIndex({ sku: 1 }, { unique: true, sparse: true })
db.products.createIndex({ category: 1, status: 1 })
db.products.createIndex({ name: "text", description: "text" })
```

**Purpose:**
- Centralized product/service catalog
- Consistent pricing
- Product analytics
- Inventory management (if needed)

---

### 3.6 Invoices Collection (Normalized)

```javascript
// Collection: invoices
{
  _id: ObjectId("..."),
  invoice_number: "INV-2025-10-0001",
  
  // ✅ REFERENCE to customer (not embedded)
  customer_id: ObjectId("..."),  // Reference to customers collection
  
  // ❌ REMOVED: Embedded customer object
  // ✅ Customer details fetched via $lookup when needed
  
  // Dates
  date_issued: ISODate("2025-10-14T00:00:00Z"),
  due_date: ISODate("2025-11-13T00:00:00Z"),
  
  // Financial totals (calculated from invoice_items)
  subtotal: 5000.00,
  tax_total: 800.00,
  discount_total: 0.00,
  total: 5800.00,
  
  // Payment tracking
  amount_paid: 5800.00,
  balance: 0.00,
  
  // Status
  status: "paid",  // draft, sent, partial, paid, overdue, cancelled, refunded
  
  // Additional info
  notes: "Thank you for your business",
  terms: "Payment due within 30 days",
  
  // Metadata
  created_at: ISODate("2025-10-14T00:00:00Z"),
  updated_at: ISODate("2025-10-14T15:00:00Z"),
  created_by: ObjectId("..."),  // Reference to users
  sent_at: ISODate("2025-10-14T10:00:00Z"),
  sent_by: ObjectId("...")
  
  // ❌ REMOVED: items array (moved to invoice_items collection)
  // ❌ REMOVED: customer object (replaced with customer_id reference)
  // ❌ REMOVED: payment_transactions array (tracked in payments collection)
}

// Indexes
db.invoices.createIndex({ invoice_number: 1 }, { unique: true })
db.invoices.createIndex({ customer_id: 1, date_issued: -1 })
db.invoices.createIndex({ status: 1, due_date: 1 })
db.invoices.createIndex({ date_issued: -1 })
db.invoices.createIndex({ created_by: 1 })
```

**Changes:**
- ✅ Customer data replaced with `customer_id` reference
- ❌ Removed embedded `items` array
- ❌ Removed `payment_transactions` array
- ✅ Added audit fields (created_by, sent_by)

---

### 3.7 Invoice Items Collection (NEW - Normalized)

```javascript
// Collection: invoice_items
{
  _id: ObjectId("..."),
  invoice_id: ObjectId("..."),  // Reference to invoices
  product_id: ObjectId("..."),   // Reference to products (if applicable)
  
  // Line item details
  line_number: 1,  // Order within invoice
  description: "Office Supplies - Premium",
  quantity: 5,
  unit_price: 1000.00,
  
  // Calculations
  subtotal: 5000.00,  // quantity * unit_price
  discount_rate: 0.00,
  discount_amount: 0.00,
  tax_rate: 0.16,
  tax_amount: 800.00,
  total: 5800.00,
  
  // ✅ SNAPSHOT: Product details at time of invoice
  product_snapshot: {
    product_id: "PROD-0001",
    name: "Office Supplies",
    sku: "OFF-SUPP-001",
    category: "office_supplies",
    standard_price: 1000.00  // Price from catalog at invoice time
  },
  
  // Metadata
  created_at: ISODate("2025-10-14T00:00:00Z")
}

// Indexes
db.invoice_items.createIndex({ invoice_id: 1, line_number: 1 })
db.invoice_items.createIndex({ product_id: 1 })
db.invoice_items.createIndex({ invoice_id: 1 })  // For fetching all items
```

**Purpose:**
- Separate invoice line items from invoice header
- Track product sales history
- Product-wise revenue analysis
- Maintain historical accuracy (snapshot of product at invoice time)

**Trade-off:**
- **Embedding vs Referencing**: Items are separated but include a snapshot
- **Rationale**: Enables product analytics while preserving historical accuracy

---

### 3.8 Payments Collection (Unified & Normalized)

```javascript
// Collection: payments
{
  _id: ObjectId("..."),
  payment_id: "PAY-2025-10-0001",  // Business ID
  
  // Payment details
  amount: 5800.00,
  currency: "KES",
  payment_date: ISODate("2025-10-14T10:00:00Z"),
  
  // Gateway information
  gateway: "mpesa",  // mpesa, bank, cash, airtel, other
  gateway_reference: "QW12345678XY",  // M-Pesa receipt, bank ref, etc.
  
  // Customer/payer information
  customer_id: ObjectId("..."),  // Reference to customers (if known)
  payer_name: "John Doe",
  payer_phone: "254712345678",
  payer_email: "john@example.com",
  
  // Invoice relationship
  invoice_id: ObjectId("..."),  // Reference to invoices
  allocated_amount: 5800.00,  // Amount applied to this invoice
  
  // Status
  status: "completed",  // initiated, pending, completed, failed, cancelled, refunded
  
  // Reconciliation
  reconciliation_status: "matched",  // pending, matched, partial, unmatched, needs_review
  reconciliation_date: ISODate("2025-10-14T10:05:00Z"),
  reconciliation_confidence: 0.95,
  reconciliation_method: "automatic",  // automatic, manual
  reconciliation_notes: "",
  
  // Metadata
  created_at: ISODate("2025-10-14T10:00:00Z"),
  updated_at: ISODate("2025-10-14T10:05:00Z"),
  created_by: ObjectId("..."),  // User who recorded payment (for manual entries)
  
  // ❌ REMOVED: Gateway-specific fields (moved to payment_gateway_data)
}

// Indexes
db.payments.createIndex({ payment_id: 1 }, { unique: true })
db.payments.createIndex({ invoice_id: 1, payment_date: -1 })
db.payments.createIndex({ customer_id: 1, payment_date: -1 })
db.payments.createIndex({ gateway_reference: 1, gateway: 1 })
db.payments.createIndex({ status: 1, payment_date: -1 })
db.payments.createIndex({ reconciliation_status: 1 })
```

**Changes:**
- ✅ Unified payment records (replaces separate `transactions` and `mpesa_payments`)
- ✅ Clear reference to invoice and customer
- ✅ Reconciliation tracking
- ❌ Removed gateway-specific fields

---

### 3.9 Payment Gateway Data Collection (NEW)

```javascript
// Collection: payment_gateway_data
{
  _id: ObjectId("..."),
  payment_id: ObjectId("..."),  // Reference to payments
  gateway: "mpesa",
  
  // Gateway-specific data (flexible schema)
  gateway_data: {
    // M-Pesa specific
    TransactionType: "CustomerPayBillOnline",
    TransID: "QW12345678XY",
    TransTime: "20251014100530",
    BusinessShortCode: "174379",
    BillRefNumber: "INV-2025-10-0001",
    MSISDN: "254712345678",
    FirstName: "John",
    MiddleName: "",
    LastName: "Doe",
    OrgAccountBalance: 1500000.00,
    
    // Or Bank Transfer specific
    // bank_name: "KCB Bank",
    // account_number: "1234567890",
    // transaction_reference: "BNK123456",
    // swift_code: "KCBLKENX"
  },
  
  // Raw callback/webhook data
  raw_request: { /* Full webhook payload */ },
  raw_response: { /* Gateway response */ },
  
  // Metadata
  created_at: ISODate("2025-10-14T10:00:00Z")
}

// Indexes
db.payment_gateway_data.createIndex({ payment_id: 1 })
db.payment_gateway_data.createIndex({ gateway: 1 })
db.payment_gateway_data.createIndex({ "gateway_data.TransID": 1 }, { sparse: true })
```

**Purpose:**
- Separate gateway-specific data from core payment records
- Flexible schema for different payment gateways
- Preserve raw webhook data for debugging
- Avoid cluttering payment collection with gateway-specific fields

---

### 3.10 Receipts Collection

```javascript
// Collection: receipts
{
  _id: ObjectId("..."),
  receipt_number: "RCT-2025-10-0001",
  
  // References
  payment_id: ObjectId("..."),  // Reference to payments
  invoice_id: ObjectId("..."),  // Reference to invoices
  customer_id: ObjectId("..."), // Reference to customers
  
  // Receipt details
  amount: 5800.00,
  payment_method: "M-Pesa",
  receipt_date: ISODate("2025-10-14T10:00:00Z"),
  
  // Receipt file (if generated)
  pdf_url: "https://storage.../receipts/RCT-2025-10-0001.pdf",
  
  // Status
  status: "issued",  // draft, issued, cancelled
  
  // Email tracking
  sent_to_email: "customer@example.com",
  sent_at: ISODate("2025-10-14T10:05:00Z"),
  
  // Metadata
  created_at: ISODate("2025-10-14T10:00:00Z"),
  created_by: ObjectId("...")
}

// Indexes
db.receipts.createIndex({ receipt_number: 1 }, { unique: true })
db.receipts.createIndex({ payment_id: 1 })
db.receipts.createIndex({ invoice_id: 1 })
db.receipts.createIndex({ customer_id: 1, receipt_date: -1 })
```

---

### 3.11 OCR Results Collection

```javascript
// Collection: ocr_results
{
  _id: ObjectId("..."),
  
  // File information
  image_path: "/uploads/receipts/20251014_receipt.jpg",
  file_hash: "sha256:abc123...",  // For deduplication
  
  // Processing details
  engine: "gemini_vision",  // tesseract, gemini_vision, combined
  status: "completed",  // pending, processing, completed, failed
  confidence: 0.85,
  processing_time: 2.5,  // seconds
  
  // OCR results
  extracted_text: "JAVA HOUSE COFFEE\nTotal: KES 928.00...",
  
  // Structured data extraction
  structured_data: {
    vendor_name: "JAVA HOUSE COFFEE",
    total_amount: 928.00,
    date: "2025-10-14",
    items: [
      { description: "Cappuccino", amount: 450.00 },
      { description: "Sandwich", amount: 478.00 }
    ]
  },
  
  // Linked records (if created)
  created_invoice_id: ObjectId("..."),
  created_expense_id: ObjectId("..."),
  
  // Metadata
  created_at: ISODate("2025-10-14T10:00:00Z"),
  created_by: ObjectId("...")
}

// Indexes
db.ocr_results.createIndex({ file_hash: 1 }, { unique: true, sparse: true })
db.ocr_results.createIndex({ status: 1, created_at: -1 })
db.ocr_results.createIndex({ created_by: 1, created_at: -1 })
```

---

## 4. Embedding vs Referencing Trade-offs

### 4.1 When to EMBED (Denormalize)

✅ **Use embedding when:**

1. **Data is accessed together** (1-to-1 or 1-to-few)
   - Example: Customer address in customer document
   - Example: AI preferences in customer document

2. **Data doesn't change independently**
   - Example: Historical item details in invoice items (snapshot)

3. **Data is specific to the parent**
   - Example: Invoice item belongs only to that invoice

4. **Read performance is critical**
   - Embedding avoids multiple queries/joins

**Examples in this schema:**
```javascript
// ✅ EMBED: Address in customer (always accessed together)
{
  customer_id: "CUST-0001",
  name: "Acme Corp",
  address: {  // EMBEDDED
    street: "123 Main St",
    city: "Nairobi"
  }
}

// ✅ EMBED: Product snapshot in invoice items (historical accuracy)
{
  invoice_id: ObjectId("..."),
  product_id: ObjectId("..."),
  description: "Office Supplies",
  product_snapshot: {  // EMBEDDED SNAPSHOT
    name: "Office Supplies",
    standard_price: 1000.00
  }
}
```

### 4.2 When to REFERENCE (Normalize)

✅ **Use referencing when:**

1. **Data is shared across documents**
   - Example: Customer referenced by multiple invoices

2. **Data changes frequently**
   - Example: Customer email/phone can change

3. **Data is large or unbounded**
   - Example: Many invoice items per invoice

4. **Need to query relationships**
   - Example: Find all invoices for a customer

5. **Duplication would cause consistency issues**
   - Example: Product pricing should be consistent

**Examples in this schema:**
```javascript
// ✅ REFERENCE: Customer in invoice (shared, updatable)
{
  invoice_number: "INV-0001",
  customer_id: ObjectId("..."),  // REFERENCE
  // Customer details fetched via $lookup when needed
}

// ✅ REFERENCE: Invoice items in separate collection (unbounded, queryable)
// Instead of embedding all items in invoice:
{
  invoice_id: ObjectId("..."),
  product_id: ObjectId("..."),
  description: "...",
  quantity: 5
}
```

### 4.3 Hybrid Approach: Reference + Snapshot

For **historical accuracy**, use both:

```javascript
// Invoice item references product BUT includes snapshot
{
  invoice_id: ObjectId("..."),
  product_id: ObjectId("..."),  // ✅ REFERENCE (for analytics)
  
  // Current values (can differ from catalog)
  description: "Office Supplies - Premium",
  unit_price: 1200.00,  // Customer-specific price
  
  product_snapshot: {  // ✅ SNAPSHOT (for history)
    product_id: "PROD-0001",
    name: "Office Supplies",
    standard_price: 1000.00,  // Catalog price at invoice time
    sku: "OFF-SUPP-001"
  }
}
```

**Benefits:**
- Can update product catalog without affecting old invoices
- Can still analyze: "Which invoices included Product X?"
- Maintains historical accuracy for auditing

---

## 5. Referential Integrity & Data Consistency

### 5.1 MongoDB Limitations

MongoDB does **NOT** enforce:
- ❌ Foreign key constraints
- ❌ Cascading deletes
- ❌ Referential integrity checks

**You must implement these at the application level!**

### 5.2 Best Practices for Referential Integrity

#### Strategy 1: Application-Level Validation

```python
async def delete_customer(customer_id: ObjectId):
    """Delete customer with integrity checks"""
    
    # Check for dependent records
    invoice_count = await db.invoices.count_documents({
        "customer_id": customer_id
    })
    
    if invoice_count > 0:
        raise ValueError(
            f"Cannot delete customer with {invoice_count} invoices. "
            "Archive instead or delete invoices first."
        )
    
    # Safe to delete
    await db.customers.delete_one({"_id": customer_id})
```

#### Strategy 2: Use MongoDB Transactions

```python
async def create_invoice_with_items(invoice_data, items_data):
    """Create invoice and items atomically"""
    
    async with await db.client.start_session() as session:
        async with session.start_transaction():
            # Insert invoice
            invoice_result = await db.invoices.insert_one(
                invoice_data,
                session=session
            )
            invoice_id = invoice_result.inserted_id
            
            # Insert invoice items
            for item in items_data:
                item["invoice_id"] = invoice_id
            
            await db.invoice_items.insert_many(
                items_data,
                session=session
            )
            
            # Both succeed or both fail
            await session.commit_transaction()
```

#### Strategy 3: Schema Validation (JSON Schema)

```javascript
// Apply schema validation at database level
db.createCollection("invoices", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["invoice_number", "customer_id", "date_issued", "total"],
      properties: {
        invoice_number: {
          bsonType: "string",
          pattern: "^INV-[0-9]{4}-[0-9]{2}-[0-9]{4}$"
        },
        customer_id: {
          bsonType: "objectId"
        },
        total: {
          bsonType: "double",
          minimum: 0
        },
        status: {
          enum: ["draft", "sent", "partial", "paid", "overdue", "cancelled"]
        }
      }
    }
  },
  validationAction: "error",  // Reject invalid documents
  validationLevel: "strict"
})
```

#### Strategy 4: Soft Deletes

```javascript
// Instead of deleting, mark as deleted
{
  customer_id: "CUST-0001",
  name: "Acme Corp",
  status: "active",
  deleted_at: null,  // null = not deleted
  deleted_by: null
}

// When "deleting":
db.customers.updateOne(
  { customer_id: "CUST-0001" },
  {
    $set: {
      deleted_at: new Date(),
      deleted_by: ObjectId("..."),
      status: "deleted"
    }
  }
)

// Filter out deleted records in queries
db.customers.find({ deleted_at: null })
```

#### Strategy 5: Background Integrity Checker

```python
async def check_orphaned_invoice_items():
    """Find invoice items without valid invoices"""
    
    # Use aggregation to find orphans
    pipeline = [
        {
            "$lookup": {
                "from": "invoices",
                "localField": "invoice_id",
                "foreignField": "_id",
                "as": "invoice"
            }
        },
        {
            "$match": {
                "invoice": { "$size": 0 }  # No matching invoice
            }
        }
    ]
    
    orphaned_items = await db.invoice_items.aggregate(pipeline).to_list(None)
    
    if orphaned_items:
        print(f"⚠️ Found {len(orphaned_items)} orphaned invoice items!")
        # Log, alert, or clean up
```

### 5.3 Data Consistency Strategies

#### A. Update Customer Financial Summaries

```python
async def update_customer_financials(customer_id: ObjectId):
    """Recalculate customer financial summary"""
    
    # Aggregate invoice totals
    pipeline = [
        { "$match": { "customer_id": customer_id } },
        {
            "$group": {
                "_id": None,
                "total_invoices": { "$sum": 1 },
                "total_billed": { "$sum": "$total" },
                "outstanding": { "$sum": "$balance" }
            }
        }
    ]
    
    result = await db.invoices.aggregate(pipeline).to_list(1)
    
    if result:
        stats = result[0]
        # Store in separate summary collection (cache)
        await db.customer_financial_summary.update_one(
            { "customer_id": customer_id },
            {
                "$set": {
                    "total_invoices": stats["total_invoices"],
                    "total_billed": stats["total_billed"],
                    "outstanding_balance": stats["outstanding"],
                    "updated_at": datetime.now()
                }
            },
            upsert=True
        )
```

#### B. Invoice Status Updates

```python
async def update_invoice_status_on_payment(payment_data):
    """Update invoice status when payment received"""
    
    invoice_id = payment_data["invoice_id"]
    payment_amount = payment_data["amount"]
    
    # Get invoice
    invoice = await db.invoices.find_one({"_id": invoice_id})
    
    if not invoice:
        raise ValueError("Invoice not found")
    
    # Calculate new balance
    new_amount_paid = invoice["amount_paid"] + payment_amount
    new_balance = invoice["total"] - new_amount_paid
    
    # Determine new status
    if new_balance <= 0:
        new_status = "paid"
    elif new_amount_paid > 0:
        new_status = "partial"
    else:
        new_status = invoice["status"]
    
    # Update invoice
    await db.invoices.update_one(
        {"_id": invoice_id},
        {
            "$set": {
                "amount_paid": new_amount_paid,
                "balance": new_balance,
                "status": new_status,
                "updated_at": datetime.now()
            }
        }
    )
```

---

## 6. Migration Strategy

### 6.1 Migration Steps

1. **Phase 1: Create New Collections**
   - Create `products`, `invoice_items`, `user_sessions`, `audit_logs`, `payment_gateway_data`
   - Add indexes

2. **Phase 2: Migrate Data**
   - Extract customers from invoices
   - Split invoice items into separate collection
   - Unify transactions and mpesa_payments into payments
   - Move gateway-specific data

3. **Phase 3: Update Application Code**
   - Update queries to use $lookup for references
   - Implement transaction support
   - Add validation logic

4. **Phase 4: Verify & Test**
   - Data integrity checks
   - Performance testing
   - Rollback plan

5. **Phase 5: Clean Up**
   - Remove old denormalized fields
   - Drop temporary migration collections

### 6.2 Example Migration Script

```python
async def migrate_invoices_to_normalized():
    """Migrate invoices to normalized schema"""
    
    print("Starting invoice migration...")
    
    # Get all invoices
    invoices = await db.invoices.find({}).to_list(None)
    
    for invoice in invoices:
        # 1. Extract customer
        customer_data = invoice.get("customer", {})
        if customer_data:
            # Check if customer exists
            existing = await db.customers.find_one({
                "email": customer_data.get("email")
            })
            
            if not existing:
                # Create new customer
                customer_doc = {
                    "customer_id": customer_data.get("id", f"CUST-{uuid.uuid4().hex[:8]}"),
                    "name": customer_data.get("name"),
                    "email": customer_data.get("email"),
                    "phone": customer_data.get("phone_number"),
                    "address": {
                        "street": customer_data.get("address", ""),
                        "city": customer_data.get("city", "Nairobi"),
                        "country": customer_data.get("country", "Kenya")
                    },
                    "status": "active",
                    "created_at": invoice.get("created_at", datetime.now()),
                    "updated_at": datetime.now()
                }
                result = await db.customers.insert_one(customer_doc)
                customer_id = result.inserted_id
            else:
                customer_id = existing["_id"]
            
            # Update invoice with customer reference
            await db.invoices.update_one(
                {"_id": invoice["_id"]},
                {
                    "$set": {"customer_id": customer_id},
                    "$unset": {"customer": ""}  # Remove embedded customer
                }
            )
        
        # 2. Extract invoice items
        items = invoice.get("items", [])
        for idx, item in enumerate(items):
            item_doc = {
                "invoice_id": invoice["_id"],
                "line_number": idx + 1,
                "description": item.get("description"),
                "quantity": item.get("quantity"),
                "unit_price": item.get("unit_price"),
                "subtotal": item.get("amount"),
                "tax_rate": item.get("tax_rate", 0.16),
                "tax_amount": item.get("tax_amount", 0),
                "discount_rate": item.get("discount_rate", 0),
                "discount_amount": item.get("discount_amount", 0),
                "total": item.get("amount", 0) + item.get("tax_amount", 0),
                "created_at": invoice.get("created_at", datetime.now())
            }
            await db.invoice_items.insert_one(item_doc)
        
        # Remove items array from invoice
        await db.invoices.update_one(
            {"_id": invoice["_id"]},
            {"$unset": {"items": ""}}
        )
    
    print(f"Migrated {len(invoices)} invoices")
```

---

## 7. Mongoose Schema Definitions

### 7.1 Customer Schema (Node.js/Mongoose)

```javascript
const mongoose = require('mongoose');

const addressSchema = new mongoose.Schema({
  street: String,
  city: { type: String, default: 'Nairobi' },
  postal_code: { type: String, default: '00100' },
  country: { type: String, default: 'Kenya' }
}, { _id: false });

const aiPreferencesSchema = new mongoose.Schema({
  invoice_template: { type: String, default: 'professional' },
  language: { type: String, default: 'english' },
  include_tax: { type: Boolean, default: true },
  default_currency: { type: String, default: 'KES' }
}, { _id: false });

const customerSchema = new mongoose.Schema({
  customer_id: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  email: { type: String, required: true, unique: true },
  phone: { type: String, required: true },
  secondary_email: String,
  secondary_phone: String,
  
  address: { type: addressSchema, default: () => ({}) },
  
  business_type: { type: String, default: 'general' },
  tax_id: String,
  
  preferred_payment_method: { type: String, default: 'mpesa' },
  payment_terms: { type: String, default: 'net_30' },
  credit_limit: Number,
  
  auto_send_invoices: { type: Boolean, default: false },
  send_reminders: { type: Boolean, default: true },
  
  ai_preferences: { type: aiPreferencesSchema, default: () => ({}) },
  
  status: { 
    type: String, 
    enum: ['active', 'inactive', 'suspended'],
    default: 'active'
  },
  
  notes: String,
  tags: [String],
  
  created_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

// Indexes
customerSchema.index({ customer_id: 1 });
customerSchema.index({ email: 1 });
customerSchema.index({ phone: 1 });
customerSchema.index({ status: 1 });
customerSchema.index({ name: 'text', email: 'text' });

// Middleware to update updated_at
customerSchema.pre('save', function(next) {
  this.updated_at = new Date();
  next();
});

module.exports = mongoose.model('Customer', customerSchema);
```

### 7.2 Invoice Schema (Mongoose)

```javascript
const invoiceSchema = new mongoose.Schema({
  invoice_number: { type: String, required: true, unique: true },
  
  // Reference to customer
  customer_id: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Customer', 
    required: true 
  },
  
  date_issued: { type: Date, required: true },
  due_date: Date,
  
  subtotal: { type: Number, required: true, min: 0 },
  tax_total: { type: Number, default: 0, min: 0 },
  discount_total: { type: Number, default: 0, min: 0 },
  total: { type: Number, required: true, min: 0 },
  
  amount_paid: { type: Number, default: 0, min: 0 },
  balance: { type: Number, default: 0 },
  
  status: {
    type: String,
    enum: ['draft', 'sent', 'partial', 'paid', 'overdue', 'cancelled', 'refunded'],
    default: 'draft'
  },
  
  notes: String,
  terms: String,
  
  created_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  sent_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  sent_at: Date,
  
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

// Indexes
invoiceSchema.index({ invoice_number: 1 });
invoiceSchema.index({ customer_id: 1, date_issued: -1 });
invoiceSchema.index({ status: 1, due_date: 1 });
invoiceSchema.index({ date_issued: -1 });

// Virtual for populating items
invoiceSchema.virtual('items', {
  ref: 'InvoiceItem',
  localField: '_id',
  foreignField: 'invoice_id'
});

// Ensure virtuals are included in JSON output
invoiceSchema.set('toJSON', { virtuals: true });
invoiceSchema.set('toObject', { virtuals: true });

module.exports = mongoose.model('Invoice', invoiceSchema);
```

### 7.3 Invoice Item Schema (Mongoose)

```javascript
const invoiceItemSchema = new mongoose.Schema({
  invoice_id: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Invoice', 
    required: true 
  },
  product_id: { 
    type: mongoose.Schema.Types.ObjectId, 
    ref: 'Product' 
  },
  
  line_number: { type: Number, required: true },
  description: { type: String, required: true },
  quantity: { type: Number, required: true, min: 0 },
  unit_price: { type: Number, required: true, min: 0 },
  
  subtotal: { type: Number, required: true, min: 0 },
  discount_rate: { type: Number, default: 0, min: 0, max: 1 },
  discount_amount: { type: Number, default: 0, min: 0 },
  tax_rate: { type: Number, default: 0.16, min: 0 },
  tax_amount: { type: Number, default: 0, min: 0 },
  total: { type: Number, required: true, min: 0 },
  
  // Product snapshot
  product_snapshot: {
    product_id: String,
    name: String,
    sku: String,
    category: String,
    standard_price: Number
  },
  
  created_at: { type: Date, default: Date.now }
});

// Indexes
invoiceItemSchema.index({ invoice_id: 1, line_number: 1 });
invoiceItemSchema.index({ product_id: 1 });

module.exports = mongoose.model('InvoiceItem', invoiceItemSchema);
```

### 7.4 Payment Schema (Mongoose)

```javascript
const paymentSchema = new mongoose.Schema({
  payment_id: { type: String, required: true, unique: true },
  
  amount: { type: Number, required: true, min: 0 },
  currency: { type: String, default: 'KES' },
  payment_date: { type: Date, required: true },
  
  gateway: { 
    type: String, 
    enum: ['mpesa', 'bank', 'cash', 'airtel', 'other'],
    required: true 
  },
  gateway_reference: String,
  
  customer_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Customer' },
  payer_name: String,
  payer_phone: String,
  payer_email: String,
  
  invoice_id: { type: mongoose.Schema.Types.ObjectId, ref: 'Invoice' },
  allocated_amount: { type: Number, min: 0 },
  
  status: {
    type: String,
    enum: ['initiated', 'pending', 'completed', 'failed', 'cancelled', 'refunded'],
    default: 'initiated'
  },
  
  reconciliation_status: {
    type: String,
    enum: ['pending', 'matched', 'partial', 'unmatched', 'needs_review'],
    default: 'pending'
  },
  reconciliation_date: Date,
  reconciliation_confidence: Number,
  reconciliation_method: String,
  reconciliation_notes: String,
  
  created_by: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  created_at: { type: Date, default: Date.now },
  updated_at: { type: Date, default: Date.now }
});

// Indexes
paymentSchema.index({ payment_id: 1 });
paymentSchema.index({ invoice_id: 1, payment_date: -1 });
paymentSchema.index({ customer_id: 1, payment_date: -1 });
paymentSchema.index({ gateway_reference: 1, gateway: 1 });
paymentSchema.index({ status: 1, payment_date: -1 });
paymentSchema.index({ reconciliation_status: 1 });

module.exports = mongoose.model('Payment', paymentSchema);
```

---

## 8. Query Examples with $lookup

### 8.1 Get Invoice with Customer Details

```javascript
// MongoDB Aggregation
db.invoices.aggregate([
  {
    $match: { invoice_number: "INV-2025-10-0001" }
  },
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "_id",
      as: "customer"
    }
  },
  {
    $unwind: "$customer"
  },
  {
    $lookup: {
      from: "invoice_items",
      localField: "_id",
      foreignField: "invoice_id",
      as: "items"
    }
  }
])

// Mongoose (using populate)
const invoice = await Invoice.findOne({ invoice_number: "INV-2025-10-0001" })
  .populate('customer_id')
  .populate({
    path: 'items',
    options: { sort: { line_number: 1 } }
  })
  .exec();
```

### 8.2 Get Customer with Invoice Summary

```javascript
// Get customer with aggregated invoice stats
db.customers.aggregate([
  {
    $match: { customer_id: "CUST-0001" }
  },
  {
    $lookup: {
      from: "invoices",
      localField: "_id",
      foreignField: "customer_id",
      as: "invoices"
    }
  },
  {
    $addFields: {
      total_invoices: { $size: "$invoices" },
      total_billed: { $sum: "$invoices.total" },
      total_paid: { $sum: "$invoices.amount_paid" },
      outstanding_balance: { $sum: "$invoices.balance" }
    }
  },
  {
    $project: {
      invoices: 0  // Remove invoices array from output
    }
  }
])
```

### 8.3 Get Payment with Full Details

```javascript
// Get payment with invoice, customer, and gateway data
db.payments.aggregate([
  {
    $match: { payment_id: "PAY-2025-10-0001" }
  },
  {
    $lookup: {
      from: "invoices",
      localField: "invoice_id",
      foreignField: "_id",
      as: "invoice"
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "customer_id",
      foreignField: "_id",
      as: "customer"
    }
  },
  {
    $lookup: {
      from: "payment_gateway_data",
      localField: "_id",
      foreignField: "payment_id",
      as: "gateway_data"
    }
  },
  {
    $unwind: { path: "$invoice", preserveNullOrEmptyArray: true }
  },
  {
    $unwind: { path: "$customer", preserveNullOrEmptyArray: true }
  },
  {
    $unwind: { path: "$gateway_data", preserveNullOrEmptyArray: true }
  }
])
```

---

## 9. Performance Considerations

### 9.1 Index Strategy

```javascript
// Critical indexes for normalized schema
db.customers.createIndex({ customer_id: 1 }, { unique: true })
db.customers.createIndex({ email: 1 }, { unique: true })

db.invoices.createIndex({ customer_id: 1, date_issued: -1 })
db.invoices.createIndex({ status: 1, due_date: 1 })

db.invoice_items.createIndex({ invoice_id: 1 })
db.invoice_items.createIndex({ product_id: 1 })

db.payments.createIndex({ invoice_id: 1 })
db.payments.createIndex({ customer_id: 1, payment_date: -1 })

db.audit_logs.createIndex({ user_id: 1, timestamp: -1 })
db.audit_logs.createIndex({ resource_type: 1, resource_id: 1 })
```

### 9.2 Aggregation Pipeline Optimization

```javascript
// Bad: Fetching all data then filtering in code
const invoices = await Invoice.find({}).populate('customer_id').exec();
const paidInvoices = invoices.filter(inv => inv.status === 'paid');

// Good: Filter in database
const paidInvoices = await Invoice.find({ status: 'paid' })
  .populate('customer_id')
  .exec();
```

### 9.3 Caching Strategy

For frequently accessed computed data:

```javascript
// Create a separate collection for cached customer summaries
db.customer_financial_summary.insertOne({
  customer_id: ObjectId("..."),
  total_invoices: 45,
  total_billed: 2500000.00,
  outstanding_balance: 400000.00,
  last_updated: new Date(),
  ttl: 3600  // Cache for 1 hour
})

// Create TTL index for auto-expiration
db.customer_financial_summary.createIndex(
  { last_updated: 1 },
  { expireAfterSeconds: 3600 }
)
```

---

## 10. Summary & Recommendations

### ✅ Key Benefits of Normalization

1. **Data Integrity**: Customer info updated once, reflected everywhere
2. **Reduced Redundancy**: No duplicate customer/product data
3. **Better Analytics**: Can query product sales, customer history separately
4. **Easier Maintenance**: Changes in one place
5. **Audit Trail**: Complete tracking of who did what and when
6. **Referential Clarity**: Clear relationships between entities

### ⚠️ Trade-offs

1. **More Complex Queries**: Need $lookup to join data
2. **Slight Performance Impact**: Joins are slower than embedded docs
3. **Application Logic**: Must enforce referential integrity in code
4. **Transaction Support**: Require multi-document transactions for atomicity

### 🎯 Recommended Approach

**For your financial application:**

1. ✅ **Normalize** customers, invoices, payments (high change frequency, shared data)
2. ✅ **Separate** invoice items (unbounded, queryable)
3. ✅ **Add** products catalog for consistency
4. ✅ **Implement** audit logs for compliance
5. ✅ **Use snapshots** for historical accuracy (product prices, etc.)
6. ✅ **Cache** computed summaries with TTL
7. ✅ **Use transactions** for critical operations
8. ✅ **Enforce validation** at database and application level

---

## 11. Next Steps

1. **Review this document** with your team
2. **Create migration scripts** (provided in Section 6)
3. **Set up test environment** to validate migration
4. **Update application code** to use new schema
5. **Performance test** with real data volumes
6. **Implement gradual rollout** (shadow mode, then cutover)
7. **Monitor and optimize** post-migration

---

**Document Version:** 1.0  
**Last Updated:** October 14, 2025  
**Author:** GitHub Copilot  
**Status:** Ready for Implementation
