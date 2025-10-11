"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

interface Payment {
  id: string;
  reference: string;
  client: string;
  date: string;
  amount: string;
  method: string;
}

export default function PaymentListPage() {
  const [search, setSearch] = useState("");
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/payments?limit=200');
      
      if (!response.ok) {
        throw new Error('Failed to fetch payments');
      }
      
      const data = await response.json();
      setPayments(data.payments || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const filteredPayments = payments.filter((payment) =>
    [payment.reference, payment.client, payment.method]
      .join(" ")
      .toLowerCase()
      .includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <Link href="/payments">
            <button className="text-blue-600 hover:underline">
              ← Back to Payments Overview
            </button>
          </Link>
        </div>
        <h1 className="text-4xl font-bold mb-8">All Payments</h1>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <input
            type="text"
            placeholder="Search payments by reference, client, or method..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 border rounded-lg"
            disabled={loading}
          />
        </div>

        {loading && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded mb-4"></div>
              <div className="h-8 bg-gray-200 rounded mb-4"></div>
              <div className="h-8 bg-gray-200 rounded mb-4"></div>
            </div>
            <p className="text-gray-500 mt-4">Loading payments...</p>
          </div>
        )}

        {error && (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <p className="text-red-500 mb-4">Error: {error}</p>
            <button
              onClick={fetchPayments}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        )}

        {!loading && !error && (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left p-4">Reference</th>
                  <th className="text-left p-4">Client</th>
                  <th className="text-left p-4">Date</th>
                  <th className="text-left p-4">Amount</th>
                  <th className="text-left p-4">Method</th>
                  <th className="text-left p-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredPayments.length > 0 ? (
                  filteredPayments.map((payment) => (
                    <tr key={payment.reference} className="border-t">
                      <td className="p-4 font-medium">{payment.reference}</td>
                      <td className="p-4">{payment.client}</td>
                      <td className="p-4">{payment.date}</td>
                      <td className="p-4">{payment.amount}</td>
                      <td className="p-4">{payment.method}</td>
                      <td className="p-4">
                        <Link href={`/payments/${payment.reference}`}>
                          <button className="text-blue-600 hover:underline">
                            View
                          </button>
                        </Link>
                      </td>
                    </tr>
                  ))
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
        )}
      </div>
    </div>
  );
}
