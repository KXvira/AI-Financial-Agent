// components/AIQuickActions.tsx
"use client";

import { useState } from 'react';
import { TrendingUp, FileText, DollarSign, BarChart3, Loader2 } from 'lucide-react';
import { aiClient, AIResponse } from '../utils/aiApi';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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
                      {result.confidence ? `Confidence: ${Math.round(result.confidence * 100)}%` : 'AI Analysis'} • 
                      {result.timestamp ? new Date(result.timestamp).toLocaleString() : new Date().toLocaleString()}
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
                
                <div className="markdown-content text-sm leading-relaxed">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Style headers
                      h1: ({ node, ...props }) => (
                        <h1 className="text-xl font-bold text-gray-900 mb-3 mt-4 pb-2 border-b border-gray-200" {...props} />
                      ),
                      h2: ({ node, ...props }) => (
                        <h2 className="text-lg font-semibold text-gray-900 mb-2 mt-3" {...props} />
                      ),
                      h3: ({ node, ...props }) => (
                        <h3 className="text-base font-semibold text-gray-800 mb-2 mt-2" {...props} />
                      ),
                      
                      // Style paragraphs
                      p: ({ node, ...props }) => (
                        <p className="text-gray-700 mb-3" {...props} />
                      ),
                      
                      // Style lists
                      ul: ({ node, ...props }) => (
                        <ul className="space-y-2 mb-3 ml-4 list-disc" {...props} />
                      ),
                      ol: ({ node, ...props }) => (
                        <ol className="space-y-2 mb-3 ml-4 list-decimal" {...props} />
                      ),
                      li: ({ node, ...props }) => (
                        <li className="text-gray-700 pl-2" {...props} />
                      ),
                      
                      // Style strong/bold text
                      strong: ({ node, ...props }) => (
                        <strong className="font-semibold text-gray-900" {...props} />
                      ),
                      
                      // Style emphasis/italic text
                      em: ({ node, ...props }) => (
                        <em className="italic text-gray-800" {...props} />
                      ),
                      
                      // Style code blocks
                      code: ({ node, inline, ...props }: any) => 
                        inline ? (
                          <code className="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded text-xs font-mono" {...props} />
                        ) : (
                          <code className="block bg-gray-900 text-gray-100 p-3 rounded-lg text-xs font-mono overflow-x-auto mb-3" {...props} />
                        ),
                      
                      // Style tables
                      table: ({ node, ...props }) => (
                        <div className="overflow-x-auto mb-3">
                          <table className="min-w-full divide-y divide-gray-200 border border-gray-200 rounded-lg" {...props} />
                        </div>
                      ),
                      thead: ({ node, ...props }) => (
                        <thead className="bg-gray-50" {...props} />
                      ),
                      tbody: ({ node, ...props }) => (
                        <tbody className="bg-white divide-y divide-gray-200" {...props} />
                      ),
                      tr: ({ node, ...props }) => (
                        <tr className="hover:bg-gray-50" {...props} />
                      ),
                      th: ({ node, ...props }) => (
                        <th className="px-4 py-2 text-left text-xs font-semibold text-gray-900 uppercase tracking-wider" {...props} />
                      ),
                      td: ({ node, ...props }) => (
                        <td className="px-4 py-2 text-sm text-gray-700" {...props} />
                      ),
                      
                      // Style blockquotes
                      blockquote: ({ node, ...props }) => (
                        <blockquote className="border-l-4 border-blue-500 pl-4 py-2 italic text-gray-700 bg-blue-50 rounded-r mb-3" {...props} />
                      ),
                      
                      // Style links
                      a: ({ node, ...props }) => (
                        <a className="text-blue-600 hover:text-blue-800 underline" {...props} />
                      ),
                    }}
                  >
                    {result.answer}
                  </ReactMarkdown>
                </div>
                
                {result.sources && result.sources.length > 0 && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-blue-900 mb-2">� Data Sources:</h5>
                    <ul className="space-y-1">
                      {result.sources.map((source, idx) => (
                        <li key={idx} className="text-sm text-blue-800">
                          • {source}
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
