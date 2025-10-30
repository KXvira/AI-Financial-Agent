# Reports Section - Implementation Plan

## 📋 Executive Summary

This document outlines the complete implementation plan for adding a comprehensive Reports section to the AI Financial Agent system. The Reports section will allow users to generate, view, export, and schedule various financial reports.

---

## 🎯 Project Overview

### Objectives
1. Create a centralized Reports section in the application
2. Enable generation of 10+ different financial report types
3. Provide interactive filtering and date range selection
4. Support multiple export formats (PDF, Excel, CSV)
5. Enable report scheduling and automation
6. Integrate AI-powered insights into reports

### Success Criteria
- Users can generate any report in < 3 seconds
- Reports are accurate (100% match with raw data)
- Export functionality works for all formats
- Mobile-responsive report viewing
- Scheduled reports delivered on time
- AI insights add value to reports

### Timeline
- **Phase 1:** 1 week - Core infrastructure & 3 basic reports
- **Phase 2:** 1 week - 5 additional reports & filtering
- **Phase 3:** 1 week - Export functionality & UI polish
- **Phase 4:** 1 week - Scheduling, automation & AI integration
- **Total:** 4 weeks

---

## 🏗️ System Architecture

### Current System Analysis

**Existing Components:**
```
✅ Backend (FastAPI)
   - /backend/reporting/service.py (basic structure exists)
   - Database connection (Motor/MongoDB)
   - AI Insights service (Gemini integration)
   - Email service (SendGrid)

✅ Frontend (Next.js)
   - React components
   - Tailwind CSS styling
   - Chart.js ready (can be installed)

✅ Database (MongoDB)
   - 261 invoices
   - 383 transactions
   - 8 customers
   - Reconciliation logs
   - Email logs

✅ Data Quality
   - 87.4% collection rate
   - Clean data structure
   - Proper indexes
```

### Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Reports Dashboard (/app/reports/page.tsx)     │  │
│  │  - Report cards/tiles                                 │  │
│  │  - Quick filters                                      │  │
│  │  - Recent reports list                                │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │      Individual Report Pages                          │  │
│  │  /app/reports/income-statement/page.tsx              │  │
│  │  /app/reports/cash-flow/page.tsx                     │  │
│  │  /app/reports/ar-aging/page.tsx                      │  │
│  │  ... (one page per report type)                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Shared Components                             │  │
│  │  - ReportViewer.tsx (common layout)                  │  │
│  │  - ReportFilters.tsx (date range, filters)           │  │
│  │  - ExportButtons.tsx (PDF, Excel, CSV)               │  │
│  │  - ReportChart.tsx (visualizations)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Report Router (API Endpoints)                 │  │
│  │  /backend/reporting/router.py                        │  │
│  │                                                          │  │
│  │  GET  /api/reports/types                             │  │
│  │  POST /api/reports/generate                          │  │
│  │  GET  /api/reports/income-statement                  │  │
│  │  GET  /api/reports/cash-flow                         │  │
│  │  GET  /api/reports/ar-aging                          │  │
│  │  GET  /api/reports/revenue                           │  │
│  │  GET  /api/reports/expense                           │  │
│  │  GET  /api/reports/customer-statement/:id            │  │
│  │  GET  /api/reports/reconciliation                    │  │
│  │  GET  /api/reports/tax-summary                       │  │
│  │  GET  /api/reports/dashboard-metrics                 │  │
│  │  POST /api/reports/export                            │  │
│  │  POST /api/reports/schedule                          │  │
│  │  GET  /api/reports/scheduled                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Report Service (Business Logic)               │  │
│  │  /backend/reporting/service.py                       │  │
│  │                                                          │  │
│  │  - ReportingService class                            │  │
│  │    • generate_income_statement()                     │  │
│  │    • generate_cash_flow()                            │  │
│  │    • generate_ar_aging()                             │  │
│  │    • generate_revenue_report()                       │  │
│  │    • generate_expense_report()                       │  │
│  │    • generate_customer_statement()                   │  │
│  │    • generate_reconciliation_report()                │  │
│  │    • generate_tax_summary()                          │  │
│  │    • get_dashboard_metrics()                         │  │
│  │    • schedule_report()                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Export Service                                │  │
│  │  /backend/reporting/export.py                        │  │
│  │                                                          │  │
│  │  - ExportService class                               │  │
│  │    • export_to_pdf()                                 │  │
│  │    • export_to_excel()                               │  │
│  │    • export_to_csv()                                 │  │
│  │    • generate_chart_images()                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Report Models                                 │  │
│  │  /backend/reporting/models.py                        │  │
│  │                                                          │  │
│  │  - Pydantic models for all report types              │  │
│  │  - Request/Response schemas                          │  │
│  │  - Validation rules                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ MongoDB Queries
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Database (MongoDB)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Collections:                                                 │
│  - invoices (261)                                            │
│  - transactions (383)                                        │
│  - customers (8)                                             │
│  - reconciliation_logs                                       │
│  - email_logs                                                │
│  - report_cache (NEW)                                        │
│  - scheduled_reports (NEW)                                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Detailed Implementation Plan

