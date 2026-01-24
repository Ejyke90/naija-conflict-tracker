import { useState, useEffect, useCallback } from 'react';
import useSWR from 'swr';
import type { ConflictEvent } from '../lib/map/clustering';

export interface MapFilters {
  dateRange?: {
    start: Date | null;
    end: Date | null;
  };
  eventTypes?: string[];
  states?: string[];
  minFatalities?: number;
  maxFatalities?: number;
  showHighFatality?: boolean;
  showMassDisplacement?: boolean;
  showRecent?: boolean;
}

interface UseMapDataOptions {
  filters?: MapFilters;
  refreshInterval?: number;
}

const fetcher = async (url: string) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error('Failed to fetch map data');
  }
  return response.json();
};

/**
 * Hook to fetch and manage conflict event data for the map
 */
export function useMapData(options: UseMapDataOptions = {}) {
  const { filters = {}, refreshInterval = 60000 } = options; // Refresh every minute
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Build query parameters from filters
  const buildQueryParams = useCallback(() => {
    const params = new URLSearchParams();
    params.append('limit', '10000'); // Get all events for map

    if (filters.dateRange?.start) {
      params.append('start_date', filters.dateRange.start.toISOString());
    }
    if (filters.dateRange?.end) {
      params.append('end_date', filters.dateRange.end.toISOString());
    }
    if (filters.eventTypes && filters.eventTypes.length > 0) {
      // Note: Backend may need to support multiple event types
      params.append('conflict_type', filters.eventTypes.join(','));
    }
    if (filters.states && filters.states.length > 0) {
      params.append('state', filters.states.join(','));
    }

    return params.toString();
  }, [filters]);

  const queryString = buildQueryParams();
  const endpoint = `${apiUrl}/api/v1/conflicts?${queryString}`;

  const { data, error, isLoading, mutate } = useSWR<any[]>(
    endpoint,
    fetcher,
    {
      refreshInterval,
      revalidateOnFocus: false,
      dedupingInterval: 30000,
    }
  );

  // Transform API data to ConflictEvent format
  const events: ConflictEvent[] = (data || [])
    .map((item: any) => {
      // Handle different possible coordinate field names
      const latitude = item.latitude || item.lat || null;
      const longitude = item.longitude || item.lng || item.lon || null;

      if (!latitude || !longitude) {
        return null;
      }

      // Calculate total fatalities
      const fatalities =
        item.fatalities ||
        (item.fatalities_male || 0) +
          (item.fatalities_female || 0) +
          (item.fatalities_unknown || 0) ||
        0;

      const injured =
        item.injured ||
        (item.injured_male || 0) +
          (item.injured_female || 0) +
          (item.injured_unknown || 0) ||
        0;

      const kidnapped =
        item.kidnapped ||
        (item.kidnapped_male || 0) +
          (item.kidnapped_female || 0) +
          (item.kidnapped_unknown || 0) ||
        0;

      // Extract actors from different possible fields
      const actors: string[] = [];
      if (item.perpetrator_group) actors.push(item.perpetrator_group);
      if (item.target_group) actors.push(item.target_group);
      if (item.actor1) actors.push(item.actor1);
      if (item.actor2) actors.push(item.actor2);
      if (item.actor3) actors.push(item.actor3);

      return {
        id: item.id,
        latitude,
        longitude,
        event_type: item.event_type || item.conflict_type || 'Other',
        fatalities,
        injured,
        kidnapped,
        displaced: item.displaced || 0,
        state: item.state,
        lga: item.lga,
        community: item.community,
        event_date: item.event_date || item.date_occurred,
        description: item.description,
        actors: actors.filter(Boolean),
        source: item.source,
        source_url: item.source_url,
      } as ConflictEvent;
    })
    .filter(Boolean) as ConflictEvent[];

  // Apply client-side filters that can't be done on backend
  const filteredEvents = events.filter((event) => {
    if (filters.minFatalities && event.fatalities < filters.minFatalities) {
      return false;
    }
    if (filters.maxFatalities && event.fatalities > filters.maxFatalities) {
      return false;
    }
    if (filters.showHighFatality && event.fatalities < 10) {
      return false;
    }
    if (filters.showMassDisplacement && (event.displaced || 0) < 100) {
      return false;
    }
    if (filters.showRecent) {
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      const eventDate = new Date(event.event_date);
      if (eventDate < thirtyDaysAgo) {
        return false;
      }
    }
    return true;
  });

  return {
    events: filteredEvents,
    isLoading,
    error,
    refresh: mutate,
    totalCount: filteredEvents.length,
    lastUpdated: new Date().toISOString(),
  };
}
