import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { predictionsService } from '@/services/api/predictions.service';
import { AIPredictionsData } from '@/types/predictions';

export function usePredictions(): UseQueryResult<AIPredictionsData> {
  return useQuery({
    queryKey: ['predictions', 'all'],
    queryFn: () => predictionsService.getAllPredictions(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 5 * 60 * 1000, // Auto-refetch every 5 minutes
    retry: 3,
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  });
}

export function useLocationPrediction(state: string, lga?: string) {
  return useQuery({
    queryKey: ['predictions', 'location', state, lga],
    queryFn: () => predictionsService.getPredictionByLocation(state, lga),
    enabled: !!state,
    staleTime: 5 * 60 * 1000,
  });
}
