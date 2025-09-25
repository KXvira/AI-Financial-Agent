// app/ai-insights/page.tsx
"use client";

import { useState, useEffect } from 'react';
import { Bot, Activity, AlertCircle, CheckCircle } from 'lucide-react';
import AIChat from '../../components/AIChat';
import AIQuickActions from '../../components/AIQuickActions';
import { aiClient, DataSummaryResponse } from '../../utils/aiApi';

export default function AIInsightsPage() {
  const [activeTab, setActiveTab] = useState<'chat' | 'quick' | 'summary'>('chat');
  const [dataSummary, setDataSummary] = useState<DataSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'error' | 'checking'>('checking');

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check health
        const health = await aiClient.checkHealth();
        setConnectionStatus('connected');
        
        // Fetch data summary
        const summary = await aiClient.getDataSummary();
        setDataSummary(summary);
      } catch (error) {
        console.error('Error fetching AI data:', error);
        setConnectionStatus('error');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const tabs = [
    { id: 'chat', label: 'AI Chat', icon: Bot },
    { id: 'quick', label: 'Quick Actions', icon: Activity },
    { id: 'summary', label: 'Data Summary', icon: CheckCircle },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading AI Insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Financial Insights</h1>
          <p className="text-gray-600">
            Get intelligent insights about your financial data using AI analysis
          </p>
        </div>
        
        {/* Connection Status */}
        <div className="mt-4 md:mt-0">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
            connectionStatus === 'connected' 
              ? 'bg-green-100 text-green-800' 
              : connectionStatus === 'error'
              ? 'bg-red-100 text-red-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {connectionStatus === 'connected' && <CheckCircle className="h-4 w-4 mr-1" />}
            {connectionStatus === 'error' && <AlertCircle className="h-4 w-4 mr-1" />}
            {connectionStatus === 'checking' && <Activity className="h-4 w-4 mr-1" />}
            
            {connectionStatus === 'connected' && 'AI Service Connected'}
            {connectionStatus === 'error' && 'AI Service Unavailable'}
            {connectionStatus === 'checking' && 'Checking Connection...'}
          </div>
        </div>
      </div>

      {/* Error State */}
      {connectionStatus === 'error' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-600 mr-3" />
            <div>
              <h3 className="font-medium text-red-800">AI Service Unavailable</h3>
              <p className="text-red-700 mt-1">
                Unable to connect to the AI backend service. Please ensure the service is running on port 8000.
              </p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Data Summary Cards */}
      {dataSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Transactions</h3>
            <p className="text-2xl font-bold text-gray-900">{dataSummary.total_transactions}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Invoices</h3>
            <p className="text-2xl font-bold text-gray-900">{dataSummary.total_invoices}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-sm font-medium text-gray-600 mb-2">M-Pesa Transactions</h3>
            <p className="text-2xl font-bold text-gray-900">{dataSummary.total_mpesa_transactions}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border">
            <h3 className="text-sm font-medium text-gray-600 mb-2">Total Revenue</h3>
            <p className="text-2xl font-bold text-gray-900">
              KES {dataSummary.summary_stats.total_revenue.toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {tabs.map(tab => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="h-4 w-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'chat' && <AIChat />}
        {activeTab === 'quick' && <AIQuickActions />}
        {activeTab === 'summary' && (
          <div className="bg-white rounded-lg shadow-md border p-6">
            <h3 className="text-lg font-semibold mb-4">Data Summary</h3>
            {dataSummary ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Date Range</h4>
                    <p className="text-sm text-gray-600">
                      {dataSummary.date_range.start} to {dataSummary.date_range.end}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-700 mb-2">Average Transaction</h4>
                    <p className="text-sm text-gray-600">
                      KES {dataSummary.summary_stats.avg_transaction_amount.toLocaleString()}
                    </p>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Most Common Transaction Type</h4>
                  <p className="text-sm text-gray-600">
                    {dataSummary.summary_stats.most_common_transaction_type}
                  </p>
                </div>
                
                <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-800">
                    💡 This data summary provides an overview of your financial data available for AI analysis.
                    Use the AI Chat or Quick Actions to get deeper insights.
                  </p>
                </div>
              </div>
            ) : (
              <p className="text-gray-600">No data summary available.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
