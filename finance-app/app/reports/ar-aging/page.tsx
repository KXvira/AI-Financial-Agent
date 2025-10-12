'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';

interface Invoice {
  invoice_id: string;
  invoice_number: string;
  customer_name: string;
  amount: number;
  date_issued: string;
  days_outstanding: number;
}

interface AgingBucket {
  bucket_name: string;
  min_days: number;
  max_days: number | null;
  invoice_count: number;
  total_amount: number;
  percentage: number;
  invoices: Invoice[];
}

interface TopCustomer {
  customer_name: string;
  outstanding_amount: number;
  invoice_count: number;
}

interface ARAgingReport {
  report_type: string;
  report_name: string;
  as_of_date: string;
  generated_at: string;
  currency: string;
  total_outstanding: number;
  total_invoices: number;
  buckets: AgingBucket[];
  current_percentage: number;
  overdue_percentage: number;
  collection_risk_score: number;
  top_customers: TopCustomer[];
}

export default function ARAgingPage() {
  const [report, setReport] = useState<ARAgingReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `http://localhost:8000/api/reports/ar-aging?as_of_date=${asOfDate}`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch AR aging report');
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching AR aging:', err);
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

  const getRiskColor = (score: number) => {
    if (score < 30) return 'text-green-600';
    if (score < 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRiskLabel = (score: number) => {
    if (score < 30) return 'Low Risk';
    if (score < 60) return 'Medium Risk';
    return 'High Risk';
  };

  const getBucketColor = (bucketName: string) => {
    if (bucketName.includes('Current')) return 'bg-green-50 border-green-300';
    if (bucketName.includes('31-60')) return 'bg-yellow-50 border-yellow-300';
    if (bucketName.includes('61-90')) return 'bg-orange-50 border-orange-300';
    return 'bg-red-50 border-red-300';
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
            📅 Accounts Receivable Aging
          </h1>
          <p className="text-gray-600">
            Outstanding invoices grouped by age
          </p>
        </div>

        {/* Date Filter */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">As Of Date</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Report Date
              </label>
              <input
                type="date"
                value={asOfDate}
                onChange={(e) => setAsOfDate(e.target.value)}
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
                <div className="text-sm text-gray-600 mb-1">Total Outstanding</div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(report.total_outstanding)}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {report.total_invoices} invoices
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Current (0-30)</div>
                <div className="text-2xl font-bold text-green-600">
                  {report.current_percentage}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Of total outstanding
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Overdue (31+)</div>
                <div className="text-2xl font-bold text-orange-600">
                  {report.overdue_percentage}%
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Needs attention
                </div>
              </div>
              
              <div className="bg-white rounded-lg shadow p-6">
                <div className="text-sm text-gray-600 mb-1">Collection Risk</div>
                <div className={`text-2xl font-bold ${getRiskColor(report.collection_risk_score)}`}>
                  {report.collection_risk_score}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {getRiskLabel(report.collection_risk_score)}
                </div>
              </div>
            </div>

            {/* Aging Buckets */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Aging Analysis
              </h2>
              
              <div className="space-y-4">
                {report.buckets.map((bucket) => (
                  <div
                    key={bucket.bucket_name}
                    className={`p-4 rounded-lg border-2 ${getBucketColor(bucket.bucket_name)}`}
                  >
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-gray-900 text-lg">
                          {bucket.bucket_name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {bucket.invoice_count} invoices • {bucket.percentage}% of total
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900">
                          {formatCurrency(bucket.total_amount)}
                        </div>
                      </div>
                    </div>
                    
                    {/* Progress Bar */}
                    {report.total_outstanding > 0 && (
                      <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
                        <div
                          className="bg-blue-600 h-3 rounded-full transition-all"
                          style={{ width: `${bucket.percentage}%` }}
                        ></div>
                      </div>
                    )}
                    
                    {/* Invoice Details */}
                    {bucket.invoices.length > 0 && (
                      <div className="mt-3 space-y-2">
                        <div className="text-sm font-medium text-gray-700 mb-2">
                          Top Invoices:
                        </div>
                        {bucket.invoices.slice(0, 5).map((invoice) => (
                          <div
                            key={invoice.invoice_id}
                            className="flex justify-between items-center p-2 bg-white rounded text-sm"
                          >
                            <div>
                              <span className="font-medium text-gray-900">
                                {invoice.invoice_number}
                              </span>
                              <span className="text-gray-600 ml-2">
                                • {invoice.customer_name}
                              </span>
                              <span className="text-gray-500 ml-2">
                                • {invoice.days_outstanding} days
                              </span>
                            </div>
                            <span className="font-bold text-gray-900">
                              {formatCurrency(invoice.amount)}
                            </span>
                          </div>
                        ))}
                        {bucket.invoices.length > 5 && (
                          <div className="text-sm text-gray-500 text-center">
                            + {bucket.invoices.length - 5} more invoices
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Top Customers with Outstanding */}
            <div className="bg-white rounded-lg shadow p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <span className="text-2xl mr-2">👥</span>
                Top Customers by Outstanding Balance
              </h2>
              
              {report.top_customers.length > 0 ? (
                <div className="space-y-3">
                  {report.top_customers.map((customer, index) => {
                    const percentage = (customer.outstanding_amount / report.total_outstanding) * 100;
                    return (
                      <div key={customer.customer_name} className="p-4 bg-gray-50 rounded-lg">
                        <div className="flex justify-between items-center mb-2">
                          <div className="flex items-center">
                            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold mr-3">
                              {index + 1}
                            </div>
                            <div>
                              <div className="font-bold text-gray-900">
                                {customer.customer_name}
                              </div>
                              <div className="text-sm text-gray-600">
                                {customer.invoice_count} outstanding {customer.invoice_count === 1 ? 'invoice' : 'invoices'}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="text-xl font-bold text-red-600">
                              {formatCurrency(customer.outstanding_amount)}
                            </div>
                            <div className="text-xs text-gray-500">
                              {percentage.toFixed(1)}% of total
                            </div>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-red-500 h-2 rounded-full transition-all"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No outstanding balances found
                </div>
              )}
            </div>

            {/* Collection Risk Alert */}
            {report.collection_risk_score > 50 && (
              <div className="bg-red-50 border border-red-300 rounded-lg p-6 mb-6">
                <h3 className="font-semibold text-red-900 mb-2 flex items-center">
                  <span className="text-xl mr-2">⚠️</span>
                  High Collection Risk
                </h3>
                <p className="text-red-700 mb-3">
                  Your collection risk score is {report.collection_risk_score}, indicating a significant 
                  portion of receivables are overdue. Consider the following actions:
                </p>
                <ul className="list-disc list-inside text-red-700 space-y-1">
                  <li>Contact customers with overdue invoices</li>
                  <li>Review payment terms and credit policies</li>
                  <li>Consider offering early payment discounts</li>
                  <li>Implement automated payment reminders</li>
                </ul>
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
