"use client";

import { useState } from "react";
import Link from "next/link";

const invoices = [
  {
    number: "INV-2024–001",
    client: "Tech Solutions Ltd",
    date: "2024-07-20",
    dueDate: "2024-08-19",
    amount: "KES 15,000",
    status: "Paid",
  },
  {
    number: "INV-2024–002",
    client: "Creative Designs Agency",
    date: "2024-07-15",
    dueDate: "2024-08-14",
    amount: "KES 8,500",
    status: "Unpaid",
  },
  {
    number: "INV-2024–003",
    client: "Global Marketing Inc",
    date: "2024-07-10",
    dueDate: "2024-08-09",
    amount: "KES 22,000",
    status: "Paid",
  },
  {
    number: "INV-2024–004",
    client: "Software Innovations Ltd",
    date: "2024-07-05",
    dueDate: "2024-08-04",
    amount: "KES 12,000",
    status: "Unpaid",
  },
  {
    number: "INV-2024–005",
    client: "Digital Media Group",
    date: "2024-06-30",
    dueDate: "2024-07-29",
    amount: "KES 18,000",
    status: "Paid",
  }
];

export default function InvoicesPage() {
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch = inv.number.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      filter === "All" || inv.status.toLowerCase() === filter.toLowerCase();
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Invoices</h1>
        <Link href="/invoices/new">
          <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            New Invoice
          </button>
        </Link>
      </div>

      <div className="flex gap-4 mb-6 flex-wrap">
        <input
          type="text"
          placeholder="Search by Invoice #"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="p-2 border rounded w-full max-w-xs"
        />
        <div className="flex gap-2">
          <button
            className={`px-3 py-1 rounded bg-gray-200 ${filter === "All" ? "font-bold" : ""}`}
            onClick={() => setFilter("All")}
          >
            All
          </button>
          <button
            className={`px-3 py-1 rounded bg-green-600 text-white ${filter === "Paid" ? "font-bold" : ""}`}
            onClick={() => setFilter("Paid")}
          >
            Paid
          </button>
          <button
            className={`px-3 py-1 rounded bg-red-600 text-white ${filter === "Unpaid" ? "font-bold" : ""}`}
            onClick={() => setFilter("Unpaid")}
          >
            Unpaid
          </button>
        </div>
      </div>

      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-100 text-gray-700">
            <tr>
              <th className="p-4 text-left">Invoice #</th>
              <th className="p-4 text-left">Client</th>
              <th className="p-4 text-left">Date</th>
              <th className="p-4 text-left">Due Date</th>
              <th className="p-4 text-left">Amount</th>
              <th className="p-4 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map((inv) => (
              <tr key={inv.number} className="hover:bg-gray-50 transition">
                <td className="p-4 font-medium text-blue-600">
                  <Link href={`/invoices/${encodeURIComponent(inv.number)}`}>
                    {inv.number}
                  </Link>
                </td>
                <td className="p-4 text-gray-800">{inv.client}</td>
                <td className="p-4 text-gray-800">{inv.date}</td>
                <td className="p-4 text-gray-800">{inv.dueDate}</td>
                <td className="p-4 text-gray-800">{inv.amount}</td>
                <td className="p-4">
                  <span
                    className={`px-3 py-1 text-sm rounded-full ${
                      inv.status === "Paid"
                        ? "bg-green-100 text-green-700"
                        : "bg-yellow-100 text-yellow-800"
                    }`}
                  >
                    {inv.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

