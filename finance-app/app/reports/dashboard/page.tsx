'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import StatCard from '@/components/StatCard';
import ReportChart, { prepareChartData } from '@/components/ReportChart';
import { exportDashboardMetricsExcel, exportToCSV, exportToPDF, formatDataForExport } from '@/utils/exportUtils';

interface DashboardMetrics {
  generated_at: string;
  total_revenue: number;
  revenue_trend: string;
  revenue_change_pct: number;
  total_invoices: number;
  paid_invoices: number;
  pending_invoices: number;
  overdue_invoices: number;
  average_invoice_value: number;
  total_customers: number;
  active_customers: number;
  revenue_per_customer: number;
  total_outstanding: number;
  collection_rate: number;
  dso: number;
  total_expenses: number;
  top_expense_category: string;
  expense_trend: string;
  net_income: number;
  profit_margin: number;
  transaction_count: number;
  reconciled_transactions: number;
  reconciliation_rate: number;
}

export default function DashboardMetricsPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/reports/dashboard-metrics');
      
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard metrics');
      }

      const data = await response.json();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return '📈';
    if (trend === 'down') return '📉';
    return '➡️';
  };

  const getTrendColor = (trend: string, isPositiveGood: boolean = true) => {
    if (trend === 'stable') return 'text-gray-600';
    const isGood = (trend === 'up' && isPositiveGood) || (trend === 'down' && !isPositiveGood);
    return isGood ? 'text-green-600' : 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                <div key={i} className="bg-white rounded-lg shadow p-6 h-32"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <h3 className="text-red-800 font-semibold mb-2">Error Loading Metrics</h3>
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={fetchMetrics}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <Link href="/reports" className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block">
              ← Back to Reports
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">
              📈 Dashboard Metrics
            </h1>
            <p className="text-gray-600 text-sm mt-1">
              Last updated: {new Date(metrics.generated_at).toLocaleString()}
            </p>
          </div>
          <button
            onClick={fetchMetrics}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Chart Visualizations */}
        <div className="mb-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Visual Analytics</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Revenue vs Expenses vs Net Income */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Financial Overview
              </h3>
              <ReportChart
                type="bar"
                data={prepareChartData(
                  ['Revenue', 'Expenses', 'Net Income'],
                  [{
                    label: 'Amount',
                    data: [
                      metrics.total_revenue,
                      metrics.total_expenses,
                      metrics.net_income
                    ],
                    backgroundColor: [
                      'rgba(34, 197, 94, 0.8)',
                      'rgba(239, 68, 68, 0.8)',
                      metrics.net_income >= 0 ? 'rgba(59, 130, 246, 0.8)' : 'rgba(239, 68, 68, 0.8)'
                    ],
                  }]
                )}
                height={300}
              />
            </div>

            {/* Invoice Status Distribution */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Invoice Status
              </h3>
              <ReportChart
                type="doughnut"
                data={prepareChartData(
                  ['Paid', 'Pending', 'Overdue'],
                  [{
                    label: '',
                    data: [
                      metrics.paid_invoices,
                      metrics.pending_invoices,
                      metrics.overdue_invoices
                    ],
                    backgroundColor: [
                      'rgba(34, 197, 94, 0.8)',   // Green for Paid
                      'rgba(59, 130, 246, 0.8)',  // Blue for Pending
                      'rgba(239, 68, 68, 0.8)',   // Red for Overdue
                    ],
                  }]
                )}
                height={300}
              />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Collection Performance */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Collection Metrics
              </h3>
              <ReportChart
                type="bar"
                data={prepareChartData(
                  ['Collection Rate', 'Reconciliation Rate', 'Target (85%)'],
                  [{
                    label: 'Percentage',
                    data: [
                      metrics.collection_rate,
                      metrics.reconciliation_rate,
                      85
                    ],
                    backgroundColor: [
                      metrics.collection_rate >= 85 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(234, 179, 8, 0.8)',
                      metrics.reconciliation_rate >= 90 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(234, 179, 8, 0.8)',
                      'rgba(156, 163, 175, 0.3)'
                    ],
                  }]
                )}
                height={300}
              />
            </div>

            {/* Customer Activity */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Customer Base
              </h3>
              <ReportChart
                type="doughnut"
                data={prepareChartData(
                  ['Active', 'Inactive'],
                  [{
                    label: '',
                    data: [
                      metrics.active_customers,
                      metrics.total_customers - metrics.active_customers
                    ],
                    backgroundColor: [
                      'rgba(34, 197, 94, 0.8)',   // Green for Active
                      'rgba(156, 163, 175, 0.8)', // Gray for Inactive
                    ],
                  }]
                )}
                height={300}
              />
            </div>
          </div>
        </div>

        {/* Export Options */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">Export Dashboard</h3>
          <div className="flex flex-wrap gap-3">
            <button 
              onClick={() => exportDashboardMetricsExcel(metrics)}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              📊 Export to Excel
            </button>
            <button 
              onClick={() => {
                const data = [{
                  'Total Revenue': metrics.total_revenue,
                  'Total Expenses': metrics.total_expenses,
                  'Net Income': metrics.net_income,
                  'Profit Margin': `${metrics.profit_margin}%`,
                  'Collection Rate': `${metrics.collection_rate}%`,
                  'DSO': metrics.dso,
                  'Total Invoices': metrics.total_invoices,
                  'Paid': metrics.paid_invoices,
                  'Pending': metrics.pending_invoices,
                  'Overdue': metrics.overdue_invoices,
                  'Total Customers': metrics.total_customers,
                  'Active Customers': metrics.active_customers,
                  'Reconciliation Rate': `${metrics.reconciliation_rate}%`
                }];
                exportToPDF(
                  'Dashboard Metrics Summary',
                  data,
                  Object.keys(data[0]),
                  'Dashboard_Metrics.pdf'
                );
              }}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              📄 Export to PDF
            </button>
            <button 
              onClick={() => {
                const data = [formatDataForExport(metrics)];
                exportToCSV(data, 'Dashboard_Metrics');
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

        {/* Summary Banner */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
          <h2 className="text-2xl font-bold mb-4">📊 Financial Health Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div className="text-sm opacity-90 mb-1">Profitability</div>
              <div className="text-3xl font-bold">{metrics.profit_margin}%</div>
              <div className="text-sm opacity-90">
                {metrics.profit_margin > 20 ? 'Excellent' : metrics.profit_margin > 15 ? 'Good' : 'Fair'}
              </div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Collection Efficiency</div>
              <div className="text-3xl font-bold">{metrics.collection_rate}%</div>
              <div className="text-sm opacity-90">
                {metrics.collection_rate > 85 ? 'Excellent' : metrics.collection_rate > 75 ? 'Good' : 'Needs improvement'}
              </div>
            </div>
            <div>
              <div className="text-sm opacity-90 mb-1">Cash Flow</div>
              <div className="text-3xl font-bold">
                {metrics.net_income > 0 ? '+' : ''}{formatCurrency(metrics.net_income)}
              </div>
              <div className="text-sm opacity-90">
                {metrics.net_income > 0 ? 'Positive' : 'Negative'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
