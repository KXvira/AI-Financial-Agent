'use client';

import { X, ExternalLink, Copy, Check } from 'lucide-react';
import { useState } from 'react';

interface EmailSetupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function EmailSetupModal({ isOpen, onClose }: EmailSetupModalProps) {
  const [copied, setCopied] = useState<string | null>(null);

  if (!isOpen) return null;

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    setCopied(label);
    setTimeout(() => setCopied(null), 2000);
  };

  const envConfig = `# Email Service - MailerSend
MAILERSEND_API_TOKEN=mlsn.your_token_here
MAILERSEND_FROM_EMAIL=noreply@yourdomain.com
MAILERSEND_FROM_NAME=Finguard

# SMTP Configuration
SMTP_HOST=smtp.mailersend.net
SMTP_PORT=587
SMTP_USER=MS_xxxxx@test-xxxxx.mlsender.net
SMTP_PASSWORD=your_smtp_password
SMTP_FROM_EMAIL=noreply@yourdomain.com
SMTP_FROM_NAME=Finguard
SMTP_USE_TLS=True`;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">📧 Email Service Setup</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="px-6 py-6 space-y-6">
          {/* Step 1 */}
          <div className="border-l-4 border-blue-500 pl-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-blue-600 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">1</span>
              <h3 className="text-lg font-semibold text-gray-900">Get MailerSend Account</h3>
            </div>
            <p className="text-gray-600 mb-3">
              Sign up for a free MailerSend account (3,000 emails/month)
            </p>
            <a
              href="https://app.mailersend.com/sign-up"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Create Free Account
              <ExternalLink size={16} />
            </a>
          </div>

          {/* Step 2 */}
          <div className="border-l-4 border-green-500 pl-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-green-600 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">2</span>
              <h3 className="text-lg font-semibold text-gray-900">Verify Your Domain</h3>
            </div>
            <ol className="text-gray-600 space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1 font-bold">→</span>
                Go to <strong>Domains</strong> in your MailerSend dashboard
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1 font-bold">→</span>
                Add your domain or use their test domain for now
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600 mt-1 font-bold">→</span>
                Follow DNS verification steps
              </li>
            </ol>
          </div>

          {/* Step 3 */}
          <div className="border-l-4 border-purple-500 pl-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-purple-600 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">3</span>
              <h3 className="text-lg font-semibold text-gray-900">Get API Token</h3>
            </div>
            <ol className="text-gray-600 space-y-2 text-sm mb-3">
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1 font-bold">→</span>
                Navigate to <strong>Settings → API Tokens</strong>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1 font-bold">→</span>
                Click <strong>"Generate New Token"</strong>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1 font-bold">→</span>
                Select <strong>"Email send"</strong> permission
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 mt-1 font-bold">→</span>
                Copy the token (starts with <code className="bg-gray-100 px-1 rounded">mlsn.</code>)
              </li>
            </ol>
          </div>

          {/* Step 4 */}
          <div className="border-l-4 border-orange-500 pl-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-orange-600 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">4</span>
              <h3 className="text-lg font-semibold text-gray-900">Configure Environment</h3>
            </div>
            <p className="text-gray-600 mb-3 text-sm">
              Add these variables to your <code className="bg-gray-100 px-2 py-1 rounded text-sm">.env</code> file:
            </p>
            
            <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm overflow-x-auto relative group">
              <button
                onClick={() => copyToClipboard(envConfig, 'config')}
                className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1.5 rounded text-xs flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {copied === 'config' ? (
                  <>
                    <Check size={14} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={14} />
                    Copy All
                  </>
                )}
              </button>
              <div className="space-y-1">
                <div className="text-gray-500"># Email Service - MailerSend</div>
                <div>MAILERSEND_API_TOKEN=<span className="text-yellow-400">mlsn.your_token_here</span></div>
                <div>MAILERSEND_FROM_EMAIL=<span className="text-yellow-400">noreply@yourdomain.com</span></div>
                <div>MAILERSEND_FROM_NAME=<span className="text-yellow-400">Finguard</span></div>
                <div className="h-2"></div>
                <div className="text-gray-500"># SMTP Configuration</div>
                <div>SMTP_HOST=<span className="text-yellow-400">smtp.mailersend.net</span></div>
                <div>SMTP_PORT=<span className="text-yellow-400">587</span></div>
                <div>SMTP_USER=<span className="text-yellow-400">MS_xxxxx@test-xxxxx.mlsender.net</span></div>
                <div>SMTP_PASSWORD=<span className="text-yellow-400">your_smtp_password</span></div>
                <div>SMTP_FROM_EMAIL=<span className="text-yellow-400">noreply@yourdomain.com</span></div>
                <div>SMTP_FROM_NAME=<span className="text-yellow-400">Finguard</span></div>
                <div>SMTP_USE_TLS=<span className="text-yellow-400">True</span></div>
              </div>
            </div>
          </div>

          {/* Step 5 */}
          <div className="border-l-4 border-red-500 pl-4">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-red-600 text-white rounded-full w-7 h-7 flex items-center justify-center text-sm font-bold">5</span>
              <h3 className="text-lg font-semibold text-gray-900">Restart Backend</h3>
            </div>
            <p className="text-gray-600 mb-3 text-sm">
              Restart your backend server to apply the new configuration:
            </p>
            
            <div className="bg-gray-900 text-green-400 p-3 rounded-lg font-mono text-sm relative group">
              <button
                onClick={() => copyToClipboard('pkill -f "uvicorn backend.app:app" && python -m uvicorn backend.app:app --reload', 'restart')}
                className="absolute top-2 right-2 bg-gray-800 hover:bg-gray-700 text-white px-3 py-1.5 rounded text-xs flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                {copied === 'restart' ? (
                  <>
                    <Check size={14} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={14} />
                    Copy
                  </>
                )}
              </button>
              <div>$ pkill -f "uvicorn backend.app:app" && python -m uvicorn backend.app:app --reload</div>
            </div>
          </div>

          {/* Help Box */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Need Help?</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• <strong>Free Tier:</strong> 3,000 emails per month</li>
              <li>• <strong>Support:</strong> <a href="https://www.mailersend.com/help" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-600">MailerSend Help Center</a></li>
              <li>• <strong>Docs:</strong> <a href="https://developers.mailersend.com/" target="_blank" rel="noopener noreferrer" className="underline hover:text-blue-600">Developer Documentation</a></li>
            </ul>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 bg-gray-50 border-t border-gray-200 px-6 py-4 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Got it!
          </button>
        </div>
      </div>
    </div>
  );
}