### PHASE 1: Core Infrastructure & Basic Reports (Week 1)

#### Day 1-2: Backend Foundation

**1.1 Report Models (`/backend/reporting/models.py`)**

Create Pydantic models:

```python
# Report request models
class ReportRequest(BaseModel):
    report_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}
    format: str = "json"  # json, pdf, excel, csv

class DateRangeFilter(BaseModel):
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    preset: Optional[str] = None  # "today", "this_week", "this_month", etc.

# Report response models
class IncomeStatementReport(BaseModel):
    report_type: str = "income_statement"
    period_start: str
    period_end: str
    generated_at: str
    revenue: RevenueSection
    expenses: ExpenseSection
    net_income: float
    net_margin: float
    currency: str = "KES"

class RevenueSection(BaseModel):
    total_revenue: float
    sales_revenue: float
    service_revenue: float
    other_revenue: float

class ExpenseSection(BaseModel):
    total_expenses: float
    by_category: Dict[str, float]
    operating_expenses: float
    
# ... (similar models for all report types)
```

**1.2 Report Service Enhancement (`/backend/reporting/service.py`)**

Implement core report generation methods:

```python
class ReportingService:
    def __init__(self, db: Database):
        self.db = db
    
    async def generate_income_statement(
        self,
        start_date: str,
        end_date: str,
        filters: Dict[str, Any] = None
    ) -> IncomeStatementReport:
        """Generate income statement for date range"""
        
        # 1. Query invoices (revenue)
        invoice_pipeline = [
            {
                "$match": {
                    "date_issued": {
                        "$gte": datetime.fromisoformat(start_date),
                        "$lte": datetime.fromisoformat(end_date)
                    },
                    "status": "paid"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount"}
                }
            }
        ]
        
        revenue_result = await self.db.invoices.aggregate(invoice_pipeline).to_list(1)
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
        
        # 2. Query expenses
        expense_pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": datetime.fromisoformat(start_date),
                        "$lte": datetime.fromisoformat(end_date)
                    },
                    "type": "expense"
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"}
                }
            }
        ]
        
        expense_results = await self.db.transactions.aggregate(expense_pipeline).to_list(None)
        expenses_by_category = {e["_id"]: e["total"] for e in expense_results}
        total_expenses = sum(expenses_by_category.values())
        
        # 3. Calculate net income
        net_income = total_revenue - total_expenses
        net_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # 4. Build report
        return IncomeStatementReport(
            period_start=start_date,
            period_end=end_date,
            generated_at=datetime.now().isoformat(),
            revenue=RevenueSection(
                total_revenue=total_revenue,
                sales_revenue=total_revenue,  # TODO: break down by type
                service_revenue=0,
                other_revenue=0
            ),
            expenses=ExpenseSection(
                total_expenses=total_expenses,
                by_category=expenses_by_category,
                operating_expenses=total_expenses
            ),
            net_income=net_income,
            net_margin=net_margin
        )
    
    async def generate_cash_flow(
        self,
        start_date: str,
        end_date: str,
        filters: Dict[str, Any] = None
    ) -> CashFlowReport:
        """Generate cash flow statement"""
        # Implementation similar to income statement
        ...
    
    async def generate_ar_aging(
        self,
        as_of_date: str = None,
        filters: Dict[str, Any] = None
    ) -> ARAgingReport:
        """Generate accounts receivable aging report"""
        # Implementation
        ...
```

