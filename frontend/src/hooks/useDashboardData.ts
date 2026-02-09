/**
 * Optimized Dashboard Data Hook
 * 
 * Replaces 5-6 individual API calls with a single batched request
 * Includes:
 * - Automatic caching (React Query)
 * - Background refetching every 5 minutes
 * - Error boundaries
 * - Loading states
 */

import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { authAPI } from './auth-api';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface MonthlyTrend {
  month: string;
  incidents: number;
  fatalities: number;
}

export interface Hotspot {
  state: string;
  lga: string;
  incident_count: number;
  fatalities: number;
}

export interface Archetype {
  archetype_name: string;
  incidents: number;
  fatalities: number;
}

export interface DashboardStatistics {
  total_incidents: number;
  total_fatalities: number;
  states_affected: number;
  lgas_affected: number;
}

export interface DashboardData {
  timeRange: {
    start: string;
    end: string;
    monthsBack: number;
  };
  state: string;
  monthlyTrends: MonthlyTrend[];
  hotspots: Hotspot[];
  archetypes: Archetype[];
  statistics: DashboardStatistics;
  generatedAt: string;
  cached: boolean;
}

export interface UseDashboardDataOptions {
  state?: string;
  monthsBack?: number;
  enabled?: boolean;
  refetchInterval?: number;  // In milliseconds
}

/**
 * Fetch dashboard overview data (single API call)
 */
async function fetchDashboardData(
  state?: string,
  monthsBack: number = 12
): Promise<DashboardData> {
  const params = new URLSearchParams({
    months_back: monthsBack.toString(),
  });

  if (state) {
    params.append('state', state);
  }

  const token = authAPI.getToken();
  const response = await fetch(`${API_URL}/api/v1/dashboard/overview?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Failed to fetch dashboard data' }));
    throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Optimized hook for dashboard data with React Query caching
 * 
 * Benefits:
 * - Single API call instead of 5-6
 * - Automatic caching (5 minutes stale time)
 * - Background refetching
 * - Request deduplication
 * - Automatic retries on failure
 * 
 * @example
 * ```tsx
 * const { data, isLoading, error } = useDashboardData({ 
 *   state: 'Borno',
 *   monthsBack: 12 
 * });
 * ```
 */
export function useDashboardData(
  options: UseDashboardDataOptions = {}
): UseQueryResult<DashboardData, Error> {
  const {
    state,
    monthsBack = 12,
    enabled = true,
    refetchInterval = 5 * 60 * 1000, // 5 minutes default
  } = options;

  return useQuery<DashboardData, Error>({
    queryKey: ['dashboard', 'overview', state || 'all', monthsBack],
    queryFn: () => fetchDashboardData(state, monthsBack),
    enabled,
    staleTime: 5 * 60 * 1000, // Consider data fresh for 5 minutes
    gcTime: 10 * 60 * 1000, // Cache for 10 minutes (formerly cacheTime)
    refetchInterval, // Auto-refresh every 5 minutes
    refetchOnWindowFocus: false, // Don't refetch on tab focus
    retry: 2, // Retry failed requests twice
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Exponential backoff
  });
}

/**
 * Prefetch dashboard data (useful for login screen)
 * Call this before navigating to dashboard for instant load
 * 
 * @example
 * ```tsx
 * // On login success
 * await prefetchDashboardData();
 * router.push('/dashboard');
 * ```
 */
export async function prefetchDashboardData(
  state?: string,
  monthsBack: number = 12
): Promise<void> {
  const { queryClient } = await import('@/lib/queryClient');
  
  await queryClient.prefetchQuery({
    queryKey: ['dashboard', 'overview', state || 'all', monthsBack],
    queryFn: () => fetchDashboardData(state, monthsBack),
    staleTime: 5 * 60 * 1000,
  });
}

/**
 * Invalidate dashboard cache (force refetch)
 * Useful after creating/updating conflict data
 * 
 * @example
 * ```tsx
 * await createConflict(newData);
 * invalidateDashboardCache(); // Force dashboard refresh
 * ```
 */
export async function invalidateDashboardCache(): Promise<void> {
  const { queryClient } = await import('@/lib/queryClient');
  
  await queryClient.invalidateQueries({
    queryKey: ['dashboard'],
  });
}
