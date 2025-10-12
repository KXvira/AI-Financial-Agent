'use client';

import Link from 'next/link';
import { Calendar, Mail, FileText, Activity, ArrowRight, CheckCircle } from 'lucide-react';

export default function AutomationPage() {
  const features = [
    {
      title: 'Scheduled Reports',
      description: 'Automate report generation and delivery with flexible scheduling options',
      icon: Calendar,
      href: '/automation/scheduled-reports',
      color: 'bg-blue-500',
      features: [
        'Daily, weekly, and monthly schedules',
        'Multiple email recipients',
        'Enable/disable schedules',
        'Run history tracking',
      ],
    },
    {
      title: 'Email Configuration',
      description: 'Configure SMTP settings for automated email delivery',
      icon: Mail,
      href: '/automation/email-config',
      color: 'bg-green-500',
      features: [
        'Gmail, Outlook, Yahoo support',
        'Test email functionality',
        'HTML email templates',
        'Attachment support',
      ],
    },
    {
      title: 'Report Templates',
      description: 'Create and manage custom report templates',
      icon: FileText,
      href: '/automation/templates',
      color: 'bg-purple-500',
      features: [
        'Default financial templates',
        'Custom template builder',
        'Multiple export formats',
        'Template categories',
      ],
    },
    {
      title: 'Real-time Dashboard',
      description: 'Monitor live metrics and updates via WebSocket',
      icon: Activity,
      href: '/automation/realtime-dashboard',
      color: 'bg-orange-500',
      features: [
        'Live metric updates',
        'Real-time alerts',
        'Transaction feed',
        'WebSocket connection',
      ],
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Automation & Real-time Features
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Streamline your workflow with automated reports, scheduled delivery, and real-time monitoring
          </p>
        </div>

        {/* Phase 4 Badge */}
        <div className="flex justify-center mb-12">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2">
            <CheckCircle size={24} />
            <span className="font-semibold text-lg">Phase 4: Automation Complete</span>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Link
                key={feature.href}
                href={feature.href}
                className="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 overflow-hidden"
              >
                <div className={`${feature.color} p-6`}>
                  <div className="flex items-center justify-between">
                    <Icon className="text-white" size={48} />
                    <ArrowRight className="text-white opacity-0 group-hover:opacity-100 transition-opacity" size={24} />
                  </div>
                </div>
                
                <div className="p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-3">{feature.title}</h2>
                  <p className="text-gray-600 mb-6">{feature.description}</p>
                  
                  <ul className="space-y-2">
                    {feature.features.map((item, index) => (
                      <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                        <CheckCircle size={16} className="text-green-500 mt-0.5 flex-shrink-0" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <div className="mt-6 flex items-center gap-2 text-blue-600 font-medium group-hover:gap-3 transition-all">
                    <span>Explore {feature.title}</span>
                    <ArrowRight size={20} />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">20+</div>
            <div className="text-gray-600">API Endpoints</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">4</div>
            <div className="text-gray-600">Major Features</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-4xl font-bold text-purple-600 mb-2">Real-time</div>
            <div className="text-gray-600">WebSocket Updates</div>
          </div>
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <div className="text-4xl font-bold text-orange-600 mb-2">Automated</div>
            <div className="text-gray-600">Report Delivery</div>
          </div>
        </div>

        {/* Getting Started */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-8 text-white">
          <h2 className="text-3xl font-bold mb-4">Getting Started</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-xl font-semibold mb-3">Quick Setup</h3>
              <ol className="space-y-2 text-blue-100">
                <li>1. Configure SMTP settings in Email Configuration</li>
                <li>2. Seed default report templates</li>
                <li>3. Create your first schedule</li>
                <li>4. Monitor live updates on the dashboard</li>
              </ol>
            </div>
            <div>
              <h3 className="text-xl font-semibold mb-3">Key Benefits</h3>
              <ul className="space-y-2 text-blue-100">
                <li>✓ Save time with automated report generation</li>
                <li>✓ Never miss a deadline with scheduled delivery</li>
                <li>✓ Monitor metrics in real-time</li>
                <li>✓ Customize reports to your needs</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Info Banner */}
        <div className="mt-8 bg-blue-50 border-l-4 border-blue-500 p-6 rounded">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">🎉 Phase 4 Complete</h3>
          <p className="text-blue-800">
            All automation features are now available! Phase 4 includes scheduled reports, email delivery,
            custom templates, and real-time monitoring. Explore each feature to streamline your financial
            reporting workflow.
          </p>
        </div>
      </div>
    </div>
  );
}
