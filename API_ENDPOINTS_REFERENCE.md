# API Endpoints - Complete Reference

## Base URL
```
http://localhost:8000
```

## Authentication
Currently: **Disabled for development**  
Future: JWT Bearer token in Authorization header

---

## Dashboard Endpoints

### Get Dashboard Statistics
```http
GET /api/dashboard/stats
```

**Response:**
```json
{
  "total_revenue": 1145892.94,
  "total_payments": 937032.34,
  "outstanding_amount": 207860.6,
  "revenue_change": 341.43,
  "payments_change": 376.97,
  "outstanding_change": 147.45,
  "recent_transactions": [...],
  "recent_payments": [...]
}
```

### Get Dashboard Summary (Stats Only)
```http
GET /api/dashboard/stats/summary
```

### Health Check
```http
GET /api/dashboard/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Dashboard API",
  "version": "1.0.0"
}
```

---

## Expense Endpoints

### Get Expense Summary
```http
GET /api/receipts/demo/summary
```

**Response:**
```json
{
  "totalExpenses": 3398773.12,
  "totalReceipts": 164,
  "monthlyTotal": 425346.64,
  "categorySummary": [
    {
      "category": "Office Supplies",
      "total": 245000.50,
      "count": 23
    }
  ],
  "recentExpenses": [...]
}
```

---

## Invoice Endpoints

### List Invoices
```http
GET /api/invoices?limit=100&status=paid&search=INV-001
```

**Query Parameters:**
- `limit` (optional): Number of results (default: 100)
- `skip` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (paid, pending, overdue)
- `search` (optional): Search by invoice number or customer name

**Response:**
```json
{
  "invoices": [
    {
      "invoice_id": "INV-1001",
      "customer_name": "Tech Solutions Ltd",
      "amount": 45000.00,
      "status": "paid",
      "issue_date": "2024-09-15",
      "due_date": "2024-10-15",
      "description": "Web Development Services"
    }
  ],
  "total": 261,
  "limit": 100,
  "skip": 0
}
```

### Get Single Invoice
```http
GET /api/invoices/{invoice_id}
```

**Response:**
```json
{
  "invoice_id": "INV-1001",
  "customer_name": "Tech Solutions Ltd",
  "customer_email": "info@techsolutions.com",
  "amount": 45000.00,
  "status": "paid",
  "issue_date": "2024-09-15",
  "due_date": "2024-10-15",
  "paid_date": "2024-10-10",
  "items": [...],
  "description": "Web Development Services"
}
```

### Get Invoice Statistics
```http
GET /api/invoices/stats/summary
```

**Response:**
```json
{
  "totalInvoices": 261,
  "paidCount": 219,
  "pendingCount": 42,
  "paidTotal": 4187861.04,
  "pendingTotal": 603405.9,
  "totalAmount": 4791266.94
}
```

---

## Payment Endpoints

### List Payments
```http
GET /api/payments?limit=100&status=completed&search=RK457
```

**Query Parameters:**
- `limit` (optional): Number of results (default: 100)
- `skip` (optional): Number of results to skip (default: 0)
- `status` (optional): Filter by status (completed, pending, failed)
- `search` (optional): Search by M-Pesa reference, customer name, invoice number, or description

**Response:**
```json
{
  "payments": [
    {
      "id": "68ea8b0cbd0e5c75480bed0f",
      "reference": "RC8712375528",
      "client": "Software Startup",
      "date": "2025-10-11",
      "amount": "KES 15,790.87",
      "amountRaw": 15790.87,
      "method": "Mpesa",
      "status": "Completed",
      "invoiceNumber": "INV-1257",
      "phoneNumber": "254722158866",
      "description": "Payment for INV-1257 - Security Audit",
      "created_at": "2025-10-11T19:51:24.590000"
    }
  ],
  "total": 219,
  "limit": 100,
  "skip": 0
}
```

### Get Single Payment
```http
GET /api/payments/{mpesa_reference}
```

