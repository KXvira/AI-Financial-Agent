'use client';

import { useState, useEffect } from 'react';
import { BudgetTemplate } from '@/types/budget';

interface TemplateLibraryProps {
  onClose: () => void;
  onSelectTemplate: (template: BudgetTemplate) => void;
}

export default function TemplateLibrary({ onClose, onSelectTemplate }: TemplateLibraryProps) {
  const [templates, setTemplates] = useState<BudgetTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/budget-templates');
      if (!response.ok) throw new Error('Failed to fetch templates');
      const data = await response.json();
      setTemplates(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const categories = ['all', ...new Set(templates.map(t => t.category))];
  
  const filteredTemplates = selectedCategory === 'all' 
    ? templates 
    : templates.filter(t => t.category === selectedCategory);

  const getPeriodIcon = (periodType: string) => {
    switch (periodType) {
      case 'weekly': return '📅';
      case 'monthly': return '🗓️';
      case 'quarterly': return '📊';
      case 'yearly': return '🎯';
      default: return '📋';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Budget Templates</h2>
            <p className="text-sm text-gray-600 mt-1">Choose a template to quickly create a budget</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Category Filter */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg font-medium transition-all capitalize ${
                  selectedCategory === category
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {category}
              </button>
            ))}
          </div>
        </div>

        {/* Templates Grid */}
        <div className="p-6 max-h-96 overflow-y-auto">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-gray-100 rounded-lg p-6 animate-pulse">
                  <div className="h-6 bg-gray-200 rounded mb-4"></div>
                  <div className="h-4 bg-gray-200 rounded mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded mb-4"></div>
                  <div className="h-10 bg-gray-200 rounded"></div>
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={fetchTemplates}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          ) : filteredTemplates.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTemplates.map(template => (
                <div
                  key={template.id}
                  className="border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-all cursor-pointer hover:border-blue-500"
                  onClick={() => onSelectTemplate(template)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-2xl">{getPeriodIcon(template.period_type)}</span>
                      <h3 className="text-lg font-bold text-gray-900">{template.name}</h3>
                    </div>
                    {template.is_default && (
                      <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded-full">
                        Default
                      </span>
                    )}
                  </div>

                  {template.subcategory && (
                    <p className="text-sm text-gray-600 mb-2">{template.subcategory}</p>
                  )}

                  {template.description && (
                    <p className="text-sm text-gray-600 mb-4">{template.description}</p>
                  )}

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Amount:</span>
                      <span className="font-semibold text-gray-900">
                        ${template.amount.toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Period:</span>
                      <span className="font-semibold text-gray-900 capitalize">
                        {template.period_type}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Alert Threshold:</span>
                      <span className="font-semibold text-gray-900">
                        {template.alert_threshold}%
                      </span>
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSelectTemplate(template);
                    }}
                    className="mt-4 w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Use This Template
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No templates found in this category</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              💡 Templates provide pre-configured budgets. You can customize amounts and dates after selection.
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
