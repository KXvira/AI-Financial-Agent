# 📊 Financial Statements & Reports - Available in Your System

## Overview

Your AI Financial Agent system can generate a comprehensive suite of financial statements and reports by leveraging the existing data in your MongoDB database and AI-powered insights. Here's what you can generate:

---

## 🗂️ Current Database Assets

### Collections Available:
1. **Invoices** - 261 documents
   - Invoice numbers, amounts, dates, status
   - Customer information
   - Line items with quantities and prices
   - Payment status

2. **Transactions** - 383 documents
   - 219 payments
   - 164 expenses
   - M-Pesa references
   - Transaction dates and amounts

3. **Customers** - 8 documents
   - Customer profiles
   - Total billed, paid, outstanding
   - Payment history
   - Contact information

4. **Receipts** - 164 documents
   - 11 expense categories
   - Receipt details
   - Dates and descriptions

5. **Reconciliation Logs**
   - Payment matching records
   - Confidence scores
   - Match timestamps

6. **Email Logs** (Phase 3)
   - Sent invoices
   - Delivery status

---

## 📈 Financial Statements You Can Generate

### 1. Income Statement (Profit & Loss Statement)
**Status:** ✅ Can be generated now

**What it shows:**
- Total Revenue (from invoices)
- Cost of Goods Sold (COGS) - if tracked
- Gross Profit
- Operating Expenses (from expense transactions)
- Operating Income
- Net Income/Loss

**Data sources:**
- Invoices collection (revenue)
- Transactions collection (expenses)
- Receipts collection (categorized expenses)

**Example report structure:**
```
INCOME STATEMENT
For the period: January 1 - December 31, 2025

REVENUE
  Sales Revenue                 KES 5,245,000
  Service Revenue               KES 1,890,000
  Total Revenue                 KES 7,135,000

OPERATING EXPENSES
  Rent                          KES 240,000
  Utilities                     KES 60,000
  Payroll                       KES 720,000
  Marketing                     KES 180,000
  Office Supplies               KES 60,000
  Travel                        KES 84,000
  Software & Technology         KES 96,000
  Total Operating Expenses      KES 1,440,000

NET INCOME                      KES 5,695,000
```

### 2. Cash Flow Statement
**Status:** ✅ Can be generated now

**What it shows:**
- Cash Inflows (customer payments)
- Cash Outflows (expenses)
- Net Cash Flow
- Beginning and Ending Cash Balance

**Data sources:**
- Transactions collection (all payment types)
- M-Pesa transactions
- Invoice payments

**Example report structure:**
```
CASH FLOW STATEMENT
For the period: January 1 - December 31, 2025

CASH INFLOWS
  Customer Payments (M-Pesa)    KES 3,200,000
  Bank Transfers                KES 1,500,000
  Cash Payments                 KES 800,000
  Total Inflows                 KES 5,500,000

CASH OUTFLOWS
  Operating Expenses            KES 1,440,000
  Vendor Payments               KES 800,000
  Tax Payments                  KES 600,000
  Total Outflows                KES 2,840,000

NET CASH FLOW                   KES 2,660,000

Beginning Cash Balance          KES 500,000
Ending Cash Balance             KES 3,160,000
```

### 3. Accounts Receivable (AR) Report
**Status:** ✅ Can be generated now

**What it shows:**
- Outstanding invoices
- Aging analysis (current, 30 days, 60 days, 90+ days)
- Customer balances
- Average days to payment

**Data sources:**
- Invoices collection (unpaid/partially paid)
- Customer collection (outstanding amounts)

**Example report structure:**
```
ACCOUNTS RECEIVABLE AGING REPORT
As of October 12, 2025

Customer              Current    1-30 Days   31-60 Days  61-90 Days  90+ Days    Total
─────────────────────────────────────────────────────────────────────────────────────
ABC Corporation       50,000     25,000      0           0           0           75,000
Tech Solutions Ltd    0          15,000      10,000      0           0           25,000
Creative Designs      30,000     0           0           5,000       2,000       37,000
XYZ Industries        20,000     10,000      0           0           0           30,000
─────────────────────────────────────────────────────────────────────────────────────
TOTAL                 100,000    50,000      10,000      5,000       2,000       167,000

Percentage            59.9%      29.9%       6.0%        3.0%        1.2%        100%
```

