/**
 * Hook to fetch all Nigerian states from the API
 */

import { useQuery } from '@tanstack/react-query';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface State {
  id: number;
  name: string;
  population?: number;
  poverty_rate?: number;
  unemployment_rate?: number;
}

export function useStates() {
  return useQuery<string[], Error>({
    queryKey: ['states'],
    queryFn: async () => {
      const response = await fetch(`${API_URL}/api/v1/locations/states`, {
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch states');
      }
      
      const states: State[] = await response.json();
      return states.map(s => s.name).sort();
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 hours - states don't change often
    gcTime: 24 * 60 * 60 * 1000,
    retry: 2, // Reduced from 3 to fail faster
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 3000), // Exponential backoff
    throwOnError: false, // Don't throw - return undefined on error
  });
}
