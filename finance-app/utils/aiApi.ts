// utils/aiApi.ts
// AI Financial Insights API Client

const API_BASE_URL = 'http://localhost:8002';

// API Response Types
export interface AIResponse {
  response: string;
  confidence: number;
  sources: string[];
  timestamp: string;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
  database_connected: boolean;
}

// AI API Client Class
export class AIFinancialInsightsClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} - ${response.statusText}`);
    }

    return response.json();
  }

  // Health check
  async checkHealth(): Promise<HealthCheckResponse> {
    return this.request<HealthCheckResponse>('/health');
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