### 4. Revenue Report (Sales Analysis)
**Status:** ✅ Can be generated now

**What it shows:**
- Total revenue by period
- Revenue by customer
- Revenue trends
- Top customers
- Revenue growth rate

**Data sources:**
- Invoices collection
- Customer collection

**Example report structure:**
```
REVENUE ANALYSIS REPORT
For the period: Q1 2025

TOTAL REVENUE: KES 2,150,000

By Month:
  January 2025          KES 680,000   (+5.2% vs prev month)
  February 2025         KES 720,000   (+5.9% vs prev month)
  March 2025            KES 750,000   (+4.2% vs prev month)

Top 5 Customers:
  1. ABC Corporation            KES 464,802  (21.6%)
  2. Tech Solutions Ltd         KES 385,900  (17.9%)
  3. Global Enterprises         KES 298,450  (13.9%)
  4. Creative Designs Agency    KES 245,678  (11.4%)
  5. XYZ Industries             KES 189,234  (8.8%)

Revenue by Service Type:
  Consulting Services           KES 850,000  (39.5%)
  Product Sales                 KES 650,000  (30.2%)
  Subscription Services         KES 450,000  (20.9%)
  Other                         KES 200,000  (9.3%)
```

### 5. Expense Report (Cost Analysis)
**Status:** ✅ Can be generated now

**What it shows:**
- Total expenses by category
- Monthly expense trends
- Budget vs actual (if budgets are set)
- Top expense categories

**Data sources:**
- Transactions collection (expense type)
- Receipts collection

**Example report structure:**
```
EXPENSE REPORT
For the period: January - March 2025

TOTAL EXPENSES: KES 450,000

By Category:
  Payroll                   KES 180,000  (40.0%)
  Rent                      KES 60,000   (13.3%)
  Marketing                 KES 45,000   (10.0%)
  Software & Technology     KES 36,000   (8.0%)
  Utilities                 KES 30,000   (6.7%)
  Office Supplies           KES 24,000   (5.3%)
  Travel                    KES 21,000   (4.7%)
  Professional Services     KES 18,000   (4.0%)
  Insurance                 KES 15,000   (3.3%)
  Telecommunications        KES 12,000   (2.7%)
  Other                     KES 9,000    (2.0%)

Monthly Trend:
  January 2025              KES 145,000
  February 2025             KES 148,000  (+2.1%)
  March 2025                KES 157,000  (+6.1%)
```

### 6. Customer Statement
**Status:** ✅ Can be generated now

**What it shows:**
- Individual customer transaction history
- All invoices (paid and unpaid)
- All payments received
- Current balance

**Data sources:**
- Invoices collection (filtered by customer)
- Transactions collection (filtered by customer)
- Customer collection

**Example report structure:**
```
CUSTOMER STATEMENT
ABC Corporation (CUST-0001)
Statement Period: January 1 - March 31, 2025

Previous Balance                        KES 50,000

TRANSACTIONS
Date          Type        Invoice/Ref      Debit       Credit      Balance
─────────────────────────────────────────────────────────────────────────────
Jan 05, 2025  Invoice     INV-2025-001     120,000     -           170,000
Jan 10, 2025  Payment     MPESA-ABC123     -           50,000      120,000
Jan 20, 2025  Invoice     INV-2025-015     85,000      -           205,000
Feb 02, 2025  Payment     MPESA-ABC456     -           100,000     105,000
Feb 15, 2025  Invoice     INV-2025-034     95,000      -           200,000
Mar 01, 2025  Payment     MPESA-ABC789     -           85,000      115,000
Mar 20, 2025  Invoice     INV-2025-067     60,000      -           175,000

CURRENT BALANCE                             KES 175,000

Aging:
  Current (0-30 days)                       KES 60,000
  31-60 days                                KES 95,000
  61-90 days                                KES 20,000
  Over 90 days                              KES 0
```

### 7. Reconciliation Report
**Status:** ✅ Can be generated now

**What it shows:**
- Matched payments vs invoices
- Unmatched transactions
- Reconciliation confidence scores
- Items needing manual review

