// app/page.tsx
'use client';

import StatCard from '../components/StatCard';
import Link from 'next/link';
import { useAuth, withAuth } from '../contexts/AuthContext';
import { useDashboard, formatCurrency, formatPercentage } from '../hooks/useDashboard';
import { SystemStatusWidget } from '../components/SystemStatusWidget';
import BudgetWidget from '../components/BudgetWidget';

function Dashboard() {
  const { user } = useAuth();
  const { data: dashboardData, loading, error, refetch } = useDashboard(30);

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-1">
            Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!
          </h1>
          <p className="text-sm text-gray-500">
            Overview of {user?.business_name ? `${user.business_name}'s` : 'your'} finances
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-500">Role</div>
          <div className="font-medium capitalize text-blue-600">{user?.role}</div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white shadow-md rounded-lg p-6 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/4"></div>
            </div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-600 text-sm">⚠️ {error}</p>
          <button
            onClick={refetch}
            className="mt-2 text-sm text-red-600 underline hover:text-red-700"
          >
            Retry
          </button>
        </div>
      )}

      {/* Stats Cards with Real Data */}
      {!loading && dashboardData && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <StatCard
              title="Total Invoices"
              amount={formatCurrency(dashboardData.statistics.total_invoices)}
              change={formatPercentage(dashboardData.statistics.invoices_change_percent)}
              isPositive={dashboardData.statistics.invoices_change_percent >= 0}
            />
            <StatCard
              title="Payments Received"
              amount={formatCurrency(dashboardData.statistics.payments_received)}
              change={formatPercentage(dashboardData.statistics.payments_change_percent)}
              isPositive={dashboardData.statistics.payments_change_percent >= 0}
            />
            <StatCard
              title="Outstanding Balance"
              amount={formatCurrency(dashboardData.statistics.outstanding_balance)}
              change={formatPercentage(dashboardData.statistics.outstanding_change_percent)}
              isPositive={dashboardData.statistics.outstanding_change_percent <= 0}
            />
            <StatCard
              title="Daily Cash Flow"
              amount={formatCurrency(dashboardData.statistics.daily_cash_flow)}
              change={formatPercentage(dashboardData.statistics.cash_flow_change_percent)}
              isPositive={dashboardData.statistics.cash_flow_change_percent >= 0}
            />
          </div>

          {/* System Status Widget */}
          <div className="mb-6">
            <SystemStatusWidget />
          </div>

          {/* Budget Widget */}
          <div className="mb-6">
            <BudgetWidget />
          </div>
        </>
      )}

      {/* AI Insights Widget */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 mb-6 border border-blue-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">AI Financial Insights</h3>
              <p className="text-sm text-gray-600">Get intelligent analysis of your financial data</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Link 
              href="/ai-insights"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Open AI Chat
            </Link>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">💡 Quick Insights</h4>
            <p className="text-sm text-gray-600">Ask AI about your transaction patterns, cash flow, and financial health</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">📊 Smart Analysis</h4>
            <p className="text-sm text-gray-600">Get automated analysis of invoices, payments, and financial trends</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm">
            <h4 className="font-medium text-gray-700 mb-2">🤖 AI Assistant</h4>
            <p className="text-sm text-gray-600">Chat with our AI to get answers about your financial data</p>
          </div>
        </div>
      </div>

      <div className="bg-white shadow-md rounded-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Recent Payments</h2>
          <Link href="/payments/list" className="text-blue-600 hover:underline text-sm">
            View all
          </Link>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm text-left">
            <thead className="text-gray-500 bg-gray-50">
              <tr>
                <th className="px-4 py-2">Reference</th>
                <th className="px-4 py-2">Client</th>
                <th className="px-4 py-2">Amount</th>
                <th className="px-4 py-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    Loading payments...
                  </td>
                </tr>
              )}
              {!loading && dashboardData && dashboardData.recent_payments.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-4 py-8 text-center text-gray-500">
                    No recent payments found
                  </td>
                </tr>
              )}
              {!loading && dashboardData && dashboardData.recent_payments.map((payment) => (
                <tr key={payment.reference} className="hover:bg-gray-50 transition">
                  <td className="px-4 py-2 font-medium text-blue-600">
                    <Link href={`/payments/${payment.reference}`} className="hover:underline">
                      {payment.reference}
                    </Link>
                  </td>
                  <td className="px-4 py-2">{payment.client}</td>
                  <td className="px-4 py-2">
                    {formatCurrency(payment.amount, payment.currency)}
                  </td>
                  <td className="px-4 py-2">
                    {new Date(payment.date).toLocaleDateString('en-KE')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default withAuth(Dashboard);


