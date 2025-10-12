"use client";

import { useState, useEffect } from "react";
import {
  Sparkles,
  AlertTriangle,
  TrendingUp,
  Download,
  RefreshCw,
  Send,
  Lightbulb,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

interface Anomaly {
  type: string;
  severity: "HIGH" | "MEDIUM" | "LOW";
  description: string;
  value?: number;
  date?: string;
}

interface AIInsight {
  category: string;
  insight: string;
  recommendation?: string;
  impact: "positive" | "negative" | "neutral";
}

interface CustomReport {
  query: string;
  summary: string;
  details: any;
  insights: string[];
  recommendations: string[];
  timestamp: string;
}

export default function AIReportsPage() {
  const [activeTab, setActiveTab] = useState<"insights" | "anomalies" | "custom">("insights");
  const [reportType, setReportType] = useState<"general" | "revenue" | "expenses" | "cash_flow">(
    "general"
  );
  const [periodDays, setPeriodDays] = useState(30);
  const [anomalyDays, setAnomalyDays] = useState(30);
  const [insights, setInsights] = useState<AIInsight[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [customQuery, setCustomQuery] = useState("");
  const [customReport, setCustomReport] = useState<CustomReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeTab === "insights") {
      fetchInsights();
    } else if (activeTab === "anomalies") {
      fetchAnomalies();
    }
  }, [activeTab, reportType, periodDays, anomalyDays]);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/reports/ai/insights?report_type=${reportType}&days=${periodDays}`
      );
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setInsights([]);
      } else {
        setInsights(data.insights || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch insights");
      setInsights([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnomalies = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:8000/reports/ai/anomaly-detection?days=${anomalyDays}`
      );
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setAnomalies([]);
      } else {
        setAnomalies(data.anomalies || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch anomalies");
      setAnomalies([]);
    } finally {
      setLoading(false);
    }
  };

  const generateCustomReport = async () => {
    if (!customQuery.trim()) {
      setError("Please enter a query");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(startDate.getDate() - periodDays);

      const response = await fetch(
        `http://localhost:8000/reports/ai/custom-report?query=${encodeURIComponent(
          customQuery
        )}&start_date=${startDate.toISOString().split("T")[0]}&end_date=${
          endDate.toISOString().split("T")[0]
        }`
      );
      const data = await response.json();

      if (data.error) {
        setError(data.error);
        setCustomReport(null);
      } else {
        setCustomReport(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate custom report");
      setCustomReport(null);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return "bg-red-100 text-red-800 border-red-200";
      case "MEDIUM":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "LOW":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "HIGH":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      case "MEDIUM":
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case "LOW":
        return <AlertCircle className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case "positive":
        return <TrendingUp className="w-5 h-5 text-green-500" />;
      case "negative":
        return <AlertTriangle className="w-5 h-5 text-red-500" />;
      default:
        return <Lightbulb className="w-5 h-5 text-blue-500" />;
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "positive":
        return "bg-green-50 border-green-200";
      case "negative":
        return "bg-red-50 border-red-200";
      default:
        return "bg-blue-50 border-blue-200";
    }
  };

  const exportData = () => {
    let data: any = {};
    let filename = "";

    if (activeTab === "insights") {
      data = { insights, reportType, periodDays };
      filename = `ai-insights-${reportType}-${periodDays}days.json`;
    } else if (activeTab === "anomalies") {
      data = { anomalies, anomalyDays };
      filename = `anomalies-${anomalyDays}days.json`;
    } else if (activeTab === "custom" && customReport) {
      data = customReport;
      filename = `custom-report-${Date.now()}.json`;
    }

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <Sparkles className="w-10 h-10 text-purple-600" />
            AI-Powered Reports
          </h1>
          <p className="text-gray-600">
            Intelligent insights and anomaly detection powered by Gemini AI
          </p>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm mb-6 overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab("insights")}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                activeTab === "insights"
                  ? "bg-purple-50 text-purple-700 border-b-2 border-purple-500"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Lightbulb className="w-4 h-4" />
              AI Insights
            </button>
            <button
              onClick={() => setActiveTab("anomalies")}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                activeTab === "anomalies"
                  ? "bg-red-50 text-red-700 border-b-2 border-red-500"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              <AlertTriangle className="w-4 h-4" />
              Anomaly Detection
            </button>
            <button
              onClick={() => setActiveTab("custom")}
              className={`flex-1 px-6 py-4 text-sm font-medium transition-colors flex items-center justify-center gap-2 ${
                activeTab === "custom"
                  ? "bg-blue-50 text-blue-700 border-b-2 border-blue-500"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              }`}
            >
              <Sparkles className="w-4 h-4" />
              Custom Query
            </button>
          </div>
        </div>

        {/* AI Insights Tab */}
        {activeTab === "insights" && (
          <>
            {/* Controls */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Report Type
                  </label>
                  <select
                    value={reportType}
                    onChange={(e) =>
                      setReportType(
                        e.target.value as "general" | "revenue" | "expenses" | "cash_flow"
                      )
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="general">General Overview</option>
                    <option value="revenue">Revenue Analysis</option>
                    <option value="expenses">Expense Analysis</option>
                    <option value="cash_flow">Cash Flow Analysis</option>
                  </select>
                </div>

                <div className="flex-1 min-w-[200px]">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Period
                  </label>
                  <select
                    value={periodDays}
                    onChange={(e) => setPeriodDays(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value={7}>Last 7 Days</option>
                    <option value={30}>Last 30 Days</option>
                    <option value={60}>Last 60 Days</option>
                    <option value={90}>Last 90 Days</option>
                  </select>
                </div>

                <button
                  onClick={fetchInsights}
                  disabled={loading}
                  className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                  Generate Insights
                </button>

                <button
                  onClick={exportData}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 text-purple-500 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Analyzing data with AI...</p>
              </div>
            )}

            {/* Insights */}
            {!loading && !error && insights.length > 0 && (
              <div className="space-y-4">
                {insights.map((insight, index) => (
                  <div
                    key={index}
                    className={`bg-white rounded-xl shadow-sm p-6 border-2 ${getImpactColor(
                      insight.impact
                    )}`}
                  >
                    <div className="flex items-start gap-4">
                      {getImpactIcon(insight.impact)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-bold text-gray-900 text-lg">
                            {insight.category}
                          </h3>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              insight.impact === "positive"
                                ? "bg-green-100 text-green-800"
                                : insight.impact === "negative"
                                ? "bg-red-100 text-red-800"
                                : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {insight.impact.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-700 mb-3">{insight.insight}</p>
                        {insight.recommendation && (
                          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                            <div className="flex items-start gap-2">
                              <CheckCircle className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
                              <div>
                                <p className="text-sm font-medium text-purple-900 mb-1">
                                  Recommendation
                                </p>
                                <p className="text-sm text-purple-800">
                                  {insight.recommendation}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && !error && insights.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm">
                <Lightbulb className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No insights available for this period</p>
              </div>
            )}
          </>
        )}

        {/* Anomaly Detection Tab */}
        {activeTab === "anomalies" && (
          <>
            {/* Controls */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex-1 min-w-[200px]">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Analysis Period
                  </label>
                  <select
                    value={anomalyDays}
                    onChange={(e) => setAnomalyDays(Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  >
                    <option value={7}>Last 7 Days</option>
                    <option value={30}>Last 30 Days</option>
                    <option value={60}>Last 60 Days</option>
                    <option value={90}>Last 90 Days</option>
                  </select>
                </div>

                <button
                  onClick={fetchAnomalies}
                  disabled={loading}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                  Detect Anomalies
                </button>

                <button
                  onClick={exportData}
                  className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div className="text-center py-12">
                <RefreshCw className="w-12 h-12 text-red-500 animate-spin mx-auto mb-4" />
                <p className="text-gray-600">Scanning for anomalies...</p>
              </div>
            )}

            {/* Anomalies */}
            {!loading && !error && anomalies.length > 0 && (
              <div className="space-y-4">
                {anomalies.map((anomaly, index) => (
                  <div
                    key={index}
                    className={`bg-white rounded-xl shadow-sm p-6 border-2 ${getSeverityColor(
                      anomaly.severity
                    )}`}
                  >
                    <div className="flex items-start gap-4">
                      {getSeverityIcon(anomaly.severity)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="font-bold text-gray-900 text-lg">{anomaly.type}</h3>
                          <span
                            className={`px-3 py-1 rounded-full text-xs font-bold ${getSeverityColor(
                              anomaly.severity
                            )}`}
                          >
                            {anomaly.severity}
                          </span>
                        </div>
                        <p className="text-gray-700">{anomaly.description}</p>
                        {anomaly.date && (
                          <p className="text-sm text-gray-500 mt-2">Date: {anomaly.date}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {!loading && !error && anomalies.length === 0 && (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm">
                <CheckCircle className="w-16 h-16 text-green-400 mx-auto mb-4" />
                <p className="text-gray-700 font-semibold mb-2">No Anomalies Detected!</p>
                <p className="text-gray-500">Your financial data looks healthy</p>
              </div>
            )}
          </>
        )}

        {/* Custom Query Tab */}
        {activeTab === "custom" && (
          <>
            {/* Query Input */}
            <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ask AI About Your Finances
              </label>
              <div className="flex gap-4">
                <input
                  type="text"
                  value={customQuery}
                  onChange={(e) => setCustomQuery(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && generateCustomReport()}
                  placeholder="e.g., What are my top expense categories this month?"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <div className="flex-shrink-0">
                  <select
                    value={periodDays}
                    onChange={(e) => setPeriodDays(Number(e.target.value))}
                    className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value={7}>7 Days</option>
                    <option value={30}>30 Days</option>
                    <option value={60}>60 Days</option>
                    <option value={90}>90 Days</option>
                  </select>
                </div>
                <button
                  onClick={generateCustomReport}
                  disabled={loading || !customQuery.trim()}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
                >
                  {loading ? (
                    <RefreshCw className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                  Generate
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">Error</h3>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            )}

            {/* Loading */}
            {loading && (
              <div className="text-center py-12">
                <Sparkles className="w-12 h-12 text-blue-500 animate-pulse mx-auto mb-4" />
                <p className="text-gray-600">AI is analyzing your query...</p>
              </div>
            )}

            {/* Custom Report */}
            {!loading && customReport && (
              <div className="space-y-6">
                {/* Summary */}
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg p-8 text-white">
                  <h2 className="text-2xl font-bold mb-4">AI Analysis</h2>
                  <p className="text-lg leading-relaxed">{customReport.summary}</p>
                  <p className="text-sm opacity-75 mt-4">
                    Generated: {new Date(customReport.timestamp).toLocaleString()}
                  </p>
                </div>

                {/* Insights */}
                {customReport.insights && customReport.insights.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <Lightbulb className="w-6 h-6 text-yellow-500" />
                      Key Insights
                    </h3>
                    <ul className="space-y-3">
                      {customReport.insights.map((insight: string, index: number) => (
                        <li key={index} className="flex items-start gap-3">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{insight}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {customReport.recommendations && customReport.recommendations.length > 0 && (
                  <div className="bg-white rounded-xl shadow-sm p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <TrendingUp className="w-6 h-6 text-blue-500" />
                      Recommendations
                    </h3>
                    <ul className="space-y-3">
                      {customReport.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="flex items-start gap-3">
                          <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Export Button */}
                <div className="flex justify-end">
                  <button
                    onClick={exportData}
                    className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Export Report
                  </button>
                </div>
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && !customReport && (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm">
                <Sparkles className="w-16 h-16 text-blue-300 mx-auto mb-4" />
                <p className="text-gray-700 font-semibold mb-2">Ask AI Anything</p>
                <p className="text-gray-500">
                  Enter a question above to get AI-powered insights
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