**Data sources:**
- Reconciliation logs collection
- Transactions collection
- Invoices collection

**Example report structure:**
```
PAYMENT RECONCILIATION REPORT
As of October 12, 2025

SUMMARY
  Total Payments Received       383
  Successfully Matched          364 (95.0%)
  Needs Manual Review           19  (5.0%)

MATCHED TRANSACTIONS (High Confidence >90%)
Date          Receipt#         Amount      Invoice#        Confidence
─────────────────────────────────────────────────────────────────────
Oct 10, 2025  MPESA-ABC123    50,000      INV-2025-123    98%
Oct 11, 2025  MPESA-XYZ456    75,000      INV-2025-124    95%
Oct 12, 2025  MPESA-DEF789    30,000      INV-2025-125    99%

NEEDS REVIEW (Confidence <90%)
Date          Receipt#         Amount      Possible Match  Confidence
─────────────────────────────────────────────────────────────────────
Oct 09, 2025  MPESA-GHI321    45,500      INV-2025-120    75%
Oct 10, 2025  MPESA-JKL654    22,000      None found      0%
Oct 11, 2025  MPESA-MNO987    15,000      INV-2025-118    60%

UNMATCHED PAYMENTS
  Amount pending allocation: KES 82,500
  Count: 19 transactions
```

### 8. Tax Report (VAT Summary)
**Status:** ✅ Can be generated now

**What it shows:**
- VAT collected on sales (output tax)
- VAT paid on purchases (input tax)
- Net VAT payable/refundable
- Tax period summary

**Data sources:**
- Invoices collection (tax calculations)
- Transactions collection (purchases with VAT)

**Example report structure:**
```
VAT SUMMARY REPORT
Tax Period: Q1 2025 (January - March)
Tax Rate: 16%

OUTPUT TAX (Sales)
  Taxable Sales                 KES 6,250,000
  VAT Collected                 KES 1,000,000

INPUT TAX (Purchases)
  Taxable Purchases             KES 1,875,000
  VAT Paid                      KES 300,000

NET VAT PAYABLE                 KES 700,000

Monthly Breakdown:
  January 2025
    Output Tax                  KES 325,000
    Input Tax                   KES 95,000
    Net Payable                 KES 230,000
  
  February 2025
    Output Tax                  KES 340,000
    Input Tax                   KES 102,000
    Net Payable                 KES 238,000
  
  March 2025
    Output Tax                  KES 335,000
    Input Tax                   KES 103,000
    Net Payable                 KES 232,000
```

### 9. Dashboard Metrics Report
**Status:** ✅ Can be generated now

**What it shows:**
- Key performance indicators (KPIs)
- Real-time financial health
- Quick snapshot of business

**Data sources:**
- All collections combined

**Example report structure:**
```
FINANCIAL DASHBOARD
As of October 12, 2025, 10:30 AM

CASH POSITION
  Current Balance               KES 3,160,000  ▲ +5,000 (today)
  Pending Receivables           KES 167,000
  Pending Payables              KES 85,000
  Net Available Cash            KES 3,242,000

REVENUE METRICS
  Month-to-Date (Oct)           KES 245,000
  Year-to-Date (2025)           KES 7,135,000  ▲ +12.5% YoY
  Average Monthly Revenue       KES 594,583

EXPENSE METRICS
  Month-to-Date (Oct)           KES 128,000
  Year-to-Date (2025)           KES 1,440,000
  Operating Margin              79.8%

ACCOUNTS RECEIVABLE
  Total Outstanding             KES 167,000
  Overdue Invoices              7
  Average Days to Payment       12 days

PAYMENT METRICS
  On-Time Payment Rate          85%
  Reconciliation Rate           95%
  Unmatched Transactions        19

TOP ALERTS
  ⚠️  7 overdue invoices (KES 82,500)
  ⚠️  3 customers over 60 days past due
  ✅  95% reconciliation rate (target met)
  ✅  Operating margin above 75% target
```

### 10. AI-Powered Financial Insights Report
**Status:** ✅ Can be generated now (using existing AI Insights service)

**What it shows:**
- Predictive analytics
- Anomaly detection
- Trend analysis
- Recommendations

**Data sources:**
- All collections
- AI/ML models via Gemini API

