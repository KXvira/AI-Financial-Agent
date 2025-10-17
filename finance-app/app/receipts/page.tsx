'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

interface Receipt {
  _id: string;
  receipt_number: string;
  receipt_type: string;
  customer?: {
    name: string;
    phone: string;
    email?: string;
  };
  customer_name?: string;
  customer_phone?: string;
  customer_email?: string;
  amount?: number;
  total?: number;
  tax_breakdown?: {
    subtotal: number;
    vat_rate: number;
    vat_amount: number;
    total: number;
  };
  payment_method: string;
  status: string;
  generated_at?: string;
  issued_date?: string;
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

  // Create Receipt Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createLoading, setCreateLoading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  
  // Manual Receipt Form
  const [formData, setFormData] = useState({
    receipt_type: 'payment',
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    amount: '',
    payment_method: 'mpesa',
    description: '',
    send_email: false,
  });

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
      const response = await fetch('http://localhost:8000/receipts/statistics/summary');
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

  const handleCreateReceipt = async () => {
    try {
      setCreateLoading(true);
      
      const payload = {
        receipt_type: formData.receipt_type,
        customer: {
          name: formData.customer_name,
          email: formData.customer_email || undefined,
          phone: formData.customer_phone || undefined,
        },
        payment_method: formData.payment_method,
        amount: parseFloat(formData.amount),
        description: formData.description,
        include_vat: true,
        send_email: formData.send_email,
      };

      const response = await fetch('http://localhost:8000/receipts/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error('Failed to create receipt');
      
      const data = await response.json();
      alert(`Receipt ${data.receipt_number} created successfully!`);
      
      // Reset form and close modal
      setShowCreateModal(false);
      setFormData({
        receipt_type: 'payment',
        customer_name: '',
        customer_email: '',
        customer_phone: '',
        amount: '',
        payment_method: 'mpesa',
        description: '',
        send_email: false,
      });
      
      // Refresh receipts list
      fetchReceipts();
      fetchStats();
    } catch (err) {
      alert('Failed to create receipt');
      console.error(err);
    } finally {
      setCreateLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    try {
      setCreateLoading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/receipts/upload-ocr', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }
      
      const data = await response.json();
      alert(`Receipt created successfully! Receipt #: ${data.receipt_number}`);
      
      setShowCreateModal(false);
      setUploadFile(null);
      
      // Refresh receipts list
      fetchReceipts();
      fetchStats();
    } catch (err: any) {
      alert(`Failed to upload receipt: ${err.message}`);
      console.error(err);
    } finally {
      setCreateLoading(false);
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
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Receipt Management</h1>
            <p className="mt-2 text-gray-600">
              Manage and track all your receipts in one place
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm"
          >
            + Create Receipt
          </button>
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
                        <div className="text-sm font-medium text-gray-900">{receipt.customer_name || receipt.customer?.name || 'Unknown'}</div>
                        <div className="text-sm text-gray-500">{receipt.customer_phone || receipt.customer?.phone || ''}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getTypeBadge(receipt.receipt_type)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {formatCurrency(receipt.amount || receipt.total || receipt.tax_breakdown?.total)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {receipt.payment_method.toUpperCase()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(receipt.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(receipt.issued_date || receipt.generated_at || '')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => downloadReceipt(receipt._id, receipt.receipt_number)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                          title="Download PDF"
                        >
                          📥
                        </button>
                        {(receipt.customer_email || receipt.customer?.email) && (
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

        {/* Create Receipt Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Create New Receipt</h2>
                <button
                  onClick={() => setShowCreateModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="p-6">
                {/* Tabs */}
                <div className="mb-6 border-b border-gray-200">
                  <div className="flex gap-4">
                    <button className="pb-3 px-4 border-b-2 border-blue-600 text-blue-600 font-medium">
                      Manual Entry
                    </button>
                    <label className="pb-3 px-4 cursor-pointer text-gray-600 hover:text-gray-900 font-medium">
                      OCR Upload
                      <input
                        type="file"
                        accept="image/*,.pdf"
                        onChange={handleFileUpload}
                        className="hidden"
                        disabled={createLoading}
                      />
                    </label>
                  </div>
                </div>

                {/* Manual Form */}
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Receipt Type *
                      </label>
                      <select
                        value={formData.receipt_type}
                        onChange={(e) => setFormData({ ...formData, receipt_type: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="payment">Payment</option>
                        <option value="invoice">Invoice</option>
                        <option value="refund">Refund</option>
                        <option value="partial_payment">Partial Payment</option>
                        <option value="expense">Expense</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Payment Method *
                      </label>
                      <select
                        value={formData.payment_method}
                        onChange={(e) => setFormData({ ...formData, payment_method: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="mpesa">M-Pesa</option>
                        <option value="bank_transfer">Bank Transfer</option>
                        <option value="cash">Cash</option>
                        <option value="card">Card</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Customer Name *
                    </label>
                    <input
                      type="text"
                      value={formData.customer_name}
                      onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter customer name"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Customer Email
                      </label>
                      <input
                        type="email"
                        value={formData.customer_email}
                        onChange={(e) => setFormData({ ...formData, customer_email: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        placeholder="customer@example.com"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Customer Phone
                      </label>
                      <input
                        type="tel"
                        value={formData.customer_phone}
                        onChange={(e) => setFormData({ ...formData, customer_phone: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        placeholder="+254712345678"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Amount (KES) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                      rows={3}
                      placeholder="Payment for services..."
                    />
                  </div>

                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="send_email"
                      checked={formData.send_email}
                      onChange={(e) => setFormData({ ...formData, send_email: e.target.checked })}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <label htmlFor="send_email" className="ml-2 block text-sm text-gray-700">
                      Send receipt via email
                    </label>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="mt-6 flex gap-3 justify-end">
                  <button
                    onClick={() => setShowCreateModal(false)}
                    className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                    disabled={createLoading}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleCreateReceipt}
                    disabled={createLoading || !formData.customer_name || !formData.amount}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    {createLoading ? 'Creating...' : 'Create Receipt'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
