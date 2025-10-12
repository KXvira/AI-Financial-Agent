"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import Chart from "@/components/Chart";
import StatCard from "@/components/StatCard";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Calendar,
  AlertCircle,
  Download,
  RefreshCw,
  Activity,
} from "lucide-react";

interface ForecastPoint {
  month: string;
  predicted_value: number;
  lower_bound?: number;
  upper_bound?: number;
  confidence?: number;
}

interface TrendAnalysis {
  trend: "increasing" | "decreasing" | "stable";
  average_growth_rate: number;
  volatility: number;
  confidence: string;
}

interface ForecastData {
  forecast: ForecastPoint[];
  historical: {
    average: number;
    std_dev: number;
    trend: string;
    months_analyzed: number;
  };
  trend_analysis: TrendAnalysis;
  accuracy_metrics: {
    method: string;
    confidence_level: number;
  };
}

interface CashFlowForecast {
  month: string;
  predicted_revenue: number;
  predicted_expenses: number;
  predicted_cash_flow: number;
  lower_bound?: number;
  upper_bound?: number;
}

export default function PredictiveAnalyticsPage() {
  const [monthsAhead, setMonthsAhead] = useState(6);
  const [includeConfidence, setIncludeConfidence] = useState(true);
  const [revenueData, setRevenueData] = useState<ForecastData | null>(null);
  const [expenseData, setExpenseData] = useState<ForecastData | null>(null);
  const [cashFlowData, setCashFlowData] = useState<{
    forecast: CashFlowForecast[];
    summary: any;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"revenue" | "expenses" | "cashflow">("revenue");

  useEffect(() => {
    fetchForecasts();
  }, [monthsAhead, includeConfidence]);

  const fetchForecasts = async () => {
    setLoading(true);
    setError(null);

    try {
      const [revenueRes, expenseRes, cashFlowRes] = await Promise.all([
        fetch(
          `http://localhost:8000/reports/predictive/revenue-forecast?months_ahead=${monthsAhead}&include_confidence=${includeConfidence}`
        ),
        fetch(
          `http://localhost:8000/reports/predictive/expense-forecast?months_ahead=${monthsAhead}&include_confidence=${includeConfidence}`
        ),
        fetch(
          `http://localhost:8000/reports/predictive/cash-flow-forecast?months_ahead=${monthsAhead}&include_confidence=${includeConfidence}`
        ),
      ]);

      const [revenue, expense, cashFlow] = await Promise.all([
        revenueRes.json(),
        expenseRes.json(),
        cashFlowRes.json(),
      ]);

      if (revenue.error) {
        setError(revenue.error);
      } else {
        setRevenueData(revenue);
      }

      if (!expense.error) {
        setExpenseData(expense);
      }

      if (!cashFlow.error) {
        setCashFlowData(cashFlow);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch forecasts");
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat("en-KE", {
      style: "currency",
      currency: "KES",
      minimumFractionDigits: 0,
    }).format(value);
  };

  const getTrendIcon = (trend?: string) => {
    if (!trend) return <Activity className="w-5 h-5 text-gray-500" />;
    if (trend === "increasing") return <TrendingUp className="w-5 h-5 text-green-500" />;
    if (trend === "decreasing") return <TrendingDown className="w-5 h-5 text-red-500" />;
    return <Activity className="w-5 h-5 text-yellow-500" />;
  };

  const getTrendColor = (trend?: string) => {
    if (!trend) return "text-gray-600";
    if (trend === "increasing") return "text-green-600";
    if (trend === "decreasing") return "text-red-600";
    return "text-yellow-600";
  };

  const exportToCSV = () => {
    let data: any[] = [];
    let filename = "";

    if (activeTab === "revenue" && revenueData) {
      data = revenueData.forecast;
      filename = "revenue-forecast.csv";
    } else if (activeTab === "expenses" && expenseData) {
      data = expenseData.forecast;
      filename = "expense-forecast.csv";
    } else if (activeTab === "cashflow" && cashFlowData) {
      data = cashFlowData.forecast;
      filename = "cash-flow-forecast.csv";
    }

    if (data.length === 0) return;

    const headers = Object.keys(data[0]).join(",");
    const rows = data.map((row) => Object.values(row).join(","));
    const csv = [headers, ...rows].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
  };

  const prepareChartData = () => {
    let data: ForecastData | null = null;
    let title = "";

    if (activeTab === "revenue") {
      data = revenueData;
      title = "Revenue Forecast";
    } else if (activeTab === "expenses") {
      data = expenseData;
      title = "Expense Forecast";
    }

    if (!data || data.forecast.length === 0) return null;

    const labels = data.forecast.map((f) => f.month);
    const values = data.forecast.map((f) => f.predicted_value);
    const lowerBounds = includeConfidence
      ? data.forecast.map((f) => f.lower_bound || 0)
      : [];
    const upperBounds = includeConfidence
      ? data.forecast.map((f) => f.upper_bound || 0)
      : [];

    const datasets = [
      {
        label: "Predicted",
        data: values,
        borderColor: activeTab === "revenue" ? "rgb(34, 197, 94)" : "rgb(239, 68, 68)",
        backgroundColor:
          activeTab === "revenue" ? "rgba(34, 197, 94, 0.1)" : "rgba(239, 68, 68, 0.1)",
        tension: 0.4,
      },
    ];

    if (includeConfidence && lowerBounds.length > 0) {
      datasets.push({
        label: "Lower Bound (95% CI)",
        data: lowerBounds,
        borderColor:
          activeTab === "revenue" ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)",
        backgroundColor: "transparent",
        borderDash: [5, 5],
        tension: 0.4,
      });
      datasets.push({
        label: "Upper Bound (95% CI)",
        data: upperBounds,
        borderColor:
          activeTab === "revenue" ? "rgba(34, 197, 94, 0.3)" : "rgba(239, 68, 68, 0.3)",
        backgroundColor: "transparent",
        borderDash: [5, 5],
        tension: 0.4,
      });
    }

    return { labels, datasets };
  };

  const prepareCashFlowChartData = () => {
    if (!cashFlowData || cashFlowData.forecast.length === 0) return null;

    const labels = cashFlowData.forecast.map((f) => f.month);
    const revenue = cashFlowData.forecast.map((f) => f.predicted_revenue);
    const expenses = cashFlowData.forecast.map((f) => f.predicted_expenses);
    const cashFlow = cashFlowData.forecast.map((f) => f.predicted_cash_flow);

    return {
      labels,
      datasets: [
        {
          label: "Revenue",
          data: revenue,
          borderColor: "rgb(34, 197, 94)",
          backgroundColor: "rgba(34, 197, 94, 0.1)",
          tension: 0.4,
        },
        {
          label: "Expenses",
          data: expenses,
          borderColor: "rgb(239, 68, 68)",
          backgroundColor: "rgba(239, 68, 68, 0.1)",
          tension: 0.4,
        },
        {
          label: "Net Cash Flow",
          data: cashFlow,
          borderColor: "rgb(59, 130, 246)",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          tension: 0.4,
        },
      ],
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Predictive Analytics
          </h1>
          <p className="text-gray-600">
            AI-powered financial forecasting and trend analysis
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex-1 min-w-[200px]">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Forecast Period
              </label>
              <select
                value={monthsAhead}
                onChange={(e) => setMonthsAhead(Number(e.target.value))}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={3}>3 Months</option>
                <option value={6}>6 Months</option>
                <option value={9}>9 Months</option>
                <option value={12}>12 Months</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="confidence"
                checked={includeConfidence}
                onChange={(e) => setIncludeConfidence(e.target.checked)}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <label htmlFor="confidence" className="text-sm font-medium text-gray-700">
                Show Confidence Intervals
              </label>
            </div>

            <button
              onClick={fetchForecasts}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>

            <button
              onClick={exportToCSV}
              className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Export CSV
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 mb-1">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <RefreshCw className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
            <p className="text-gray-600">Analyzing data and generating forecasts...</p>
          </div>
        )}

        {/* Content */}
        {!loading && !error && (revenueData || expenseData || cashFlowData) && (
          <>
            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-sm mb-6 overflow-hidden">
              <div className="flex border-b border-gray-200">
                <button
                  onClick={() => setActiveTab("revenue")}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === "revenue"
                      ? "bg-green-50 text-green-700 border-b-2 border-green-500"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  Revenue Forecast
                </button>
                <button
                  onClick={() => setActiveTab("expenses")}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === "expenses"
                      ? "bg-red-50 text-red-700 border-b-2 border-red-500"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  Expense Forecast
                </button>
                <button
                  onClick={() => setActiveTab("cashflow")}
                  className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${
                    activeTab === "cashflow"
                      ? "bg-blue-50 text-blue-700 border-b-2 border-blue-500"
                      : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  Cash Flow Forecast
                </button>
              </div>
            </div>

            {/* Revenue Tab */}
            {activeTab === "revenue" && revenueData && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <StatCard
                    title="Average Forecast"
                    value={formatCurrency(
                      revenueData.forecast.reduce((sum, f) => sum + f.predicted_value, 0) /
                        revenueData.forecast.length
                    )}
                    icon={<DollarSign className="w-6 h-6" />}
                    trend={{
                      value: revenueData.trend_analysis.average_growth_rate,
                      isPositive: revenueData.trend_analysis.average_growth_rate > 0,
                    }}
                    color="green"
                  />
                  <StatCard
                    title="Trend Direction"
                    value={
                      revenueData.trend_analysis.trend.charAt(0).toUpperCase() +
                      revenueData.trend_analysis.trend.slice(1)
                    }
                    icon={getTrendIcon(revenueData.trend_analysis.trend)}
                    color="blue"
                  />
                  <StatCard
                    title="Historical Average"
                    value={formatCurrency(revenueData.historical.average)}
                    icon={<Calendar className="w-6 h-6" />}
                    color="purple"
                  />
                  <StatCard
                    title="Confidence Level"
                    value={`${revenueData.accuracy_metrics.confidence_level}%`}
                    icon={<Activity className="w-6 h-6" />}
                    color="indigo"
                  />
                </div>

                {/* Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Revenue Forecast</h2>
                  {prepareChartData() && (
                    <Chart
                      type="line"
                      data={prepareChartData()!}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: "top",
                          },
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                return `${context.dataset.label}: ${formatCurrency(
                                  context.parsed.y
                                )}`;
                              },
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            ticks: {
                              callback: (value) => formatCurrency(Number(value)),
                            },
                          },
                        },
                      }}
                      height="400px"
                    />
                  )}
                </div>

                {/* Trend Analysis */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Trend Analysis</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Trend Direction</p>
                      <p className={`text-2xl font-bold ${getTrendColor(revenueData.trend_analysis.trend)}`}>
                        {revenueData.trend_analysis.trend.charAt(0).toUpperCase() +
                          revenueData.trend_analysis.trend.slice(1)}
                      </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Average Growth Rate</p>
                      <p className={`text-2xl font-bold ${
                        revenueData.trend_analysis.average_growth_rate > 0
                          ? "text-green-600"
                          : "text-red-600"
                      }`}>
                        {revenueData.trend_analysis.average_growth_rate.toFixed(2)}%
                      </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Volatility</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {revenueData.trend_analysis.volatility.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Expenses Tab */}
            {activeTab === "expenses" && expenseData && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <StatCard
                    title="Average Forecast"
                    value={formatCurrency(
                      expenseData.forecast.reduce((sum, f) => sum + f.predicted_value, 0) /
                        expenseData.forecast.length
                    )}
                    icon={<DollarSign className="w-6 h-6" />}
                    trend={{
                      value: Math.abs(expenseData.trend_analysis.average_growth_rate),
                      isPositive: expenseData.trend_analysis.average_growth_rate < 0,
                    }}
                    color="red"
                  />
                  <StatCard
                    title="Trend Direction"
                    value={
                      expenseData.trend_analysis.trend.charAt(0).toUpperCase() +
                      expenseData.trend_analysis.trend.slice(1)
                    }
                    icon={getTrendIcon(expenseData.trend_analysis.trend)}
                    color="blue"
                  />
                  <StatCard
                    title="Historical Average"
                    value={formatCurrency(expenseData.historical.average)}
                    icon={<Calendar className="w-6 h-6" />}
                    color="purple"
                  />
                  <StatCard
                    title="Confidence Level"
                    value={`${expenseData.accuracy_metrics.confidence_level}%`}
                    icon={<Activity className="w-6 h-6" />}
                    color="indigo"
                  />
                </div>

                {/* Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Expense Forecast</h2>
                  {prepareChartData() && (
                    <Chart
                      type="line"
                      data={prepareChartData()!}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: "top",
                          },
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                return `${context.dataset.label}: ${formatCurrency(
                                  context.parsed.y
                                )}`;
                              },
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            ticks: {
                              callback: (value) => formatCurrency(Number(value)),
                            },
                          },
                        },
                      }}
                      height="400px"
                    />
                  )}
                </div>

                {/* Trend Analysis */}
                <div className="bg-white rounded-xl shadow-sm p-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">Trend Analysis</h2>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Trend Direction</p>
                      <p className={`text-2xl font-bold ${getTrendColor(expenseData.trend_analysis.trend)}`}>
                        {expenseData.trend_analysis.trend.charAt(0).toUpperCase() +
                          expenseData.trend_analysis.trend.slice(1)}
                      </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Average Growth Rate</p>
                      <p className={`text-2xl font-bold ${
                        expenseData.trend_analysis.average_growth_rate > 0
                          ? "text-red-600"
                          : "text-green-600"
                      }`}>
                        {expenseData.trend_analysis.average_growth_rate.toFixed(2)}%
                      </p>
                    </div>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600 mb-1">Volatility</p>
                      <p className="text-2xl font-bold text-gray-900">
                        {expenseData.trend_analysis.volatility.toFixed(2)}%
                      </p>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Cash Flow Tab */}
            {activeTab === "cashflow" && cashFlowData && (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <StatCard
                    title="Average Net Cash Flow"
                    value={formatCurrency(
                      cashFlowData.forecast.reduce((sum, f) => sum + f.predicted_cash_flow, 0) /
                        cashFlowData.forecast.length
                    )}
                    icon={<DollarSign className="w-6 h-6" />}
                    color="blue"
                  />
                  <StatCard
                    title="Total Projected Revenue"
                    value={formatCurrency(
                      cashFlowData.forecast.reduce((sum, f) => sum + f.predicted_revenue, 0)
                    )}
                    icon={<TrendingUp className="w-6 h-6" />}
                    color="green"
                  />
                  <StatCard
                    title="Total Projected Expenses"
                    value={formatCurrency(
                      cashFlowData.forecast.reduce((sum, f) => sum + f.predicted_expenses, 0)
                    )}
                    icon={<TrendingDown className="w-6 h-6" />}
                    color="red"
                  />
                  <StatCard
                    title="Net Position"
                    value={formatCurrency(
                      cashFlowData.forecast.reduce(
                        (sum, f) =>
                          sum + (f.predicted_revenue - f.predicted_expenses),
                        0
                      )
                    )}
                    icon={<Activity className="w-6 h-6" />}
                    color={
                      cashFlowData.forecast.reduce(
                        (sum, f) => sum + f.predicted_cash_flow,
                        0
                      ) > 0
                        ? "green"
                        : "red"
                    }
                  />
                </div>

                {/* Chart */}
                <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
                  <h2 className="text-xl font-bold text-gray-900 mb-4">
                    Cash Flow Forecast
                  </h2>
                  {prepareCashFlowChartData() && (
                    <Chart
                      type="line"
                      data={prepareCashFlowChartData()!}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            display: true,
                            position: "top",
                          },
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                return `${context.dataset.label}: ${formatCurrency(
                                  context.parsed.y
                                )}`;
                              },
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                            ticks: {
                              callback: (value) => formatCurrency(Number(value)),
                            },
                          },
                        },
                      }}
                      height="400px"
                    />
                  )}
                </div>

                {/* Monthly Breakdown Table */}
                <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h2 className="text-xl font-bold text-gray-900">Monthly Breakdown</h2>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Month
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Revenue
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Expenses
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Net Cash Flow
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {cashFlowData.forecast.map((item, index) => (
                          <tr key={index} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {item.month}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-green-600">
                              {formatCurrency(item.predicted_revenue)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-red-600">
                              {formatCurrency(item.predicted_expenses)}
                            </td>
                            <td
                              className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${
                                item.predicted_cash_flow >= 0
                                  ? "text-green-600"
                                  : "text-red-600"
                              }`}
                            >
                              {formatCurrency(item.predicted_cash_flow)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
