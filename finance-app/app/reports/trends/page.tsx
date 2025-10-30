'use client';

import Link from 'next/link';
import TrendChart from '@/components/TrendChart';

export default function TrendsPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link href="/reports" className="text-blue-600 hover:text-blue-800 text-sm mb-2 inline-block">
            ← Back to Reports
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            📈 Trend Analysis & Forecasting
          </h1>
          <p className="text-gray-600">
            Analyze historical performance and identify trends over time
          </p>
        </div>

        {/* Trend Charts */}
        <TrendChart />

        {/* Info Banner */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="text-xl mr-2">💡</span>
            Understanding Your Trends
          </h3>
          <div className="text-blue-800 space-y-2 text-sm">
            <p>
              <strong>Revenue Trends:</strong> Track how your income has changed over time. An upward trend (📈) indicates growth,
              while a downward trend (📉) may require attention.
            </p>
            <p>
              <strong>Expense Trends:</strong> Monitor spending patterns. Ideally, expenses should remain stable or decrease
              while revenue grows to improve profitability.
            </p>
            <p>
              <strong>Month-over-Month:</strong> Short-term comparison helps identify immediate changes and seasonal patterns.
            </p>
            <p>
              <strong>Year-over-Year:</strong> Long-term comparison shows business growth trajectory and helps with annual planning.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
