# FinGuard Lite - AI-Powered Financial Management for Kenyan SMEs

[![Build Status](https://img.shields.io/badge/build-audit_complete-yellow)](https://github.com/KXvira/AI-Financial-Agent)
[![Sprint Progress](https://img.shields.io/badge/sprints-4%2F7_complete-orange)](https://github.com/KXvira/AI-Financial-Agent)
[![MVP Status](https://img.shields.io/badge/mvp-68%25_complete-yellow)](https://github.com/KXvira/AI-Financial-Agent)

> **🚧 Project Status:** Post-Sprint 4 Audit Complete | Sprint 5-7 Planning Phase  
> **📊 Current Completion:** 68% MVP | Production Target: 80%+

A comprehensive AI-powered financial management system specifically designed for Kenyan SMEs, featuring M-Pesa integration, automated reconciliation, OCR expense tracking, and predictive cash flow analytics.

## 🎯 Project Overview

FinGuard Lite empowers Kenyan small and medium enterprises with intelligent financial management through:

- **🤖 AI-Powered Financial Insights** - Gemini-based analysis and recommendations
- **💰 M-Pesa Integration** - Complete Daraja API implementation with webhooks
- **📄 Automated Invoice Management** - LLM-powered invoice generation and tracking
- **📷 OCR Expense Processing** - Receipt scanning and categorization
- **📈 Predictive Analytics** - Cash flow forecasting with ML models
- **🔔 Intelligent Alerts** - Proactive financial health monitoring

## 📊 Current Sprint Status

### ✅ **Completed Sprints (1-4)**

| Sprint | Focus Area | Completion | Status |
|--------|------------|------------|--------|
| **Sprint 1** | M-Pesa + Auth | 70% | ⚠️ Auth Missing |
| **Sprint 2** | Invoice Engine | 75% | ✅ Core Complete |
| **Sprint 3** | OCR Expenses | 45% | ❌ Critical Gap |
| **Sprint 4** | Predictions | 55% | ⚠️ Models Missing |

### 🔄 **Upcoming Sprints (5-7)**

| Sprint | Focus Area | Duration | Priority |
|--------|------------|----------|----------|
| **Sprint 5** | Security & Testing | 2 weeks | 🔴 Critical |
| **Sprint 6** | OCR Implementation | 2 weeks | 🔴 Critical |
| **Sprint 7** | ML & Analytics | 2 weeks | 🟡 High |

> 📋 **Detailed Analysis:** See [SPRINT_AUDIT_REPORT.md](./SPRINT_AUDIT_REPORT.md)  
> 🗺️ **Implementation Plan:** See [SPRINT_PLAN_5-7.md](./SPRINT_PLAN_5-7.md)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (React/Next)  │────│   (FastAPI)     │────│   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │   Database      │              │
         └──────────────│   (MongoDB)     │──────────────┘
                        └─────────────────┘
                                 │
                        ┌─────────────────┐
                        │   External APIs │
                        │  (M-Pesa/SMS)   │
                        └─────────────────┘
```

## 🚀 Features Status

### ✅ **Implemented Features**
- **M-Pesa Integration** - Complete Daraja API with STK Push, callbacks, and reconciliation
- **AI Financial Insights** - RAG-based analysis using Gemini SDK
- **Invoice Management** - Full CRUD operations with PDF generation
- **Interactive Dashboard** - Real-time financial metrics and AI chat
- **Database Architecture** - Comprehensive MongoDB schemas with indexing
- **API Documentation** - Complete OpenAPI/Swagger documentation

### ⚠️ **Partially Implemented**
- **Authentication System** - Database models exist, JWT implementation missing
- **Reconciliation Engine** - Core logic complete, needs comprehensive testing
- **Reporting System** - Framework in place, advanced features pending
- **Alert System** - Basic structure, notification delivery missing

### ❌ **Missing Critical Features**
- **OCR Receipt Processing** - Tesseract integration and image preprocessing
- **User Authentication** - Login, registration, and role-based access control
- **Prediction Models** - Prophet/LSTM forecasting implementations
- **Expense Management** - Complete expense tracking and categorization
- **Testing Framework** - Unit and integration test suites

## 🛠️ Tech Stack

### **Backend**
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database with Motor async driver
- **Gemini AI** - Google's generative AI for insights
- **Pydantic** - Data validation and serialization
- **Python 3.9+** - Core runtime environment

### **Frontend**
- **Next.js 15.3.5** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Modern icon library

### **AI/ML Stack**
- **Google Gemini** - Large language model for insights
- **Tesseract OCR** - Text extraction from receipts *(planned)*
- **Prophet** - Time series forecasting *(planned)*
- **LSTM** - Neural networks for prediction *(planned)*
- **OpenCV** - Image preprocessing *(planned)*

### **Infrastructure**
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline *(planned)*
- **MongoDB Atlas** - Cloud database
- **Railway/Vercel** - Deployment platforms

## 🏃‍♂️ Quick Start

### **Prerequisites**
- Node.js 18.x+
- Python 3.9+
- MongoDB (local or Atlas)
- Git

### **Environment Setup**
```bash
# Clone repository
git clone https://github.com/KXvira/AI-Financial-Agent.git
cd AI-Financial-Agent

# Copy environment template
cp .env.example .env
# Edit .env with your API keys and database URLs
```

### **Backend Setup**
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Initialize database (optional)
python scripts/initialize_database.py

# Start backend server
cd backend
python app.py
# Server runs on http://localhost:8002
```

### **Frontend Setup**
```bash
# Install Node dependencies
cd finance-app
npm install

# Start development server
npm run dev
# Frontend runs on http://localhost:3000
```

### **Full-Stack Demo**
```bash
# Run integrated full-stack service
python fullstack_main.py
# Access at http://localhost:8002
```

## 📚 API Documentation

Once running, access interactive API documentation:
- **Swagger UI**: `http://localhost:8002/docs`
- **ReDoc**: `http://localhost:8002/redoc`

### **Key Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ai/ask` | AI financial insights query |
| GET | `/ai/health` | Service health check |
| POST | `/api/mpesa/stk-push` | Initiate M-Pesa payment |
| POST | `/api/mpesa/callback` | Handle payment callbacks |
| POST | `/api/reconciliation/reconcile` | Payment reconciliation |

## 🧪 Testing

### **Current Test Suite**
```bash
# Test AI insights service
python scripts/test_ai_insights.py

# Test full-stack integration
python test_fullstack_service.py

# Test Gemini API connection
python scripts/test_gemini_api.py
```

### **Planned Testing (Sprint 5)**
- Unit tests with pytest
- Integration test automation
- Code coverage reporting
- CI/CD pipeline integration

## 🔒 Security Status

### **Implemented**
- CORS middleware configuration
- Input validation with Pydantic
- Environment variable management
- API rate limiting (basic)

### **Missing (Sprint 5 Priority)**
- JWT authentication system
- Role-based access control
- Webhook signature validation
- Comprehensive security audit

## 📈 Performance Metrics

### **Current Performance**
- AI Query Response: ~2-5 seconds
- M-Pesa Transaction: ~1-3 seconds
- Dashboard Load: ~2-4 seconds
- Database Queries: ~100-300ms

### **Targets (Sprint 5-7)**
- Authentication: <200ms
- Receipt Processing: <10s
- Predictions: <5s
- 99.5% uptime capability

## 🗺️ Roadmap

### **Sprint 5: Security & Testing** (2 weeks)
- [ ] Complete JWT authentication system
- [ ] Role-based access control
- [ ] Comprehensive testing framework
- [ ] Security hardening and validation

### **Sprint 6: OCR & Expenses** (2 weeks)
- [ ] Tesseract OCR integration
- [ ] Receipt upload and processing
- [ ] Expense categorization with AI
- [ ] User feedback and correction system

### **Sprint 7: Prediction & Analytics** (2 weeks)
- [ ] Prophet cash flow forecasting
- [ ] LSTM neural network models
- [ ] Explainable AI with SHAP
- [ ] Advanced alert system

### **Future Enhancements**
- Mobile application (React Native)
- Multi-tenant architecture
- Advanced fraud detection
- Industry benchmark integration

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Follow code style guidelines in [CONTRIBUTING.md](./CONTRIBUTING.md)
4. Add tests for new features
5. Submit pull request with detailed description

### **Coding Standards**
- Python: PEP 8 with Black formatting
- TypeScript: ESLint with Prettier
- Commit messages: Conventional Commits format
- Testing: 80%+ coverage requirement

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Documentation**
- [Sprint Audit Report](./SPRINT_AUDIT_REPORT.md) - Comprehensive analysis
- [Sprint Implementation Plan](./SPRINT_PLAN_5-7.md) - Detailed roadmap
- [AI Insights Documentation](./docs/AI_INSIGHTS_SERVICE.md) - Technical details

### **Get Help**
- 📧 Email: support@finguardlite.com
- 🐛 Issues: [GitHub Issues](https://github.com/KXvira/AI-Financial-Agent/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/KXvira/AI-Financial-Agent/discussions)

---

**Built with ❤️ for Kenyan SMEs** | **Powered by AI** | **© 2025 FinGuard Lite**