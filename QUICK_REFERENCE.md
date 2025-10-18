# FinGuard - Quick Reference Guide

## 🚀 Quick Start Commands

### Start the Application

```bash
# Start Backend (Port 8000)
cd /home/munga/Desktop/AI-Financial-Agent
source venv-ocr/bin/activate
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Start Frontend (Port 3000)
cd /home/munga/Desktop/AI-Financial-Agent/finance-app
npm run dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📊 System Overview

### Technology Stack
| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | Next.js | 15.3.5 |
| Backend | FastAPI (Python) | 3.12 |
| Database | MongoDB | Latest |
| Cache | Redis | Latest |
| AI Engine | Google Gemini AI | 2.0-flash |
| PDF Generation | ReportLab | Latest |

---

## 🗄️ Database Collections

### Core Collections
1. **transactions** - Payment transactions (707 records)
2. **invoices** - Customer invoices (999 records)
3. **receipts** - Generated receipts with OCR
4. **customers** - Customer database
5. **users** - System users (authentication)
6. **analytics_cache** - Cached analytics data

### Database Connection
```python
MONGODB_URL = "mongodb+srv://munga21407@cluster0.y7595ne.mongodb.net/"
DATABASE_NAME = "financial_agent"
```

---

## 🔌 Key API Endpoints

### Receipt Management
```bash
# Create receipt manually
POST /receipts/generate

# Upload receipt image (OCR)
POST /receipts/upload-ocr

# List all receipts
GET /receipts/?page=1&page_size=20

# Get receipt details
GET /receipts/{receipt_id}

# Download receipt PDF
GET /receipts/{receipt_id}/download

# Get receipt statistics
GET /receipts/statistics/summary
```

### AI Insights
```bash
# Query AI assistant
POST /api/ai-insights/query
{
  "query": "What are my spending patterns?"
}

# Check AI service health
GET /api/ai-insights/health
```

### Dashboard
```bash
# Get dashboard statistics
GET /api/dashboard/stats

# Get summary only
GET /api/dashboard/stats/summary
```

### Invoices
```bash
# List invoices
GET /api/invoices?limit=100&status=paid

# Create invoice
POST /api/invoices

# Get invoice details
GET /api/invoices/{invoice_id}

# Download invoice PDF
GET /api/invoices/{invoice_id}/download
```

### Payments
```bash
# List payments
GET /api/payments

# Record payment
POST /api/payments

# M-Pesa STK Push
POST /api/mpesa/stk-push
```

### Customers
```bash
# List customers
GET /api/customers

# Create customer
POST /api/customers

# Get customer details
GET /api/customers/{customer_id}
```

---

## 🎨 Frontend Routes

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/auth/login` | Login page |
| `/auth/register` | Registration page |
| `/dashboard` | Main dashboard |
| `/receipts` | Receipt management |
| `/receipts/[id]` | Receipt details |
| `/invoices` | Invoice management |
| `/invoices/[id]` | Invoice details |
| `/payments` | Payment management |
| `/customers` | Customer management |
| `/customers/[id]` | Customer details |
| `/ai-insights` | AI Financial Assistant |
| `/expenses` | Expense management |
| `/reports` | Financial reports |

---

## 🔐 Authentication

### JWT Token Authentication

```javascript
// Login
POST /auth/login
{
  "email": "admin@example.com",
  "password": "your_password"
}

// Response
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}

// Use token in requests
Headers: {
  "Authorization": "Bearer eyJ..."
}
```

### User Roles
- **admin** - Full system access
- **accountant** - Financial operations
- **user** - Limited access
- **viewer** - Read-only access

---

## 📦 Project Structure

```
AI-Financial-Agent/
├── backend/                 # FastAPI backend
│   ├── app.py              # Main application
│   ├── auth/               # Authentication
│   ├── receipts/           # Receipt management
│   ├── invoices/           # Invoice management
│   ├── payments/           # Payment processing
│   ├── customers/          # Customer management
│   ├── ai_insights/        # AI insights (RAG)
│   ├── ocr/                # OCR processing
│   ├── mpesa/              # M-Pesa integration
│   ├── dashboard/          # Dashboard API
│   └── database/           # Database layer
│
├── finance-app/            # Next.js frontend
│   ├── app/                # App Router pages
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   └── types/              # TypeScript types
│
├── uploads/                # File storage
│   └── receipts/
│       ├── images/         # OCR uploaded images
│       └── pdfs/           # Generated PDFs
│
└── venv-ocr/               # Python virtual environment
```

---

## 🧪 Testing

### Backend Tests
```bash
# Run receipt system tests
python test_receipt_system.py

# Quick receipt test
bash test_receipt_quick.sh

# Run all tests
pytest backend/tests/
```

### Manual API Testing
```bash
# Test receipt creation
curl -X POST http://localhost:8000/receipts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "receipt_type": "payment",
    "customer": {
      "name": "Test User",
      "email": "test@example.com"
    },
    "amount": 1000,
    "description": "Test receipt"
  }'

# Test OCR upload
curl -X POST http://localhost:8000/receipts/upload-ocr \
  -F "file=@receipt.jpg"

# Test AI Insights
curl -X POST http://localhost:8000/api/ai-insights/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me my financial summary"}'
```

