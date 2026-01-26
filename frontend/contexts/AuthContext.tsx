/**
 * AuthContext - Global authentication state management
 * 
 * Provides:
 * - User state and loading states
 * - Login/logout/register functions
 * - Token management (localStorage)
 * - Auto token refresh
 * - Protected route utilities
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/router';
import { authAPI, User, LoginCredentials, RegisterData, LoginResponse } from '@/lib/auth-api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USER_KEY = 'user';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  /**
   * Get token from localStorage
   */
  const getStoredToken = useCallback(() => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(TOKEN_KEY);
  }, []);

  /**
   * Get refresh token from localStorage
   */
  const getStoredRefreshToken = useCallback(() => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }, []);

  /**
   * Store tokens in localStorage
   */
  const storeTokens = useCallback((accessToken: string, refreshToken: string) => {
    localStorage.setItem(TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  }, []);

  /**
   * Store user in localStorage and state
   */
  const storeUser = useCallback((userData: User) => {
    localStorage.setItem(USER_KEY, JSON.stringify(userData));
    setUser(userData);
  }, []);

  /**
   * Clear all auth data
   */
  const clearAuthData = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    setUser(null);
  }, []);

  /**
   * Refresh user data from API
   */
  const refreshUser = useCallback(async () => {
    const token = getStoredToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    try {
      const userData = await authAPI.getMe(token);
      storeUser(userData);
      setError(null);
    } catch (err) {
      console.error('Failed to refresh user:', err);
      // Token might be expired, try refresh
      const refreshToken = getStoredRefreshToken();
      if (refreshToken) {
        try {
          const tokens = await authAPI.refreshToken(refreshToken);
          storeTokens(tokens.access_token, tokens.refresh_token);
          // Retry getting user
          const userData = await authAPI.getMe(tokens.access_token);
          storeUser(userData);
          setError(null);
        } catch (refreshErr) {
          console.error('Token refresh failed:', refreshErr);
          clearAuthData();
        }
      } else {
        clearAuthData();
      }
    } finally {
      setIsLoading(false);
    }
  }, [getStoredToken, getStoredRefreshToken, storeTokens, storeUser, clearAuthData]);

  /**
   * Login function
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true);
    setError(null);

    try {
      const response: LoginResponse = await authAPI.login(credentials);
      
      // Store tokens and user
      storeTokens(response.access_token, response.refresh_token);
      storeUser(response.user);
      
      setError(null);
      
      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router, storeTokens, storeUser]);

  /**
   * Register function
   */
  const register = useCallback(async (data: RegisterData) => {
    setIsLoading(true);
    setError(null);

    try {
      await authAPI.register(data);
      setError(null);
      
      // Redirect to login page
      router.push('/login?registered=true');
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.message || 'Registration failed');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  /**
   * Logout function
   */
  const logout = useCallback(async () => {
    setIsLoading(true);

    try {
      const token = getStoredToken();
      if (token) {
        // Call logout endpoint to blacklist token
        await authAPI.logout(token);
      }
    } catch (err) {
      console.error('Logout error:', err);
      // Continue with local logout even if API call fails
    } finally {
      clearAuthData();
      setIsLoading(false);
      router.push('/login');
    }
  }, [getStoredToken, clearAuthData, router]);

  /**
   * Clear error
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  /**
   * Initialize auth state on mount
   */
  useEffect(() => {
    // Load user from localStorage on mount
    const storedUser = localStorage.getItem(USER_KEY);
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (err) {
        console.error('Failed to parse stored user:', err);
        clearAuthData();
      }
    }

    // Refresh user from API to validate token
    refreshUser();
  }, [refreshUser, clearAuthData]);

  /**
   * Auto-refresh token every 50 minutes (before 1 hour expiry)
   */
  useEffect(() => {
    if (!user) return;

    const interval = setInterval(async () => {
      const refreshToken = getStoredRefreshToken();
      if (refreshToken) {
        try {
          const tokens = await authAPI.refreshToken(refreshToken);
          storeTokens(tokens.access_token, tokens.refresh_token);
          console.log('Token auto-refreshed');
        } catch (err) {
          console.error('Auto token refresh failed:', err);
          // Don't logout on auto-refresh failure, user might be offline
        }
      }
    }, 50 * 60 * 1000); // 50 minutes

    return () => clearInterval(interval);
  }, [user, getStoredRefreshToken, storeTokens]);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshUser,
    clearError,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

/**
 * Hook to use auth context
 */
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

/**
 * Get access token for API calls
 */
export const getAccessToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
};

/**
 * Check if user has required role
 */
export const hasRole = (user: User | null, requiredRole: 'admin' | 'analyst' | 'viewer'): boolean => {
  if (!user) return false;
  
  const roleHierarchy = {
    viewer: 1,
    analyst: 2,
    admin: 3,
  };
  
  return roleHierarchy[user.role] >= roleHierarchy[requiredRole];
};
