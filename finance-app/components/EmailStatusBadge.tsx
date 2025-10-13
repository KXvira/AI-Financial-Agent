'use client';

import { useState, useEffect } from 'react';
import { Mail, CheckCircle, XCircle, Send, Loader2 } from 'lucide-react';

interface EmailStatusBadgeProps {
  onSetupClick?: () => void;
  showTestButton?: boolean;
  className?: string;
}

export function EmailStatusBadge({ 
  onSetupClick, 
  showTestButton = true,
  className = '' 
}: EmailStatusBadgeProps) {
  const [isConfigured, setIsConfigured] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [testEmail, setTestEmail] = useState('');
  const [showTestForm, setShowTestForm] = useState(false);

  useEffect(() => {
    fetchEmailConfig();
  }, []);

  const fetchEmailConfig = async () => {
    try {
      const response = await fetch('http://localhost:8000/automation/email/config');
      const data = await response.json();
      setIsConfigured(data.is_configured);
    } catch (error) {
      console.error('Error fetching email config:', error);
      setIsConfigured(false);
    } finally {
      setLoading(false);
    }
  };

  const sendTestEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    setTesting(true);
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
      
      if (response.ok) {
        setTimeout(() => {
          setShowTestForm(false);
          setTestEmail('');
          setTestResult(null);
        }, 3000);
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Error sending test email. Please check your configuration.',
      });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <Loader2 className="animate-spin text-gray-400" size={20} />
        <span className="text-sm text-gray-600">Checking email service...</span>
      </div>
    );
  }

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-3">
        {isConfigured ? (
          <>
            <CheckCircle className="text-green-600" size={20} />
            <div>
              <p className="text-sm font-medium text-gray-900">Email Service Configured</p>
              <p className="text-xs text-gray-500">Ready to send emails</p>
            </div>
          </>
        ) : (
          <>
            <XCircle className="text-red-600" size={20} />
            <div>
              <p className="text-sm font-medium text-gray-900">Email Service Not Configured</p>
              <p className="text-xs text-gray-500">Configure SMTP settings to send emails</p>
            </div>
          </>
        )}
        
        {!isConfigured && onSetupClick && (
          <button
            onClick={onSetupClick}
            className="ml-auto px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Setup Now
          </button>
        )}
      </div>

      {isConfigured && showTestButton && (
        <div>
          {!showTestForm ? (
            <button
              onClick={() => setShowTestForm(true)}
              className="flex items-center gap-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <Send size={16} />
              Test Email Delivery
            </button>
          ) : (
            <form onSubmit={sendTestEmail} className="space-y-2">
              <div className="flex gap-2">
                <input
                  type="email"
                  value={testEmail}
                  onChange={(e) => setTestEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                  disabled={testing}
                />
                <button
                  type="submit"
                  disabled={testing}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
                >
                  {testing ? (
                    <>
                      <Loader2 className="animate-spin" size={16} />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={16} />
                      Send Test
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowTestForm(false);
                    setTestEmail('');
                    setTestResult(null);
                  }}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
                >
                  Cancel
                </button>
              </div>
              
              {testResult && (
                <div className={`p-3 rounded-lg text-sm flex items-center gap-2 ${
                  testResult.success 
                    ? 'bg-green-50 text-green-800 border border-green-200' 
                    : 'bg-red-50 text-red-800 border border-red-200'
                }`}>
                  {testResult.success ? (
                    <CheckCircle size={16} className="flex-shrink-0" />
                  ) : (
                    <XCircle size={16} className="flex-shrink-0" />
                  )}
                  <span>{testResult.message}</span>
                </div>
              )}
            </form>
          )}
        </div>
      )}
    </div>
  );
}