---

## 🔧 Environment Variables

### Required Variables
```bash
# .env file
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB=financial_agent
GEMINI_API_KEY=your_gemini_api_key
JWT_SECRET_KEY=your_secret_key_min_32_chars
SECRET_KEY=your_app_secret_key
```

### Optional Variables
```bash
REDIS_URL=redis://localhost:6379/0
MPESA_CONSUMER_KEY=your_mpesa_key
MPESA_CONSUMER_SECRET=your_mpesa_secret
DEBUG=false
LOG_LEVEL=info
```

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

### Backend Not Starting
```bash
# Check MongoDB connection
python -c "from pymongo import MongoClient; print(MongoClient('your-uri').admin.command('ping'))"

# Check Gemini API key
echo $GEMINI_API_KEY

# Check Python version
python --version  # Should be 3.12+
```

### Frontend Build Errors
```bash
# Clear cache and reinstall
cd finance-app
rm -rf node_modules package-lock.json .next
npm install
npm run dev
```

### AI Insights Not Working
```bash
# Check if backend is running
curl http://localhost:8000/api/ai-insights/health

# Check database connection
# See backend logs for collection access

# Restart backend to apply changes
lsof -ti:8000 | xargs kill -9
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### PDF Preview Not Loading
- Old receipts automatically converted via adapter
- PDF generated on-demand
- Check backend logs for errors
- Verify /receipts/{id}/download endpoint

---

## 📈 System Statistics

### Current Data (October 2025)
- **Total Transactions**: 707
- **Total Invoices**: 999
- **Total Revenue**: KES 48,908,755.00
- **Customers**: Active customer base
- **Receipts**: OCR-enabled receipt system

---

## 🚢 Deployment

### Docker Deployment
```bash
# Build and start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production Checklist
- [ ] Set production environment variables
- [ ] Configure MongoDB Atlas connection
- [ ] Set up SSL/TLS certificates
- [ ] Configure Nginx reverse proxy
- [ ] Enable monitoring (Prometheus/Grafana)
- [ ] Set up backups
- [ ] Configure rate limiting
- [ ] Test all endpoints
- [ ] Run security audit

---

## 📞 Support

### Documentation Files
- `SYSTEM_ARCHITECTURE.md` - Complete system architecture
- `README.md` - Project overview and setup
- `DOCUMENTATION_CONSOLIDATION_SUMMARY.txt` - Documentation changes

### Key Features Documentation
- **Receipt System**: OCR upload, PDF generation, backward compatibility
- **AI Insights**: RAG architecture with Gemini AI
- **M-Pesa**: Payment integration for Kenyan market
- **Dashboard**: Real-time financial metrics
- **Security**: JWT auth, RBAC, encryption

---

## 🎯 Common Tasks

### Add New User
```python
# Using FastAPI
POST /auth/register
{
  "email": "user@example.com",
  "password": "secure_password",
  "full_name": "User Name",
  "role": "user"
}
```

### Generate Receipt from Image
1. Go to http://localhost:3000/receipts
2. Click "Upload Receipt Image"
3. Select receipt image (JPG, PNG, WEBP, PDF)
4. Wait for AI processing
5. Review extracted data
6. Download PDF

### Query AI Assistant
1. Go to http://localhost:3000/ai-insights
2. Type your question in natural language
3. Examples:
   - "What are my spending patterns this month?"
   - "Show me my revenue trends"
   - "Which customers have outstanding invoices?"
   - "Forecast my cash flow"

### Create Invoice
1. Go to http://localhost:3000/invoices
2. Click "New Invoice"
3. Select customer
4. Add line items
5. Set due date
6. Generate PDF
7. Send to customer

---

## 🔄 Data Flow Examples

### Receipt OCR Flow
```
User uploads image
    ↓
Frontend sends to /receipts/upload-ocr
    ↓
Backend saves image to /uploads/receipts/images/
    ↓
Gemini AI processes image
    ↓
Extract customer, items, amounts
    ↓
Create receipt in MongoDB
    ↓
Generate PDF with ReportLab
    ↓
Save PDF to /uploads/receipts/pdfs/
    ↓
Return receipt data to frontend
    ↓
Display receipt with preview
```

### AI Insights Flow
```
User asks question
    ↓
Frontend sends to /api/ai-insights/query
    ↓
Backend retrieves context from MongoDB
    ↓
- Query transactions collection
    - Query invoices collection
    - Query receipts collection
    - Query customers collection
    ↓
Build structured context
    ↓
Send to Gemini AI with user query
    ↓
AI generates analysis
    ↓
Return formatted response
    ↓
Display in chat interface
```

---

**Document Version**: 1.0  
**Last Updated**: October 18, 2025  
**Quick Reference for**: FinGuard Development Team
