"use client";

import Link from "next/link";
import { useState } from "react";

const payments = [
  {
    reference: "PAY-2023-001",
    client: "Tech Solutions Ltd.",
    date: "2023-08-16",
    amount: "KES 50,000",
    method: "Bank Transfer",
  },
  {
    reference: "PAY-2023-002",
    client: "Global Imports Ltd.",
    date: "2023-08-26",
    amount: "KES 100,000",
    method: "Mobile Money",
  },
  {
    reference: "PAY-2023-003",
    client: "Digital Marketing Agency",
    date: "2023-09-06",
    amount: "KES 85,000",
    method: "Bank Transfer",
  },
  {
    reference: "PAY-2023-004",
    client: "Tech Solutions Ltd.",
    date: "2023-09-10",
    amount: "KES 75,000",
    method: "Mobile Money",
  },
  {
    reference: "PAY-2023-005",
    client: "Creative Designs Co.",
    date: "2023-09-15",
    amount: "KES 60,000",
    method: "Bank Transfer",
  },
];

export default function PaymentListPage() {
  const [search, setSearch] = useState("");

  const filteredPayments = payments.filter((p) =>
    p.reference.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Payment List</h1>
        <Link href="/payments/new">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            Add Payment
          </button>
        </Link>
      </div>

      <input
        type="text"
        placeholder="Search by Payment Reference"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="mb-6 p-2 border rounded w-full max-w-sm"
      />

      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="px-6 py-3 text-left">Payment #</th>
              <th className="px-6 py-3 text-left">Client</th>
              <th className="px-6 py-3 text-left">Date</th>
              <th className="px-6 py-3 text-left">Amount</th>
              <th className="px-6 py-3 text-left">Method</th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.map((payment) => (
              <tr key={payment.reference} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 font-medium text-blue-600">
                  <Link
                    href={`/payments/${encodeURIComponent(payment.reference)}`}
                    className="hover:underline"
                  >
                    {payment.reference}
                  </Link>
                </td>
                <td className="px-6 py-4 text-gray-800">{payment.client}</td>
                <td className="px-6 py-4 text-gray-800">{payment.date}</td>
                <td className="px-6 py-4 text-gray-800">{payment.amount}</td>
                <td className="px-6 py-4 text-gray-800">{payment.method}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
