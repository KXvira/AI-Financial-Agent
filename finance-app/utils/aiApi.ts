// utils/aiApi.ts
// AI Financial Insights API Client

const API_BASE_URL = 'http://localhost:8000';

// API Response Types
export interface AIResponse {
  response: string;
  confidence: number;
  sources: string[];
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  database?: string;
  gemini_api?: string;
  timestamp: string;
  error?: string;
}

export interface DataSummaryResponse {
  total_transactions: number;
  total_invoices: number;
  mpesa_transactions: number;
  pending_invoices: number;
  total_revenue: string;
  pending_amount: string;
}

// AI API Client Class
export class AIFinancialInsightsClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Generic request method with authentication
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    // Get authentication token if available
    const token = typeof window !== 'undefined' ? 
      document.cookie.split('; ').find(row => row.startsWith('fintrack_access_token='))?.split('=')[1] ||
      localStorage.getItem('fintrack_access_token') : null;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if token exists
    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      // If unauthorized, might need to refresh token or redirect to login
      if (response.status === 401 && typeof window !== 'undefined') {
        // Clear tokens and redirect to login
        document.cookie = 'fintrack_access_token=; Max-Age=0';
        document.cookie = 'fintrack_refresh_token=; Max-Age=0';
        localStorage.removeItem('fintrack_access_token');
        localStorage.removeItem('fintrack_refresh_token');
        window.location.href = '/auth/login';
      }
      
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async checkHealth(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/ai/health');
  }

  // Ask AI question
  async askQuestion(question: string): Promise<AIResponse> {
    return this.request<AIResponse>('/ai/ask', {
      method: 'POST',
      body: JSON.stringify({ query: question }),
    });
  }

  // Get financial insights (generic)
  async getFinancialInsights(): Promise<AIResponse> {
    return this.askQuestion("Provide me with general financial insights based on my data.");
  }

  // Get transaction analysis
  async getTransactionAnalysis(): Promise<AIResponse> {
    return this.askQuestion("Analyze my recent transactions and spending patterns.");
  }

  // Get invoice insights
  async getInvoiceInsights(): Promise<AIResponse> {
    return this.askQuestion("Analyze my invoices and billing patterns.");
  }

  // Get cash flow analysis
  async getCashFlowAnalysis(): Promise<AIResponse> {
    return this.askQuestion("Analyze my cash flow and provide insights.");
  }

  // Get data summary
  async getDataSummary(): Promise<DataSummaryResponse> {
    return this.request<DataSummaryResponse>('/ai/data-summary');
  }
}

// Export a default instance
export const aiClient = new AIFinancialInsightsClient();

// Hook for React components
export const useAIInsights = () => {
  return {
    client: aiClient,
    // Add any additional hooks or utilities here
  };
};
