/**
 * Shared API Response Types
 * Used across all dashboard API endpoints
 */

/**
 * Standard API response format for all dashboard endpoints
 * Provides consistent error handling and graceful degradation
 */
export interface ApiResponse<T> {
  /** Response status: 'ok' (fresh data), 'degraded' (cached data), 'error' (failure) */
  status: 'ok' | 'degraded' | 'error';
  
  /** The actual data payload */
  data: T[];
  
  /** Optional message explaining the response (useful for empty data or errors) */
  message: string | null;
  
  /** Whether the data comes from cache instead of fresh database query */
  cached: boolean;
  
  /** ISO8601 timestamp when the cached data was last updated, null if fresh */
  cached_at: string | null;

  /** Optional pagination metadata for large datasets */
  pagination?: {
    total_items: number;
    page_size: number;
    offset: number;
  };
}

/**
 * Type guard to check if response is ApiResponse format
 */
export function isApiResponse<T>(value: any): value is ApiResponse<T> {
  return (
    value &&
    typeof value === 'object' &&
    ('status' in value) &&
    ('data' in value) &&
    ('cached' in value)
  );
}

/**
 * Helper to format cached_at timestamp for display
 */
export function formatCachedTime(isoString: string | null): string {
  if (!isoString) return '';
  
  try {
    const date = new Date(isoString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  } catch {
    return isoString;
  }
}
