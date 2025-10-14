'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { EmailSetupModal } from '@/components/EmailSetupModal';
import { checkEmailConfig } from '@/utils/checkEmailConfig';

interface Receipt {
  _id: string;
  receipt_number: string;
  receipt_type: string;
  customer: {
    name: string;
    phone: string;
    email?: string;
    address?: string;
  };
  line_items: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    amount: number;
    tax_rate?: number;
    tax_amount?: number;
  }>;
  subtotal: number;
  tax_total: number;
  total: number;
  payment_method: string;
  payment_reference?: string;
  status: string;
  generated_at: string;
  pdf_path?: string;
  qr_code?: string;
  notes?: string;
  metadata?: any;
}

export default function ReceiptDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [receipt, setReceipt] = useState<Receipt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [showEmailSetup, setShowEmailSetup] = useState(false);

  useEffect(() => {
    fetchReceipt();
  }, [params.id]);

  const fetchReceipt = async () => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/receipts/${params.id}`);
      const data = await response.json();
      setReceipt(data);
      
      // Fetch PDF preview
      if (data.pdf_path) {
        const pdfResponse = await fetch(`http://localhost:8000/receipts/${params.id}/download`);
        const blob = await pdfResponse.blob();
        const url = window.URL.createObjectURL(blob);
        setPdfUrl(url);
      }
    } catch (err) {
      setError('Failed to load receipt');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const downloadReceipt = async () => {
    if (!receipt) return;
    
    try {
      const response = await fetch(`http://localhost:8000/receipts/${params.id}/download`);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${receipt.receipt_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      alert('Failed to download receipt');
      console.error(err);
    }
  };

  const sendEmail = async () => {
    // Check email configuration first
    const result = await checkEmailConfig();
    
    if (!result.isConfigured) {
      // Show setup modal if email not configured
      setShowEmailSetup(true);
      return;
    }
    
    // If configured, proceed with sending
    const email = prompt('Enter email address:', receipt?.customer.email || '');
    if (!email) return;
    
    try {
      const response = await fetch(`http://localhost:8000/receipts/${params.id}/email?email=${email}`, {
        method: 'POST'
      });
      const data = await response.json();
      alert(data.message || 'Email sent successfully');
    } catch (err) {
      alert('Failed to send email');
      console.error(err);
    }
  };

  const voidReceipt = async () => {
    if (!confirm('Are you sure you want to void this receipt? This action cannot be undone.')) {
      return;
    }
    
    const reason = prompt('Enter reason for voiding:');
    if (!reason) return;
    
    try {
      const response = await fetch(`http://localhost:8000/receipts/${params.id}/void`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason })
      });
      const data = await response.json();
      alert(data.message || 'Receipt voided successfully');
      fetchReceipt();
    } catch (err) {
      alert('Failed to void receipt');
      console.error(err);
    }
  };

  const formatCurrency = (amount: number) => {
    return `KES ${amount.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-KE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading receipt...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !receipt) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-red-600">
            {error || 'Receipt not found'}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <div>
            <button
              onClick={() => router.back()}
              className="text-blue-600 hover:text-blue-800 mb-2"
            >
              ← Back to Receipts
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Receipt {receipt.receipt_number}</h1>
            <p className="mt-2 text-sm text-gray-600">
              Generated on {formatDate(receipt.generated_at)}
            </p>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={downloadReceipt}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              📥 Download PDF
            </button>
            <button
              onClick={sendEmail}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              📧 Send Email
            </button>
            {receipt.status !== 'voided' && (
              <button
                onClick={voidReceipt}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                ❌ Void Receipt
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Receipt Details */}
          <div className="space-y-6">
            {/* Customer Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Customer Information</h2>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-600">Name:</span>
                  <p className="text-sm text-gray-900">{receipt.customer.name}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Phone:</span>
                  <p className="text-sm text-gray-900">{receipt.customer.phone}</p>
                </div>
                {receipt.customer.email && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Email:</span>
                    <p className="text-sm text-gray-900">{receipt.customer.email}</p>
                  </div>
                )}
                {receipt.customer.address && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Address:</span>
                    <p className="text-sm text-gray-900">{receipt.customer.address}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Receipt Information */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Receipt Information</h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-600">Type:</span>
                  <span className="text-sm text-gray-900 capitalize">{receipt.receipt_type.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className={`text-sm font-semibold ${
                    receipt.status === 'voided' ? 'text-red-600' : 'text-green-600'
                  }`}>
                    {receipt.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium text-gray-600">Payment Method:</span>
                  <span className="text-sm text-gray-900 uppercase">{receipt.payment_method}</span>
                </div>
                {receipt.payment_reference && (
                  <div className="flex justify-between">
                    <span className="text-sm font-medium text-gray-600">Payment Reference:</span>
                    <span className="text-sm text-gray-900">{receipt.payment_reference}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Line Items */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Items</h2>
              <div className="space-y-3">
                {receipt.line_items.map((item, index) => (
                  <div key={index} className="border-b border-gray-200 pb-3 last:border-0">
                    <div className="flex justify-between mb-1">
                      <span className="text-sm font-medium text-gray-900">{item.description}</span>
                      <span className="text-sm font-medium text-gray-900">{formatCurrency(item.amount)}</span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500">
                      <span>{item.quantity} × {formatCurrency(item.unit_price)}</span>
                      {item.tax_rate && <span>VAT: {item.tax_rate}%</span>}
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Subtotal:</span>
                  <span className="text-gray-900">{formatCurrency(receipt.subtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">VAT (16%):</span>
                  <span className="text-gray-900">{formatCurrency(receipt.tax_total)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold">
                  <span className="text-gray-900">Total:</span>
                  <span className="text-green-600">{formatCurrency(receipt.total)}</span>
                </div>
              </div>
            </div>

            {/* Notes */}
            {receipt.notes && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">Notes</h2>
                <p className="text-sm text-gray-700">{receipt.notes}</p>
              </div>
            )}

            {/* QR Code */}
            {receipt.qr_code && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-lg font-semibold text-gray-900 mb-4">QR Code</h2>
                <div className="flex justify-center">
                  <img src={`data:image/png;base64,${receipt.qr_code}`} alt="Receipt QR Code" className="w-48 h-48" />
                </div>
                <p className="text-xs text-center text-gray-500 mt-2">Scan to verify receipt</p>
              </div>
            )}
          </div>

          {/* PDF Preview */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">PDF Preview</h2>
            {pdfUrl ? (
              <iframe
                src={pdfUrl}
                className="w-full h-[800px] border border-gray-300 rounded"
                title="Receipt PDF Preview"
              />
            ) : (
              <div className="text-center text-gray-500 py-8">
                PDF preview not available
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Email Setup Modal */}
      <EmailSetupModal 
        isOpen={showEmailSetup}
        onClose={() => setShowEmailSetup(false)}
      />
    </div>
  );
}
