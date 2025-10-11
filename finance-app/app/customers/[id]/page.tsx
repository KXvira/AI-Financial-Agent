'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

// Types
interface Customer {
  customer_id: string;
  name: string;
  email: string;
  phone: string;
  secondary_email?: string;
  secondary_phone?: string;
  address?: {
    street?: string;
    city?: string;
    state?: string;
    postal_code?: string;
    country?: string;
  };
  business_type?: string;
  tax_id?: string;
  payment_terms?: number;
  status: string;
  payment_status: string;
  total_invoices: number;
  total_billed: number;
  total_paid: number;
  outstanding_amount: number;
  last_invoice_date?: string;
  last_payment_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface FinancialSummary {
  customer_id: string;
  customer_name: string;
  total_invoices: number;
  total_billed: number;
  total_paid: number;
  outstanding_amount: number;
  average_invoice_amount: number;
  average_payment_days: number;
  payment_score: number;
  last_invoice_date?: string;
  last_payment_date?: string;
  payment_status: string;
}

interface Invoice {
  invoice_id: string;
  customer_name: string;
  amount: number;
  status: string;
  due_date: string;
  issue_date: string;
  paid_amount?: number;
}

interface Payment {
  reference: string;
  amount: number;
  transaction_date: string;
  payment_method: string;
  status: string;
}

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.id as string;

