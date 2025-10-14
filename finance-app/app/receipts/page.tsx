'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';

interface Receipt {
  _id: string;
  receipt_number: string;
  receipt_type: string;
  customer: {
    name: string;
    phone: string;
    email?: string;
  };
  total: number;
  payment_method: string;
  status: string;
  generated_at: string;
  pdf_path?: string;
}

interface ReceiptStats {
  total_receipts: number;
  total_amount: number;
  receipts_by_type: { [key: string]: number };
  receipts_by_status: { [key: string]: number };
}

export default function ReceiptsPage() {
  const router = useRouter();
  const [receipts, setReceipts] = useState<Receipt[]>([]);
  const [stats, setStats] = useState<ReceiptStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');

  useEffect(() => {
    fetchReceipts();
    fetchStats();
  }, [typeFilter, statusFilter, searchQuery]);

  const fetchReceipts = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (typeFilter) params.append('receipt_type', typeFilter);
      if (statusFilter) params.append('status', statusFilter);
      if (searchQuery) params.append('search', searchQuery);
      
      const response = await fetch(`http://localhost:8000/receipts/?${params.toString()}`);
      const data = await response.json();
      
      if (data.receipts) {
        setReceipts(data.receipts);
      }
    } catch (err) {
      setError('Failed to load receipts');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/receipts/statistics');
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const downloadReceipt = async (receiptId: string, receiptNumber: string) => {
    try {
      const response = await fetch(`http://localhost:8000/receipts/${receiptId}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${receiptNumber}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download receipt');
      console.error(err);
    }
  };

  const sendEmail = async (receiptId: string) => {
    const email = prompt('Enter email address:');
    if (!email) return;
    
    try {
      const response = await fetch(`http://localhost:8000/receipts/${receiptId}/email?email=${email}`, {
        method: 'POST'
      });
      const data = await response.json();
      alert(data.message || 'Email sent successfully');
    } catch (err) {
      alert('Failed to send email');
      console.error(err);
    }
  };

  const formatCurrency = (amount: number | undefined) => {
    if (amount === undefined || amount === null) {
      return 'KES 0.00';
    }
    return `KES ${amount.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status: string) => {
    const statusColors: { [key: string]: string } = {
      generated: 'bg-green-100 text-green-800',
      sent: 'bg-blue-100 text-blue-800',
      viewed: 'bg-purple-100 text-purple-800',
      downloaded: 'bg-indigo-100 text-indigo-800',
      voided: 'bg-red-100 text-red-800',
      draft: 'bg-gray-100 text-gray-800'
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  const getTypeBadge = (type: string) => {
    const typeColors: { [key: string]: string } = {
      payment: 'bg-green-100 text-green-800',
      invoice: 'bg-blue-100 text-blue-800',
      refund: 'bg-red-100 text-red-800',
      partial_payment: 'bg-yellow-100 text-yellow-800',
      expense: 'bg-purple-100 text-purple-800'
    };
    
    return (
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${typeColors[type] || 'bg-gray-100 text-gray-800'}`}>
        {type.replace('_', ' ').toUpperCase()}
      </span>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Receipt Management</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage and track all your receipts in one place
          </p>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Total Receipts</div>
              <div className="text-2xl font-bold text-gray-900 mt-2">{stats.total_receipts}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Total Amount</div>
              <div className="text-2xl font-bold text-green-600 mt-2">
                {formatCurrency(stats.total_amount)}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Payment Receipts</div>
              <div className="text-2xl font-bold text-blue-600 mt-2">
                {stats?.receipts_by_type?.payment || 0}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm font-medium text-gray-600">Invoice Receipts</div>
              <div className="text-2xl font-bold text-purple-600 mt-2">
                {stats?.receipts_by_type?.invoice || 0}
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Types</option>
                <option value="payment">Payment</option>
                <option value="invoice">Invoice</option>
                <option value="refund">Refund</option>
                <option value="partial_payment">Partial Payment</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="generated">Generated</option>
                <option value="sent">Sent</option>
                <option value="viewed">Viewed</option>
                <option value="downloaded">Downloaded</option>
                <option value="voided">Voided</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Search
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Receipt number or customer..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Receipts Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading receipts...</p>
            </div>
          ) : error ? (
            <div className="p-8 text-center text-red-600">
              {error}
            </div>
          ) : receipts.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No receipts found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Receipt Number
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Customer
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Amount
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Payment
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {receipts.map((receipt) => (
                    <tr key={receipt._id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <button
                          onClick={() => router.push(`/receipts/${receipt._id}`)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          {receipt.receipt_number}
                        </button>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{receipt.customer.name}</div>
                        <div className="text-sm text-gray-500">{receipt.customer.phone}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getTypeBadge(receipt.receipt_type)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(receipt.total)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {receipt.payment_method.toUpperCase()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(receipt.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(receipt.generated_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => downloadReceipt(receipt._id, receipt.receipt_number)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                          title="Download PDF"
                        >
                          📥
                        </button>
                        {receipt.customer.email && (
                          <button
                            onClick={() => sendEmail(receipt._id)}
                            className="text-green-600 hover:text-green-900 mr-3"
                            title="Send Email"
                          >
                            📧
                          </button>
                        )}
                        <button
                          onClick={() => router.push(`/receipts/${receipt._id}`)}
                          className="text-purple-600 hover:text-purple-900"
                          title="View Details"
                        >
                          👁️
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
