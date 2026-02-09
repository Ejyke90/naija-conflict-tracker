/**
 * API Client Utility
 * Provides fetch wrapper with timeout support for all API calls
 *
 * Note: Uses relative URLs that are proxied by Next.js rewrites to the backend API
 */

const REQUEST_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_REQUEST_TIMEOUT || '15000', 10);

/**
 * Fetch wrapper with configurable timeout
 * @param url - API endpoint URL
 * @param options - Fetch options
 * @param timeout - Timeout in milliseconds (uses REQUEST_TIMEOUT env var if not provided)
 */
export async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeout: number = REQUEST_TIMEOUT
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    return await fetch(url, {
      ...options,
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw new Error(`Request timeout after ${timeout / 1000}s`);
    }
    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
}

/**
 * Build a full API URL (deprecated - now just returns relative endpoint)
 * @param endpoint - API endpoint path (e.g., "/api/v1/conflicts/heatmap")
 */
export function buildApiUrl(endpoint: string): string {
  return endpoint;
}

/**
 * Fetch JSON response with timeout
 */
export async function fetchJson<T>(
  url: string,
  options: RequestInit = {},
  timeout?: number
): Promise<T> {
  const response = await fetchWithTimeout(url, options, timeout);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

const apiClient = {
  fetchWithTimeout,
  buildApiUrl,
  fetchJson,
};

export default apiClient;