**Example report structure:**
```
AI FINANCIAL INSIGHTS REPORT
Generated: October 12, 2025

KEY INSIGHTS

1. Revenue Trend Analysis
   📈 Revenue growing at 12.5% year-over-year
   💡 Insight: Strong growth in Q2-Q3, slight slowdown in Q4
   🎯 Recommendation: Focus on customer retention campaigns in Q4

2. Cash Flow Predictions
   💰 Projected cash position in 30 days: KES 3,450,000 (+9%)
   💡 Insight: Healthy cash flow with seasonal variations
   🎯 Recommendation: Consider investment opportunities

3. Anomaly Detection
   ⚠️  Detected 3 unusual transactions:
       - MPESA-XYZ789: KES 125,000 at 2:30 AM (unusual time)
       - Payment from new customer: 3x average amount
       - Expense spike in "Travel" category (+45% vs avg)
   
4. Customer Analysis
   ⭐ Top performers: ABC Corp, Tech Solutions Ltd
   ⚠️  At-risk customers (declining payment patterns): 2
   💡 Insight: 85% customer retention rate (healthy)
   
5. Expense Optimization
   💡 Payroll is 40% of total expenses (industry avg: 35%)
   💡 Marketing ROI: KES 12 revenue per KES 1 spent
   🎯 Recommendation: Increase marketing budget by 20%

6. Payment Behavior Patterns
   📊 Peak payment times: 9 AM - 11 AM, 2 PM - 4 PM
   📊 Average payment delay: 12 days after invoice
   💡 85% pay within 30 days (good payment behavior)

PREDICTIONS
  Next Month Revenue (Nov 2025):     KES 620,000 - 680,000
  Confidence: 87%
  
  Q4 2025 Total Revenue:             KES 2,100,000 - 2,300,000
  Confidence: 82%
  
  Year-End Cash Position:            KES 3,800,000 - 4,100,000
  Confidence: 85%
```

---

## 🤖 AI-Powered Reports (Advanced)

### 11. Conversational Financial Analysis
**Status:** ✅ Available now via AI Insights API

Ask questions in natural language and get AI-generated insights:

**Example queries:**
- "What were my top 3 expenses last month?"
- "Which customers haven't paid in over 60 days?"
- "Show me revenue trends for Q3"
- "Predict cash flow for next month"
- "Identify unusual transactions this week"
- "Compare this month's performance to last month"

### 12. Custom Reports via AI
**Status:** ✅ Can be generated using AI service

Generate custom reports by asking:
- "Create a report showing my most profitable customers"
- "Analyze payment patterns by day of week"
- "Show me expense distribution for the last quarter"
- "Which invoices are at risk of becoming overdue?"

---

## 🚀 How to Generate These Reports

### Option 1: Create Reporting API Endpoints (Recommended)

**Step 1:** Extend the existing reporting service
```python
# backend/reporting/service.py

async def generate_income_statement(start_date, end_date):
    # Query invoices for revenue
    revenue = await db.invoices.aggregate([...])
    
    # Query transactions for expenses
    expenses = await db.transactions.aggregate([...])
    
    # Calculate profit/loss
    return income_statement

async def generate_cash_flow_statement(start_date, end_date):
    # Similar implementation
    ...

async def generate_ar_aging_report(as_of_date):
    # Query unpaid invoices
    ...
```

**Step 2:** Create API endpoints
```python
# backend/reporting/router.py

@router.get("/api/reports/income-statement")
async def get_income_statement(
    start_date: str,
    end_date: str
):
    return await service.generate_income_statement(start_date, end_date)

@router.get("/api/reports/cash-flow")
async def get_cash_flow(...):
    ...

@router.get("/api/reports/ar-aging")
async def get_ar_aging(...):
    ...
```

**Step 3:** Create frontend components
```typescript
// finance-app/app/reports/income-statement/page.tsx

export default function IncomeStatementPage() {
  // Fetch and display income statement
  ...
}
```

### Option 2: Use AI Insights for Dynamic Reports

**Query the AI Insights API:**
```bash
POST http://localhost:8000/api/ai-insights/query
Content-Type: application/json

{
  "question": "Generate an income statement for Q3 2025",
  "date_range": {
    "start": "2025-07-01",
    "end": "2025-09-30"
  }
}
```