  const [customer, setCustomer] = useState<Customer | null>(null);
  const [financialSummary, setFinancialSummary] = useState<FinancialSummary | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCustomerData();
  }, [customerId]);

  useEffect(() => {
    if (activeTab === 'invoices' && invoices.length === 0) {
      fetchInvoices();
    } else if (activeTab === 'payments' && payments.length === 0) {
      fetchPayments();
    }
  }, [activeTab]);

  const fetchCustomerData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch customer details and financial summary in parallel
      const [customerRes, financialRes] = await Promise.all([
        fetch(`http://localhost:8000/api/customers/${customerId}`),
        fetch(`http://localhost:8000/api/customers/${customerId}/financial-summary`)
      ]);

      if (!customerRes.ok) {
        throw new Error(`Failed to fetch customer: ${customerRes.status}`);
      }

      if (!financialRes.ok) {
        throw new Error(`Failed to fetch financial summary: ${financialRes.status}`);
      }

      const customerData = await customerRes.json();
      const financialData = await financialRes.json();

      setCustomer(customerData);
      setFinancialSummary(financialData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch customer data');
      console.error('Error fetching customer data:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/customers/${customerId}/invoices?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setInvoices(data.invoices || []);
      }
    } catch (err) {
      console.error('Error fetching invoices:', err);
    }
  };

  const fetchPayments = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/customers/${customerId}/payments?limit=50`);
      if (response.ok) {
        const data = await response.json();
        setPayments(data.payments || []);
      }
    } catch (err) {
      console.error('Error fetching payments:', err);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusBadgeClass = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower === 'good') return 'bg-green-100 text-green-800';
    if (statusLower === 'warning') return 'bg-yellow-100 text-yellow-800';
    if (statusLower === 'overdue') return 'bg-red-100 text-red-800';
    if (statusLower === 'paid') return 'bg-green-100 text-green-800';
    if (statusLower === 'pending') return 'bg-yellow-100 text-yellow-800';
    if (statusLower === 'active') return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  const getPaymentScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
            <div className="h-96 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !customer || !financialSummary) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800 mb-4">{error || 'Customer not found'}</p>
            <button
              onClick={() => router.push('/customers')}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Back to Customers
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <Link
                href="/customers"
                className="text-blue-600 hover:text-blue-800 mb-2 inline-block"
              >
                ← Back to Customers
              </Link>
              <h1 className="text-3xl font-bold text-gray-900">{customer.name}</h1>
              <p className="text-gray-600 mt-1">{customer.customer_id}</p>
            </div>
            <div className="flex gap-3">
              <Link
                href={`/customers/${customerId}/edit`}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Edit Customer
              </Link>
              <Link
                href={`/invoices/ai-generate?customer_id=${customerId}&customer_name=${encodeURIComponent(customer.name)}`}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
              >
                🤖 Generate Invoice (AI)
              </Link>
            </div>
          </div>
        </div>

        {/* Financial Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Total Billed</p>
            <p className="text-2xl font-bold text-gray-900">{formatCurrency(financialSummary.total_billed)}</p>
            <p className="text-gray-500 text-sm mt-2">{financialSummary.total_invoices} invoices</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Total Paid</p>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(financialSummary.total_paid)}</p>
            <p className="text-gray-500 text-sm mt-2">Avg: {formatCurrency(financialSummary.average_invoice_amount)}</p>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Outstanding</p>
            <p className="text-2xl font-bold text-orange-600">{formatCurrency(financialSummary.outstanding_amount)}</p>
            <span className={`inline-block px-2 py-1 rounded text-xs font-semibold mt-2 ${getStatusBadgeClass(financialSummary.payment_status)}`}>
              {financialSummary.payment_status.toUpperCase()}
            </span>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <p className="text-gray-600 text-sm mb-2">Payment Score</p>
            <p className={`text-2xl font-bold ${getPaymentScoreColor(financialSummary.payment_score)}`}>
              {financialSummary.payment_score}/100
            </p>
            <p className="text-gray-500 text-sm mt-2">Avg: {financialSummary.average_payment_days} days</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-6 py-3 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('invoices')}
                className={`px-6 py-3 font-medium text-sm ${
                  activeTab === 'invoices'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Invoices ({customer.total_invoices})
              </button>
              <button
                onClick={() => setActiveTab('payments')}
                className={`px-6 py-3 font-medium text-sm ${
                  activeTab === 'payments'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Payments
              </button>
            </nav>
          </div>

          <div className="p-6">
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Contact Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Primary Email</p>
                      <p className="text-gray-900">{customer.email}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Primary Phone</p>
                      <p className="text-gray-900">{customer.phone}</p>
                    </div>
                    {customer.secondary_email && (
                      <div>
                        <p className="text-sm text-gray-600">Secondary Email</p>
                        <p className="text-gray-900">{customer.secondary_email}</p>
                      </div>
                    )}
                    {customer.secondary_phone && (
                      <div>
                        <p className="text-sm text-gray-600">Secondary Phone</p>
                        <p className="text-gray-900">{customer.secondary_phone}</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Address */}
                {customer.address && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Address</h3>
                    <div className="text-gray-900">
                      {customer.address.street && <p>{customer.address.street}</p>}
                      {customer.address.city && customer.address.state && (
                        <p>{customer.address.city}, {customer.address.state} {customer.address.postal_code}</p>
                      )}
                      {customer.address.country && <p>{customer.address.country}</p>}
                    </div>
                  </div>
                )}

                {/* Business Information */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Business Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {customer.business_type && (
                      <div>
                        <p className="text-sm text-gray-600">Business Type</p>
                        <p className="text-gray-900">{customer.business_type}</p>
                      </div>
                    )}
                    {customer.tax_id && (
                      <div>
                        <p className="text-sm text-gray-600">Tax ID</p>
                        <p className="text-gray-900">{customer.tax_id}</p>
                      </div>
                    )}
                    {customer.payment_terms && (
                      <div>
                        <p className="text-sm text-gray-600">Payment Terms</p>
                        <p className="text-gray-900">{customer.payment_terms} days</p>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${getStatusBadgeClass(customer.status)}`}>
                        {customer.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Activity */}
                <div>
                  <h3 className="text-lg font-semibold mb-4">Activity</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Last Invoice</p>
                      <p className="text-gray-900">{formatDate(customer.last_invoice_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Last Payment</p>
                      <p className="text-gray-900">{formatDate(customer.last_payment_date)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Customer Since</p>
                      <p className="text-gray-900">{formatDate(customer.created_at)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Last Updated</p>
                      <p className="text-gray-900">{formatDate(customer.updated_at)}</p>
                    </div>
                  </div>
                </div>

                {/* Notes */}
                {customer.notes && (
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Notes</h3>
                    <p className="text-gray-900 whitespace-pre-wrap">{customer.notes}</p>
                  </div>
                )}
              </div>
            )}

            {/* Invoices Tab */}
            {activeTab === 'invoices' && (
              <div>
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold">Customer Invoices</h3>
                  <Link
                    href={`/invoices/new?customer_id=${customerId}`}
                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                  >
                    Create Invoice
                  </Link>
                </div>
                {invoices.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No invoices found</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice ID</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Issue Date</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Paid</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {invoices.map((invoice) => (
                          <tr key={invoice.invoice_id} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {invoice.invoice_id}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(invoice.issue_date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(invoice.due_date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(invoice.amount)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(invoice.paid_amount || 0)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(invoice.status)}`}>
                                {invoice.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <Link
                                href={`/invoices/${invoice.invoice_id}`}
                                className="text-blue-600 hover:text-blue-900"
                              >
                                View
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Payments Tab */}
            {activeTab === 'payments' && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Payment History</h3>
                {payments.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No payments found</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reference</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Method</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {payments.map((payment) => (
                          <tr key={payment.reference} className="hover:bg-gray-50">
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {payment.reference}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {formatDate(payment.transaction_date)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                              {formatCurrency(payment.amount)}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {payment.payment_method}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(payment.status)}`}>
                                {payment.status}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <Link
                                href={`/payments/${payment.reference}`}
                                className="text-blue-600 hover:text-blue-900"
                              >
                                View
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
