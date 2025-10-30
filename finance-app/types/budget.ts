export interface Budget {
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

export interface BudgetSummary {
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

export interface BudgetTemplate {
  id: string;
  name: string;
  description?: string;
  category: string;
  subcategory?: string;
  amount: number;
  period_type: string;
  alert_threshold: number;
  is_default: boolean;
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface BudgetTemplateCreate {
  name: string;
  description?: string;
  category: string;
  subcategory?: string;
  amount: number;
  period_type: string;
  alert_threshold: number;
}