**1.3 Report Router (`/backend/reporting/router.py`)**

Create API endpoints:

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from .models import *
from .service import ReportingService
from database.mongodb import get_database

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/types")
async def get_report_types():
    """Get list of available report types"""
    return {
        "report_types": [
            {
                "id": "income_statement",
                "name": "Income Statement",
                "description": "Profit & Loss statement showing revenue and expenses",
                "category": "financial",
                "requires_date_range": True
            },
            {
                "id": "cash_flow",
                "name": "Cash Flow Statement",
                "description": "Shows cash inflows and outflows",
                "category": "financial",
                "requires_date_range": True
            },
            {
                "id": "ar_aging",
                "name": "Accounts Receivable Aging",
                "description": "Outstanding invoices by age",
                "category": "receivables",
                "requires_date_range": False
            },
            # ... more report types
        ]
    }

@router.get("/income-statement")
async def get_income_statement(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Database = Depends(get_database)
):
    """Generate income statement"""
    service = ReportingService(db)
    
    try:
        report = await service.generate_income_statement(start_date, end_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cash-flow")
async def get_cash_flow(
    start_date: str = Query(...),
    end_date: str = Query(...),
    db: Database = Depends(get_database)
):
    """Generate cash flow statement"""
    service = ReportingService(db)
    
    try:
        report = await service.generate_cash_flow(start_date, end_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ar-aging")
async def get_ar_aging(
    as_of_date: Optional[str] = Query(None),
    db: Database = Depends(get_database)
):
    """Generate AR aging report"""
    service = ReportingService(db)
    
    try:
        report = await service.generate_ar_aging(as_of_date)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**1.4 Register Router in Main App**

Update `backend/standalone_app.py`:

```python
try:
    from reporting.router import router as reporting_router
    print("✅ Reporting router imported")
except ImportError as e:
    print(f"❌ Reporting router import failed: {e}")
    reporting_router = None

# ... in app setup
if reporting_router:
    app.include_router(reporting_router, prefix="/api")
    print("✅ Reporting routes added")
```

#### Day 3-4: Frontend Foundation

**2.1 Reports Dashboard Page (`/finance-app/app/reports/page.tsx`)**

```typescript
'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface ReportType {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
}

export default function ReportsPage() {
  const [reportTypes, setReportTypes] = useState<ReportType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReportTypes();
  }, []);

  const fetchReportTypes = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/reports/types');
      const data = await response.json();
      setReportTypes(data.report_types);
    } catch (error) {
      console.error('Error fetching report types:', error);
    } finally {
      setLoading(false);
    }
  };

  const categories = {
    financial: { name: 'Financial Statements', icon: '📊' },
    receivables: { name: 'Accounts Receivable', icon: '💰' },
    analytics: { name: 'Analytics & Insights', icon: '📈' },
    operational: { name: 'Operational Reports', icon: '⚙️' },
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-2">
          Generate financial reports and insights from your data
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Reports"
          value="10"
          icon="📄"
          color="blue"
        />
        <StatCard
          title="Last Generated"
          value="Today"
          icon="⏰"
          color="green"
        />
        <StatCard
          title="Scheduled"
          value="3"
          icon="📅"
          color="purple"
        />
        <StatCard
          title="Exports"
          value="25"
          icon="📥"
          color="orange"
        />
      </div>

      {/* Report Categories */}
      {Object.entries(categories).map(([key, category]) => {
        const categoryReports = reportTypes.filter(r => r.category === key);
        
        if (categoryReports.length === 0) return null;

        return (
          <div key={key} className="mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="text-2xl">{category.icon}</span>
              {category.name}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoryReports.map(report => (
                <ReportCard key={report.id} report={report} />
              ))}
            </div>
          </div>
        );
      })}

      {loading && (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  const colors = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className={`inline-flex p-3 rounded-lg ${colors[color]} mb-3`}>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className="text-gray-600 text-sm">{title}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}

function ReportCard({ report }: { report: ReportType }) {
  return (
    <Link href={`/reports/${report.id}`}>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer border border-gray-200 hover:border-blue-500">
        <div className="flex items-start justify-between mb-4">
          <div className="bg-blue-50 p-3 rounded-lg">
            <span className="text-2xl">{report.icon}</span>
          </div>
        </div>
        <h3 className="text-lg font-semibold mb-2">{report.name}</h3>
        <p className="text-gray-600 text-sm">{report.description}</p>
        <div className="mt-4 flex items-center text-blue-600 text-sm font-medium">
          Generate Report
          <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </Link>
  );
}
```

**2.2 Shared Components**

Create `/finance-app/components/reports/`:
- `ReportViewer.tsx` - Common layout for all reports
- `ReportFilters.tsx` - Date range and filter controls
- `ReportHeader.tsx` - Report title, export buttons
- `LoadingReport.tsx` - Loading skeleton

**2.3 Example: Income Statement Page**

`/finance-app/app/reports/income-statement/page.tsx`:

```typescript
'use client';

import { useState, useEffect } from 'react';
import ReportViewer from '@/components/reports/ReportViewer';
import ReportFilters from '@/components/reports/ReportFilters';

export default function IncomeStatementPage() {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState({
    start: '2025-01-01',
    end: '2025-12-31',
  });

  const generateReport = async () => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/reports/income-statement?start_date=${dateRange.start}&end_date=${dateRange.end}`
      );
      const data = await response.json();
      setReport(data);
    } catch (error) {
      console.error('Error generating report:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    generateReport();
  }, []);

  return (
    <ReportViewer
      title="Income Statement"
      subtitle="Profit & Loss Report"
      loading={loading}
      filters={
        <ReportFilters
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
          onGenerate={generateReport}
        />
      }
    >
      {report && (
        <div className="space-y-6">
          {/* Revenue Section */}
          <Section title="REVENUE">
            <LineItem label="Total Revenue" amount={report.revenue.total_revenue} bold />
          </Section>

          {/* Expenses Section */}
          <Section title="OPERATING EXPENSES">
            {Object.entries(report.expenses.by_category).map(([category, amount]) => (
              <LineItem key={category} label={category} amount={amount} />
            ))}
            <LineItem label="Total Expenses" amount={report.expenses.total_expenses} bold />
          </Section>

          {/* Net Income */}
          <div className="border-t-2 border-gray-800 pt-4">
            <LineItem 
              label="NET INCOME" 
              amount={report.net_income} 
              bold 
              highlight 
            />
            <div className="text-right text-gray-600 mt-2">
              Net Margin: {report.net_margin.toFixed(1)}%
            </div>
          </div>
        </div>
      )}
    </ReportViewer>
  );
}

