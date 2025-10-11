'use client';

import { useState, useEffect } from 'react';

interface EmailHistoryItem {
  id: string;
  invoice_id: string;
  recipient_email: string;
  recipient_name?: string;
  subject: string;
  status: string;
  sent_at: string;
  method: string;
  error_message?: string;
}

interface EmailHistoryProps {
  invoiceId?: string;
}

export default function EmailHistory({ invoiceId }: EmailHistoryProps) {
  const [emails, setEmails] = useState<EmailHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'sent' | 'failed'>('all');

  useEffect(() => {
    fetchEmailHistory();
  }, [invoiceId]);

  const fetchEmailHistory = async () => {
    setLoading(true);
    setError(null);

    try {
      let url = 'http://localhost:8000/api/email/history';
      if (invoiceId) {
        url = `http://localhost:8000/api/email/history/${invoiceId}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('Failed to fetch email history');
      }

      const data = await response.json();
      setEmails(data.emails || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load email history');
      console.error('Error fetching email history:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredEmails = emails.filter(email => {
    if (filter === 'all') return true;
    return filter === 'sent' ? email.status === 'sent' : email.status === 'failed';
  });

  const getStatusBadge = (status: string, method: string) => {
    if (status === 'sent') {
      const bgColor = method === 'sendgrid' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800';
      return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${bgColor}`}>
          {method === 'sendgrid' ? '✓ Sent' : '✓ Mock'}
        </span>
      );
    }
    return (
      <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
        ✗ Failed
      </span>
    );
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-600" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
          <button
            onClick={fetchEmailHistory}
            className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-6 border-b">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Email History</h3>
            <p className="text-sm text-gray-600 mt-1">
              {emails.length} {emails.length === 1 ? 'email' : 'emails'} sent
            </p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-lg text-sm ${
                filter === 'all'
                  ? 'bg-blue-100 text-blue-800 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('sent')}
              className={`px-3 py-1 rounded-lg text-sm ${
                filter === 'sent'
                  ? 'bg-green-100 text-green-800 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Sent
            </button>
            <button
              onClick={() => setFilter('failed')}
              className={`px-3 py-1 rounded-lg text-sm ${
                filter === 'failed'
                  ? 'bg-red-100 text-red-800 font-medium'
                  : 'text-gray-600 hover:bg-gray-100'
              }`}
            >
              Failed
            </button>
          </div>
        </div>
      </div>

      {filteredEmails.length === 0 ? (
        <div className="p-8 text-center text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <p>No emails found</p>
          <p className="text-sm mt-1">
            {filter === 'all' ? 'No emails have been sent yet' : `No ${filter} emails`}
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Invoice
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recipient
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Subject
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredEmails.map((email) => (
                <tr key={email.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{email.invoice_id}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900">{email.recipient_name || email.recipient_email}</div>
                    <div className="text-xs text-gray-500">{email.recipient_email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs truncate">{email.subject}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {new Date(email.sent_at).toLocaleDateString()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(email.sent_at).toLocaleTimeString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(email.status, email.method)}
                    {email.error_message && (
                      <div className="text-xs text-red-600 mt-1 max-w-xs truncate" title={email.error_message}>
                        {email.error_message}
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="p-4 border-t bg-gray-50 flex justify-between items-center">
        <p className="text-sm text-gray-600">
          Showing {filteredEmails.length} of {emails.length} emails
        </p>
        <button
          onClick={fetchEmailHistory}
          className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>
  );
}
