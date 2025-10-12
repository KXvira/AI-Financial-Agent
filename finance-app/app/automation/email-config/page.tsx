'use client';

import { useState, useEffect } from 'react';
import { Mail, Send, CheckCircle, XCircle, AlertCircle, Key, Server } from 'lucide-react';

interface EmailConfig {
  is_configured: boolean;
  smtp_host?: string;
  smtp_port?: number;
  smtp_user?: string;
  from_email?: string;
  from_name?: string;
  use_tls?: boolean;
}

export default function EmailConfigPage() {
  const [config, setConfig] = useState<EmailConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [testEmail, setTestEmail] = useState('');
  const [testLoading, setTestLoading] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/automation/email/config');
      const data = await response.json();
      setConfig(data);
    } catch (error) {
      console.error('Error fetching email config:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendTestEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setTestLoading(true);
    setTestResult(null);

    try {
      const response = await fetch('http://localhost:8000/automation/email/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ to_email: testEmail }),
      });

      const data = await response.json();
      setTestResult({
        success: response.ok,
        message: data.message || (response.ok ? 'Test email sent successfully!' : 'Failed to send test email'),
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Error sending test email. Please check your configuration.',
      });
    } finally {
      setTestLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Mail className="animate-pulse mx-auto mb-4 text-blue-600" size={60} />
          <p className="text-gray-600">Loading email configuration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Email Configuration</h1>
          <p className="text-gray-600 mt-2">Configure SMTP settings for automated report delivery</p>
        </div>

        {/* Status Card */}
        <div className={`rounded-lg shadow-lg p-6 mb-8 ${
          config?.is_configured ? 'bg-green-50 border-2 border-green-200' : 'bg-yellow-50 border-2 border-yellow-200'
        }`}>
          <div className="flex items-center gap-4">
            {config?.is_configured ? (
              <CheckCircle className="text-green-600" size={48} />
            ) : (
              <AlertCircle className="text-yellow-600" size={48} />
            )}
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                {config?.is_configured ? 'Email Service Configured' : 'Email Service Not Configured'}
              </h2>
              <p className="text-gray-600 mt-1">
                {config?.is_configured
                  ? 'Your SMTP settings are configured and ready to send emails'
                  : 'Configure environment variables to enable email delivery'}
              </p>
            </div>
          </div>
        </div>

        {/* Configuration Details */}
        {config?.is_configured && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold text-gray-900">Current Configuration</h2>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex items-start gap-3">
                  <Server className="text-blue-600 mt-1" size={20} />
                  <div>
                    <p className="text-sm font-medium text-gray-700">SMTP Server</p>
                    <p className="text-gray-900">{config.smtp_host || 'Not set'}</p>
                    <p className="text-sm text-gray-500">Port: {config.smtp_port || 'Not set'}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Key className="text-blue-600 mt-1" size={20} />
                  <div>
                    <p className="text-sm font-medium text-gray-700">Authentication</p>
                    <p className="text-gray-900">{config.smtp_user || 'Not set'}</p>
                    <p className="text-sm text-gray-500">TLS: {config.use_tls ? 'Enabled' : 'Disabled'}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Mail className="text-blue-600 mt-1" size={20} />
                  <div>
                    <p className="text-sm font-medium text-gray-700">From Email</p>
                    <p className="text-gray-900">{config.from_email || 'Not set'}</p>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Mail className="text-blue-600 mt-1" size={20} />
                  <div>
                    <p className="text-sm font-medium text-gray-700">From Name</p>
                    <p className="text-gray-900">{config.from_name || 'Not set'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Test Email */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Test Email Delivery</h2>
            <p className="text-gray-600 mt-1">Send a test email to verify your configuration</p>
          </div>
          <div className="p-6">
            <form onSubmit={sendTestEmail} className="max-w-xl">
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recipient Email
                </label>
                <input
                  type="email"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full border border-gray-300 rounded-lg px-4 py-2"
                  required
                  disabled={!config?.is_configured}
                />
              </div>

              {testResult && (
                <div className={`mb-4 p-4 rounded-lg flex items-center gap-3 ${
                  testResult.success ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
                }`}>
                  {testResult.success ? (
                    <CheckCircle size={24} />
                  ) : (
                    <XCircle size={24} />
                  )}
                  <p>{testResult.message}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={!config?.is_configured || testLoading}
                className={`px-6 py-3 rounded-lg flex items-center gap-2 transition-colors ${
                  config?.is_configured && !testLoading
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                <Send size={20} />
                {testLoading ? 'Sending...' : 'Send Test Email'}
              </button>
            </form>
          </div>
        </div>

        {/* Setup Instructions */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Setup Instructions</h2>
          </div>
          <div className="p-6">
            <div className="prose max-w-none">
              <p className="text-gray-600 mb-4">
                To enable email delivery, configure the following environment variables:
              </p>

              <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm mb-6 overflow-x-auto">
                <div className="mb-2"># Email Configuration</div>
                <div>SMTP_HOST=smtp.gmail.com</div>
                <div>SMTP_PORT=587</div>
                <div>SMTP_USER=your-email@gmail.com</div>
                <div>SMTP_PASSWORD=your-app-password</div>
                <div>FROM_EMAIL=your-email@gmail.com</div>
                <div>FROM_NAME="Fin Guard Reports"</div>
                <div>SMTP_USE_TLS=true</div>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-3">For Gmail:</h3>
              <ol className="list-decimal list-inside space-y-2 text-gray-600 mb-6">
                <li>Enable 2-Factor Authentication on your Google account</li>
                <li>Go to Google Account Settings → Security → App Passwords</li>
                <li>Generate a new app password for "Mail"</li>
                <li>Use the generated password in SMTP_PASSWORD</li>
              </ol>

              <h3 className="text-lg font-semibold text-gray-900 mb-3">For Other Providers:</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm text-gray-600">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left">Provider</th>
                      <th className="px-4 py-2 text-left">SMTP Host</th>
                      <th className="px-4 py-2 text-left">Port</th>
                      <th className="px-4 py-2 text-left">TLS</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    <tr>
                      <td className="px-4 py-2">Gmail</td>
                      <td className="px-4 py-2">smtp.gmail.com</td>
                      <td className="px-4 py-2">587</td>
                      <td className="px-4 py-2">Yes</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">Outlook</td>
                      <td className="px-4 py-2">smtp.office365.com</td>
                      <td className="px-4 py-2">587</td>
                      <td className="px-4 py-2">Yes</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">Yahoo</td>
                      <td className="px-4 py-2">smtp.mail.yahoo.com</td>
                      <td className="px-4 py-2">587</td>
                      <td className="px-4 py-2">Yes</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2">SendGrid</td>
                      <td className="px-4 py-2">smtp.sendgrid.net</td>
                      <td className="px-4 py-2">587</td>
                      <td className="px-4 py-2">Yes</td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="mt-6 p-4 bg-blue-50 border-l-4 border-blue-500 text-blue-700">
                <p className="font-medium">💡 Pro Tip</p>
                <p className="mt-1">
                  After configuring environment variables, restart the backend server for changes to take effect.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
