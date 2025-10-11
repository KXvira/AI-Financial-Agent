// hooks/useDashboard.ts
import { useState, useEffect, useCallback } from 'react';
import { AuthAPI } from '../utils/authApi';

export interface DashboardStats {
  total_invoices: number;
  total_invoices_count: number;
  invoices_change_percent: number;
  payments_received: number;
  payments_count: number;
  payments_change_percent: number;
  outstanding_balance: number;
  outstanding_change_percent: number;
  daily_cash_flow: number;
  cash_flow_change_percent: number;
  period_start?: string;
  period_end?: string;
}

export interface RecentPayment {
  reference: string;
  client: string;
  amount: number;
  currency: string;
  date: string;
  status: string;
}

export interface DashboardData {
  statistics: DashboardStats;
  recent_payments: RecentPayment[];
  recent_transactions: any[];
  total_expenses: number;
  expenses_change_percent: number;
}

interface UseDashboardResult {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export const useDashboard = (periodDays: number = 30): UseDashboardResult => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDashboard = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Try to get token, but don't fail if it's not available
      const token = AuthAPI.getToken();
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(
        `http://localhost:8000/api/dashboard/stats?period_days=${periodDays}`,
        { headers }
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }

      const dashboardData: DashboardData = await response.json();
      setData(dashboardData);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load dashboard data');
      
      // Set default empty data on error
      setData({
        statistics: {
          total_invoices: 0,
          total_invoices_count: 0,
          invoices_change_percent: 0,
          payments_received: 0,
          payments_count: 0,
          payments_change_percent: 0,
          outstanding_balance: 0,
          outstanding_change_percent: 0,
          daily_cash_flow: 0,
          cash_flow_change_percent: 0,
        },
        recent_payments: [],
        recent_transactions: [],
        total_expenses: 0,
        expenses_change_percent: 0,
      });
    } finally {
      setLoading(false);
    }
  }, [periodDays]);

  useEffect(() => {
    fetchDashboard();
  }, [fetchDashboard]);

  return {
    data,
    loading,
    error,
    refetch: fetchDashboard,
  };
};

// Utility function to format currency
export const formatCurrency = (amount: number, currency: string = 'KES'): string => {
  return `${currency} ${amount.toLocaleString('en-KE', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
};

// Utility function to format percentage
export const formatPercentage = (percent: number): string => {
  const sign = percent >= 0 ? '+' : '';
  return `${sign}${percent.toFixed(1)}%`;
};
