'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import BudgetCard from '@/components/BudgetCard';
import BudgetForm from '@/components/BudgetForm';

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

interface BudgetSummary {
  total_budgets: number;
  total_budgeted: number;
  total_spent: number;
  total_remaining: number;
  average_utilization: number;
  budgets_exceeded: number;
  budgets_on_track: number;
  budgets_warning: number;
  budgets_critical: number;
}

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [summary, setSummary] = useState<BudgetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    fetchBudgets();
    fetchSummary();
  }, []);

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/budgets');
      
      if (!response.ok) {
        throw new Error('Failed to fetch budgets');
      }

      const data = await response.json();
      setBudgets(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error('Error fetching budgets:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/budgets/summary');
      
      if (!response.ok) {
        throw new Error('Failed to fetch summary');
      }

      const data = await response.json();
      setSummary(data);
    } catch (err) {
      console.error('Error fetching summary:', err);
    }
  };

  const handleBudgetCreated = () => {
    setShowCreateForm(false);
    fetchBudgets();
    fetchSummary();
  };

  const handleBudgetDeleted = () => {
    fetchBudgets();
    fetchSummary();
  };

  const getUtilizationPercentage = (budget: Budget) => {
    return budget.amount > 0 ? (budget.actual_spent / budget.amount) * 100 : 0;
  };

  const filteredBudgets = budgets.filter(budget => {
    if (filterStatus === 'all') return true;
    if (filterStatus === 'exceeded') return budget.alert_level === 'exceeded';
    if (filterStatus === 'critical') return budget.alert_level === 'critical';
    if (filterStatus === 'warning') return budget.alert_level === 'warning';
    if (filterStatus === 'on-track') return budget.alert_level === 'none';
    return true;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Budget Management
              </h1>
              <p className="text-gray-600">
                Track and manage your budgets across different categories
              </p>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center space-x-2"
            >
              <span className="text-xl">+</span>
              <span>Create Budget</span>
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Budgeted</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${summary.total_budgeted.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Remaining</p>
                  <p className="text-2xl font-bold text-gray-900">
                    ${summary.total_remaining.toLocaleString()}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Avg. Utilization</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {summary.average_utilization.toFixed(1)}%
                  </p>
                </div>
                <div className="p-3 bg-orange-100 rounded-lg">
                  <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-red-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Needs Attention</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {summary.budgets_critical + summary.budgets_exceeded}
                  </p>
                </div>
                <div className="p-3 bg-red-100 rounded-lg">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterStatus === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            All ({budgets.length})
          </button>
          <button
            onClick={() => setFilterStatus('on-track')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterStatus === 'on-track'
                ? 'bg-green-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            On Track ({summary?.budgets_on_track || 0})
          </button>
          <button
            onClick={() => setFilterStatus('warning')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterStatus === 'warning'
                ? 'bg-yellow-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Warning ({summary?.budgets_warning || 0})
          </button>
          <button
            onClick={() => setFilterStatus('critical')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterStatus === 'critical'
                ? 'bg-orange-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Critical ({summary?.budgets_critical || 0})
          </button>
          <button
            onClick={() => setFilterStatus('exceeded')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filterStatus === 'exceeded'
                ? 'bg-red-600 text-white'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            Exceeded ({summary?.budgets_exceeded || 0})
          </button>
        </div>

        {/* Error State */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-red-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-semibold text-red-800">Error Loading Budgets</h3>
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            </div>
            <button
              onClick={fetchBudgets}
              className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map(i => (
              <div key={i} className="bg-white rounded-lg shadow-md p-6 animate-pulse">
                <div className="h-6 bg-gray-200 rounded mb-4"></div>
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-8 bg-gray-200 rounded mb-4"></div>
                <div className="h-20 bg-gray-200 rounded"></div>
              </div>
            ))}
          </div>
        ) : (
          <>
            {/* Budgets Grid */}
            {filteredBudgets.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredBudgets.map(budget => (
                  <BudgetCard
                    key={budget.id}
                    budget={budget}
                    onDelete={handleBudgetDeleted}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 bg-white rounded-lg shadow-md">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">No budgets found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  {filterStatus === 'all' 
                    ? 'Get started by creating a new budget.' 
                    : 'No budgets match the selected filter.'}
                </p>
                {filterStatus === 'all' && (
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Create Budget
                  </button>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Budget Modal */}
      {showCreateForm && (
        <BudgetForm
          onClose={() => setShowCreateForm(false)}
          onSuccess={handleBudgetCreated}
        />
      )}
    </div>
  );
}