function Section({ title, children }: any) {
  return (
    <div className="border-b pb-4">
      <h3 className="text-lg font-semibold mb-3 text-gray-700">{title}</h3>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function LineItem({ label, amount, bold, highlight }: any) {
  return (
    <div className={`flex justify-between ${bold ? 'font-semibold' : ''} ${highlight ? 'bg-green-50 p-2 rounded' : ''}`}>
      <span>{label}</span>
      <span>KES {amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span>
    </div>
  );
}
```

#### Day 5: Testing & Polish

- Test all 3 reports (Income Statement, Cash Flow, AR Aging)
- Fix bugs and edge cases
- Add loading states
- Add error handling
- Write basic tests

**Deliverables for Phase 1:**
✅ Backend infrastructure for reports
✅ 3 working reports (Income Statement, Cash Flow, AR Aging)
✅ Reports dashboard page
✅ Basic filtering (date range)
✅ API documentation

---

### PHASE 2: Additional Reports & Advanced Filtering (Week 2)

#### Day 1-2: Implement 5 More Reports

1. **Revenue Report**
   - Total revenue by period
   - Revenue by customer
   - Revenue trends
   - Top customers

2. **Expense Report**
   - Expenses by category
   - Monthly trends
   - Budget vs actual
   - Top expense categories

3. **Customer Statement**
   - Individual customer transactions
   - All invoices and payments
   - Current balance
   - Aging analysis

4. **Reconciliation Report**
   - Matched transactions
   - Unmatched items
   - Confidence scores
   - Items needing review

5. **Dashboard Metrics**
   - KPIs and quick metrics
   - Real-time data
   - Trend indicators

#### Day 3-4: Advanced Filtering

**Implement filter system:**
- Date range presets (Today, This Week, This Month, This Quarter, This Year, Custom)
- Customer filter (multi-select)
- Status filter (paid, pending, overdue)
- Category filter (expense categories)
- Amount range filter
- Search functionality

**Create filter components:**
- `DateRangeFilter.tsx`
- `CustomerFilter.tsx`
- `StatusFilter.tsx`
- `CategoryFilter.tsx`
- `AmountRangeFilter.tsx`

#### Day 5: Report Comparisons

- Compare periods (This Month vs Last Month)
- Year-over-Year comparisons
- Trend indicators (↑↓)
- Percentage changes

**Deliverables for Phase 2:**
✅ 8 total reports working
✅ Advanced filtering system
✅ Period comparisons
✅ Improved UI/UX

---

### PHASE 3: Export Functionality & UI Polish (Week 3)

#### Day 1-2: Export Service

**Create `/backend/reporting/export.py`:**

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import pandas as pd
from io import BytesIO

class ExportService:
    """Service for exporting reports to various formats"""
    
    def export_to_pdf(self, report_data: Dict, report_type: str) -> BytesIO:
        """Export report to PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        
        # Build PDF content
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1E40AF'),
            spaceAfter=30,
        )
        title = Paragraph(report_data['title'], title_style)
        story.append(title)
        
        # Period
        period_text = f"Period: {report_data['period_start']} to {report_data['period_end']}"
        story.append(Paragraph(period_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Data table
        if report_type == 'income_statement':
            table_data = self._build_income_statement_table(report_data)
        elif report_type == 'cash_flow':
            table_data = self._build_cash_flow_table(report_data)
        # ... more report types
        
        table = Table(table_data, colWidths=[4*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def export_to_excel(self, report_data: Dict, report_type: str) -> BytesIO:
        """Export report to Excel"""
        buffer = BytesIO()
        
        # Convert report data to DataFrame
        df = self._report_to_dataframe(report_data, report_type)
        
        # Write to Excel with formatting
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Report', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Report']
            
            # Add formatting
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#1E40AF',
                'font_color': 'white',
                'border': 1
            })
            
            # Apply header format
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 15)
        
        buffer.seek(0)
        return buffer
    
    def export_to_csv(self, report_data: Dict, report_type: str) -> str:
        """Export report to CSV"""
        df = self._report_to_dataframe(report_data, report_type)
        return df.to_csv(index=False)
```

**Add export endpoint:**

```python
@router.post("/export")
async def export_report(
    report_request: ExportRequest,
    db: Database = Depends(get_database)
):
    """Export report to specified format"""
    
    # Generate report
    service = ReportingService(db)
    report_data = await service.generate_report(
        report_request.report_type,
        report_request.start_date,
        report_request.end_date
    )
    
    # Export to requested format
    export_service = ExportService()
    
    if report_request.format == 'pdf':
        buffer = export_service.export_to_pdf(report_data, report_request.report_type)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report.pdf"}
        )
    elif report_request.format == 'excel':
        buffer = export_service.export_to_excel(report_data, report_request.report_type)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=report.xlsx"}
        )
    elif report_request.format == 'csv':
        csv_content = export_service.export_to_csv(report_data, report_request.report_type)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=report.csv"}
        )
```

#### Day 3-4: Frontend Export Buttons

**Create `ExportButtons.tsx`:**

```typescript
'use client';

import { useState } from 'react';

interface ExportButtonsProps {
  reportType: string;
  startDate: string;
  endDate: string;
  filters?: any;
}

export default function ExportButtons({ reportType, startDate, endDate, filters }: ExportButtonsProps) {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format: 'pdf' | 'excel' | 'csv') => {
    setExporting(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/reports/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          report_type: reportType,
          start_date: startDate,
          end_date: endDate,
          filters,
          format
        }),
      });

      // Download file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_${startDate}_to_${endDate}.${format === 'excel' ? 'xlsx' : format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="flex gap-2">
      <button
        onClick={() => handleExport('pdf')}
        disabled={exporting}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 flex items-center gap-2"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
        </svg>
        Export PDF
      </button>
      
      <button
        onClick={() => handleExport('excel')}
        disabled={exporting}
        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 flex items-center gap-2"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
        </svg>
        Export Excel
      </button>
      
      <button
        onClick={() => handleExport('csv')}
        disabled={exporting}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2"
      >
        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" />
        </svg>
        Export CSV
      </button>
    </div>
  );
}
```

#### Day 5: UI Polish

- Add charts and visualizations
- Improve responsive design
- Add print styles
- Add keyboard shortcuts
- Improve accessibility

**Deliverables for Phase 3:**
✅ PDF export
✅ Excel export
✅ CSV export
✅ Polished UI
✅ Charts/visualizations
✅ Print-friendly layouts

---

### PHASE 4: Scheduling, Automation & AI (Week 4)

#### Day 1-2: Report Scheduling

**Backend:**
- Create `scheduled_reports` collection
- Implement scheduling service
- Set up cron-like scheduler
- Email delivery integration

**Frontend:**
- Schedule report modal
- Manage scheduled reports page
- Edit/delete schedules

#### Day 3-4: AI Integration

- Integrate with existing AI Insights service
- Add AI commentary to reports
- Predictive analytics
- Anomaly detection highlights
- Trend explanations

#### Day 5: Final Polish & Documentation

- Complete testing
- Write API documentation
- Create user guide
- Video tutorials
- Deployment preparation

**Deliverables for Phase 4:**
✅ Report scheduling
✅ Automated email delivery
✅ AI-powered insights
✅ Complete documentation
✅ Production-ready system

---

## 📦 Dependencies to Install

### Backend
```bash
pip install reportlab==4.2.5          # PDF generation
pip install pandas==2.0.3              # Excel/CSV export
pip install xlsxwriter==3.1.2          # Excel formatting
pip install matplotlib==3.7.2          # Chart generation (for PDF)
pip install apscheduler==3.10.1        # Report scheduling
```

### Frontend
```bash
npm install chart.js react-chartjs-2  # Charts
npm install date-fns                   # Date utilities
npm install react-datepicker           # Date picker
npm install jspdf                      # Client-side PDF (optional)
```

---

## 🗂️ File Structure

```
AI-Financial-Agent/
├── backend/
│   └── reporting/
│       ├── __init__.py
│       ├── router.py          (NEW - API endpoints)
│       ├── service.py          (ENHANCED - report logic)
│       ├── models.py           (NEW - Pydantic models)
│       ├── export.py           (NEW - export service)
│       └── scheduler.py        (NEW - report scheduling)
│
├── finance-app/
│   ├── app/
│   │   └── reports/
│   │       ├── page.tsx                    (NEW - dashboard)
│   │       ├── income-statement/
│   │       │   └── page.tsx                (NEW)
│   │       ├── cash-flow/
│   │       │   └── page.tsx                (NEW)
│   │       ├── ar-aging/
│   │       │   └── page.tsx                (NEW)
│   │       ├── revenue/
│   │       │   └── page.tsx                (NEW)
│   │       ├── expense/
│   │       │   └── page.tsx                (NEW)
│   │       ├── customer-statement/
│   │       │   └── [id]/
│   │       │       └── page.tsx            (NEW)
│   │       ├── reconciliation/
│   │       │   └── page.tsx                (NEW)
│   │       ├── dashboard-metrics/
│   │       │   └── page.tsx                (NEW)
│   │       └── scheduled/
│   │           └── page.tsx                (NEW)
│   │
│   └── components/
│       └── reports/
│           ├── ReportViewer.tsx            (NEW)
│           ├── ReportFilters.tsx           (NEW)
│           ├── ReportHeader.tsx            (NEW)
│           ├── ExportButtons.tsx           (NEW)
│           ├── DateRangeFilter.tsx         (NEW)
│           ├── CustomerFilter.tsx          (NEW)
│           ├── ReportChart.tsx             (NEW)
│           ├── LoadingReport.tsx           (NEW)
│           └── ScheduleReportModal.tsx     (NEW)
│
├── scripts/
│   └── generate_income_statement.py   (EXISTING - demo)
│
└── docs/
    ├── FINANCIAL_STATEMENTS_GUIDE.md  (EXISTING)
    └── REPORTS_IMPLEMENTATION_PLAN.md (THIS FILE)
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_reporting_service.py

async def test_generate_income_statement():
    service = ReportingService(mock_db)
    report = await service.generate_income_statement('2025-01-01', '2025-12-31')
    
    assert report.net_income > 0
    assert report.net_margin > 0
    assert len(report.expenses.by_category) > 0
```

### Integration Tests
```python
async def test_income_statement_endpoint():
    response = await client.get('/api/reports/income-statement?start_date=2025-01-01&end_date=2025-12-31')
    
    assert response.status_code == 200
    data = response.json()
    assert 'net_income' in data
    assert 'revenue' in data
```

### Frontend Tests
```typescript
// __tests__/reports/income-statement.test.tsx

describe('Income Statement Page', () => {
  it('renders report data correctly', () => {
    render(<IncomeStatementPage />);
    expect(screen.getByText('Income Statement')).toBeInTheDocument();
  });
  
  it('generates report on button click', async () => {
    // ... test implementation
  });
});
```

---

## 🚀 Deployment Checklist

### Backend
- [ ] Install Python dependencies
- [ ] Run database migrations
- [ ] Set environment variables
- [ ] Test all API endpoints
- [ ] Set up error monitoring
- [ ] Configure CORS for frontend
- [ ] Enable API rate limiting

### Frontend
- [ ] Install npm packages
- [ ] Update API base URLs for production
- [ ] Build production bundle
- [ ] Test all pages
- [ ] Optimize images/assets
- [ ] Enable caching
- [ ] Set up CDN (optional)

### Database
- [ ] Create new collections (report_cache, scheduled_reports)
- [ ] Add indexes for report queries
- [ ] Test query performance
- [ ] Set up backup strategy

---

## 📊 Success Metrics

### Performance
- Report generation time < 3 seconds
- Page load time < 2 seconds
- Export time < 5 seconds

### Quality
- 100% data accuracy
- 0 critical bugs
- 95%+ test coverage
- A+ accessibility score

### User Experience
- < 3 clicks to any report
- Intuitive navigation
- Mobile responsive
- Fast load times

---

## 🎯 Summary

This plan provides a complete roadmap for implementing a comprehensive Reports section in your AI Financial Agent system.

**Timeline:** 4 weeks
**Effort:** ~160 hours
**Team:** 1-2 developers

**Phase Breakdown:**
- **Week 1:** Core infrastructure (3 reports)
- **Week 2:** 5 more reports + filtering
- **Week 3:** Export functionality + UI
- **Week 4:** Scheduling + AI + polish

**Key Deliverables:**
- 10+ financial reports
- PDF/Excel/CSV export
- Advanced filtering
- Report scheduling
- AI-powered insights
- Mobile-responsive UI
- Complete documentation

**Ready to start implementation?** Begin with Phase 1, Day 1! 🚀

---

**Document Version:** 1.0  
**Date:** October 12, 2025  
**Status:** Ready for Implementation  
**Next Step:** Create backend models and service layer