### Option 3: Export to PDF/Excel

**Add export functionality:**
```python
# backend/reporting/export.py

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd

def export_to_pdf(report_data, filename):
    # Generate PDF report
    ...

def export_to_excel(report_data, filename):
    df = pd.DataFrame(report_data)
    df.to_excel(filename)
```

---

## 📋 Implementation Priority

### Phase 1: Essential Reports (Week 1)
1. ✅ Dashboard Metrics (basic version exists)
2. ✅ Revenue Report (can use existing data)
3. ✅ Expense Report (can use existing data)
4. ✅ AR Aging Report (customer data available)

### Phase 2: Financial Statements (Week 2)
1. Income Statement
2. Cash Flow Statement
3. Customer Statement
4. Reconciliation Report

### Phase 3: Advanced Reports (Week 3)
1. Tax Report (VAT Summary)
2. Predictive Analytics
3. Custom AI Reports
4. Export functionality (PDF/Excel)

### Phase 4: Automation (Week 4)
1. Scheduled reports
2. Email delivery
3. Real-time dashboards
4. Report templates

---

## 💻 Quick Start: Generate Your First Report

### 1. Income Statement (Simple Version)

Create a new script:
```bash
cd /home/munga/Desktop/AI-Financial-Agent
nano scripts/generate_income_statement.py
```

```python
#!/usr/bin/env python3
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

MONGO_URI = "mongodb+srv://munga21407:Wazimba21407@cluster0.y7595ne.mongodb.net/"
DB_NAME = "financial_agent"

async def generate_income_statement():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Get all paid invoices (revenue)
    invoices = await db.invoices.find({"status": "paid"}).to_list(None)
    total_revenue = sum(inv.get("amount", 0) for inv in invoices)
    
    # Get all expenses
    expenses = await db.transactions.find({"type": "expense"}).to_list(None)
    
    # Group by category
    expense_by_category = {}
    for exp in expenses:
        category = exp.get("category", "Other")
        amount = exp.get("amount", 0)
        expense_by_category[category] = expense_by_category.get(category, 0) + amount
    
    total_expenses = sum(expense_by_category.values())
    net_income = total_revenue - total_expenses
    
    # Print report
    print("=" * 60)
    print("INCOME STATEMENT")
    print("For All Time")
    print("=" * 60)
    print(f"\nREVENUE")
    print(f"  Total Revenue                 KES {total_revenue:,.2f}")
    print(f"\nOPERATING EXPENSES")
    for category, amount in expense_by_category.items():
        print(f"  {category:<25} KES {amount:,.2f}")
    print(f"  {'Total Expenses':<25} KES {total_expenses:,.2f}")
    print(f"\nNET INCOME                      KES {net_income:,.2f}")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(generate_income_statement())
```

Run it:
```bash
python scripts/generate_income_statement.py
```

---

## 📚 Next Steps

1. **Review current data** in MongoDB to understand what's available
2. **Choose reports** you want to prioritize
3. **Implement reporting service** in backend
4. **Create frontend UI** for report viewing
5. **Add export functionality** (PDF/Excel)
6. **Set up scheduled reports** for automation

---

## 🎯 Summary

Your system already has the data to generate:
- ✅ Income Statement
- ✅ Cash Flow Statement
- ✅ AR Aging Report
- ✅ Revenue Analysis
- ✅ Expense Report
- ✅ Customer Statements
- ✅ Reconciliation Report
- ✅ Tax Reports (VAT)
- ✅ Dashboard Metrics
- ✅ AI-Powered Insights

**What you need to do:**
1. Create reporting API endpoints
2. Build frontend UI for reports
3. Add PDF/Excel export
4. Set up scheduling for automatic reports

**Estimated Development Time:**
- Phase 1 (Essential Reports): 1 week
- Phase 2 (Financial Statements): 1 week
- Phase 3 (Advanced Features): 1 week
- Phase 4 (Automation): 1 week

**Total: 4 weeks for complete reporting system** 📊

---

**Document Version:** 1.0  
**Date:** October 12, 2025  
**Status:** Ready for implementation
