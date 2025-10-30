'use client';

import { useState } from 'react';

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

interface BudgetCardProps {
  budget: Budget;
  onDelete: () => void;
  onEdit: () => void;
}

export default function BudgetCard({ budget, onDelete, onEdit }: BudgetCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const utilization = budget.amount > 0 ? (budget.actual_spent / budget.amount) * 100 : 0;
  const remaining = budget.amount - budget.actual_spent;

  const getAlertColor = () => {
    switch (budget.alert_level) {
      case 'exceeded':
        return 'border-red-500 bg-red-50';
      case 'critical':
        return 'border-orange-500 bg-orange-50';
      case 'warning':
        return 'border-yellow-500 bg-yellow-50';
      default:
        return 'border-green-500 bg-white';
    }
  };

  const getAlertBadgeColor = () => {
    switch (budget.alert_level) {
      case 'exceeded':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'critical':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getProgressBarColor = () => {
    switch (budget.alert_level) {
      case 'exceeded':
        return 'bg-red-500';
      case 'critical':
        return 'bg-orange-500';
      case 'warning':
        return 'bg-yellow-500';
      default:
        return 'bg-green-500';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getPeriodIcon = () => {
    switch (budget.period_type) {
      case 'weekly':
        return '📅';
      case 'monthly':
        return '🗓️';
      case 'quarterly':
        return '📊';
      case 'yearly':
        return '🎯';
      default:
        return '📋';
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/budgets/${budget.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete budget');
      }

      onDelete();
      setShowDeleteConfirm(false);
    } catch (error) {
      console.error('Error deleting budget:', error);
      alert('Failed to delete budget. Please try again.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <>
      <div className={`rounded-lg shadow-md p-6 border-l-4 ${getAlertColor()} transition-all hover:shadow-lg`}>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-2xl">{getPeriodIcon()}</span>
              <h3 className="text-lg font-bold text-gray-900">{budget.category}</h3>
            </div>
            {budget.subcategory && (
              <p className="text-sm text-gray-600 ml-9">{budget.subcategory}</p>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={onEdit}
              className="p-2 text-gray-400 hover:text-blue-600 transition-colors rounded-lg hover:bg-blue-50"
              title="Edit budget"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onClick={() => setShowDeleteConfirm(true)}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors rounded-lg hover:bg-red-50"
              title="Delete budget"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Alert Badge */}
        {budget.alert_level !== 'none' && (
          <div className={`inline-block px-3 py-1 rounded-full text-xs font-semibold border mb-4 ${getAlertBadgeColor()}`}>
            {budget.alert_level.toUpperCase()}
          </div>
        )}

        {/* Budget Amount */}
        <div className="mb-4">
          <div className="flex items-baseline justify-between mb-2">
            <span className="text-2xl font-bold text-gray-900">
              KSh {budget.actual_spent.toLocaleString()}
            </span>
            <span className="text-sm text-gray-600">
              of KSh {budget.amount.toLocaleString()}
            </span>
          </div>
          
          {/* Progress Bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${getProgressBarColor()}`}
              style={{ width: `${Math.min(utilization, 100)}%` }}
            />
          </div>
          
          <div className="flex items-center justify-between mt-2 text-sm">
            <span className={`font-semibold ${utilization > 100 ? 'text-red-600' : 'text-gray-700'}`}>
              {utilization.toFixed(1)}% used
            </span>
            <span className={remaining >= 0 ? 'text-green-600' : 'text-red-600'}>
              {remaining >= 0 ? `KSh ${remaining.toLocaleString()} left` : `KSh ${Math.abs(remaining).toLocaleString()} over`}
            </span>
          </div>
        </div>

        {/* Period Info */}
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span className="capitalize">{budget.period_type}</span>
            </div>
            <div>
              {formatDate(budget.start_date)} - {formatDate(budget.end_date)}
            </div>
          </div>

          {budget.description && (
            <p className="mt-3 text-sm text-gray-600 italic">
              {budget.description}
            </p>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <div className="flex items-center mb-4">
              <div className="p-3 bg-red-100 rounded-full mr-4">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">Delete Budget</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Are you sure you want to delete the "{budget.category}" budget?
                </p>
              </div>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-6">
              <p className="text-sm text-yellow-800">
                This action cannot be undone. All budget data will be permanently removed.
              </p>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center space-x-2"
              >
                {isDeleting ? (
                  <>
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Deleting...</span>
                  </>
                ) : (
                  <span>Delete Budget</span>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
