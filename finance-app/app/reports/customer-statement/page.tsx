"use client";

import { useState, useEffect } from "react";
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  Calendar,
  FileText,
  DollarSign,
  AlertCircle,
  CheckCircle,
  Clock,
  Download,
  TrendingUp,
  TrendingDown
} from "lucide-react";

interface Customer {
  id: string;
  name: string;
  email: string;
  phone: string;
  address: string | {
    street: string;
    city: string;
    postal_code: string;
    country: string;
  };
  city: string | null;
  country: string;
}

interface Transaction {
  date: string;
  type: string;
  reference: string;
  description: string;
  invoice_id: string;
  amount: number;
  payment: number;
  balance: number;
  status: string;
  due_date?: string;
}

interface CustomerStatement {
  customer: Customer;
  statement_period: {
    start_date: string;
    end_date: string;
    days: number;
  };
  summary: {
    opening_balance: number;
    total_invoiced: number;
    total_paid: number;
    closing_balance: number;
    total_invoices: number;
    paid_invoices: number;
    pending_invoices: number;
    overdue_invoices: number;
    overdue_amount: number;
  };
  aging: {
    current: number;
    "1-30_days": number;
    "31-60_days": number;
    "61-90_days": number;
    over_90_days: number;
  };
  transactions: Transaction[];
  generated_at: string;
}

interface CustomerListItem {
  id: string;
  name: string;
  email: string;
  phone: string;
  outstanding_balance: number;
  invoice_count: number;
}

