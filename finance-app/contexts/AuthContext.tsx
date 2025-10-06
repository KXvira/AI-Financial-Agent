// contexts/AuthContext.tsx
// React Context for authentication state management

'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, AuthContextType, LoginCredentials, RegisterData, PasswordChange } from '../types/auth';
import AuthAPI, { AuthAPIError } from '../utils/authApi';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Initialize auth state on mount
  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    try {
      setLoading(true);
      
      // Check if user has valid token
      if (AuthAPI.isAuthenticated()) {
        const userData = await AuthAPI.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth initialization failed:', error);
      // Clear invalid tokens
      AuthAPI.clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<void> => {
    try {
      setLoading(true);
      const response = await AuthAPI.login(credentials);
      setUser(response.user);
    } catch (error) {
      setUser(null);
      throw error; // Re-throw for component error handling
    } finally {
      setLoading(false);
    }
  };

  const register = async (data: RegisterData): Promise<void> => {
    try {
      setLoading(true);
      const response = await AuthAPI.register(data);
      setUser(response.user);
    } catch (error) {
      setUser(null);
      throw error; // Re-throw for component error handling
    } finally {
      setLoading(false);
    }
  };

  const logout = async (): Promise<void> => {
    try {
      setLoading(true);
      await AuthAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
      // Continue with local logout even if API call fails
    } finally {
      setUser(null);
      setLoading(false);
      
      // Redirect to login page
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
  };

  const refreshToken = async (): Promise<void> => {
    try {
      await AuthAPI.refreshTokens();
      // Optionally refresh user data
      if (user) {
        const userData = await AuthAPI.getCurrentUser();
        setUser(userData);
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      // If refresh fails, log out user
      await logout();
      throw error;
    }
  };

  const updateProfile = async (data: Partial<User>): Promise<void> => {
    try {
      const response = await AuthAPI.updateProfile(data);
      setUser(response.user);
    } catch (error) {
      throw error; // Re-throw for component error handling
    }
  };

  const changePassword = async (data: PasswordChange): Promise<void> => {
    try {
      await AuthAPI.changePassword(data);
      // Password change doesn't update user object
    } catch (error) {
      throw error; // Re-throw for component error handling
    }
  };

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(async () => {
      try {
        await refreshToken();
      } catch (error) {
        console.error('Auto token refresh failed:', error);
        // This will trigger logout in refreshToken function
      }
    }, 25 * 60 * 1000); // Refresh every 25 minutes (token expires in 30)

    return () => clearInterval(interval);
  }, [user]);

  const contextValue: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    refreshToken,
    updateProfile,
    changePassword,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

// Higher-order component for protecting routes
export function withAuth<T extends {}>(Component: React.ComponentType<T>) {
  return function AuthenticatedComponent(props: T) {
    const { user, loading } = useAuth();

    if (loading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      );
    }

    if (!user) {
      // Redirect to login if not authenticated
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
      return null;
    }

    return <Component {...props} />;
  };
}

// Hook for role-based access control
export function useRequireRole(requiredRoles: string[]) {
  const { user } = useAuth();
  
  const hasRole = user && requiredRoles.includes(user.role);
  const canAccess = hasRole;
  
  return { canAccess, userRole: user?.role || null };
}

export default AuthContext;