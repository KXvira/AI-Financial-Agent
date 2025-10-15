# Audit Verification Scripts

## Overview

This directory contains comprehensive verification scripts to test all audit findings from the post-migration assessment. These scripts validate:

- ✅ Backend API endpoints
- ✅ Database schema and relationships
- ✅ Frontend-backend integration
- ✅ Authentication and security
- ✅ Performance benchmarks
- ✅ Data integrity

## Files

### 1. `verify_audit.py` - Backend & Database Verification

Python script that performs comprehensive backend testing:

- **Database Schema**: Validates collections, document counts, and relationships
- **Indexes**: Verifies all required indexes are in place
- **Normalized Schema**: Tests relationships between invoices, invoice_items, payments, customers
- **API Endpoints**: Tests all FastAPI routes (GET, POST, PUT, DELETE)
- **Authentication**: Validates JWT token generation and protected endpoints
- **Data Integrity**: Verifies invoice calculations and payment matching
- **Performance**: Measures API response times
- **Security**: Tests authentication requirements and CORS configuration

**Requirements**:
- Python 3.9+
- `httpx`, `motor`, `pymongo`

**Usage**:
```bash
# Basic usage
python3 verify_audit.py

# Custom backend URL
python3 verify_audit.py --base-url http://api.example.com

# Custom MongoDB URI
python3 verify_audit.py --mongo-uri "mongodb://localhost:27017/mydb"
```

### 2. `verify_frontend.js` - Frontend Integration Verification

Node.js script that tests frontend integration:

- **Page Accessibility**: Verifies all Next.js pages are accessible
- **API Integration**: Tests fetch calls to backend endpoints
- **Authentication Flow**: Validates login and token storage
- **Response Structure**: Verifies API responses match expected formats
- **CORS Configuration**: Tests cross-origin resource sharing

**Requirements**:
- Node.js 18+
- No additional packages (uses built-in `http`/`https` modules)

**Usage**:
```bash
# Basic usage
node verify_frontend.js

# Script will test:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
```

### 3. `run_audit_verification.sh` - Complete Test Suite Runner

Bash script that orchestrates both verification scripts:

- Checks if backend and frontend are running
- Runs backend verification
- Runs frontend verification
- Generates combined summary report

**Usage**:
```bash
# Make executable (first time only)
chmod +x run_audit_verification.sh

# Run complete verification
./run_audit_verification.sh
```

## Quick Start

### Prerequisites

1. **Start Backend** (in one terminal):
```bash
cd /home/munga/Desktop/AI-Financial-Agent
source venv-ocr/bin/activate
cd backend
uvicorn main:app --reload
```

2. **Start Frontend** (in another terminal):
```bash
cd /home/munga/Desktop/AI-Financial-Agent/finance-app
npm run dev
```

3. **Run Verification** (in third terminal):
```bash
cd /home/munga/Desktop/AI-Financial-Agent
./run_audit_verification.sh
```

## Sample Output

### Backend Verification
```
╔══════════════════════════════════════════════════════════════════╗
║     POST-MIGRATION AUDIT VERIFICATION SCRIPT                     ║
║     Testing Backend Endpoints, Database Schema & Integration    ║
╚══════════════════════════════════════════════════════════════════╝

==================================================================
  Phase 1: Database Schema Verification
==================================================================

✅ Database connection established
✅ Collection 'users' has 8 documents (expected ~8)
✅ Collection 'customers' has 100 documents (expected ~100)
✅ Collection 'invoices' has 2370 documents (expected ~2370)
✅ Collection 'invoice_items' has 9231 documents (expected ~9231)
...

Overall Score: 94.0/100
Status: PRODUCTION READY ✅

Report saved to: audit_report_20250115_143052.json
```

### Frontend Verification
```
======================================================================
     FRONTEND INTEGRATION VERIFICATION SCRIPT
     Testing Next.js Frontend & Backend Integration
======================================================================

==================================================================
  Phase 1: Frontend Accessibility
==================================================================

✅ Home/Dashboard (/) - Accessible
✅ Login Page (/login) - Accessible
✅ Register Page (/register) - Accessible
⚠️  Invoices Page (/invoices) - Redirects (auth required)
...

Overall Score: 92.5/100
Status: PRODUCTION READY ✅

Report saved to: frontend_audit_report_2025-01-15T14-31-25.json
```

## Test Coverage

### Backend Tests (50+ tests)

