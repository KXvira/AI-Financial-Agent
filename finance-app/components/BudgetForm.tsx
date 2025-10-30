'use client';

import { useState, useEffect } from 'react';
import { BudgetTemplate } from '@/types/budget';

interface Budget {
  id: string;
  category: string;
  subcategory?: string;
  amount: number;
  actual_spent: number;
  period_type: string;
  start_date: string;
  end_date: string;
  alert_threshold: number;
  description?: string;
  status: string;
  alert_level: string;
  created_at: string;
  updated_at: string;
}

interface BudgetFormProps {
  onClose: () => void;
  onSuccess: () => void;
  budget?: Budget; // Optional: for edit mode
  template?: BudgetTemplate | null; // Optional: for template-based creation
}

export default function BudgetForm({ onClose, onSuccess, budget, template }: BudgetFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isEditMode = !!budget;
  const isFromTemplate = !!template && !budget;

  const [formData, setFormData] = useState({
    category: budget?.category || template?.category || '',
    subcategory: budget?.subcategory || template?.subcategory || '',
    amount: budget?.amount.toString() || template?.amount.toString() || '',
    period_type: budget?.period_type || template?.period_type || 'monthly',
    start_date: budget?.start_date || new Date().toISOString().split('T')[0],
    end_date: budget?.end_date || '',
    alert_threshold: budget?.alert_threshold.toString() || template?.alert_threshold.toString() || '80',
    description: budget?.description || ''
  });

  // Auto-calculate end_date on mount if editing
  useEffect(() => {
    if (!isEditMode && !formData.end_date && formData.start_date) {
      calculateEndDate(formData.period_type, formData.start_date);
    }
  }, []);

  const calculateEndDate = (periodType: string, startDate: string) => {
    const start = new Date(startDate);
    const end = new Date(start);
    
    switch (periodType) {
      case 'weekly':
        end.setDate(end.getDate() + 7);
        break;
      case 'monthly':
        end.setMonth(end.getMonth() + 1);
        break;
      case 'quarterly':
        end.setMonth(end.getMonth() + 3);
        break;
      case 'yearly':
        end.setFullYear(end.getFullYear() + 1);
        break;
    }
    
    setFormData(prev => ({
      ...prev,
      end_date: end.toISOString().split('T')[0]
    }));
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Auto-calculate end_date based on period_type and start_date (only in create mode)
    if (!isEditMode && (name === 'period_type' || name === 'start_date')) {
      const startDate = name === 'start_date' ? value : formData.start_date;
      const periodType = name === 'period_type' ? value : formData.period_type;
      
      if (startDate && periodType) {
        calculateEndDate(periodType, startDate);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validation
      if (!formData.category.trim()) {
        throw new Error('Category is required');
      }

      const amount = parseFloat(formData.amount);
      if (isNaN(amount) || amount <= 0) {
        throw new Error('Amount must be a positive number');
      }

      const alertThreshold = parseFloat(formData.alert_threshold);
      if (isNaN(alertThreshold) || alertThreshold < 0 || alertThreshold > 100) {
        throw new Error('Alert threshold must be between 0 and 100');
      }

      if (!formData.start_date || !formData.end_date) {
        throw new Error('Start and end dates are required');
      }

      if (new Date(formData.start_date) >= new Date(formData.end_date)) {
        throw new Error('End date must be after start date');
      }

      // Prepare request body
      const requestBody = {
        category: formData.category.trim(),
        subcategory: formData.subcategory.trim() || undefined,
        amount: amount,
        period_type: formData.period_type,
        start_date: formData.start_date,
        end_date: formData.end_date,
        alert_threshold: alertThreshold,
        description: formData.description.trim() || undefined
      };

      // Submit to API
      const url = isEditMode 
        ? `http://localhost:8000/api/budgets/${budget.id}`
        : 'http://localhost:8000/api/budgets';
      
      const method = isEditMode ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Failed to ${isEditMode ? 'update' : 'create'} budget`);
      }

      // Success
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error creating budget:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full my-8">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              {isEditMode ? 'Edit Budget' : isFromTemplate ? `Create Budget from "${template?.name}" Template` : 'Create New Budget'}
            </h2>
            {isFromTemplate && (
              <p className="text-sm text-gray-600 mt-1">
                Template values are pre-filled. You can customize them before creating.
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="p-2 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100 disabled:opacity-50"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Error Message */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-red-800 text-sm font-medium">{error}</p>
              </div>
            </div>
          )}

          <div className="space-y-6">
            {/* Category */}
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                Category <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="category"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="e.g., Marketing, Salaries, Office Supplies"
              />
            </div>

            {/* Subcategory */}
            <div>
              <label htmlFor="subcategory" className="block text-sm font-medium text-gray-700 mb-2">
                Subcategory (Optional)
              </label>
              <input
                type="text"
                id="subcategory"
                name="subcategory"
                value={formData.subcategory}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                placeholder="e.g., Digital Ads, Payroll, Stationery"
              />
            </div>

            {/* Amount and Alert Threshold */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="amount" className="block text-sm font-medium text-gray-700 mb-2">
                  Budget Amount <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                  <input
                    type="number"
                    id="amount"
                    name="amount"
                    value={formData.amount}
                    onChange={handleChange}
                    required
                    min="0"
                    step="0.01"
                    className="w-full pl-8 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="alert_threshold" className="block text-sm font-medium text-gray-700 mb-2">
                  Alert Threshold <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <input
                    type="number"
                    id="alert_threshold"
                    name="alert_threshold"
                    value={formData.alert_threshold}
                    onChange={handleChange}
                    required
                    min="0"
                    max="100"
                    step="1"
                    className="w-full pr-8 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                  />
                  <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500">%</span>
                </div>
                <p className="mt-1 text-xs text-gray-500">Get warned when budget reaches this percentage</p>
              </div>
            </div>

            {/* Period Type */}
            <div>
              <label htmlFor="period_type" className="block text-sm font-medium text-gray-700 mb-2">
                Period Type <span className="text-red-500">*</span>
              </label>
              <select
                id="period_type"
                name="period_type"
                value={formData.period_type}
                onChange={handleChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              >
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
              </select>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label htmlFor="start_date" className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  id="start_date"
                  name="start_date"
                  value={formData.start_date}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>

              <div>
                <label htmlFor="end_date" className="block text-sm font-medium text-gray-700 mb-2">
                  End Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  id="end_date"
                  name="end_date"
                  value={formData.end_date}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
                />
              </div>
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows={3}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none"
                placeholder="Add any notes or details about this budget..."
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 font-medium flex items-center space-x-2"
            >
              {isSubmitting ? (
                <>
                  <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>{isEditMode ? 'Updating...' : 'Creating...'}</span>
                </>
              ) : (
                <span>{isEditMode ? 'Update Budget' : 'Create Budget'}</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
