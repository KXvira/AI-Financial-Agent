// components/auth/ProtectedRoute.tsx
// Component to protect routes based on authentication and roles

'use client';

import { ReactNode } from 'react';
import { useAuth, useRequireRole } from '../../contexts/AuthContext';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRoles?: string[];
  fallback?: ReactNode;
}

export default function ProtectedRoute({ 
  children, 
  requiredRoles = [], 
  fallback 
}: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const { canAccess, userRole } = useRequireRole(requiredRoles);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/login';
    }
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  // Check role-based access if required roles are specified
  if (requiredRoles.length > 0 && !canAccess) {
    return fallback || (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="mb-4">
            <svg className="mx-auto h-12 w-12 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-4">
            You need {requiredRoles.join(' or ')} role to access this page.
          </p>
          <p className="text-sm text-gray-500">
            Your current role: <span className="font-medium capitalize">{userRole}</span>
          </p>
          <div className="mt-6">
            <button
              onClick={() => window.history.back()}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  // User is authenticated and has required role, render children
  return <>{children}</>;
}

// Higher-order component version
export function withProtectedRoute<T extends {}>(
  Component: React.ComponentType<T>,
  requiredRoles?: string[]
) {
  return function ProtectedComponent(props: T) {
    return (
      <ProtectedRoute requiredRoles={requiredRoles}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}