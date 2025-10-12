'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

interface CashFlowInflows {
  total_inflows: number;
  customer_payments: number;
  other_income: number;
  transaction_count: number;
}

interface CashFlowOutflows {
  total_outflows: number;
  by_category: Record<string, number>;
  transaction_count: number;
}

interface CashFlowReport {
  report_type: string;
  report_name: string;
  period_start: string;
  period_end: string;
  generated_at: string;
  currency: string;
  inflows: CashFlowInflows;
  outflows: CashFlowOutflows;
  net_cash_flow: number;
  opening_balance: number;
  closing_balance: number;
  burn_rate: number | null;
  runway_months: number | null;
}

export default function CashFlowPage() {
  const [report, setReport] = useState<CashFlowReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/api/reports/cash-flow?start_date=${startDate}&end_date=${endDate}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch cash flow report');
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching cash flow:', err);
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/reports" className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block">
            ← Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            💰 Cash Flow Statement
          </h1>
          <p className="text-gray-600">
            Track cash inflows and outflows during the period
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
                className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400"
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
            </div>
          </div>
        )}

        {/* Report Content */}
        {!loading && report && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Total Inflows</div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(report.inflows.total_inflows)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.inflows.transaction_count} transactions
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Total Outflows</div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(report.outflows.total_outflows)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.outflows.transaction_count} transactions
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Net Cash Flow</div>
                <div className={`text-2xl font-bold ${report.net_cash_flow >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                  {report.net_cash_flow >= 0 ? '+' : ''}{formatCurrency(report.net_cash_flow)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.net_cash_flow >= 0 ? 'Positive' : 'Negative'} flow
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Closing Balance</div>
                <div className="text-2xl font-bold text-purple-600">
                  {formatCurrency(report.closing_balance)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Period end
                </div>
              </div>
            </div>

            {/* Cash Flow Waterfall */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Cash Flow Summary
              </h2>
              
              <div className="space-y-4">
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <span className="font-medium text-gray-700">Opening Balance</span>
                  <span className="font-bold text-lg">{formatCurrency(report.opening_balance)}</span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg border-l-4 border-green-500">
                  <div>
                    <div className="font-medium text-gray-900">+ Cash Inflows</div>
                    <div className="text-sm text-gray-600">{report.inflows.transaction_count} transactions</div>
                  </div>
                  <span className="font-bold text-lg text-green-600">
                    +{formatCurrency(report.inflows.total_inflows)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-red-50 rounded-lg border-l-4 border-red-500">
                  <div>
                    <div className="font-medium text-gray-900">- Cash Outflows</div>
                    <div className="text-sm text-gray-600">{report.outflows.transaction_count} transactions</div>
                  </div>
                  <span className="font-bold text-lg text-red-600">
                    -{formatCurrency(report.outflows.total_outflows)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg border-2 border-blue-300">
                  <div>
                    <div className="font-bold text-blue-900 text-lg">Net Cash Flow</div>
                    <div className="text-sm text-blue-700">
                      {report.net_cash_flow >= 0 ? 'Surplus' : 'Deficit'}
                    </div>
                  </div>
                  <span className={`font-bold text-2xl ${report.net_cash_flow >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                    {report.net_cash_flow >= 0 ? '+' : ''}{formatCurrency(report.net_cash_flow)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center p-4 bg-purple-50 rounded-lg">
                  <span className="font-bold text-gray-900">Closing Balance</span>
                  <span className="font-bold text-xl text-purple-600">
                    {formatCurrency(report.closing_balance)}
                  </span>
                </div>
              </div>
            </div>

            {/* Inflows Breakdown */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-2">💵</span>
                Cash Inflows Breakdown
              </h2>
              
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <span className="text-gray-700">Customer Payments</span>
                  <span className="font-bold text-green-600">
                    {formatCurrency(report.inflows.customer_payments)}
                  </span>
                </div>
                
                {report.inflows.other_income > 0 && (
                  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <span className="text-gray-700">Other Income</span>
                    <span className="font-bold text-green-600">
                      {formatCurrency(report.inflows.other_income)}
                    </span>
                  </div>
                )}
                
                <div className="flex justify-between items-center p-3 bg-green-100 rounded-lg border border-green-300">
                  <span className="font-bold text-gray-900">Total Inflows</span>
                  <span className="font-bold text-lg text-green-600">
                    {formatCurrency(report.inflows.total_inflows)}
                  </span>
                </div>
              </div>
            </div>

            {/* Outflows by Category */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-2">💸</span>
                Cash Outflows by Category
              </h2>
              
              <div className="space-y-2">
                {Object.entries(report.outflows.by_category)
                  .sort(([, a], [, b]) => b - a)
                  .map(([category, amount]) => {
                    const percentage = (amount / report.outflows.total_outflows) * 100;
                    return (
                      <div key={category} className="p-3 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-gray-700 font-medium">{category}</span>
                          <span className="font-bold">{formatCurrency(amount)}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-red-500 h-2 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {percentage.toFixed(1)}% of total outflows
                        </div>
                      </div>
                    );
                  })}
                
                <div className="flex justify-between items-center p-4 bg-red-100 rounded-lg border border-red-300 mt-4">
                  <span className="font-bold text-gray-900">Total Outflows</span>
                  <span className="font-bold text-lg text-red-600">
                    {formatCurrency(report.outflows.total_outflows)}
                  </span>
                </div>
              </div>
            </div>

            {/* Burn Rate Alert (if negative cash flow) */}
            {report.burn_rate && report.runway_months && (
              <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-yellow-900 mb-2 flex items-center">
                  <span className="text-xl mr-2">⚠️</span>
                  Cash Burn Alert
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm text-yellow-700">Monthly Burn Rate</div>
                    <div className="text-2xl font-bold text-yellow-900">
                      {formatCurrency(report.burn_rate)}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-yellow-700">Runway Remaining</div>
                    <div className="text-2xl font-bold text-yellow-900">
                      {report.runway_months.toFixed(1)} months
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Export Options */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Export Report</h3>
              <div className="flex flex-wrap gap-3">
                <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                  📊 Export to Excel
                </button>
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                  📄 Export to PDF
                </button>
                <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
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
