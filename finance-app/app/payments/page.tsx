"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface PaymentStats {
  totalPayments: number;
  completedCount: number;
  pendingCount: number;
  completedTotal: number;
  monthlyTotal: number;
  matchedCount: number;
  unmatchedCount: number;
  aiAccuracy: number;
}

interface Payment {
  id: string;
  reference: string;
  client: string;
  date: string;
  amount: string;
  amountRaw: number;
  method: string;
  status: string;
  invoiceNumber: string;
  phoneNumber: string;
  description: string;
  created_at: string;
}

export default function PaymentsPage() {
  const [search, setSearch] = useState("");
  const [stats, setStats] = useState<PaymentStats | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [statsRes, paymentsRes] = await Promise.all([
        fetch('http://localhost:8000/api/payments/stats/summary'),
        fetch('http://localhost:8000/api/payments?limit=50')
      ]);

      if (!statsRes.ok || !paymentsRes.ok) {
        throw new Error('Failed to fetch payment data');
      }

      const statsData = await statsRes.json();
      const paymentsData = await paymentsRes.json();

      setStats(statsData);
      setPayments(paymentsData.payments || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const filteredPayments = payments.filter(
    (p) =>
      p.invoiceNumber?.toLowerCase().includes(search.toLowerCase()) ||
      p.reference?.toLowerCase().includes(search.toLowerCase()) ||
      p.client?.toLowerCase().includes(search.toLowerCase())
  );

  const formatAmount = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-1">Payments Overview</h1>
            <p className="text-gray-500">Monitor AI matching status and handle pending payments.</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white shadow-lg rounded-lg p-5 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
        <p className="text-center text-gray-500">Loading payment data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-1">Payments Overview</h1>
            <p className="text-gray-500">Monitor AI matching status and handle pending payments.</p>
          </div>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-8 text-center">
          <p className="text-red-500 mb-4">Error: {error}</p>
          <button
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-1">Payments Overview</h1>
          <p className="text-gray-500">Monitor AI matching status and handle pending payments.</p>
        </div>
        <Link
          href="/payments/list"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          View All Payments
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">AI Accuracy</p>
          <p className="text-3xl font-semibold text-blue-700">
            {stats?.aiAccuracy.toFixed(1)}%
          </p>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">Total Payments</p>
          <p className="text-3xl font-semibold text-green-600">
            {stats?.totalPayments || 0}
          </p>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">Matched</p>
          <p className="text-3xl font-semibold text-green-600">
            {stats?.matchedCount || 0}
          </p>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">Unmatched</p>
          <p className="text-3xl font-semibold text-yellow-600">
            {stats?.unmatchedCount || 0}
          </p>
        </div>
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="Search by Invoice, Payment Reference, or Customer Name"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-6 p-3 border rounded-lg w-full md:w-1/2 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-300"
      />

      {/* Table */}
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-600">
            <tr>
              <th className="p-3 text-left">Invoice #</th>
              <th className="p-3 text-left">Customer</th>
              <th className="p-3 text-left">M-Pesa Reference</th>
              <th className="p-3 text-left">Amount</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.length > 0 ? (
              filteredPayments.map((payment, idx) => {
                // Check if payment has an invoice number (indicating it's matched)
                const isMatched = payment.invoiceNumber && payment.invoiceNumber !== 'N/A';
                const statusColor = isMatched 
                  ? "bg-green-100 text-green-700" 
                  : "bg-yellow-100 text-yellow-700";
                const statusText = isMatched ? "Matched" : "Unmatched";
                
                return (
                  <tr key={idx} className="hover:bg-gray-50 transition-all border-t">
                    <td className="p-3 font-medium text-blue-700">
                      {payment.invoiceNumber || 'N/A'}
                    </td>
                    <td className="p-3">{payment.client}</td>
                    <td className="p-3 text-blue-700 font-mono text-xs">
                      {payment.reference}
                    </td>
                    <td className="p-3 font-semibold">{formatAmount(payment.amountRaw)}</td>
                    <td className="p-3">
                      <span className={`px-3 py-1 text-xs rounded-full ${statusColor}`}>
                        {statusText}
                      </span>
                    </td>
                    <td className="p-3 text-gray-600">
                      {new Date(payment.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={6} className="p-8 text-center text-gray-500">
                  No payments found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
