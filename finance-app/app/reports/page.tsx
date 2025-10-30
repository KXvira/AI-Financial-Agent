'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { EmailStatusBadge } from '../../components/EmailStatusBadge';
import { EmailSetupModal } from '../../components/EmailSetupModal';
import { ScheduleReportModal } from '../../components/ScheduleReportModal';

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

interface Schedule {
  id: string;
  name: string;
  report_type: string;
  schedule: {
    frequency: string;
    time: string;
    day_of_week?: number;
    day_of_month?: number;
  };
  recipients: string[];
  enabled: boolean;
  last_run?: string;
  next_run?: string;
}

export default function ReportsPage() {
  const [reportTypes, setReportTypes] = useState<ReportType[]>([]);
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [schedulesLoading, setSchedulesLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showEmailSetup, setShowEmailSetup] = useState(false);
  const [showScheduleModal, setShowScheduleModal] = useState(false);

  useEffect(() => {
    fetchReportTypes();
    fetchSchedules();
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

  const fetchSchedules = async () => {
    try {
      setSchedulesLoading(true);
      const response = await fetch('http://localhost:8000/automation/schedules');
      
      if (!response.ok) {
        throw new Error('Failed to fetch schedules');
      }

      const data = await response.json();
      setSchedules(data.schedules || []);
    } catch (err) {
      console.error('Error fetching schedules:', err);
      setSchedules([]);
    } finally {
      setSchedulesLoading(false);
    }
  };

  const formatScheduleTime = (schedule: Schedule) => {
    const { frequency, time, day_of_week, day_of_month } = schedule.schedule;
    const daysOfWeek = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    
    if (frequency === 'daily') {
      return `Daily at ${time}`;
    } else if (frequency === 'weekly') {
      return `Every ${daysOfWeek[day_of_week || 0]} at ${time}`;
    } else if (frequency === 'monthly') {
      return `Monthly on day ${day_of_month} at ${time}`;
    } else if (frequency === 'quarterly') {
      return `Quarterly at ${time}`;
    }
    return `${frequency} at ${time}`;
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

        {/* Email Status Badge */}
        <div className="mb-6">
          <EmailStatusBadge 
            onSetupClick={() => setShowEmailSetup(true)}
            showTestButton={true}
          />
        </div>

        {/* Scheduled Reports Section */}
        <div className="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-6 border border-indigo-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-indigo-100 rounded-lg">
                <svg className="h-5 w-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-800">📅 Scheduled Reports</h3>
                <p className="text-sm text-gray-600">Automate report generation and email delivery</p>
              </div>
            </div>
            <button 
              onClick={() => setShowScheduleModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium"
            >
              + Schedule Report
            </button>
          </div>
          
          {schedulesLoading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : schedules.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {schedules.map((schedule, index) => {
                const borderColors = ['border-indigo-400', 'border-purple-400', 'border-green-400', 'border-blue-400', 'border-pink-400'];
                return (
                  <div key={schedule.id} className={`bg-white rounded-lg p-4 shadow-sm border-l-4 ${borderColors[index % borderColors.length]}`}>
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-700">{schedule.name}</h4>
                      {schedule.enabled ? (
                        <span className="inline-block px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Active</span>
                      ) : (
                        <span className="inline-block px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">Paused</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{formatScheduleTime(schedule)}</p>
                    <p className="text-xs text-gray-500 mb-1">
                      Recipients: {schedule.recipients.length}
                    </p>
                    {schedule.last_run ? (
                      <p className="text-xs text-gray-500">
                        Last sent: {new Date(schedule.last_run).toLocaleDateString()}
                      </p>
                    ) : (
                      <p className="text-xs text-gray-500">Last sent: Never</p>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-center py-8 border-2 border-dashed border-indigo-300 rounded-lg">
              <p className="text-gray-600 mb-2">📅 No scheduled reports yet</p>
              <p className="text-sm text-gray-500">Click "+ Schedule Report" to create your first automated report</p>
            </div>
          )}

          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              ✅ <span className="font-medium">Email service is configured</span> - Ready to schedule automated reports
            </div>
            <button
              onClick={() => setShowEmailSetup(true)}
              className="text-xs text-indigo-600 hover:text-indigo-800 underline"
            >
              View Email Settings
            </button>
          </div>
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

      {/* Email Setup Modal */}
      <EmailSetupModal 
        isOpen={showEmailSetup}
        onClose={() => setShowEmailSetup(false)}
      />

      {/* Schedule Report Modal */}
      <ScheduleReportModal
        isOpen={showScheduleModal}
        onClose={() => setShowScheduleModal(false)}
        reportTypes={reportTypes}
        onScheduleCreated={fetchSchedules}
      />
    </div>
  );
}
