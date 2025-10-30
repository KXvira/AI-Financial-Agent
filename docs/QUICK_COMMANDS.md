# 🚀 Quick Command Reference - Phase 3

## Server Management

### Start Backend
```bash
cd /home/munga/Desktop/AI-Financial-Agent
source venv-ocr/bin/activate
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Start Backend (Background)
```bash
cd /home/munga/Desktop/AI-Financial-Agent
source venv-ocr/bin/activate
nohup python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

### Check Backend Status
```bash
ps aux | grep uvicorn | grep -v grep
tail -f backend.log
```

### Stop Backend
```bash
pkill -f "uvicorn backend.app:app"
```

### Start Frontend
```bash
cd /home/munga/Desktop/AI-Financial-Agent/finance-app
npm run dev -- -p 3001
```

---

## Phase 3 Endpoint Testing

### Predictive Analytics Endpoints

#### Revenue Forecast (3 months)
```bash
curl "http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=3&include_confidence=true"
```

#### Revenue Forecast (6 months)
```bash
curl "http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=6&include_confidence=true"
```

#### Expense Forecast
```bash
curl "http://localhost:8000/reports/predictive/expense-forecast?months_ahead=6&include_confidence=true"
```

#### Cash Flow Forecast
```bash
curl "http://localhost:8000/reports/predictive/cash-flow-forecast?months_ahead=12&include_confidence=true"
```

#### Predictive Summary
```bash
curl "http://localhost:8000/reports/predictive/summary"
```

### AI Reports Endpoints

#### General Insights (30 days)
```bash
curl "http://localhost:8000/reports/ai/insights?report_type=general&days=30"
```

#### Revenue Insights (60 days)
```bash
curl "http://localhost:8000/reports/ai/insights?report_type=revenue&days=60"
```

#### Expense Insights (90 days)
```bash
curl "http://localhost:8000/reports/ai/insights?report_type=expenses&days=90"
```

#### Cash Flow Insights
```bash
curl "http://localhost:8000/reports/ai/insights?report_type=cash_flow&days=30"
```

#### Anomaly Detection
```bash
curl "http://localhost:8000/reports/ai/anomaly-detection?days=30"
```

#### Custom Report (POST)
```bash
curl -X POST "http://localhost:8000/reports/ai/custom-report" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=What are my top expenses this month?" \
  -d "start_date=2025-01-01" \
  -d "end_date=2025-01-12" \
  -d "include_data=true"
```

#### Executive Summary (Current Month)
```bash
curl "http://localhost:8000/reports/ai/executive-summary?month=2025-01"
```

---

## Quick Verification Script

### Test All Phase 3 Endpoints
```bash
#!/bin/bash

echo "=== PHASE 3 ENDPOINT VERIFICATION ==="
echo ""

# Predictive Analytics
echo "1. Revenue Forecast:"
curl -s "http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=3" | head -c 100
echo -e "\n"

echo "2. Expense Forecast:"
curl -s "http://localhost:8000/reports/predictive/expense-forecast?months_ahead=3" | head -c 100
echo -e "\n"

echo "3. Cash Flow Forecast:"
curl -s "http://localhost:8000/reports/predictive/cash-flow-forecast?months_ahead=3" | head -c 100
echo -e "\n"

# AI Reports
echo "4. AI Insights:"
curl -s "http://localhost:8000/reports/ai/insights?report_type=general&days=30" | head -c 100
echo -e "\n"

echo "5. Anomaly Detection:"
curl -s "http://localhost:8000/reports/ai/anomaly-detection?days=30" | head -c 100
echo -e "\n"

echo "=== VERIFICATION COMPLETE ==="
```

---

## Frontend URLs

### Main Pages
```
Reports Landing:        http://localhost:3001/reports
Predictive Analytics:   http://localhost:3001/reports/predictive-analytics
AI Reports:            http://localhost:3001/reports/ai-reports
```

### Other Reports (Phase 1 & 2)
```
Dashboard:             http://localhost:3001/reports/dashboard
Income Statement:      http://localhost:3001/reports/income-statement
Cash Flow:             http://localhost:3001/reports/cash-flow
AR Aging:              http://localhost:3001/reports/ar-aging
Customer Statement:    http://localhost:3001/reports/customer-statement
Reconciliation:        http://localhost:3001/reports/reconciliation
Tax Summary:           http://localhost:3001/reports/tax-summary
```

---

## Database Commands

### Connect to MongoDB
```bash
mongosh "mongodb+srv://cluster0.lqkix.mongodb.net/" --apiVersion 1 --username michaelm
```

