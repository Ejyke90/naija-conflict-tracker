import { useState, useCallback, useMemo } from 'react';
import { subDays, subMonths, subYears, startOfYear } from 'date-fns';

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

export type DatePreset =
  | 'last7days'
  | 'last30days'
  | 'lastQuarter'
  | 'lastYear'
  | '2024'
  | '2023'
  | 'allTime';

/**
 * Hook to manage map filter state
 */
export function useMapFilters() {
  const [filters, setFilters] = useState<MapFilters>({
    dateRange: {
      start: null,
      end: null,
    },
    eventTypes: [],
    states: [],
    minFatalities: undefined,
    maxFatalities: undefined,
    showHighFatality: false,
    showMassDisplacement: false,
    showRecent: false,
  });

  const setDateRange = useCallback(
    (start: Date | null, end: Date | null) => {
      setFilters((prev) => ({
        ...prev,
        dateRange: { start, end },
      }));
    },
    []
  );

  const setDatePreset = useCallback((preset: DatePreset) => {
    const now = new Date();
    let start: Date | null = null;
    let end: Date | null = now;

    switch (preset) {
      case 'last7days':
        start = subDays(now, 7);
        break;
      case 'last30days':
        start = subDays(now, 30);
        break;
      case 'lastQuarter':
        start = subMonths(now, 3);
        break;
      case 'lastYear':
        start = subYears(now, 1);
        break;
      case '2024':
        start = new Date('2024-01-01');
        end = new Date('2024-12-31');
        break;
      case '2023':
        start = new Date('2023-01-01');
        end = new Date('2023-12-31');
        break;
      case 'allTime':
        start = null;
        end = null;
        break;
    }

    setFilters((prev) => ({
      ...prev,
      dateRange: { start, end },
    }));
  }, []);

  const toggleEventType = useCallback((eventType: string) => {
    setFilters((prev) => {
      const currentTypes = prev.eventTypes || [];
      const newTypes = currentTypes.includes(eventType)
        ? currentTypes.filter((t) => t !== eventType)
        : [...currentTypes, eventType];
      return {
        ...prev,
        eventTypes: newTypes,
      };
    });
  }, []);

  const setEventTypes = useCallback((eventTypes: string[]) => {
    setFilters((prev) => ({
      ...prev,
      eventTypes,
    }));
  }, []);

  const toggleState = useCallback((state: string) => {
    setFilters((prev) => {
      const currentStates = prev.states || [];
      const newStates = currentStates.includes(state)
        ? currentStates.filter((s) => s !== state)
        : [...currentStates, state];
      return {
        ...prev,
        states: newStates,
      };
    });
  }, []);

  const setStates = useCallback((states: string[]) => {
    setFilters((prev) => ({
      ...prev,
      states,
    }));
  }, []);

  const setFatalityRange = useCallback(
    (min?: number, max?: number) => {
      setFilters((prev) => ({
        ...prev,
        minFatalities: min,
        maxFatalities: max,
      }));
    },
    []
  );

  const toggleQuickFilter = useCallback((filterName: keyof MapFilters) => {
    setFilters((prev) => ({
      ...prev,
      [filterName]: !prev[filterName],
    }));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters({
      dateRange: {
        start: null,
        end: null,
      },
      eventTypes: [],
      states: [],
      minFatalities: undefined,
      maxFatalities: undefined,
      showHighFatality: false,
      showMassDisplacement: false,
      showRecent: false,
    });
  }, []);

  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.dateRange?.start || filters.dateRange?.end) count++;
    if (filters.eventTypes && filters.eventTypes.length > 0) count++;
    if (filters.states && filters.states.length > 0) count++;
    if (filters.minFatalities !== undefined || filters.maxFatalities !== undefined)
      count++;
    if (filters.showHighFatality) count++;
    if (filters.showMassDisplacement) count++;
    if (filters.showRecent) count++;
    return count;
  }, [filters]);

  return {
    filters,
    setFilters,
    setDateRange,
    setDatePreset,
    toggleEventType,
    setEventTypes,
    toggleState,
    setStates,
    setFatalityRange,
    toggleQuickFilter,
    clearFilters,
    activeFilterCount,
  };
}
