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
      const response = await fetch(`${API_URL}/api/v1/locations/states`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch states');
      }
      
      const states: State[] = await response.json();
      return states.map(s => s.name).sort();
    },
    staleTime: 24 * 60 * 60 * 1000, // 24 hours - states don't change often
    gcTime: 24 * 60 * 60 * 1000,
    retry: 3,
  });
}