### Check Collections
```javascript
use financial_agent
show collections
db.invoices.countDocuments()
db.transactions.countDocuments()
db.customers.countDocuments()
```

### Sample Data Queries
```javascript
// Get recent invoices
db.invoices.find().sort({issue_date: -1}).limit(5)

// Get recent transactions
db.transactions.find().sort({transaction_date: -1}).limit(5)

// Get all customers
db.customers.find()
```

---

## Logs & Debugging

### View Backend Logs (Live)
```bash
tail -f /home/munga/Desktop/AI-Financial-Agent/backend.log
```

### View Backend Logs (Last 50 lines)
```bash
tail -50 /home/munga/Desktop/AI-Financial-Agent/backend.log
```

### View Frontend Logs
```bash
# Frontend logs appear in terminal where `npm run dev` is running
```

### Check Server Processes
```bash
# Backend
ps aux | grep uvicorn

# Frontend  
ps aux | grep "next dev"

# All Python processes
ps aux | grep python
```

---

## Python Environment

### Activate Virtual Environment
```bash
cd /home/munga/Desktop/AI-Financial-Agent
source venv-ocr/bin/activate
```

### Check Installed Packages
```bash
pip list | grep -E "(fastapi|motor|pydantic|google)"
```

### Install Missing Package
```bash
pip install <package-name>
```

---

## File Locations

### Phase 3 Frontend Files
```
/finance-app/app/reports/predictive-analytics/page.tsx
/finance-app/app/reports/ai-reports/page.tsx
/finance-app/app/reports/page.tsx
```

### Phase 3 Backend Files
```
/backend/reporting/predictive_service.py
/backend/reporting/ai_reports_service.py
/backend/reporting/router.py
```

### Documentation
```
/docs/PHASE_3_COMPLETION.md
/docs/PHASE_3_SUMMARY.md
/docs/PHASE_3_SUCCESS.md
/docs/QUICK_COMMANDS.md (this file)
```

---

## Git Commands

### Check Status
```bash
cd /home/munga/Desktop/AI-Financial-Agent
git status
```

### View Changes
```bash
git diff
git diff --staged
```

### Commit Phase 3
```bash
git add .
git commit -m "Complete Phase 3: Predictive Analytics & AI Reports"
git push origin main
```

---

## Troubleshooting

### Backend Won't Start
```bash
# Check if port is in use
lsof -i :8000

# Kill process on port 8000
kill -9 $(lsof -t -i:8000)

# Check for Python errors
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
```

### Frontend Won't Start
```bash
# Check if port is in use
lsof -i :3001

# Kill process on port 3001
kill -9 $(lsof -t -i:3001)

# Reinstall dependencies
cd finance-app
npm install
npm run dev -- -p 3001
```

### Database Connection Issues
```bash
# Check MongoDB connection string
cat backend/config/settings.py | grep MONGODB

# Test connection
python -c "from motor.motor_asyncio import AsyncIOMotorClient; client = AsyncIOMotorClient('your-connection-string'); print('Connected!')"
```

### Import Errors
```bash
# Ensure virtual environment is activated
source venv-ocr/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

---

## Performance Testing

### Load Test Backend
```bash
# Install apache bench
sudo apt-get install apache2-utils

# Test endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 "http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=3"
```

### Check Memory Usage
```bash
# Backend process
ps aux | grep uvicorn | awk '{print $2}' | xargs ps -p -o pid,rss,vsz,cmd

# All processes
htop
```

---

## Quick Stats

### Count Lines of Code
```bash
# Phase 3 frontend
wc -l /home/munga/Desktop/AI-Financial-Agent/finance-app/app/reports/predictive-analytics/page.tsx
wc -l /home/munga/Desktop/AI-Financial-Agent/finance-app/app/reports/ai-reports/page.tsx

# Phase 3 backend
wc -l /home/munga/Desktop/AI-Financial-Agent/backend/reporting/predictive_service.py
wc -l /home/munga/Desktop/AI-Financial-Agent/backend/reporting/ai_reports_service.py

# All TypeScript files
find finance-app -name "*.tsx" -exec wc -l {} + | tail -1

# All Python files
find backend -name "*.py" -exec wc -l {} + | tail -1
```

---

## Environment Variables

### Check Current Environment
```bash
echo $GEMINI_API_KEY
echo $MONGODB_URI
```

### Set Environment Variables
```bash
export GEMINI_API_KEY="your-api-key"
export MONGODB_URI="your-mongodb-uri"
```

---

**Last Updated:** January 12, 2025  
**Phase:** 3 (Complete)  
**Progress:** 75%
