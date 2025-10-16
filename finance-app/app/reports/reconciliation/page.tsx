"use client";

import { useState, useEffect } from "react";
import { 
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  RefreshCw,
  Download,
  TrendingUp,
  FileCheck,
  AlertCircle,
  Search,
  Filter
} from "lucide-react";

interface Transaction {
  id: string;
  date: string;
  reference: string;
  amount: number;
  phone: string;
  description: string;
  invoice_id: string;
  invoice_number: string;
  customer_name: string;
  reconciliation_status: string;
  confidence_score: number;
  needs_review: boolean;
  review_reason: string;
}

interface UnmatchedInvoice {
  id: string;
  invoice_number: string;
  date: string;
  customer_name: string;
  total_amount: number;
  amount_paid: number;
  outstanding: number;
  due_date: string;
  status: string;
}

interface ReconciliationIssue {
  type: string;
  severity: string;
  description: string;
  count?: number;
  total_amount?: number;
  transactions?: string[];
  invoices?: string[];
  matches?: any[];
}

interface ReconciliationReport {
  report_period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  summary: {
    total_transactions: number;
    matched_count: number;
    unmatched_count: number;
    partial_count: number;
    needs_review_count: number;
    match_rate: number;
    total_matched_amount: number;
    total_unmatched_amount: number;
    total_partial_amount: number;
    unmatched_invoices: number;
    total_outstanding: number;
  };
  transactions: {
    matched: Transaction[];
    unmatched: Transaction[];
    partial: Transaction[];
    needs_review: Transaction[];
  };
  unmatched_invoices: UnmatchedInvoice[];
  issues: ReconciliationIssue[];
  generated_at: string;
}

