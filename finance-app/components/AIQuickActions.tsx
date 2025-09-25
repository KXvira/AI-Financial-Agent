// components/AIQuickActions.tsx
"use client";

import { useState } from 'react';
import { TrendingUp, FileText, DollarSign, BarChart3, Loader2 } from 'lucide-react';
import { aiClient, AIResponse } from '../utils/aiApi';

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  action: () => Promise<AIResponse>;
  color: string;
}

export default function AIQuickActions() {
  const [isLoading, setIsLoading] = useState<string | null>(null);
  const [results, setResults] = useState<{ [key: string]: AIResponse }>({});

  const quickActions: QuickAction[] = [
    {
      id: 'insights',
      title: 'Financial Insights',
      description: 'Get overall financial health analysis',
      icon: TrendingUp,
      action: () => aiClient.getFinancialInsights(),
      color: 'bg-blue-500'
    },
    {
      id: 'transactions',
      title: 'Transaction Analysis',
      description: 'Analyze recent transaction patterns',
      icon: BarChart3,
      action: () => aiClient.getTransactionAnalysis(),
      color: 'bg-green-500'
    },
    {
      id: 'invoices',
      title: 'Invoice Insights',
      description: 'Review invoice status and patterns',
      icon: FileText,
      action: () => aiClient.getInvoiceInsights(),
      color: 'bg-purple-500'
    },
    {
      id: 'cashflow',
      title: 'Cash Flow Analysis',
      description: 'Analyze cash flow trends and predictions',
      icon: DollarSign,
      action: () => aiClient.getCashFlowAnalysis(),
      color: 'bg-orange-500'
    }
  ];

  const handleAction = async (actionId: string, actionFn: () => Promise<AIResponse>) => {
    setIsLoading(actionId);
    try {
      const result = await actionFn();
      setResults(prev => ({
        ...prev,
        [actionId]: result
      }));
    } catch (error) {
      console.error(`Error executing ${actionId}:`, error);
      // You might want to show an error message to the user
    } finally {
      setIsLoading(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Quick Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {quickActions.map((action) => {
          const Icon = action.icon;
          const isActionLoading = isLoading === action.id;
          
          return (
            <button
              key={action.id}
              onClick={() => handleAction(action.id, action.action)}
              disabled={isLoading !== null}
              className="p-4 bg-white rounded-lg shadow-md border hover:shadow-lg transition-shadow duration-200 text-left disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <div className="flex items-center mb-3">
                <div className={`p-2 rounded-lg ${action.color} text-white mr-3`}>
                  {isActionLoading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">{action.title}</h3>
                </div>
              </div>
              <p className="text-sm text-gray-600">{action.description}</p>
            </button>
          );
        })}
      </div>

      {/* Results Section */}
      {Object.keys(results).length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-800">Analysis Results</h3>
          
          {Object.entries(results).map(([actionId, result]) => {
            const action = quickActions.find(a => a.id === actionId);
            if (!action) return null;
            
            const Icon = action.icon;
            
            return (
              <div key={actionId} className="bg-white rounded-lg shadow-md border p-6">
                <div className="flex items-center mb-4">
                  <div className={`p-2 rounded-lg ${action.color} text-white mr-3`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-gray-800">{action.title}</h4>
                    <p className="text-sm text-gray-600">
                      Confidence: {Math.round(result.confidence * 100)}% • 
                      {new Date(result.metadata.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => setResults(prev => {
                      const newResults = { ...prev };
                      delete newResults[actionId];
                      return newResults;
                    })}
                    className="text-gray-400 hover:text-gray-600 text-sm"
                  >
                    ✕
                  </button>
                </div>
                
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {result.response}
                  </p>
                </div>
                
                {result.insights && result.insights.length > 0 && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-2">💡 Key Insights:</h5>
                    <ul className="space-y-1">
                      {result.insights.map((insight, idx) => (
                        <li key={idx} className="text-sm text-blue-800">
                          • {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