**Example:**
```http
GET /api/payments/RC8712375528
```

**Response:**
```json
{
  "id": "68ea8b0cbd0e5c75480bed0f",
  "reference": "RC8712375528",
  "client": "Software Startup",
  "date": "2025-10-11",
  "amount": "KES 15,790.87",
  "amountRaw": 15790.87,
  "method": "Mpesa",
  "status": "Completed",
  "invoiceNumber": "INV-1257",
  "phoneNumber": "254722158866",
  "description": "Payment for INV-1257 - Security Audit",
  "created_at": "2025-10-11T19:51:24.590000",
  "invoice_id": "68ea89dcc2d973dca0591d83"
}
```

### Get Payment Statistics
```http
GET /api/payments/stats/summary
```

**Response:**
```json
{
  "totalPayments": 219,
  "completedCount": 219,
  "pendingCount": 0,
  "completedTotal": 4187861.04,
  "monthlyTotal": 1152365.9,
  "matchedCount": 219,
  "unmatchedCount": 0,
  "aiAccuracy": 100.0
}
```

---

## Response Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (when auth is enabled) |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

---

## Error Response Format

```json
{
  "detail": "Error message description"
}
```

---

## Testing Commands

### Using curl

#### Dashboard
```bash
curl http://localhost:8000/api/dashboard/health
curl http://localhost:8000/api/dashboard/stats/summary
```

#### Expenses
```bash
curl http://localhost:8000/api/receipts/demo/summary
```

#### Invoices
```bash
curl "http://localhost:8000/api/invoices?limit=5"
curl "http://localhost:8000/api/invoices?status=paid"
curl http://localhost:8000/api/invoices/stats/summary
```

#### Payments
```bash
curl "http://localhost:8000/api/payments?limit=5"
curl http://localhost:8000/api/payments/RC8712375528
curl http://localhost:8000/api/payments/stats/summary
```

### Using Python
```python
import requests

# Get payment statistics
response = requests.get("http://localhost:8000/api/payments/stats/summary")
data = response.json()
print(f"AI Accuracy: {data['aiAccuracy']}%")

# Search payments
response = requests.get(
    "http://localhost:8000/api/payments",
    params={"search": "Software", "limit": 10}
)
payments = response.json()["payments"]
```

---

## Database Collections

### Invoices Collection
- Total: 261 documents
- Structure: invoice_id, customer_name, amount, status, dates, items

### Transactions Collection
- Total: 383 documents (219 payments + 164 expenses)
- Types: "payment", "expense"
- Structure: mpesa_reference, customer_name, amount, invoice_id, type

### Receipts Collection
- Total: 164 documents
- Categories: 11 categories
- Structure: receipt_id, category, amount, date, description

---

## Frontend Pages

### Dashboard
- **URL:** `http://localhost:3000/`
- **Data Sources:** 
  - `/api/dashboard/stats`
  - Real-time period comparisons

### Expenses
- **URL:** `http://localhost:3000/expenses` (if exists)
- **Data Source:** `/api/receipts/demo/summary`

### Invoices List
- **URL:** `http://localhost:3000/invoices`
- **Data Sources:**
  - `/api/invoices` (list)
  - `/api/invoices/stats/summary` (statistics)

### Payments Overview
- **URL:** `http://localhost:3000/payments`
- **Data Sources:**
  - `/api/payments/stats/summary` (statistics)
  - `/api/payments?limit=50` (recent payments)

### Payments List
- **URL:** `http://localhost:3000/payments/list`
- **Data Source:** `/api/payments?limit=200`

---

## Notes

1. All endpoints currently work without authentication
2. MongoDB connection: `mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/financial_agent`
3. Database: `financial_agent`
4. All monetary values in KES (Kenyan Shillings)
5. Dates in ISO 8601 format
6. M-Pesa references are unique transaction identifiers

---

**Last Updated:** October 11, 2025  
**API Version:** 1.0.0  
**Status:** Production Ready (pending auth re-enablement)
