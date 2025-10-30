// utils/authApi.ts
// Authentication API Client for backend communication

import Cookies from 'js-cookie';
import { 
  LoginCredentials, 
  RegisterData, 
  AuthResponse, 
  User, 
  PasswordChange,
  AuditLog 
} from '../types/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const AUTH_BASE_URL = `${API_BASE_URL}/api/auth`;

// Token management
const TOKEN_KEY = 'fintrack_access_token';
const REFRESH_TOKEN_KEY = 'fintrack_refresh_token';

export class AuthAPIError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'AuthAPIError';
  }
}

export class AuthAPI {
  // Token management methods
  static getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return Cookies.get(TOKEN_KEY) || localStorage.getItem(TOKEN_KEY) || null;
  }

  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return Cookies.get(REFRESH_TOKEN_KEY) || localStorage.getItem(REFRESH_TOKEN_KEY) || null;
  }

  static setTokens(accessToken: string, refreshToken: string): void {
    if (typeof window === 'undefined') return;
    
    // Store in both cookies (secure) and localStorage (fallback)
    const cookieOptions = {
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict' as const,
      expires: 7 // 7 days for refresh token
    };

    Cookies.set(TOKEN_KEY, accessToken, { ...cookieOptions, expires: 1/24 }); // 1 hour
    Cookies.set(REFRESH_TOKEN_KEY, refreshToken, cookieOptions);
    
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }

  static clearTokens(): void {
    if (typeof window === 'undefined') return;
    
    Cookies.remove(TOKEN_KEY);
    Cookies.remove(REFRESH_TOKEN_KEY);
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  // Generic request method with automatic token handling
  private static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${AUTH_BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add authorization header if token exists
    if (token && !endpoint.includes('/register') && !endpoint.includes('/login')) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle token expiry
      if (response.status === 401 && token) {
        // Try to refresh token
        const refreshed = await this.tryRefreshToken();
        if (refreshed) {
          // Retry original request with new token
          headers['Authorization'] = `Bearer ${this.getToken()}`;
          const retryResponse = await fetch(url, {
            ...options,
            headers,
          });
          
          if (!retryResponse.ok) {
            throw new AuthAPIError(
              'Request failed after token refresh',
              retryResponse.status
            );
          }
          
          return retryResponse.json();
        } else {
          // Refresh failed, redirect to login
          this.clearTokens();
          if (typeof window !== 'undefined') {
            window.location.href = '/auth/login';
          }
          throw new AuthAPIError('Session expired', 401);
        }
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new AuthAPIError(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof AuthAPIError) {
        throw error;
      }
      throw new AuthAPIError(
        'Network error or server unavailable',
        0,
        { originalError: error }
      );
    }
  }

  // Token refresh method
  private static async tryRefreshToken(): Promise<boolean> {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) return false;

      const response = await fetch(`${AUTH_BASE_URL}/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      this.setTokens(data.access_token, data.refresh_token);
      return true;
    } catch {
      return false;
    }
  }

  // Authentication endpoints
  static async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // Store tokens after successful registration
    this.setTokens(response.access_token, response.refresh_token);
    
    return response;
  }

  static async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    // Store tokens after successful login
    this.setTokens(response.access_token, response.refresh_token);
    
    return response;
  }

  static async logout(): Promise<void> {
    try {
      // Call logout endpoint if we have a token
      if (this.getToken()) {
        await this.request('/logout', { method: 'POST' });
      }
    } catch (error) {
      // Ignore logout errors, still clear local tokens
      console.warn('Logout API call failed:', error);
    } finally {
      this.clearTokens();
    }
  }

  static async getCurrentUser(): Promise<User> {
    return this.request<User>('/me');
  }

  static async updateProfile(data: Partial<User>): Promise<{ message: string; user: User }> {
    return this.request(`/me`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static async changePassword(data: PasswordChange): Promise<{ message: string }> {
    return this.request('/change-password', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async refreshTokens(): Promise<void> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      throw new AuthAPIError('No refresh token available', 401);
    }

    const response = await this.request<{ access_token: string; refresh_token: string }>('/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    this.setTokens(response.access_token, response.refresh_token);
  }

  static async getAuditLogs(limit = 50, skip = 0): Promise<{
    logs: AuditLog[];
    total: number;
    limit: number;
    skip: number;
  }> {
    return this.request(`/audit-logs?limit=${limit}&skip=${skip}`);
  }

  static async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request('/health');
  }

  // Check if user is authenticated
  static isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Get user role from token (basic client-side check)
  static getUserRole(): string | null {
    const token = this.getToken();
    if (!token) return null;

    try {
      // Basic JWT decode (not secure, just for UI purposes)
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.role || null;
    } catch {
      return null;
    }
  }
}

export default AuthAPI;