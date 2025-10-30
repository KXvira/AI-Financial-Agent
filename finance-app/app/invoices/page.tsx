"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Invoice {
  id: string;
  number: string;
  client: string;
  date: string;
  dueDate: string;
  amount: string;
  status: string;
}

export default function InvoicesPage() {
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInvoices();
  }, []);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/invoices?limit=100');
      
      if (!response.ok) {
        throw new Error('Failed to fetch invoices');
      }
      
      const data = await response.json();
      setInvoices(data.invoices || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch = inv.number.toLowerCase().includes(search.toLowerCase()) ||
                          inv.client.toLowerCase().includes(search.toLowerCase());
    const matchesStatus =
      filter === "All" || 
      inv.status.toLowerCase() === filter.toLowerCase() ||
      (filter === "Unpaid" && inv.status.toLowerCase() === "pending");
    return matchesSearch && matchesStatus;
  });

  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">Error loading invoices: {error}</p>
          <button 
            onClick={fetchInvoices}
            className="mt-2 text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

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

