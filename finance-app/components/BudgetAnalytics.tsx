'use client';

import { useEffect, useState } from 'react';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  PointElement,
  LineElement
);

interface Budget {
  id: string;
  category: string;
  amount: number;
  actual_spent: number;
  alert_level: string;
  period_type: string;
}

export default function BudgetAnalytics() {
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBudgets();
  }, []);

  const fetchBudgets = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/budgets');
      if (response.ok) {
        const data = await response.json();
        setBudgets(data);
      }
    } catch (error) {
      console.error('Error fetching budgets:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-64 bg-gray-200 rounded"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (budgets.length === 0) {
    return null;
  }

  // Budget vs Actual Bar Chart Data
  const barChartData = {
    labels: budgets.map(b => b.category),
    datasets: [
      {
        label: 'Budgeted Amount',
        data: budgets.map(b => b.amount),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1
      },
      {
        label: 'Actual Spent',
        data: budgets.map(b => b.actual_spent),
        backgroundColor: budgets.map(b => {
          const utilization = (b.actual_spent / b.amount) * 100;
          if (utilization > 100) return 'rgba(239, 68, 68, 0.8)'; // red
          if (utilization > 80) return 'rgba(251, 146, 60, 0.8)'; // orange
          if (utilization > 50) return 'rgba(234, 179, 8, 0.8)'; // yellow
          return 'rgba(34, 197, 94, 0.8)'; // green
        }),
        borderWidth: 1
      }
    ]
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Budget vs Actual Spending',
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.dataset.label}: KSh ${context.parsed.y.toLocaleString()}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  // Utilization Doughnut Chart Data
  const utilizationData = budgets.map(b => ({
    category: b.category,
    utilization: Math.min((b.actual_spent / b.amount) * 100, 100),
    alert_level: b.alert_level
  }));

  const doughnutChartData = {
    labels: utilizationData.map(d => d.category),
    datasets: [
      {
        label: 'Utilization %',
        data: utilizationData.map(d => d.utilization),
        backgroundColor: utilizationData.map(d => {
          if (d.alert_level === 'exceeded') return 'rgba(239, 68, 68, 0.8)';
          if (d.alert_level === 'critical') return 'rgba(251, 146, 60, 0.8)';
          if (d.alert_level === 'warning') return 'rgba(234, 179, 8, 0.8)';
          return 'rgba(34, 197, 94, 0.8)';
        }),
        borderColor: '#fff',
        borderWidth: 2
      }
    ]
  };

  const doughnutChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
      title: {
        display: true,
        text: 'Budget Utilization Distribution',
        font: {
          size: 16,
          weight: 'bold' as const
        }
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `${context.label}: ${context.parsed.toFixed(1)}%`;
          }
        }
      }
    }
  };

  // Category Spending Breakdown
  const totalSpent = budgets.reduce((sum, b) => sum + b.actual_spent, 0);
  const totalBudget = budgets.reduce((sum, b) => sum + b.amount, 0);

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mt-8">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Budget Analytics</h2>
        <p className="text-gray-600">Visual insights into your budget performance</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <p className="text-sm text-blue-600 font-medium mb-1">Total Budgeted</p>
          <p className="text-2xl font-bold text-blue-900">${totalBudget.toLocaleString()}</p>
        </div>
        <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
          <p className="text-sm text-orange-600 font-medium mb-1">Total Spent</p>
          <p className="text-2xl font-bold text-orange-900">${totalSpent.toLocaleString()}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <p className="text-sm text-green-600 font-medium mb-1">Overall Utilization</p>
          <p className="text-2xl font-bold text-green-900">
            {totalBudget > 0 ? ((totalSpent / totalBudget) * 100).toFixed(1) : 0}%
          </p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        {/* Bar Chart */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div style={{ height: '350px' }}>
            <Bar data={barChartData} options={barChartOptions} />
          </div>
        </div>

        {/* Doughnut Chart */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div style={{ height: '350px' }}>
            <Doughnut data={doughnutChartData} options={doughnutChartOptions} />
          </div>
        </div>
      </div>

      {/* Detailed Breakdown Table */}
      <div className="overflow-x-auto">
        <h3 className="text-lg font-bold text-gray-900 mb-4">Detailed Breakdown</h3>
        <table className="min-w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Category
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Budgeted
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Spent
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Remaining
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Utilization
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {budgets.map((budget) => {
              const remaining = budget.amount - budget.actual_spent;
              const utilization = (budget.actual_spent / budget.amount) * 100;
              
              return (
                <tr key={budget.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="text-sm font-medium text-gray-900">{budget.category}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${budget.amount.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${budget.actual_spent.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={remaining >= 0 ? 'text-green-600' : 'text-red-600'}>
                      ${Math.abs(remaining).toLocaleString()}
                      {remaining < 0 && ' over'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className={`h-2 rounded-full ${
                            budget.alert_level === 'exceeded' ? 'bg-red-500' :
                            budget.alert_level === 'critical' ? 'bg-orange-500' :
                            budget.alert_level === 'warning' ? 'bg-yellow-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${Math.min(utilization, 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{utilization.toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      budget.alert_level === 'exceeded' ? 'bg-red-100 text-red-800' :
                      budget.alert_level === 'critical' ? 'bg-orange-100 text-orange-800' :
                      budget.alert_level === 'warning' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {budget.alert_level === 'none' ? 'On Track' : budget.alert_level}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
