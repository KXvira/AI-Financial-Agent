'use client';

import { useSearchParams } from 'next/navigation';
import AIInvoiceGenerator from '@/components/AIInvoiceGenerator';
import { Suspense } from 'react';

function AIInvoiceContent() {
  const searchParams = useSearchParams();
  const customerId = searchParams.get('customer_id') || '';
  const customerName = searchParams.get('customer_name') || 'Customer';

  if (!customerId) {
    return (
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Customer Required</h2>
          <p className="text-gray-600 mb-6">
            Please select a customer to generate an invoice.
          </p>
          <a
            href="/customers"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Go to Customers
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <AIInvoiceGenerator
        customerId={customerId}
        customerName={customerName}
      />
    </div>
  );
}

export default function AIInvoicePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gray-50 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <AIInvoiceContent />
    </Suspense>
  );
}