**Database (12 tests)**:
- Collection existence and document counts
- Index verification
- Normalized schema relationships
- Foreign key integrity

**Authentication (8 tests)**:
- User registration
- Login with JWT
- Token refresh
- Protected endpoint access
- Password hashing
- Audit log creation

**API Endpoints (25+ tests)**:
- Dashboard statistics
- Invoice CRUD operations
- Payment management
- Customer management
- Receipt/OCR processing
- Reporting endpoints
- Tax calculations
- Trends and comparisons

**Data Integrity (5 tests)**:
- Invoice total calculations
- Payment matching accuracy
- Customer balance calculations
- Transaction history
- Tax computations

**Performance (5 tests)**:
- Dashboard load time (< 1s)
- Report generation (< 3s)
- API response times
- Database query performance

**Security (5 tests)**:
- Authentication requirements
- CORS configuration
- JWT token validation
- Role-based access
- Input sanitization

### Frontend Tests (20+ tests)

**Page Accessibility (8 tests)**:
- Home/Dashboard
- Login/Register
- Invoices, Payments, Receipts
- Reports, Customers

**API Integration (10+ tests)**:
- Authentication flow
- Dashboard data fetching
- Invoice operations
- Payment queries
- Report generation
- Customer statements

**Response Validation (5 tests)**:
- Dashboard stats structure
- Invoice list format
- Payment list format
- Report data structure
- Customer data structure

## Report Files

Both scripts generate JSON reports with detailed results:

### Backend Report (`audit_report_*.json`)
```json
{
  "timestamp": "2025-01-15T14:30:52.123456",
  "statistics": {
    "total": 50,
    "passed": 47,
    "warnings": 2,
    "failed": 1
  },
  "results": {
    "passed": ["Database connection established", ...],
    "warnings": ["CORS allows all origins", ...],
    "failed": []
  },
  "score": 94.0
}
```

### Frontend Report (`frontend_audit_report_*.json`)
```json
{
  "timestamp": "2025-01-15T14:31:25.789Z",
  "frontendUrl": "http://localhost:3000",
  "backendUrl": "http://localhost:8000",
  "statistics": {
    "total": 20,
    "passed": 18,
    "warnings": 2,
    "failed": 0,
    "score": 92.5
  },
  "results": { ... }
}
```

## Interpreting Results

### Status Indicators

- ✅ **PASSED** - Test completed successfully
- ⚠️ **WARNING** - Test passed with minor issues (e.g., CORS configuration)
- ❌ **FAILED** - Test failed (needs immediate attention)

### Score Ranges

- **90-100**: Production Ready ✅
- **75-89**: Needs Minor Fixes ⚠️
- **0-74**: Needs Attention ❌

## Common Issues & Solutions

### Issue: "Database connection failed"
**Solution**: Check MongoDB URI and ensure database is accessible
```bash
# Test MongoDB connection
python3 -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('your-uri').admin.command('ping'))"
```

### Issue: "Backend not running"
**Solution**: Start backend server
```bash
cd backend
uvicorn main:app --reload
```

### Issue: "Frontend not accessible"
**Solution**: Start Next.js development server
```bash
cd finance-app
npm run dev
```

### Issue: "Authentication failed"
**Solution**: Check default credentials or create test user
```bash
# Default credentials
Email: admin@finagent.com
Password: admin123
```

### Issue: "CORS warnings"
**Solution**: Update CORS configuration in `backend/app.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## Continuous Integration

These scripts can be integrated into CI/CD pipelines:

### GitHub Actions Example
```yaml
name: Audit Verification

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run backend verification
        run: python3 verify_audit.py
      - name: Upload reports
        uses: actions/upload-artifact@v2
        with:
          name: audit-reports
          path: audit_report_*.json
```

## Maintenance

### Updating Tests

To add new tests, edit the respective verification scripts:

**Backend tests**: Edit `verify_audit.py`, add methods to `AuditVerifier` class
**Frontend tests**: Edit `verify_frontend.js`, add tests to `FrontendVerifier` class

### Version History

- **v1.0** (2025-01-15): Initial release
  - 50+ backend tests
  - 20+ frontend tests
  - JSON report generation
  - Combined test runner

## Support

For issues or questions:
1. Check the generated JSON reports for detailed error messages
2. Review the console output for specific test failures
3. Consult the main audit report in the project documentation

## License

Part of the AI-Powered Financial Management System
