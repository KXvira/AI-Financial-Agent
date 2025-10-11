'use client';

import { useState } from 'react';

interface SendInvoiceEmailModalProps {
  invoiceId: string;
  customerEmail?: string;
  customerName?: string;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function SendInvoiceEmailModal({
  invoiceId,
  customerEmail = '',
  customerName = '',
  onClose,
  onSuccess
}: SendInvoiceEmailModalProps) {
  const [recipientEmail, setRecipientEmail] = useState(customerEmail);
  const [recipientName, setRecipientName] = useState(customerName);
  const [ccEmails, setCcEmails] = useState('');
  const [customMessage, setCustomMessage] = useState('');
  const [attachPdf, setAttachPdf] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [sendResult, setSendResult] = useState<any>(null);

  const handleSend = async () => {
    if (!recipientEmail) {
      setError('Recipient email is required');
      return;
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(recipientEmail)) {
      setError('Invalid email format');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      // Parse CC emails
      const ccEmailsList = ccEmails
        .split(',')
        .map(email => email.trim())
        .filter(email => email && emailRegex.test(email));

      const requestBody: any = {
        invoice_id: invoiceId,
        recipient_email: recipientEmail,
        attach_pdf: attachPdf,
      };

      if (recipientName) {
        requestBody.recipient_name = recipientName;
      }

      if (ccEmailsList.length > 0) {
        requestBody.cc_emails = ccEmailsList;
      }

      if (customMessage) {
        requestBody.custom_message = customMessage;
      }

      const response = await fetch('http://localhost:8000/api/email/send-invoice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to send email');
      }

      const result = await response.json();
      setSendResult(result);
      setSuccess(true);

      // Call onSuccess callback if provided
      if (onSuccess) {
        setTimeout(() => {
          onSuccess();
          onClose();
        }, 2000);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send email');
      console.error('Error sending email:', err);
    } finally {
      setLoading(false);
    }
  };

  if (success && sendResult) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
              <svg className="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">Email Sent Successfully!</h3>
            <p className="text-sm text-gray-600 mb-4">
              Invoice {invoiceId} has been sent to {sendResult.recipient}
            </p>
            {sendResult.method === 'mock' && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <p className="text-xs text-yellow-800">
                  ⚠️ Mock Mode: SendGrid not configured. Email was simulated.
                </p>
              </div>
            )}
            <div className="text-xs text-gray-500">
              <p>Sent at: {new Date(sendResult.sent_at).toLocaleString()}</p>
              <p>Method: {sendResult.method}</p>
            </div>
            <button
              onClick={onClose}
              className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Send Invoice via Email</h2>
              <p className="text-gray-600 mt-1">Invoice: {invoiceId}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Form */}
          <div className="space-y-6">
            <div>
              <label htmlFor="recipientEmail" className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="recipientEmail"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="customer@example.com"
              />
            </div>

            <div>
              <label htmlFor="recipientName" className="block text-sm font-medium text-gray-700 mb-2">
                Recipient Name
              </label>
              <input
                type="text"
                id="recipientName"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label htmlFor="ccEmails" className="block text-sm font-medium text-gray-700 mb-2">
                CC Emails (comma-separated)
              </label>
              <input
                type="text"
                id="ccEmails"
                value={ccEmails}
                onChange={(e) => setCcEmails(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="accounting@example.com, manager@example.com"
              />
              <p className="mt-1 text-xs text-gray-500">Separate multiple emails with commas</p>
            </div>

            <div>
              <label htmlFor="customMessage" className="block text-sm font-medium text-gray-700 mb-2">
                Custom Message (Optional)
              </label>
              <textarea
                id="customMessage"
                value={customMessage}
                onChange={(e) => setCustomMessage(e.target.value)}
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Add a personal message to include in the email..."
              />
              <p className="mt-1 text-xs text-gray-500">
                This message will appear prominently in the email
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="attachPdf"
                checked={attachPdf}
                onChange={(e) => setAttachPdf(e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="attachPdf" className="ml-2 block text-sm text-gray-700">
                Attach PDF invoice
              </label>
            </div>

            {/* Email Preview Info */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="text-sm font-medium text-blue-900 mb-2">📧 Email Preview</h4>
              <ul className="text-xs text-blue-800 space-y-1">
                <li>• Professional HTML email with invoice details</li>
                <li>• Invoice number, dates, and total amount</li>
                {attachPdf && <li>• PDF attachment with complete invoice</li>}
                <li>• Payment instructions and due date</li>
                {customMessage && <li>• Your custom message highlighted</li>}
              </ul>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 mt-6 pt-6 border-t">
            <button
              onClick={onClose}
              disabled={loading}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSend}
              disabled={loading || !recipientEmail}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Sending...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Send Invoice
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
