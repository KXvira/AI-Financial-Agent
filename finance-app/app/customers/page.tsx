"use client";

import Link from "next/link";
import { useState, useEffect } from "react";

interface Customer {
  customer_id: string;
  name: string;
  email: string;
  phone: string;
  total_invoices: number;
  outstanding_balance: number;
  payment_status: string;
  status: string;
  last_invoice_date: string | null;
}

interface CustomerStats {
  total_customers: number;
  active_customers: number;
  total_outstanding: number;
  customers_with_overdue: number;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [stats, setStats] = useState<CustomerStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const [customersRes, statsRes] = await Promise.all([
        fetch("http://localhost:8000/api/customers/?limit=100"),
        fetch("http://localhost:8000/api/customers/stats/summary"),
      ]);

      if (!customersRes.ok || !statsRes.ok) {
        throw new Error("Failed to fetch customer data");
      }

      const customersData = await customersRes.json();
      const statsData = await statsRes.json();

      setCustomers(customersData.customers || []);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter((customer) => {
    const matchesSearch =
      customer.name.toLowerCase().includes(search.toLowerCase()) ||
      customer.email.toLowerCase().includes(search.toLowerCase()) ||
      customer.customer_id.toLowerCase().includes(search.toLowerCase());

    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && customer.status === "active") ||
      (statusFilter === "overdue" && customer.payment_status === "overdue");

    return matchesSearch && matchesStatus;
  });

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-KE", {
      style: "currency",
      currency: "KES",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good":
        return "bg-green-100 text-green-800";
      case "warning":
        return "bg-yellow-100 text-yellow-800";
      case "overdue":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">Customers</h1>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-white shadow-lg rounded-lg p-6 animate-pulse"
            >
              <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            </div>
          ))}
        </div>
        <p className="text-center text-gray-500">Loading customers...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-6">Customers</h1>
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
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Customers</h1>
          <p className="text-gray-500 mt-1">
            Manage your customers and track their invoices
          </p>
        </div>
        <Link
          href="/customers/new"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
        >
          + Create Customer
        </Link>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white shadow-lg rounded-lg p-6">
            <p className="text-gray-500 text-sm mb-1">Total Customers</p>
            <p className="text-3xl font-bold text-blue-700">
              {stats.total_customers}
            </p>
          </div>
          <div className="bg-white shadow-lg rounded-lg p-6">
            <p className="text-gray-500 text-sm mb-1">Active</p>
            <p className="text-3xl font-bold text-green-600">
              {stats.active_customers}
            </p>
          </div>
          <div className="bg-white shadow-lg rounded-lg p-6">
            <p className="text-gray-500 text-sm mb-1">Total Outstanding</p>
            <p className="text-3xl font-bold text-orange-600">
              {formatCurrency(stats.total_outstanding)}
            </p>
          </div>
          <div className="bg-white shadow-lg rounded-lg p-6">
            <p className="text-gray-500 text-sm mb-1">With Overdue</p>
            <p className="text-3xl font-bold text-red-600">
              {stats.customers_with_overdue}
            </p>
          </div>
        </div>
      )}

      {/* Search and Filter */}
      <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
        <div className="flex gap-4">
          <input
            type="text"
            placeholder="Search by name, email, or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-300"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="overdue">Overdue Payments</option>
          </select>
        </div>
      </div>

      {/* Customers Table */}
      <div className="bg-white shadow-lg rounded-lg overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-gray-700">
            <tr>
              <th className="p-4 text-left">Customer ID</th>
              <th className="p-4 text-left">Name</th>
              <th className="p-4 text-left">Contact</th>
              <th className="p-4 text-left">Invoices</th>
              <th className="p-4 text-left">Outstanding</th>
              <th className="p-4 text-left">Status</th>
              <th className="p-4 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredCustomers.length > 0 ? (
              filteredCustomers.map((customer) => (
                <tr
                  key={customer.customer_id}
                  className="hover:bg-gray-50 transition border-t"
                >
                  <td className="p-4 font-medium text-blue-700">
                    {customer.customer_id}
                  </td>
                  <td className="p-4 font-semibold">{customer.name}</td>
                  <td className="p-4">
                    <div className="text-sm">
                      <div>{customer.email}</div>
                      <div className="text-gray-500">{customer.phone}</div>
                    </div>
                  </td>
                  <td className="p-4 text-center">
                    <span className="font-semibold">
                      {customer.total_invoices}
                    </span>
                  </td>
                  <td className="p-4 font-semibold">
                    {formatCurrency(customer.outstanding_balance)}
                  </td>
                  <td className="p-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
                        customer.payment_status
                      )}`}
                    >
                      {customer.payment_status.toUpperCase()}
                    </span>
                  </td>
                  <td className="p-4">
                    <Link
                      href={`/customers/${customer.customer_id}`}
                      className="text-blue-600 hover:underline mr-3"
                    >
                      View
                    </Link>
                    <Link
                      href={`/customers/${customer.customer_id}/edit`}
                      className="text-gray-600 hover:underline"
                    >
                      Edit
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="p-8 text-center text-gray-500">
                  No customers found
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-4 text-sm text-gray-600">
        Showing {filteredCustomers.length} of {customers.length} customers
      </div>
    </div>
  );
}

