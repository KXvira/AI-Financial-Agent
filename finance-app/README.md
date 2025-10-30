# FinGuard Frontend - Next.js Application

[![Next.js](https://img.shields.io/badge/Next.js-15.3.5-black)](https://nextjs.org)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue)](https://www.typescriptlang.org)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.x-38B2AC)](https://tailwindcss.com)

Modern, responsive frontend for the FinGuard AI-Powered Financial Management System built with Next.js 15, React 18, TypeScript, and TailwindCSS.

---

## 🚀 Quick Start

### Prerequisites
- **Node.js**: 18.x or higher (required for Next.js 15)
- **npm**: 9.x or higher
- **Backend API**: Running on http://localhost:8000

### Installation

```bash
# Navigate to frontend directory
cd finance-app

# Install dependencies
npm install

# Run development server
npm run dev
```

The application will be available at **http://localhost:3000**

### Development Commands

```bash
# Development server with hot reload
npm run dev

# Production build
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Type checking
npm run type-check
```

---

## 📁 Project Structure

```
finance-app/
├── app/                          # Next.js App Router
│   ├── layout.tsx                # Root layout with sidebar
│   ├── page.tsx                  # Home page
│   │
│   ├── auth/                     # Authentication
│   │   ├── login/
│   │   │   └── page.tsx          # Login page
│   │   └── register/
│   │       └── page.tsx          # Registration page
│   │
│   ├── dashboard/                # Main Dashboard
│   │   └── page.tsx              # Dashboard with metrics & charts
│   │
│   ├── receipts/                 # Receipt Management ✨
│   │   ├── page.tsx              # Receipt list, creation & OCR upload
│   │   └── [id]/
│   │       └── page.tsx          # Receipt details & PDF preview
│   │
│   ├── invoices/                 # Invoice Management
│   │   ├── page.tsx              # Invoice list
│   │   ├── new/
│   │   │   └── page.tsx          # Create new invoice
│   │   └── [id]/
│   │       └── page.tsx          # Invoice details & actions
│   │
│   ├── payments/                 # Payment Management
│   │   ├── page.tsx              # Payment list with AI matching
│   │   ├── list/
│   │   │   └── page.tsx          # Detailed payment list
│   │   ├── new/
│   │   │   └── page.tsx          # Record new payment
│   │   └── [reference]/
│   │       └── page.tsx          # Payment details by reference
│   │
│   ├── customers/                # Customer Management
│   │   ├── page.tsx              # Customer list
│   │   ├── invoice/              # Customer invoices
│   │   │   └── [id]/
│   │   │       └── page.tsx      # Customer invoice details
│   │   ├── status/
│   │   │   └── page.tsx          # M-Pesa payment status
│   │   └── [id]/
│   │       └── page.tsx          # Customer details & downloads
│   │
│   ├── ai-insights/              # AI Financial Assistant
│   │   └── page.tsx              # Chat interface with Gemini AI
│   │
│   ├── expenses/                 # Expense Management
│   │   └── page.tsx              # Expense tracking & OCR
│   │
│   └── reports/                  # Financial Reports
│       └── page.tsx              # Report generation & export
│
├── components/                   # Reusable Components
│   ├── ui/                       # UI Components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Table.tsx
│   │   └── ...
│   │
│   ├── layout/                   # Layout Components
│   │   ├── Sidebar.tsx           # Main navigation sidebar
│   │   ├── Header.tsx            # Top header bar
│   │   └── Footer.tsx
│   │
│   ├── forms/                    # Form Components
│   │   ├── ReceiptForm.tsx       # Receipt creation form
│   │   ├── InvoiceForm.tsx       # Invoice creation form
│   │   └── CustomerForm.tsx      # Customer form
│   │
│   └── ReceiptUploader.tsx       # OCR upload component
│
├── lib/                          # Utilities & Helpers
│   ├── api.ts                    # API client configuration
│   ├── auth.ts                   # Authentication utilities
│   ├── utils.ts                  # Helper functions
│   └── constants.ts              # App constants
│
├── types/                        # TypeScript Type Definitions
│   ├── receipt.ts                # Receipt types
│   ├── invoice.ts                # Invoice types
│   ├── payment.ts                # Payment types
│   ├── customer.ts               # Customer types
│   └── index.ts                  # Exported types
│
├── hooks/                        # Custom React Hooks
│   ├── useAuth.ts                # Authentication hook
│   ├── useReceipts.ts            # Receipt data hook
│   ├── useInvoices.ts            # Invoice data hook
│   └── usePayments.ts            # Payment data hook
│
├── styles/                       # Global Styles
│   └── globals.css               # Global CSS with Tailwind
│
├── public/                       # Static Assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── package.json                  # Dependencies & scripts
├── tsconfig.json                 # TypeScript configuration
├── tailwind.config.js            # TailwindCSS configuration
├── next.config.js                # Next.js configuration
├── postcss.config.js             # PostCSS configuration
└── .eslintrc.json                # ESLint configuration
```

---

## 🎨 Key Features

### 1. Dashboard
- **Real-time Metrics**: Total revenue, transactions, invoices
- **Interactive Charts**: Revenue trends, payment distribution
- **Recent Activity**: Latest transactions and payments
- **Quick Actions**: Fast access to common tasks

### 2. Receipt Management ✨
- **Manual Creation**: Create receipts with line items
- **OCR Upload**: Upload receipt images for automatic data extraction
- **AI Processing**: Google Gemini AI extracts customer, items, amounts
- **PDF Generation**: Download professional receipts with QR codes
- **List & Filter**: Search, filter by type, status, date
- **Statistics**: Receipt analytics and summaries

### 3. Invoice Management
- **Create Invoices**: Multi-line item invoices with tax calculation
- **Customer Selection**: Link invoices to customers
- **Status Tracking**: Draft, sent, paid, overdue
- **PDF Download**: Generate and download invoice PDFs
- **Email Sending**: Send invoices to customers
- **Payment Matching**: Automatic payment reconciliation

### 4. Payment Processing
- **Record Payments**: Manual payment entry
- **M-Pesa Integration**: STK Push for mobile payments
- **Payment Status**: Track payment confirmations
- **AI Matching**: Automatic invoice-payment matching
- **Payment History**: Complete payment tracking

### 5. Customer Management
- **Customer Profiles**: Complete customer information
- **Contact Details**: Email, phone, address
- **Business Info**: KRA PIN, registration details
- **Transaction History**: All customer transactions
- **Invoice History**: Customer invoices and payments
- **Outstanding Balance**: Real-time balance tracking

### 6. AI Financial Insights
- **Conversational AI**: Natural language financial queries
- **Transaction Analysis**: Spending patterns and trends
- **Cash Flow Forecasting**: AI-powered predictions
- **Financial Recommendations**: Actionable insights
- **Data Visualization**: Charts and graphs

### 7. Expense Management
- **Expense Recording**: Track business expenses
- **Receipt Attachment**: Upload expense receipts
- **Category Management**: Organize by expense type
- **Expense Reports**: Generate expense summaries

### 8. Financial Reports
- **Income Statement**: Profit & loss reports
- **Balance Sheet**: Financial position reports
- **Cash Flow**: Cash flow statements
- **Export Options**: PDF, Excel, CSV

---

## 🔌 API Integration

### Backend Configuration

The frontend connects to the FastAPI backend at:
- **Development**: http://localhost:8000
- **Production**: Configured via environment variables

### API Endpoints Used

| Feature | Endpoint | Method |
|---------|----------|--------|
| Dashboard Stats | `/api/dashboard/stats` | GET |
| Receipt List | `/receipts/` | GET |
| Receipt Upload (OCR) | `/receipts/upload-ocr` | POST |
| Receipt Details | `/receipts/{id}` | GET |
| Receipt PDF | `/receipts/{id}/download` | GET |
| Invoice List | `/api/invoices` | GET |
| Create Invoice | `/api/invoices` | POST |
| Payment List | `/api/payments` | GET |
| Record Payment | `/api/payments` | POST |
| Customer List | `/api/customers` | GET |
| AI Query | `/api/ai-insights/query` | POST |

---

## 🎨 UI/UX Features

### Design System
- **Color Palette**: Professional blue/gray theme
- **Typography**: Geist font family optimized by Next.js
- **Icons**: Lucide React icon library
- **Responsive**: Mobile-first design
- **Dark Mode Ready**: Theme support built-in

### Components
- **Reusable UI Components**: Buttons, cards, inputs, modals
- **Form Validation**: Client-side validation with Zod
- **Loading States**: Skeleton loaders and spinners
- **Error Handling**: User-friendly error messages
- **Toast Notifications**: Success/error notifications

### Accessibility
- **ARIA Labels**: Screen reader support
- **Keyboard Navigation**: Full keyboard accessibility
- **Color Contrast**: WCAG compliant colors
- **Focus States**: Clear focus indicators

---

## 🔐 Authentication

### JWT Authentication Flow

```typescript
// Login
const response = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

// Store token
localStorage.setItem('token', response.access_token);

// Use in requests
const headers = {
  'Authorization': `Bearer ${token}`
};
```

### Protected Routes
- Dashboard and all main features require authentication
- Automatic redirect to login if not authenticated
- Token refresh mechanism for session persistence

---

## 🧪 Testing

### Manual Testing
```bash
# Test receipt OCR upload
1. Go to http://localhost:3000/receipts
2. Click "Upload Receipt Image"
3. Select a receipt image (JPG, PNG)
4. Verify data extraction
5. Check PDF generation

# Test AI Insights
1. Go to http://localhost:3000/ai-insights
2. Ask: "What are my spending patterns?"
3. Verify AI response with data
```

### Type Checking
```bash
npm run type-check
```

---

## 🌐 Environment Variables

Create a `.env.local` file:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Configuration
NEXT_PUBLIC_APP_NAME=FinGuard
NEXT_PUBLIC_APP_VERSION=1.0.0

# Optional: Analytics
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

---

## 🚀 Deployment

### Production Build

```bash
# Create production build
npm run build

# Test production build locally
npm start

# Deploy to Vercel (recommended)
vercel deploy
```

### Docker Deployment

```bash
# Build Docker image
docker build -t finguard-frontend .

# Run container
docker run -p 3000:3000 finguard-frontend
```

### Environment-specific Builds
- Development: Hot reload, source maps enabled
- Production: Optimized bundles, minified code
- Docker: Containerized with nginx

---

## 📊 Performance Optimization

### Next.js Features Used
- **App Router**: Improved routing and layouts
- **Server Components**: Reduced client-side JavaScript
- **Image Optimization**: Automatic image optimization
- **Code Splitting**: Automatic route-based splitting
- **Font Optimization**: Optimized font loading

### Performance Metrics
- **Lighthouse Score**: 90+ on all metrics
- **First Contentful Paint**: < 1.5s
- **Time to Interactive**: < 3s
- **Bundle Size**: Optimized with tree shaking

---

## 🛠️ Technology Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| **Next.js** | 15.3.5 | React framework with App Router |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **TailwindCSS** | 3.x | Utility-first CSS |
| **Lucide React** | Latest | Icon library |
| **React Hook Form** | Latest | Form handling |
| **Zod** | Latest | Schema validation |
| **date-fns** | Latest | Date utilities |
| **Chart.js** | Latest | Data visualization |

---

## 🐛 Troubleshooting

### Common Issues

**Port 3000 already in use:**
```bash
lsof -ti:3000 | xargs kill -9
npm run dev
```

**Build errors:**
```bash
rm -rf .next node_modules package-lock.json
npm install
npm run build
```

**Backend not connecting:**
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in .env.local
- Verify CORS settings in backend

**OCR upload failing:**
- Check file size (max 25MB)
- Verify file format (JPG, PNG, WEBP, PDF)
- Ensure backend has Gemini API key configured

---

## 📚 Documentation

- **Main Documentation**: See `/SYSTEM_ARCHITECTURE.md` in root
- **API Reference**: See `/QUICK_REFERENCE.md` in root
- **Backend Docs**: http://localhost:8000/docs

---

## 🤝 Contributing

### Development Workflow
1. Create feature branch from `main`
2. Make changes with TypeScript type safety
3. Test locally with backend running
4. Submit pull request with description

### Code Style
- Follow TypeScript best practices
- Use functional components with hooks
- Maintain component modularity
- Add proper types for all props
- Use TailwindCSS utility classes

---

## 📝 License

This project is part of the FinGuard financial management system.

---

## 🔗 Related Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)
- [TailwindCSS Documentation](https://tailwindcss.com/docs)
- [FinGuard Backend](../backend/README.md)

---

**Version**: 1.0.0  
**Last Updated**: October 18, 2025  
**Frontend Team**: FinGuard Development Team 