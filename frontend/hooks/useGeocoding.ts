import { useState, useCallback } from 'react';

interface UseGeocoding {
  search: (query: string) => Promise<any[]>;
  isSearching: boolean;
  error: string | null;
}

/**
 * Hook for geocoding and location search using Mapbox Geocoding API
 */
export function useGeocoding(accessToken: string): UseGeocoding {
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const search = useCallback(
    async (query: string) => {
      if (!query || query.length < 3) {
        return [];
      }

      setIsSearching(true);
      setError(null);

      try {
        // Bias search towards Nigeria
        const country = 'ng'; // Nigeria ISO code
        const endpoint = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(
          query
        )}.json`;

        const params = new URLSearchParams({
          access_token: accessToken,
          country,
          limit: '5',
          types: 'place,locality,district,region',
        });

        const response = await fetch(`${endpoint}?${params.toString()}`);

        if (!response.ok) {
          throw new Error('Geocoding request failed');
        }

        const data = await response.json();
        return data.features || [];
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : 'Failed to search location';
        setError(errorMessage);
        return [];
      } finally {
        setIsSearching(false);
      }
    },
    [accessToken]
  );

  return {
    search,
    isSearching,
    error,
  };
}
