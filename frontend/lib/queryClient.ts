import { QueryClient } from '@tanstack/react-query';

/**
 * Global QueryClient instance for server-side and utility functions
 * 
 * Note: This is separate from the QueryClient created in _app.tsx
 * to avoid hydration issues. Use this for:
 * - Server-side prefetching
 * - Utility functions that need to access the query cache
 * - Functions outside of React components
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});
