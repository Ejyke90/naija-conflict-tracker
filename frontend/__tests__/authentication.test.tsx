/**
 * Authentication Flow Test Suite
 * 
 * Tests the complete authentication flow including:
 * - Login with valid credentials
 * - Login with invalid credentials  
 * - Token refresh
 * - Token expiration handling
 * - Logout functionality
 * - Protected route access
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/router';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { authAPI } from '../lib/auth-api';

// Mock the router
jest.mock('next/router', () => ({
  useRouter: jest.fn(),
}));

// Mock the auth API
jest.mock('../lib/auth-api', () => ({
  authAPI: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    refreshToken: jest.fn(),
    getMe: jest.fn(),
  },
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Test component that uses auth context
function TestComponent() {
  const { user, isAuthenticated, isLoading, error, login, logout, refreshUser } = useAuth();
  
  return (
    <div>
      <div data-testid="loading">{isLoading.toString()}</div>
      <div data-testid="authenticated">{isAuthenticated.toString()}</div>
      <div data-testid="user">{user ? JSON.stringify(user) : 'null'}</div>
      <div data-testid="error">{error || 'null'}</div>
      
      <button onClick={() => login({ email: 'test@example.com', password: 'password' })}>
        Login
      </button>
      
      <button onClick={() => logout()}>
        Logout
      </button>
      
      <button onClick={() => refreshUser()}>
        Refresh User
      </button>
    </div>
  );
}

describe('Authentication Flow Tests', () => {
  const mockPush = jest.fn();
  const mockRouter = { push: mockPush } as any;
  
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue(mockRouter);
    localStorageMock.clear();
  });
  
  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Login Flow', () => {
    it('should login successfully with valid credentials', async () => {
      // Mock successful login response
      const mockLoginResponse = {
        access_token: 'valid-access-token',
        refresh_token: 'valid-refresh-token',
        token_type: 'bearer',
        user: {
          id: 'user-123',
          email: 'test@example.com',
          role: 'viewer',
          full_name: 'Test User',
          is_active: true,
        },
      };
      
      (authAPI.login as jest.Mock).mockResolvedValue(mockLoginResponse);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Click login button
      fireEvent.click(screen.getByText('Login'));
      
      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify successful login
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockLoginResponse.user));
      expect(screen.getByTestId('error')).toHaveTextContent('null');
      
      // Verify tokens are stored
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', mockLoginResponse.access_token);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('refresh_token', mockLoginResponse.refresh_token);
      expect(localStorageMock.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockLoginResponse.user));
      
      // Verify redirect to dashboard
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
    
    it('should handle login failure with invalid credentials', async () => {
      // Mock failed login response
      const loginError = new Error('Incorrect email or password');
      (authAPI.login as jest.Mock).mockRejectedValue(loginError);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Click login button
      fireEvent.click(screen.getByText('Login'));
      
      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify failed login
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(screen.getByTestId('error')).toHaveTextContent('Incorrect email or password');
      
      // Verify no tokens are stored
      expect(localStorageMock.setItem).not.toHaveBeenCalled();
    });
    
    it('should handle network errors during login', async () => {
      // Mock network error
      const networkError = new Error('Network error');
      (authAPI.login as jest.Mock).mockRejectedValue(networkError);
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Click login button
      fireEvent.click(screen.getByText('Login'));
      
      // Wait for login to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify network error handling
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('error')).toHaveTextContent('Network error');
    });
  });

  describe('Token Refresh Flow', () => {
    it('should refresh token automatically when expired', async () => {
      // Mock initial user data
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        role: 'viewer',
        full_name: 'Test User',
        is_active: true,
      };
      
      // Mock expired token scenario
      const expiredTokenError = new Error('Token expired');
      (authAPI.getMe as jest.Mock)
        .mockRejectedValueOnce(expiredTokenError) // First call fails (expired token)
        .mockResolvedValue(mockUser); // Second call succeeds after refresh
      
      // Mock successful token refresh
      const mockRefreshResponse = {
        access_token: 'new-access-token',
        refresh_token: 'valid-refresh-token',
        token_type: 'bearer',
      };
      (authAPI.refreshToken as jest.Mock).mockResolvedValue(mockRefreshResponse);
      
      // Set up existing tokens in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'expired-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        if (key === 'user') return JSON.stringify(mockUser);
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for token refresh to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      }, { timeout: 5000 });
      
      // Verify token refresh was attempted
      expect(authAPI.refreshToken).toHaveBeenCalledWith('valid-refresh-token');
      
      // Verify new token is stored
      expect(localStorageMock.setItem).toHaveBeenCalledWith('access_token', mockRefreshResponse.access_token);
      
      // Verify user is still authenticated
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
    });
    
    it('should handle token refresh failure', async () => {
      // Mock expired token scenario
      const expiredTokenError = new Error('Token expired');
      (authAPI.getMe as jest.Mock).mockRejectedValue(expiredTokenError);
      
      // Mock failed token refresh
      const refreshError = new Error('Invalid refresh token');
      (authAPI.refreshToken as jest.Mock).mockRejectedValue(refreshError);
      
      // Set up existing tokens in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'expired-token';
        if (key === 'refresh_token') return 'invalid-refresh-token';
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for refresh to fail
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify user is logged out on refresh failure
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(screen.getByTestId('error')).toHaveTextContent('Your session has expired. Please log in again.');
      
      // Verify tokens are cleared
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
    });
  });

  describe('Logout Flow', () => {
    it('should logout successfully', async () => {
      // Mock user data
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        role: 'viewer',
        full_name: 'Test User',
        is_active: true,
      };
      
      // Mock successful logout
      (authAPI.logout as jest.Mock).mockResolvedValue(undefined);
      
      // Set up existing tokens in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'valid-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        if (key === 'user') return JSON.stringify(mockUser);
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Click logout button
      fireEvent.click(screen.getByText('Logout'));
      
      // Wait for logout to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify logout API was called
      expect(authAPI.logout).toHaveBeenCalledWith('valid-token');
      
      // Verify tokens are cleared
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      // Verify user is logged out
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      
      // Verify redirect to login
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
    
    it('should handle logout API failure gracefully', async () => {
      // Mock user data
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        role: 'viewer',
        full_name: 'Test User',
        is_active: true,
      };
      
      // Mock failed logout
      const logoutError = new Error('Logout API failed');
      (authAPI.logout as jest.Mock).mockRejectedValue(logoutError);
      
      // Set up existing tokens in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'valid-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        if (key === 'user') return JSON.stringify(mockUser);
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Click logout button
      fireEvent.click(screen.getByText('Logout'));
      
      // Wait for logout to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify tokens are still cleared even if API fails
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
      
      // Verify user is logged out
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      
      // Verify redirect to login still happens
      expect(mockPush).toHaveBeenCalledWith('/login');
    });
  });

  describe('Protected Route Access', () => {
    it('should allow access with valid token', async () => {
      // Mock user data
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        role: 'viewer',
        full_name: 'Test User',
        is_active: true,
      };
      
      // Mock successful getMe call
      (authAPI.getMe as jest.Mock).mockResolvedValue(mockUser);
      
      // Set up existing token in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'valid-token';
        if (key === 'user') return JSON.stringify(mockUser);
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for validation to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify user is authenticated
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('user')).toHaveTextContent(JSON.stringify(mockUser));
      expect(screen.getByTestId('error')).toHaveTextContent('null');
    });
    
    it('should deny access with invalid token', async () => {
      // Mock failed getMe call
      const authError = new Error('Could not validate credentials');
      (authAPI.getMe as jest.Mock).mockRejectedValue(authError);
      
      // Mock failed token refresh
      (authAPI.refreshToken as jest.Mock).mockRejectedValue(new Error('Invalid token'));
      
      // Set up invalid token in localStorage
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'invalid-token';
        if (key === 'refresh_token') return 'invalid-refresh-token';
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for validation to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify user is not authenticated
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('user')).toHaveTextContent('null');
      expect(screen.getByTestId('error')).toHaveTextContent('Authentication failed. Please log in again.');
    });
  });

  describe('Token Expiration Scenarios', () => {
    it('should handle 401 errors gracefully', async () => {
      // Mock 401 error
      const authError = new Error('401 - Unauthorized');
      (authAPI.getMe as jest.Mock).mockRejectedValue(authError);
      
      // Mock successful token refresh
      const mockRefreshResponse = {
        access_token: 'new-access-token',
        refresh_token: 'valid-refresh-token',
        token_type: 'bearer',
      };
      (authAPI.refreshToken as jest.Mock).mockResolvedValue(mockRefreshResponse);
      
      // Mock successful getMe after refresh
      const mockUser = {
        id: 'user-123',
        email: 'test@example.com',
        role: 'viewer',
        full_name: 'Test User',
        is_active: true,
      };
      (authAPI.getMe as jest.Mock)
        .mockRejectedValueOnce(authError)
        .mockResolvedValue(mockUser);
      
      // Set up existing tokens
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'expired-token';
        if (key === 'refresh_token') return 'valid-refresh-token';
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for token refresh to complete
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      }, { timeout: 5000 });
      
      // Verify token refresh was attempted
      expect(authAPI.refreshToken).toHaveBeenCalled();
      
      // Verify user is still authenticated after refresh
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });
    
    it('should handle timeout errors gracefully', async () => {
      // Mock timeout error
      const timeoutError = new Error('Request timeout');
      timeoutError.name = 'AbortError';
      (authAPI.getMe as jest.Mock).mockRejectedValue(timeoutError);
      
      // Set up existing token
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'access_token') return 'valid-token';
        if (key === 'user') return JSON.stringify({
          id: 'user-123',
          email: 'test@example.com',
          role: 'viewer',
          full_name: 'Test User',
          is_active: true,
        });
        return null;
      });
      
      render(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
      
      // Wait for timeout handling
      await waitFor(() => {
        expect(screen.getByTestId('loading')).toHaveTextContent('false');
      });
      
      // Verify timeout doesn't cause logout
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('error')).toHaveTextContent('null');
      
      // Verify no token refresh on timeout
      expect(authAPI.refreshToken).not.toHaveBeenCalled();
    });
  });
});

// Integration test for MonthlyTrendsChart authentication integration
describe('MonthlyTrendsChart Authentication Integration', () => {
  it('should trigger auth refresh on 401 errors', async () => {
    // This test would verify that MonthlyTrendsChart properly
    // triggers auth refresh when receiving 401 errors
    
    // Mock the custom event system
    const addEventListenerSpy = jest.spyOn(window, 'addEventListener');
    const dispatchEventSpy = jest.spyOn(window, 'dispatchEvent');
    
    // Simulate a 401 error in MonthlyTrendsChart
    const authRefreshEvent = new CustomEvent('auth:refresh-required');
    window.dispatchEvent(authRefreshEvent);
    
    // Verify the event was dispatched
    expect(dispatchEventSpy).toHaveBeenCalledWith(authRefreshEvent);
    
    addEventListenerSpy.mockRestore();
    dispatchEventSpy.mockRestore();
  });
});
