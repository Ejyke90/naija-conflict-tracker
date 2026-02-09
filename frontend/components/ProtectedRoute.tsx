/**
 * ProtectedRoute Component
 * 
 * Wraps pages that require authentication
 * Redirects to login if user is not authenticated
 * Supports role-based access control (RBAC)
 * 
 * Usage:
 * <ProtectedRoute>
 *   <YourComponent />
 * </ProtectedRoute>
 * 
 * With role requirement:
 * <ProtectedRoute requiredRole="analyst">
 *   <AnalyticsPage />
 * </ProtectedRoute>
 */

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { useAuth, hasRole } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'admin' | 'analyst' | 'viewer';
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole = 'viewer',
  redirectTo = '/login',
}) => {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuth();
  const [slowLoad, setSlowLoad] = useState(false);

  useEffect(() => {
    // Wait for auth state to load
    if (isLoading) return;

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      router.push(`${redirectTo}?redirect=${encodeURIComponent(router.asPath)}`);
      return;
    }

    // Check role requirement
    if (requiredRole && !hasRole(user, requiredRole)) {
      // User doesn't have required role - redirect to unauthorized page
      router.push('/unauthorized');
      return;
    }
  }, [isAuthenticated, isLoading, user, requiredRole, redirectTo, router]);

  // Track if loading is taking too long (more than 5 seconds)
  useEffect(() => {
    if (!isLoading) {
      setSlowLoad(false);
      return;
    }

    const timer = setTimeout(() => {
      setSlowLoad(true);
    }, 5000);

    return () => clearTimeout(timer);
  }, [isLoading]);

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md">
          <svg
            className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4"
            viewBox="0 0 24 24"
            fill="none"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="text-gray-600">Loading...</p>
          {slowLoad && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-xs text-yellow-700">
                The authentication service is taking longer than expected. This usually happens when:
              </p>
              <ul className="text-xs text-yellow-700 mt-2 space-y-1 text-left">
                <li>• Backend server is starting up</li>
                <li>• Database migrations are running</li>
                <li>• Network connection is slow</li>
              </ul>
              <p className="text-xs text-yellow-700 mt-3">
                Please wait a moment or refresh the page.
              </p>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Don't render children if not authenticated or insufficient role
  if (!isAuthenticated || (requiredRole && !hasRole(user, requiredRole))) {
    return null;
  }

  // Render children if authenticated and has required role
  return <>{children}</>;
};

export default ProtectedRoute;
