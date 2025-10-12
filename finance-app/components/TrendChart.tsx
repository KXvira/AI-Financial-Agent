'use client';

import { useEffect, useState } from 'react';
import ReportChart, { prepareChartData } from './ReportChart';

interface TrendData {
  period: string;
  revenue?: number;
  expenses?: number;
  change_pct?: number | null;
  trend?: string;
  invoice_count?: number;
  transaction_count?: number;
}

interface TrendResponse {
  period: string;
  months_included: number;
  overall_trend: string;
  data: TrendData[];
}

interface ComparisonData {
  period: string;
  current_month?: string;
  previous_month?: string;
  current_year?: number;
  previous_year?: number;
  current: {
    revenue: number;
    expenses: number;
    net_income: number;
    invoice_count: number;
  };
  previous: {
    revenue: number;
    expenses: number;
    net_income: number;
    invoice_count: number;
  };
  changes: {
    revenue_change_pct?: number;
    expense_change_pct?: number;
    net_income_change_pct?: number;
    revenue_growth_pct?: number;
    expense_growth_pct?: number;
    net_income_growth_pct?: number;
  };
}

export default function TrendChart() {
  const [revenueTrends, setRevenueTrends] = useState<TrendResponse | null>(null);
  const [expenseTrends, setExpenseTrends] = useState<TrendResponse | null>(null);
  const [momComparison, setMomComparison] = useState<ComparisonData | null>(null);
  const [yoyComparison, setYoyComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedMonths, setSelectedMonths] = useState(12);

  useEffect(() => {
    fetchTrendData();
  }, [selectedMonths]);

  const fetchTrendData = async () => {
    try {
      setLoading(true);
      
      // Fetch all trend data
      const [revenue, expenses, mom, yoy] = await Promise.all([
        fetch(`http://localhost:8000/api/reports/trends/revenue?months=${selectedMonths}`).then(r => r.json()),
        fetch(`http://localhost:8000/api/reports/trends/expenses?months=${selectedMonths}`).then(r => r.json()),
        fetch('http://localhost:8000/api/reports/comparison/mom').then(r => r.json()),
        fetch('http://localhost:8000/api/reports/comparison/yoy').then(r => r.json())
      ]);

      setRevenueTrends(revenue);
      setExpenseTrends(expenses);
      setMomComparison(mom);
      setYoyComparison(yoy);
    } catch (error) {
      console.error('Error fetching trend data:', error);
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

  const getTrendIcon = (trend: string) => {
    if (trend === 'up') return '📈';
    if (trend === 'down') return '📉';
    return '➡️';
  };

  const getTrendColor = (value: number) => {
    if (value > 5) return 'text-green-600';
    if (value < -5) return 'text-red-600';
    return 'text-gray-600';
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="bg-white rounded-lg shadow p-6 h-96"></div>
        <div className="bg-white rounded-lg shadow p-6 h-96"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Month Selector */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">📊 Trend Analysis</h3>
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Time Period:</label>
            <select
              value={selectedMonths}
              onChange={(e) => setSelectedMonths(Number(e.target.value))}
              className="px-3 py-1.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={3}>Last 3 Months</option>
              <option value={6}>Last 6 Months</option>
              <option value={12}>Last 12 Months</option>
              <option value={24}>Last 24 Months</option>
            </select>
          </div>
        </div>
      </div>

      {/* Revenue Trend Chart */}
      {revenueTrends && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">💰 Revenue Trend</h3>
              <p className="text-sm text-gray-600">
                Overall trend: {getTrendIcon(revenueTrends.overall_trend)} {revenueTrends.overall_trend}
              </p>
            </div>
          </div>
          
          <ReportChart
            type="line"
            data={prepareChartData(
              revenueTrends.data.map(d => d.period),
              [{
                label: 'Revenue',
                data: revenueTrends.data.map(d => d.revenue || 0),
                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                borderColor: 'rgba(34, 197, 94, 1)',
              }]
            )}
            height={300}
          />

          {/* Period Details */}
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            {revenueTrends.data.slice(-4).map((item, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-600">{item.period}</div>
                <div className="text-lg font-bold text-gray-900">
                  {formatCurrency(item.revenue || 0)}
                </div>
                {item.change_pct !== null && item.change_pct !== undefined && (
                  <div className={`text-sm font-medium ${getTrendColor(item.change_pct)}`}>
                    {item.change_pct > 0 ? '+' : ''}{item.change_pct.toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Expense Trend Chart */}
      {expenseTrends && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">💸 Expense Trend</h3>
              <p className="text-sm text-gray-600">
                Overall trend: {getTrendIcon(expenseTrends.overall_trend)} {expenseTrends.overall_trend}
              </p>
            </div>
          </div>
          
          <ReportChart
            type="line"
            data={prepareChartData(
              expenseTrends.data.map(d => d.period),
              [{
                label: 'Expenses',
                data: expenseTrends.data.map(d => d.expenses || 0),
                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                borderColor: 'rgba(239, 68, 68, 1)',
              }]
            )}
            height={300}
          />

          {/* Period Details */}
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            {expenseTrends.data.slice(-4).map((item, idx) => (
              <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                <div className="text-xs text-gray-600">{item.period}</div>
                <div className="text-lg font-bold text-gray-900">
                  {formatCurrency(item.expenses || 0)}
                </div>
                {item.change_pct !== null && item.change_pct !== undefined && (
                  <div className={`text-sm font-medium ${getTrendColor(item.change_pct)}`}>
                    {item.change_pct > 0 ? '+' : ''}{item.change_pct.toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Comparison Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Month-over-Month */}
        {momComparison && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📅 Month-over-Month Comparison
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600">Current Month</div>
                  <div className="font-bold text-gray-900">{momComparison.current_month}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Previous Month</div>
                  <div className="font-bold text-gray-900">{momComparison.previous_month}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Revenue:</span>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(momComparison.current.revenue)}</div>
                    <div className={`text-sm ${getTrendColor(momComparison.changes.revenue_change_pct || 0)}`}>
                      {momComparison.changes.revenue_change_pct && momComparison.changes.revenue_change_pct > 0 ? '+' : ''}
                      {momComparison.changes.revenue_change_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Expenses:</span>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(momComparison.current.expenses)}</div>
                    <div className={`text-sm ${getTrendColor(-(momComparison.changes.expense_change_pct || 0))}`}>
                      {momComparison.changes.expense_change_pct && momComparison.changes.expense_change_pct > 0 ? '+' : ''}
                      {momComparison.changes.expense_change_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                  <span className="text-gray-900 font-semibold">Net Income:</span>
                  <div className="text-right">
                    <div className="font-bold text-blue-600">{formatCurrency(momComparison.current.net_income)}</div>
                    <div className={`text-sm ${getTrendColor(momComparison.changes.net_income_change_pct || 0)}`}>
                      {momComparison.changes.net_income_change_pct && momComparison.changes.net_income_change_pct > 0 ? '+' : ''}
                      {momComparison.changes.net_income_change_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Year-over-Year */}
        {yoyComparison && (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              📈 Year-over-Year Comparison
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
                <div>
                  <div className="text-sm text-gray-600">Current Year</div>
                  <div className="font-bold text-gray-900">{yoyComparison.current_year}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-600">Previous Year</div>
                  <div className="font-bold text-gray-900">{yoyComparison.previous_year}</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Revenue Growth:</span>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(yoyComparison.current.revenue)}</div>
                    <div className={`text-sm ${getTrendColor(yoyComparison.changes.revenue_growth_pct || 0)}`}>
                      {yoyComparison.changes.revenue_growth_pct && yoyComparison.changes.revenue_growth_pct > 0 ? '+' : ''}
                      {yoyComparison.changes.revenue_growth_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Expense Growth:</span>
                  <div className="text-right">
                    <div className="font-bold">{formatCurrency(yoyComparison.current.expenses)}</div>
                    <div className={`text-sm ${getTrendColor(-(yoyComparison.changes.expense_growth_pct || 0))}`}>
                      {yoyComparison.changes.expense_growth_pct && yoyComparison.changes.expense_growth_pct > 0 ? '+' : ''}
                      {yoyComparison.changes.expense_growth_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="flex justify-between items-center pt-3 border-t border-gray-200">
                  <span className="text-gray-900 font-semibold">Net Income Growth:</span>
                  <div className="text-right">
                    <div className="font-bold text-purple-600">{formatCurrency(yoyComparison.current.net_income)}</div>
                    <div className={`text-sm ${getTrendColor(yoyComparison.changes.net_income_growth_pct || 0)}`}>
                      {yoyComparison.changes.net_income_growth_pct && yoyComparison.changes.net_income_growth_pct > 0 ? '+' : ''}
                      {yoyComparison.changes.net_income_growth_pct?.toFixed(1)}%
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
