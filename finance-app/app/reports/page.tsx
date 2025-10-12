'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

interface ReportType {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  requires_date_range: boolean;
  available_formats: string[];
  estimated_time: string;
}

interface ReportTypesResponse {
  report_types: ReportType[];
  total: number;
  categories: string[];
}

export default function ReportsPage() {
  const [reportTypes, setReportTypes] = useState<ReportType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchReportTypes();
  }, []);

  const fetchReportTypes = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/reports/types');
      
      if (!response.ok) {
        throw new Error('Failed to fetch report types');
      }

      const data: ReportTypesResponse = await response.json();
      setReportTypes(data.report_types);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching report types:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredReports = selectedCategory === 'all' 
    ? reportTypes 
    : reportTypes.filter(report => report.category === selectedCategory);

  const categories = ['all', ...Array.from(new Set(reportTypes.map(r => r.category)))];

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      financial: 'bg-blue-100 text-blue-800 border-blue-300',
      receivables: 'bg-green-100 text-green-800 border-green-300',
      analytics: 'bg-purple-100 text-purple-800 border-purple-300',
      all: 'bg-gray-100 text-gray-800 border-gray-300'
    };
    return colors[category] || colors.all;
  };

  const getReportLink = (reportId: string) => {
    const links: Record<string, string> = {
      income_statement: '/reports/income-statement',
      cash_flow: '/reports/cash-flow',
      ar_aging: '/reports/ar-aging',
      dashboard_metrics: '/reports/dashboard'
    };
    return links[reportId] || '/reports';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📊 Financial Reports
          </h1>
          <p className="text-gray-600">
            Generate comprehensive financial reports and analytics
          </p>
        </div>

        {/* Category Filters */}
        <div className="mb-6 flex flex-wrap gap-2">
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className={`px-4 py-2 rounded-lg border-2 font-medium transition-all ${
                selectedCategory === category
                  ? getCategoryColor(category) + ' border-current'
                  : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
              }`}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <span className="text-red-600 text-lg mr-2">⚠️</span>
              <div>
                <h3 className="font-semibold text-red-800">Error Loading Reports</h3>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
            <button
              onClick={fetchReportTypes}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-12 w-12 bg-gray-200 rounded-lg mb-4"></div>
                <div className="h-6 bg-gray-200 rounded mb-3"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Reports Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {/* Customer Statement Card */}
              <Link
                href="/reports/customer-statement"
                className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-blue-400 text-white"
              >
                <div className="text-4xl mb-4">👤</div>
                <h3 className="text-2xl font-bold mb-2">Customer Statement</h3>
                <p className="text-blue-100 mb-4">
                  Detailed transaction history and account status for individual customers
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="mr-1">📊</span>
                    Transaction history
                  </div>
                  <div className="flex items-center">
                    <span className="mr-1">💰</span>
                    Balance tracking
                  </div>
                  <div className="flex items-center">
                    <span className="mr-1">⏰</span>
                    Aging analysis
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-blue-600 py-2 rounded-lg hover:bg-blue-50 transition-colors font-medium">
                  View Statements →
                </button>
              </Link>

              {/* Reconciliation Report Card */}
              <Link
                href="/reports/reconciliation"
                className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-purple-400 text-white"
              >
                <div className="text-4xl mb-4">🔄</div>
                <h3 className="text-2xl font-bold mb-2">Reconciliation Report</h3>
                <p className="text-purple-100 mb-4">
                  Track payment matching status and identify reconciliation issues
                </p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center">
                    <span className="mr-1">✅</span>
                    Match rate tracking
                  </div>
                  <div className="flex items-center">
                    <span className="mr-1">⚠️</span>
                    Issue detection
                  </div>
                  <div className="flex items-center">
                    <span className="mr-1">📋</span>
                    Unmatched transactions
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-purple-600 py-2 rounded-lg hover:bg-purple-50 transition-colors font-medium">
                  View Report →
                </button>
              </Link>

              {/* Trend Analysis Card (Special Card) */}
              <Link
                href="/reports/trends"
                className="bg-gradient-to-br from-indigo-500 to-pink-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-indigo-400 text-white"
              >
                <div className="text-4xl mb-4">📈</div>
                <h3 className="text-xl font-bold mb-2">
                  Trend Analysis
                </h3>
                <p className="text-purple-100 text-sm mb-4">
                  Analyze revenue and expense trends over time with month-over-month and year-over-year comparisons
                </p>
                <div className="space-y-2 mb-4">
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">📊</span>
                    Visual trend charts
                  </div>
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">📅</span>
                    MoM & YoY comparisons
                  </div>
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">💡</span>
                    Actionable insights
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-purple-600 py-2 rounded-lg hover:bg-purple-50 transition-colors font-medium">
                  View Trends →
                </button>
              </Link>

              {/* Tax & VAT Summary Card (NEW - Phase 3) */}
              <Link
                href="/reports/tax-summary"
                className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-green-400 text-white"
              >
                <div className="text-4xl mb-4">📋</div>
                <h3 className="text-xl font-bold mb-2">
                  Tax & VAT Summary
                </h3>
                <p className="text-green-100 text-sm mb-4">
                  Complete VAT report with output VAT (sales) and input VAT (purchases) for tax compliance and filing
                </p>
                <div className="space-y-2 mb-4">
                  <div className="text-xs text-green-100 flex items-center">
                    <span className="mr-1">💰</span>
                    VAT by rate breakdown
                  </div>
                  <div className="text-xs text-green-100 flex items-center">
                    <span className="mr-1">📅</span>
                    Filing deadline tracking
                  </div>
                  <div className="text-xs text-green-100 flex items-center">
                    <span className="mr-1">✅</span>
                    Compliance status
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-green-600 py-2 rounded-lg hover:bg-green-50 transition-colors font-medium">
                  View Tax Report →
                </button>
              </Link>

              {/* Predictive Analytics Card (Phase 3) */}
              <Link
                href="/reports/predictive-analytics"
                className="bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-cyan-400 text-white"
              >
                <div className="text-4xl mb-4">🔮</div>
                <h3 className="text-xl font-bold mb-2">
                  Predictive Analytics
                </h3>
                <p className="text-cyan-100 text-sm mb-4">
                  AI-powered forecasting for revenue, expenses, and cash flow with confidence intervals and trend analysis
                </p>
                <div className="space-y-2 mb-4">
                  <div className="text-xs text-cyan-100 flex items-center">
                    <span className="mr-1">📈</span>
                    3-12 month forecasts
                  </div>
                  <div className="text-xs text-cyan-100 flex items-center">
                    <span className="mr-1">🎯</span>
                    95% confidence intervals
                  </div>
                  <div className="text-xs text-cyan-100 flex items-center">
                    <span className="mr-1">🔍</span>
                    Trend detection
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-cyan-600 py-2 rounded-lg hover:bg-cyan-50 transition-colors font-medium">
                  View Forecasts →
                </button>
              </Link>

              {/* AI Reports Card (Phase 3) */}
              <Link
                href="/reports/ai-reports"
                className="bg-gradient-to-br from-purple-500 to-fuchsia-600 rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-purple-400 text-white"
              >
                <div className="text-4xl mb-4">✨</div>
                <h3 className="text-xl font-bold mb-2">
                  AI-Powered Reports
                </h3>
                <p className="text-purple-100 text-sm mb-4">
                  Custom AI insights, anomaly detection, and natural language queries powered by Gemini AI
                </p>
                <div className="space-y-2 mb-4">
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">💡</span>
                    AI insights & recommendations
                  </div>
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">⚠️</span>
                    Anomaly detection
                  </div>
                  <div className="text-xs text-purple-100 flex items-center">
                    <span className="mr-1">💬</span>
                    Natural language queries
                  </div>
                </div>
                <button className="mt-4 w-full bg-white text-purple-600 py-2 rounded-lg hover:bg-purple-50 transition-colors font-medium">
                  Ask AI →
                </button>
              </Link>

              {filteredReports.map(report => (
                <Link
                  key={report.id}
                  href={getReportLink(report.id)}
                  className="bg-white rounded-lg shadow-md hover:shadow-xl transition-all transform hover:-translate-y-1 p-6 border border-gray-200"
                >
                  {/* Icon */}
                  <div className="text-4xl mb-4">{report.icon}</div>
                  
                  {/* Title */}
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {report.name}
                  </h3>
                  
                  {/* Description */}
                  <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                    {report.description}
                  </p>
                  
                  {/* Metadata */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(report.category)}`}>
                        {report.category}
                      </span>
                      <span className="text-xs text-gray-500">
                        ⏱️ {report.estimated_time}
                      </span>
                    </div>
                    
                    {report.requires_date_range && (
                      <div className="text-xs text-gray-500 flex items-center">
                        <span className="mr-1">📅</span>
                        Date range required
                      </div>
                    )}
                    
                    {/* Available Formats */}
                    <div className="flex flex-wrap gap-1">
                      {report.available_formats.map(format => (
                        <span
                          key={format}
                          className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded"
                        >
                          {format.toUpperCase()}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  {/* View Button */}
                  <button className="mt-4 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                    Generate Report →
                  </button>
                </Link>
              ))}
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                📈 Quick Stats
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">
                    {reportTypes.length}
                  </div>
                  <div className="text-sm text-gray-600">Available Reports</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {categories.length - 1}
                  </div>
                  <div className="text-sm text-gray-600">Categories</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-purple-600">4</div>
                  <div className="text-sm text-gray-600">Export Formats</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">
                    &lt;3s
                  </div>
                  <div className="text-sm text-gray-600">Avg Generation</div>
                </div>
              </div>
            </div>

            {/* Info Banner */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start">
                <span className="text-blue-600 text-lg mr-2">💡</span>
                <div>
                  <h3 className="font-semibold text-blue-800 mb-1">
                    Pro Tip
                  </h3>
                  <p className="text-blue-700 text-sm">
                    All reports are generated in real-time from your latest financial data. 
                    You can export reports in multiple formats including PDF, Excel, and CSV.
                  </p>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
