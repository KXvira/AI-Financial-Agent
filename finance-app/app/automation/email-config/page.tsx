'use client';

import { useState, useEffect } from 'react';
import { Mail, Send, CheckCircle, XCircle, AlertCircle, Key, Server, ExternalLink, Copy, Check } from 'lucide-react';

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
  const [copied, setCopied] = useState<string | null>(null);

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

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
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

        {/* Setup Instructions - MailerSend */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-gray-900">🚀 Quick Setup with MailerSend</h2>
              <a
                href="https://app.mailersend.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                Open MailerSend Dashboard
                <ExternalLink size={16} />
              </a>
            </div>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {/* Step 1 */}
              <div className="border-l-4 border-blue-500 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-blue-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">1</span>
                  <h3 className="text-lg font-semibold text-gray-900">Sign Up & Verify Domain</h3>
                </div>
                <p className="text-gray-600 mb-3">
                  Create a free MailerSend account (3,000 emails/month) and verify your domain
                </p>
                <a
                  href="https://www.mailersend.com/pricing"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700"
                >
                  View Pricing & Features <ExternalLink size={14} />
                </a>
              </div>

              {/* Step 2 */}
              <div className="border-l-4 border-green-500 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-green-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">2</span>
                  <h3 className="text-lg font-semibold text-gray-900">Get Your API Token</h3>
                </div>
                <ol className="text-gray-600 space-y-2 mb-3 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">→</span>
                    Navigate to Settings → API Tokens in your MailerSend dashboard
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">→</span>
                    Click "Generate New Token" and select "Email send" permission
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-600 mt-1">→</span>
                    Copy the token (starts with mlsn.)
                  </li>
                </ol>
              </div>

              {/* Step 3 */}
              <div className="border-l-4 border-purple-500 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-purple-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">3</span>
                  <h3 className="text-lg font-semibold text-gray-900">Configure Environment Variables</h3>
                </div>
                <p className="text-gray-600 mb-3">
                  Add these variables to your <code className="bg-gray-100 px-2 py-1 rounded text-sm">.env</code> file:
                </p>
                
                <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto relative group">
                  <button
                    onClick={() => copyToClipboard(`MAILERSEND_API_TOKEN=mlsn.your_token_here
MAILERSEND_FROM_EMAIL=noreply@yourdomain.com
MAILERSEND_FROM_NAME=Finguard

SMTP_HOST=smtp.mailersend.net
SMTP_PORT=587
SMTP_USER=MS_xxxxx@test-xxxxx.mlsender.net
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Finguard
SMTP_USE_TLS=True`, 'config')}
                    className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    {copied === 'config' ? <Check size={14} /> : <Copy size={14} />}
                    {copied === 'config' ? 'Copied!' : 'Copy'}
                  </button>
                  <div className="mb-2 text-gray-500"># MailerSend Configuration</div>
                  <div>MAILERSEND_API_TOKEN=<span className="text-yellow-400">mlsn.your_token_here</span></div>
                  <div>MAILERSEND_FROM_EMAIL=<span className="text-yellow-400">noreply@yourdomain.com</span></div>
                  <div>MAILERSEND_FROM_NAME=<span className="text-yellow-400">Finguard</span></div>
                  <div className="mb-2"></div>
                  <div className="text-gray-500"># SMTP Configuration (Optional)</div>
                  <div>SMTP_HOST=<span className="text-yellow-400">smtp.mailersend.net</span></div>
                  <div>SMTP_PORT=<span className="text-yellow-400">587</span></div>
                  <div>SMTP_USER=<span className="text-yellow-400">MS_xxxxx@test-xxxxx.mlsender.net</span></div>
                  <div>SMTP_PASSWORD=<span className="text-yellow-400">your_smtp_password</span></div>
                  <div>SMTP_FROM_EMAIL=<span className="text-yellow-400">noreply@yourdomain.com</span></div>
                  <div>SMTP_FROM_NAME=<span className="text-yellow-400">Finguard</span></div>
                  <div>SMTP_USE_TLS=<span className="text-yellow-400">True</span></div>
                </div>
              </div>

              {/* Step 4 */}
              <div className="border-l-4 border-orange-500 pl-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-orange-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold">4</span>
                  <h3 className="text-lg font-semibold text-gray-900">Restart Backend Server</h3>
                </div>
                <p className="text-gray-600 mb-3">
                  Restart your backend to apply the new configuration
                </p>
                <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm relative group">
                  <button
                    onClick={() => copyToClipboard('pkill -f "uvicorn backend.app:app" && python -m uvicorn backend.app:app --reload', 'restart')}
                    className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1 rounded text-xs flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    {copied === 'restart' ? <Check size={14} /> : <Copy size={14} />}
                    {copied === 'restart' ? 'Copied!' : 'Copy'}
                  </button>
                  <div>$ pkill -f "uvicorn backend.app:app" && python -m uvicorn backend.app:app --reload</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features Card */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">✨ What You Get with MailerSend</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start gap-3">
              <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={20} />
              <div>
                <p className="font-medium text-gray-900">3,000 Free Emails/Month</p>
                <p className="text-sm text-gray-600">Perfect for small to medium businesses</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={20} />
              <div>
                <p className="font-medium text-gray-900">Real-time Analytics</p>
                <p className="text-sm text-gray-600">Track opens, clicks, and deliverability</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={20} />
              <div>
                <p className="font-medium text-gray-900">Professional Templates</p>
                <p className="text-sm text-gray-600">Beautiful, responsive email designs</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle className="text-green-600 mt-1 flex-shrink-0" size={20} />
              <div>
                <p className="font-medium text-gray-900">99.9% Uptime SLA</p>
                <p className="text-sm text-gray-600">Reliable email delivery</p>
              </div>
            </div>
          </div>
        </div>

        {/* Alternative Providers */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">Alternative Email Providers</h2>
            <p className="text-gray-600 mt-1">Other SMTP services you can use</p>
          </div>
          <div className="p-6">
            <div className="overflow-x-auto">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">SMTP Host</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Port</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Free Tier</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">MailerSend ⭐</div>
                      <div className="text-sm text-gray-500">Recommended</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">smtp.mailersend.net</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">587</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">3,000/month</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">SendGrid</div>
                      <div className="text-sm text-gray-500">By Twilio</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">smtp.sendgrid.net</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">587</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">100/day</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">Gmail</div>
                      <div className="text-sm text-gray-500">Google Workspace</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">smtp.gmail.com</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">587</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-orange-600">500/day</td>
                  </tr>
                  <tr className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-gray-900">Mailgun</div>
                      <div className="text-sm text-gray-500">By Sinch</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-mono">smtp.mailgun.org</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">587</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">5,000/month</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
