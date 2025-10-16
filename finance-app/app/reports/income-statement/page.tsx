'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import ReportChart, { prepareChartData } from '@/components/ReportChart';
import { exportIncomeStatementPDF, exportToExcel, exportToCSV, formatDataForExport } from '@/utils/exportUtils';

interface RevenueSection {
  total_revenue: number;
  invoiced_amount: number;
  paid_amount: number;
  pending_amount: number;
  invoice_count: number;
  paid_invoice_count: number;
}

interface ExpenseCategory {
  category: string;
  amount: number;
  percentage: number;
}

interface ExpenseSection {
  total_expenses: number;
  by_category: Record<string, number>;
  transaction_count: number;
  top_categories: ExpenseCategory[];
}

interface IncomeStatement {
  report_type: string;
  report_name: string;
  period_start: string;
  period_end: string;
  generated_at: string;
  currency: string;
  revenue: RevenueSection;
  expenses: ExpenseSection;
  gross_profit: number;
  operating_income: number;
  net_income: number;
  profit_margin: number;
  collection_rate: number;
}

export default function IncomeStatementPage() {
  const [report, setReport] = useState<IncomeStatement | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/reports/income-statement?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch income statement');
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching income statement:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/reports" className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block">
            ← Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📊 Income Statement
          </h1>
          <p className="text-gray-600">
            Profit & Loss statement showing revenue and expenses
          </p>
        </div>

        {/* Date Range Filter */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Report Period</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                End Date
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div className="flex items-end">
              <button
                onClick={fetchReport}
                disabled={loading}
                className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? 'Loading...' : '🔄 Generate Report'}
              </button>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
            <h3 className="text-red-800 font-semibold mb-2">Error</h3>
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="space-y-4">
              <div className="h-6 bg-gray-200 rounded w-1/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/3"></div>
            </div>
          </div>
        )}

        {/* Report Content */}
        {!loading && report && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Total Revenue</div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(report.revenue.total_revenue)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.revenue.paid_invoice_count} paid invoices
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Total Expenses</div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(report.expenses.total_expenses)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.expenses.transaction_count} transactions
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Net Income</div>
                <div className={`text-2xl font-bold ${report.net_income >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                  {formatCurrency(report.net_income)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.profit_margin}% margin
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Collection Rate</div>
                <div className="text-2xl font-bold text-purple-600">
                  {report.collection_rate}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {formatCurrency(report.revenue.pending_amount)} pending
                </div>
              </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Revenue Breakdown Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Revenue Breakdown
                </h3>
                <ReportChart
                  type="doughnut"
                  data={prepareChartData(
                    ['Paid', 'Pending'],
                    [{
                      label: 'Revenue Status',
                      data: [report.revenue.paid_amount, report.revenue.pending_amount],
                      backgroundColor: [
                        'rgba(16, 185, 129, 0.8)',  // Green for paid
                        'rgba(245, 158, 11, 0.8)',   // Orange for pending
                      ],
                    }]
                  )}
                  height={250}
                />
              </div>

              {/* Top Expenses Chart */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Top 5 Expense Categories
                </h3>
                <ReportChart
                  type="bar"
                  data={prepareChartData(
                    report.expenses.top_categories.map(cat => cat.category),
                    [{
                      label: 'Expenses',
                      data: report.expenses.top_categories.map(cat => cat.amount),
                      backgroundColor: 'rgba(239, 68, 68, 0.8)',
                      borderColor: 'rgba(239, 68, 68, 1)',
                    }]
                  )}
                  height={250}
                />
              </div>
            </div>

            {/* Profit & Loss Chart */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Profit & Loss Overview
              </h3>
              <ReportChart
                type="bar"
                data={prepareChartData(
                  ['Revenue', 'Expenses', 'Net Income'],
                  [{
                    label: 'Amount (KES)',
                    data: [
                      report.revenue.total_revenue,
                      report.expenses.total_expenses,
                      report.net_income
                    ],
                    backgroundColor: [
                      'rgba(16, 185, 129, 0.8)',  // Green for revenue
                      'rgba(239, 68, 68, 0.8)',    // Red for expenses
                      report.net_income >= 0 ? 'rgba(59, 130, 246, 0.8)' : 'rgba(239, 68, 68, 0.8)', // Blue or Red for net income
                    ],
                  }]
                )}
                height={300}
              />
            </div>

            {/* Detailed Income Statement */}
            <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
              <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">
                  Income Statement Details
                </h2>
                <p className="text-sm text-gray-600">
                  Period: {new Date(report.period_start).toLocaleDateString()} - {new Date(report.period_end).toLocaleDateString()}
                </p>
              </div>

              <div className="p-6">
                {/* Revenue Section */}
                <div className="mb-8">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <span className="text-2xl mr-2">💰</span>
                    Revenue
                  </h3>
                  
                  <div className="space-y-3 ml-8">
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-700">Total Invoiced</span>
                      <span className="font-medium">{formatCurrency(report.revenue.invoiced_amount)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-700">Paid Amount</span>
                      <span className="font-medium text-green-600">{formatCurrency(report.revenue.paid_amount)}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-200">
                      <span className="text-gray-700">Pending Amount</span>
                      <span className="font-medium text-yellow-600">{formatCurrency(report.revenue.pending_amount)}</span>
                    </div>
                    <div className="flex justify-between items-center py-3 bg-green-50 px-4 rounded-lg">
                      <span className="font-bold text-gray-900">Total Revenue</span>
                      <span className="font-bold text-green-600 text-lg">{formatCurrency(report.revenue.total_revenue)}</span>
                    </div>
                  </div>
                </div>

                {/* Expenses Section */}
                <div className="mb-8">
                  <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                    <span className="text-2xl mr-2">💸</span>
                    Expenses by Category
                  </h3>
                  
                  <div className="space-y-3 ml-8">
                    {report.expenses.top_categories.map((cat) => (
                      <div key={cat.category} className="flex justify-between items-center py-2 border-b border-gray-200">
                        <div className="flex items-center">
                          <span className="text-gray-700">{cat.category}</span>
                          <span className="ml-2 text-xs bg-gray-100 px-2 py-1 rounded">
                            {cat.percentage}%
                          </span>
                        </div>
                        <span className="font-medium">{formatCurrency(cat.amount)}</span>
                      </div>
                    ))}
                    
                    <div className="flex justify-between items-center py-3 bg-red-50 px-4 rounded-lg">
                      <span className="font-bold text-gray-900">Total Expenses</span>
                      <span className="font-bold text-red-600 text-lg">{formatCurrency(report.expenses.total_expenses)}</span>
                    </div>
                  </div>
                </div>

                {/* Bottom Line */}
                <div className="border-t-2 border-gray-300 pt-6">
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-3 px-4 bg-gray-50 rounded-lg">
                      <span className="font-bold text-gray-900">Gross Profit</span>
                      <span className="font-bold text-lg">{formatCurrency(report.gross_profit)}</span>
                    </div>
                    
                    <div className="flex justify-between items-center py-4 px-4 bg-blue-50 rounded-lg border-2 border-blue-200">
                      <div>
                        <div className="font-bold text-blue-900 text-lg">Net Income</div>
                        <div className="text-sm text-blue-700">Profit Margin: {report.profit_margin}%</div>
                      </div>
                      <span className={`font-bold text-2xl ${report.net_income >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                        {formatCurrency(report.net_income)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Export Options */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Export Report</h3>
              <div className="flex flex-wrap gap-3">
                <button 
                  onClick={() => {
                    const exportData = report.expenses.top_categories.map(cat => ({
                      Category: cat.category,
                      Amount: cat.amount,
                      Percentage: `${cat.percentage}%`
                    }));
                    exportToExcel(
                      [
                        { 
                          Metric: 'Total Revenue', 
                          Value: report.revenue.total_revenue 
                        },
                        { 
                          Metric: 'Total Expenses', 
                          Value: report.expenses.total_expenses 
                        },
                        { 
                          Metric: 'Net Income', 
                          Value: report.net_income 
                        },
                        { 
                          Metric: 'Profit Margin', 
                          Value: `${report.profit_margin}%` 
                        },
                        ...exportData
                      ],
                      'Income Statement',
                      `income_statement_${report.period_start}_${report.period_end}.xlsx`
                    );
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  📊 Export to Excel
                </button>
                <button 
                  onClick={() => exportIncomeStatementPDF(report)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  📄 Export to PDF
                </button>
                <button 
                  onClick={() => {
                    const exportData = report.expenses.top_categories.map(cat => ({
                      Category: cat.category,
                      Amount: cat.amount,
                      Percentage: cat.percentage
                    }));
                    exportToCSV(
                      [
                        { Metric: 'Total Revenue', Value: report.revenue.total_revenue },
                        { Metric: 'Total Expenses', Value: report.expenses.total_expenses },
                        { Metric: 'Net Income', Value: report.net_income },
                        { Metric: 'Profit Margin', Value: report.profit_margin },
                        ...exportData
                      ],
                      `income_statement_${report.period_start}_${report.period_end}.csv`
                    );
                  }}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  📋 Export to CSV
                </button>
                <button
                  onClick={() => window.print()}
                  className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  🖨️ Print
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
