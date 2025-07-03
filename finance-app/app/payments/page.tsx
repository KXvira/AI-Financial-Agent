"use client";

import { useState } from "react";
import { CheckCircle, XCircle } from "lucide-react";
import Link from "next/link";

const mockInvoices = {
  "INV-2024–002": {
    number: "INV-2024–002",
    client: "Creative Designs Agency",
    issueDate: "2024-07-15",
    dueDate: "2024-08-14",
    amount: "KES 8,500",
    status: "Unpaid",
    items: [{ item: "Logo Design", quantity: 1, price: 8500, amount: 8500 }],
    notes: "Please pay by the due date.",
    payment: null,
  },
  "INV-2024–003": {
    number: "INV-2024–003",
    client: "Digital Concepts Ltd.",
    issueDate: "2024-07-22",
    dueDate: "2024-08-21",
    amount: "KES 12,000",
    status: "Paid",
    items: [{ item: "Social Media Design", quantity: 1, price: 12000, amount: 12000 }],
    notes: "Thanks for your business!",
    payment: {
      method: "M-Pesa",
      date: "2024-07-25",
      transactionId: "PAY-2024-010",
    },
  },
};

const initialMatches = Object.values(mockInvoices).reduce((acc, invoice) => {
  acc[invoice.number] = invoice.payment ? "Matched" : "Pending";
  return acc;
}, {} as Record<string, "Matched" | "Not Matched" | "Pending">);

const payments = Object.values(mockInvoices).map((invoice) => ({
  invoice: invoice.number,
  reference: invoice.payment?.transactionId || `REF-${invoice.number}`,
  amount: invoice.amount,
}));

export default function PaymentsPage() {
  const [search, setSearch] = useState("");
  const [matchStatus, setMatchStatus] = useState(initialMatches);

  const filteredPayments = payments.filter(
    (p) =>
      p.invoice.toLowerCase().includes(search.toLowerCase()) ||
      p.reference.toLowerCase().includes(search.toLowerCase())
  );

  const handleMatch = (invoice: string, matched: boolean) => {
    const status = matched ? "Matched" : "Not Matched";
    setMatchStatus((prev) => ({ ...prev, [invoice]: status }));
  };

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
          View Payments
        </Link>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">AI Accuracy</p>
          <p className="text-3xl font-semibold text-blue-700">95%</p>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">Pending Matches</p>
          <p className="text-3xl font-semibold text-yellow-600">
            {Object.values(matchStatus).filter((s) => s === "Pending").length}
          </p>
        </div>
        <div className="bg-white shadow-lg rounded-lg p-5">
          <p className="text-gray-500 text-sm mb-1">Total Matched</p>
          <p className="text-3xl font-semibold text-green-600">
            {Object.values(matchStatus).filter((s) => s === "Matched").length}
          </p>
        </div>
      </div>

      {/* Search */}
      <input
        type="text"
        placeholder="Search by Invoice or Payment Reference"
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
              <th className="p-3 text-left">Payment Reference</th>
              <th className="p-3 text-left">Amount</th>
              <th className="p-3 text-left">Status</th>
              <th className="p-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.map((payment, idx) => {
              const currentStatus = matchStatus[payment.invoice];
              return (
                <tr key={payment.invoice} className="hover:bg-gray-50 transition-all">
                  <td className="p-3 font-medium text-blue-700">{payment.invoice}</td>
                  <td className="p-3 text-blue-700">{payment.reference}</td>
                  <td className="p-3">{payment.amount}</td>
                  <td className="p-3">
                    <span
                      className={`px-3 py-1 text-xs rounded-full ${
                        currentStatus === "Matched"
                          ? "bg-green-100 text-green-700"
                          : currentStatus === "Not Matched"
                          ? "bg-red-100 text-red-700"
                          : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {currentStatus}
                    </span>
                  </td>
                  <td className="p-3 flex gap-3">
                    <button
                      onClick={() => handleMatch(payment.invoice, true)}
                      title="Confirm Match"
                      className={`transition-opacity ${
                        currentStatus === "Not Matched" ? "opacity-30" : "opacity-100"
                      } text-green-600 hover:text-green-800`}
                    >
                      <CheckCircle size={20} />
                    </button>
                    <button
                      onClick={() => handleMatch(payment.invoice, false)}
                      title="Reject Match"
                      className={`transition-opacity ${
                        currentStatus === "Matched" ? "opacity-30" : "opacity-100"
                      } text-red-600 hover:text-red-800`}
                    >
                      <XCircle size={20} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