export default function CustomerStatementPage() {
  const [customerList, setCustomerList] = useState<CustomerListItem[]>([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState<string>("");
  const [statement, setStatement] = useState<CustomerStatement | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [includePaid, setIncludePaid] = useState(true);

  // Fetch customer list on mount
  useEffect(() => {
    fetchCustomerList();
  }, []);

  const fetchCustomerList = async () => {
    try {
      const response = await fetch("http://localhost:8000/reports/customers");
      if (!response.ok) throw new Error("Failed to fetch customers");
      const data = await response.json();
      setCustomerList(data.customers || []);
    } catch (err: any) {
      console.error("Error fetching customers:", err);
      setError(err.message);
    }
  };

  const fetchStatement = async () => {
    if (!selectedCustomerId) {
      setError("Please select a customer");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (startDate) params.append("start_date", startDate);
      if (endDate) params.append("end_date", endDate);
      params.append("include_paid", includePaid.toString());

      const response = await fetch(
        `http://localhost:8000/reports/customer-statement/${selectedCustomerId}?${params}`
      );
      
      if (!response.ok) throw new Error("Failed to fetch statement");
      
      const data = await response.json();
      
      // Check if backend returned an error
      if (data.error) {
        throw new Error(data.error);
      }
      
      setStatement(data);
    } catch (err: any) {
      setError(err.message);
      setStatement(null);
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "paid":
        return "text-green-600 bg-green-100";
      case "overdue":
        return "text-red-600 bg-red-100";
      case "pending":
      case "sent":
        return "text-yellow-600 bg-yellow-100";
      case "completed":
        return "text-blue-600 bg-blue-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  const exportToCSV = () => {
    if (!statement) return;

    const csvRows = [];
    csvRows.push(["Customer Statement"]);
    csvRows.push([`Customer: ${statement.customer.name}`]);
    csvRows.push([`Period: ${formatDate(statement.statement_period.start_date)} - ${formatDate(statement.statement_period.end_date)}`]);
    csvRows.push([]);
    csvRows.push(["Date", "Type", "Reference", "Description", "Debit", "Credit", "Balance", "Status"]);

    statement.transactions.forEach((txn) => {
      csvRows.push([
        formatDate(txn.date),
        txn.type,
        txn.reference,
        txn.description,
        txn.amount > 0 ? txn.amount.toString() : "",
        txn.payment > 0 ? txn.payment.toString() : "",
        txn.balance.toString(),
        txn.status,
      ]);
    });

    const csvContent = csvRows.map((row) => row.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `customer-statement-${statement.customer.name}-${new Date().toISOString().split("T")[0]}.csv`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8">
        {/* Back Button */}
        <a
          href="/reports"
          className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-4 transition-colors"
        >
          ← Back to Reports
        </a>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800">Customer Statement</h1>
          <p className="text-gray-600 mt-2">
            View detailed transaction history and account status for individual customers
          </p>
        </div>

        {/* Customer Selection & Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 text-gray-800">Select Customer & Period</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
            {/* Customer Dropdown */}
            <div className="lg:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Customer
              </label>
              <select
                value={selectedCustomerId}
                onChange={(e) => setSelectedCustomerId(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select a customer...</option>
                {customerList.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.name} - {formatCurrency(customer.outstanding_balance)} outstanding
                  </option>
                ))}
              </select>
            </div>

            {/* Date Filters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Start Date
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
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
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex items-end">
              <button
                onClick={fetchStatement}
                disabled={!selectedCustomerId || loading}
                className="w-full px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all"
              >
                {loading ? "Loading..." : "Generate Statement"}
              </button>
            </div>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="includePaid"
              checked={includePaid}
              onChange={(e) => setIncludePaid(e.target.checked)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="includePaid" className="ml-2 text-sm text-gray-700">
              Include paid invoices and transactions
            </label>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center">
            <AlertCircle className="w-5 h-5 text-red-600 mr-3" />
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Statement Content */}
        {statement && (
          <>
            {/* Customer Info */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-800 mb-4">
                    {statement.customer.name}
                  </h2>
                  <div className="space-y-2">
                    {statement.customer.email && (
                      <div className="flex items-center text-gray-600">
                        <Mail className="w-4 h-4 mr-2" />
                        {statement.customer.email}
                      </div>
                    )}
                    {statement.customer.phone && (
                      <div className="flex items-center text-gray-600">
                        <Phone className="w-4 h-4 mr-2" />
                        {statement.customer.phone}
                      </div>
                    )}
                    {statement.customer.address && (
                      <div className="flex items-center text-gray-600">
                        <MapPin className="w-4 h-4 mr-2" />
                        {typeof statement.customer.address === 'string' 
                          ? `${statement.customer.address}, ${statement.customer.city}, ${statement.customer.country}`
                          : `${statement.customer.address.street}, ${statement.customer.address.city}, ${statement.customer.address.country}`
                        }
                      </div>
                    )}
                  </div>
                </div>

                <button
                  onClick={exportToCSV}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export CSV
                </button>
              </div>

              {/* Period Info */}
              <div className="bg-blue-50 rounded-lg p-4">
                <div className="flex items-center text-blue-800">
                  <Calendar className="w-5 h-5 mr-2" />
                  <span className="font-semibold">
                    Statement Period: {formatDate(statement.statement_period.start_date)} - {formatDate(statement.statement_period.end_date)}
                  </span>
                  <span className="ml-2 text-blue-600">
                    ({statement.statement_period.days} days)
                  </span>
                </div>
              </div>
            </div>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              {/* Opening Balance */}
              <div className="bg-gradient-to-br from-gray-500 to-gray-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <TrendingUp className="w-8 h-8 opacity-80" />
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Opening Balance</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(statement.summary.opening_balance)}
                </p>
              </div>

              {/* Total Invoiced */}
              <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <FileText className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">{statement.summary.total_invoices} invoices</span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Total Invoiced</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(statement.summary.total_invoiced)}
                </p>
              </div>

              {/* Total Paid */}
              <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl shadow-lg p-6 text-white">
                <div className="flex items-center justify-between mb-2">
                  <CheckCircle className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">{statement.summary.paid_invoices} paid</span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Total Paid</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(statement.summary.total_paid)}
                </p>
              </div>

              {/* Closing Balance */}
              <div className={`rounded-xl shadow-lg p-6 text-white ${
                statement.summary.closing_balance > 0 
                  ? "bg-gradient-to-br from-red-500 to-red-600" 
                  : "bg-gradient-to-br from-purple-500 to-purple-600"
              }`}>
                <div className="flex items-center justify-between mb-2">
                  <DollarSign className="w-8 h-8 opacity-80" />
                  <span className="text-sm opacity-90">
                    {statement.summary.pending_invoices} pending
                  </span>
                </div>
                <h3 className="text-lg font-medium opacity-90 mb-1">Current Balance</h3>
                <p className="text-3xl font-bold">
                  {formatCurrency(statement.summary.closing_balance)}
                </p>
              </div>
            </div>

            {/* Overdue Alert */}
            {statement.summary.overdue_invoices > 0 && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center">
                <AlertCircle className="w-6 h-6 text-red-600 mr-3 flex-shrink-0" />
                <div>
                  <p className="font-semibold text-red-800">
                    {statement.summary.overdue_invoices} Overdue Invoice{statement.summary.overdue_invoices !== 1 ? "s" : ""}
                  </p>
                  <p className="text-red-700">
                    Total overdue amount: {formatCurrency(statement.summary.overdue_amount)}
                  </p>
                </div>
              </div>
            )}

            {/* Aging Analysis */}
            <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Aging Analysis</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Current</p>
                  <p className="text-xl font-bold text-green-700">
                    {formatCurrency(statement.aging.current)}
                  </p>
                </div>
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">1-30 Days</p>
                  <p className="text-xl font-bold text-yellow-700">
                    {formatCurrency(statement.aging["1-30_days"])}
                  </p>
                </div>
                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">31-60 Days</p>
                  <p className="text-xl font-bold text-orange-700">
                    {formatCurrency(statement.aging["31-60_days"])}
                  </p>
                </div>
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">61-90 Days</p>
                  <p className="text-xl font-bold text-red-700">
                    {formatCurrency(statement.aging["61-90_days"])}
                  </p>
                </div>
                <div className="text-center p-4 bg-red-100 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Over 90 Days</p>
                  <p className="text-xl font-bold text-red-800">
                    {formatCurrency(statement.aging.over_90_days)}
                  </p>
                </div>
              </div>
            </div>

            {/* Transaction History */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold mb-4 text-gray-800">
                Transaction History
              </h3>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b-2 border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Date</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Type</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Reference</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Description</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-700">Debit</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-700">Credit</th>
                      <th className="text-right py-3 px-4 font-semibold text-gray-700">Balance</th>
                      <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {statement.transactions.map((txn, index) => (
                      <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {formatDate(txn.date)}
                        </td>
                        <td className="py-3 px-4">
                          <span className={`text-xs px-2 py-1 rounded ${
                            txn.type === "invoice" 
                              ? "bg-blue-100 text-blue-700" 
                              : "bg-green-100 text-green-700"
                          }`}>
                            {txn.type}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-800 font-medium">
                          {txn.reference}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600">
                          {txn.description}
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-gray-800 font-medium">
                          {txn.amount > 0 ? formatCurrency(txn.amount) : "-"}
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-green-600 font-medium">
                          {txn.payment > 0 ? formatCurrency(txn.payment) : "-"}
                        </td>
                        <td className="py-3 px-4 text-sm text-right font-bold text-gray-800">
                          {formatCurrency(txn.balance)}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className={`text-xs px-2 py-1 rounded ${getStatusColor(txn.status)}`}>
                            {txn.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {statement.transactions.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No transactions found for the selected period
                </div>
              )}
            </div>
          </>
        )}

        {/* No Data State */}
        {!loading && !statement && !error && (
          <div className="bg-white rounded-xl shadow-lg p-12 text-center">
            <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">
              Select a customer and click "Generate Statement" to view their transaction history
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