export default function ReconciliationReportPage() {
  const [report, setReport] = useState<ReconciliationReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [activeTab, setActiveTab] = useState<"matched" | "unmatched" | "partial" | "needs_review" | "invoices">("unmatched");

  useEffect(() => {
    // Set default dates (last 30 days)
    const end = new Date();
    const start = new Date();
    start.setDate(start.getDate() - 30);
    
    setEndDate(end.toISOString().split("T")[0]);
    setStartDate(start.toISOString().split("T")[0]);
  }, []);

  const fetchReport = async () => {
    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      if (statusFilter) params.append("status", statusFilter);

      const response = await fetch(
        `http://localhost:8000/reports/reconciliation?${params}`
      );
      
      if (!response.ok) throw new Error("Failed to fetch reconciliation report");
      
      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      setError(err.message);
      setReport(null);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-KE", {
      style: "currency",
      currency: "KES",
      minimumFractionDigits: 2,
    }).format(amount);
  };

  const formatDate = (dateStr: string) => {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "high":
        return "text-red-600 bg-red-100 border-red-200";
      case "medium":
        return "text-yellow-600 bg-yellow-100 border-yellow-200";
      case "low":
        return "text-blue-600 bg-blue-100 border-blue-200";
      default:
        return "text-gray-600 bg-gray-100 border-gray-200";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "matched":
        return <CheckCircle2 className="w-4 h-4 text-green-600" />;
      case "unmatched":
        return <XCircle className="w-4 h-4 text-red-600" />;
      case "partial":
      case "partial_match":
        return <AlertTriangle className="w-4 h-4 text-yellow-600" />;
      case "needs_review":
        return <Clock className="w-4 h-4 text-orange-600" />;
      default:
        return <AlertCircle className="w-4 h-4 text-gray-600" />;
    }
  };

  const exportToCSV = () => {
    if (!report) return;

    const csvRows = [];
    csvRows.push(["Reconciliation Report"]);
    csvRows.push([`Period: ${formatDate(report.report_period.start_date)} - ${formatDate(report.report_period.end_date)}`]);
    csvRows.push([]);
    
    // Transactions based on active tab
    csvRows.push(["Date", "Reference", "Amount", "Customer", "Invoice", "Status", "Confidence"]);
    
    const transactions = report.transactions[activeTab === "invoices" ? "unmatched" : activeTab];
    transactions.forEach((txn) => {
      csvRows.push([
        formatDate(txn.date),
        txn.reference,
        txn.amount.toString(),
        txn.customer_name || "",
        txn.invoice_number || "",
        txn.reconciliation_status,
        txn.confidence_score?.toString() || "",
      ]);
    });

    const csvContent = csvRows.map((row) => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `reconciliation-report-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Reconciliation Report</h1>
          <p className="text-gray-600">
            Track payment matching status and identify reconciliation issues
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Report Filters
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status Filter
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="">All Statuses</option>
                <option value="matched">Matched</option>
                <option value="unmatched">Unmatched</option>
                <option value="partial">Partial Match</option>
                <option value="needs_review">Needs Review</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchReport}
                disabled={loading}
                className="w-full px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all flex items-center justify-center gap-2"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                {loading ? "Loading..." : "Generate Report"}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Report Content */}
        {report && (
          <>
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              {/* Match Rate */}
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <CheckCircle2 className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">
                    {report.summary.matched_count}/{report.summary.total_transactions}
                  </span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Match Rate</h3>
                <p className="text-4xl font-bold">{report.summary.match_rate.toFixed(1)}%</p>
                <p className="text-sm opacity-80 mt-2">
                  {formatCurrency(report.summary.total_matched_amount)} matched
                </p>
              </div>

              {/* Unmatched */}
              <div className="bg-gradient-to-br from-red-500 to-red-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <XCircle className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">{report.summary.unmatched_count} txns</span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Unmatched Payments</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(report.summary.total_unmatched_amount)}
                </p>
              </div>

              {/* Needs Review */}
              <div className="bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <Clock className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">{report.summary.needs_review_count} txns</span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Needs Review</h3>
                <p className="text-3xl font-bold">
                  {report.summary.needs_review_count + report.summary.partial_count}
                </p>
                <p className="text-sm opacity-80 mt-2">Low confidence matches</p>
              </div>

              {/* Outstanding Invoices */}
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <FileCheck className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">{report.summary.unmatched_invoices} invoices</span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Outstanding</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(report.summary.total_outstanding)}
                </p>
              </div>
            </div>

            {/* Issues Alert */}
            {report.issues && report.issues.length > 0 && (
              <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
                <h3 className="text-xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
                  <AlertTriangle className="w-6 h-6 text-orange-600" />
                  Reconciliation Issues Detected
                </h3>
                <div className="space-y-3">
                  {report.issues.map((issue, index) => (
                    <div
                      key={index}
                      className={`border rounded-lg p-4 ${getSeverityColor(issue.severity)}`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold mb-1">{issue.description}</p>
                          {issue.count && (
                            <p className="text-sm">
                              Count: {issue.count} | Amount: {formatCurrency(issue.total_amount || 0)}
                            </p>
                          )}
                        </div>
                        <span className="text-xs px-2 py-1 rounded bg-white bg-opacity-50">
                          {issue.severity.toUpperCase()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Tabs */}
            <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-6">
              <div className="flex border-b border-gray-200 overflow-x-auto">
                <button
                  onClick={() => setActiveTab("unmatched")}
                  className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${
                    activeTab === "unmatched"
                      ? "bg-red-50 text-red-700 border-b-2 border-red-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <XCircle className="w-4 h-4" />
                  Unmatched ({report.summary.unmatched_count})
                </button>
                <button
                  onClick={() => setActiveTab("needs_review")}
                  className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${
                    activeTab === "needs_review"
                      ? "bg-yellow-50 text-yellow-700 border-b-2 border-yellow-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <Clock className="w-4 h-4" />
                  Needs Review ({report.summary.needs_review_count})
                </button>
                <button
                  onClick={() => setActiveTab("partial")}
                  className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${
                    activeTab === "partial"
                      ? "bg-orange-50 text-orange-700 border-b-2 border-orange-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <AlertTriangle className="w-4 h-4" />
                  Partial ({report.summary.partial_count})
                </button>
                <button
                  onClick={() => setActiveTab("matched")}
                  className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${
                    activeTab === "matched"
                      ? "bg-green-50 text-green-700 border-b-2 border-green-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4" />
                  Matched ({report.summary.matched_count})
                </button>
                <button
                  onClick={() => setActiveTab("invoices")}
                  className={`px-6 py-3 font-medium transition-colors flex items-center gap-2 ${
                    activeTab === "invoices"
                      ? "bg-purple-50 text-purple-700 border-b-2 border-purple-600"
                      : "text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <FileCheck className="w-4 h-4" />
                  Unpaid Invoices ({report.summary.unmatched_invoices})
                </button>
              </div>

              {/* Tab Content - Transactions */}
              {activeTab !== "invoices" && (
                <div className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-800">
                      {activeTab === "matched" && "Matched Transactions"}
                      {activeTab === "unmatched" && "Unmatched Transactions"}
                      {activeTab === "partial" && "Partial Matches"}
                      {activeTab === "needs_review" && "Transactions Needing Review"}
                    </h3>
                    <button
                      onClick={exportToCSV}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b-2 border-gray-200">
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Reference</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Amount</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Customer</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Invoice</th>
                          <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                          {activeTab !== "matched" && (
                            <th className="text-center py-3 px-4 font-semibold text-gray-700">Confidence</th>
                          )}
                        </tr>
                      </thead>
                      <tbody>
                        {report.transactions[activeTab].map((txn) => (
                          <tr key={txn.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {formatDate(txn.date)}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-800 font-medium">
                              {txn.reference}
                            </td>
                            <td className="py-3 px-4 text-sm text-right text-gray-800 font-bold">
                              {formatCurrency(txn.amount)}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {txn.customer_name || "-"}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {txn.invoice_number || "-"}
                            </td>
                            <td className="py-3 px-4 text-center">
                              <div className="flex items-center justify-center gap-1">
                                {getStatusIcon(txn.reconciliation_status)}
                              </div>
                            </td>
                            {activeTab !== "matched" && (
                              <td className="py-3 px-4 text-center text-sm">
                                {txn.confidence_score ? (
                                  <span className={`px-2 py-1 rounded ${
                                    txn.confidence_score > 0.8 
                                      ? "bg-green-100 text-green-700" 
                                      : txn.confidence_score > 0.5
                                      ? "bg-yellow-100 text-yellow-700"
                                      : "bg-red-100 text-red-700"
                                  }`}>
                                    {(txn.confidence_score * 100).toFixed(0)}%
                                  </span>
                                ) : "-"}
                              </td>
                            )}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {report.transactions[activeTab].length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No {activeTab} transactions found
                    </div>
                  )}
                </div>
              )}

              {/* Tab Content - Unmatched Invoices */}
              {activeTab === "invoices" && (
                <div className="p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-800">
                      Unpaid Invoices
                    </h3>
                    <button
                      onClick={exportToCSV}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Export
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b-2 border-gray-200">
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Invoice #</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Customer</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Total</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Paid</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-700">Outstanding</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-700">Due Date</th>
                          <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {report.unmatched_invoices.map((inv) => (
                          <tr key={inv.id} className="border-b border-gray-100 hover:bg-gray-50">
                            <td className="py-3 px-4 text-sm text-gray-800 font-medium">
                              {inv.invoice_number}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {formatDate(inv.date)}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {inv.customer_name}
                            </td>
                            <td className="py-3 px-4 text-sm text-right text-gray-800">
                              {formatCurrency(inv.total_amount)}
                            </td>
                            <td className="py-3 px-4 text-sm text-right text-green-600">
                              {formatCurrency(inv.amount_paid)}
                            </td>
                            <td className="py-3 px-4 text-sm text-right text-red-600 font-bold">
                              {formatCurrency(inv.outstanding)}
                            </td>
                            <td className="py-3 px-4 text-sm text-gray-600">
                              {formatDate(inv.due_date)}
                            </td>
                            <td className="py-3 px-4 text-center">
                              <span className={`text-xs px-2 py-1 rounded ${
                                inv.status === "overdue" 
                                  ? "bg-red-100 text-red-700"
                                  : "bg-yellow-100 text-yellow-700"
                              }`}>
                                {inv.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {report.unmatched_invoices.length === 0 && (
                    <div className="text-center py-8 text-gray-500">
                      No unpaid invoices found
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}

        {/* No Data State */}
        {!loading && !report && !error && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <FileCheck className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              Click "Generate Report" to view reconciliation status
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
