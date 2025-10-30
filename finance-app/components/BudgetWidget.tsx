'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Budget {
  id: string;
  category: string;
  amount: number;
  actual_spent: number;
  alert_level: string;
  period_type: string;
}

interface BudgetSummary {
  total_budgets: number;
  budgets_warning: number;
  budgets_critical: number;
  budgets_exceeded: number;
}

export default function BudgetWidget() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [summary, setSummary] = useState<BudgetSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [budgetsRes, summaryRes] = await Promise.all([
        fetch('http://localhost:8000/api/budgets'),
        fetch('http://localhost:8000/api/budgets/summary')
      ]);

      if (budgetsRes.ok) {
        const budgetsData = await budgetsRes.json();
        // Sort by utilization (highest first) and take top 3
        const sortedBudgets = budgetsData
          .map((b: Budget) => ({
            ...b,
            utilization: b.amount > 0 ? (b.actual_spent / b.amount) * 100 : 0
          }))
          .sort((a: any, b: any) => b.utilization - a.utilization)
          .slice(0, 3);
        setBudgets(sortedBudgets);
      }

      if (summaryRes.ok) {
        const summaryData = await summaryRes.json();
        setSummary(summaryData);
      }
    } catch (error) {
      console.error('Error fetching budget data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getProgressBarColor = (alertLevel: string) => {
    switch (alertLevel) {
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

  const alertsCount = summary 
    ? summary.budgets_warning + summary.budgets_critical + summary.budgets_exceeded
    : 0;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 animate-pulse">
        <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
        <div className="space-y-3">
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
          <div className="h-16 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
          </svg>
          <h3 className="text-lg font-bold text-gray-900">Budget Overview</h3>
        </div>
        <Link 
          href="/budgets"
          className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center space-x-1"
        >
          <span>View All</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>

      {/* Alert Badge */}
      {alertsCount > 0 && (
        <div className="mb-4 px-4 py-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span className="text-sm font-semibold text-red-800">
              {alertsCount} budget{alertsCount !== 1 ? 's' : ''} need attention
            </span>
          </div>
        </div>
      )}

      {/* Budgets List */}
      {budgets.length > 0 ? (
        <div className="space-y-4">
          {budgets.map((budget: any) => (
            <div key={budget.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-2">
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900">{budget.category}</h4>
                  <p className="text-xs text-gray-500 capitalize">{budget.period_type}</p>
                </div>
                {budget.alert_level !== 'none' && (
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    budget.alert_level === 'exceeded' ? 'bg-red-100 text-red-800' :
                    budget.alert_level === 'critical' ? 'bg-orange-100 text-orange-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {budget.alert_level}
                  </span>
                )}
              </div>

              {/* Progress Bar */}
              <div className="mb-2">
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${getProgressBarColor(budget.alert_level)}`}
                    style={{ width: `${Math.min(budget.utilization, 100)}%` }}
                  />
                </div>
              </div>

              {/* Budget Details */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">
                  ${budget.actual_spent.toLocaleString()} / ${budget.amount.toLocaleString()}
                </span>
                <span className={`font-semibold ${
                  budget.utilization > 100 ? 'text-red-600' : 'text-gray-700'
                }`}>
                  {budget.utilization.toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          <svg className="mx-auto h-12 w-12 text-gray-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <p className="text-sm">No budgets created yet</p>
          <Link 
            href="/budgets"
            className="mt-3 inline-block text-sm text-blue-600 hover:text-blue-700 font-medium"
          >
            Create your first budget →
          </Link>
        </div>
      )}

      {/* Summary Stats */}
      {summary && summary.total_budgets > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-gray-900">{summary.total_budgets}</p>
              <p className="text-xs text-gray-600">Total Budgets</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-red-600">{alertsCount}</p>
              <p className="text-xs text-gray-600">Alerts</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
