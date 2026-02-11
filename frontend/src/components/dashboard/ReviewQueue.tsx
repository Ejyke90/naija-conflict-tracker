'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { format } from 'date-fns';

interface PendingConflict {
  id: number;
  incidence_date: string | null;
  conflict_type: string;
  description: string;
  state_id: number | null;
  state_name: string | null;
  total_deaths: number;
  total_kidnapped: number;
  created_at: string | null;
}

interface VerificationResponse {
  success: boolean;
  message: string;
  conflict_id: number;
  verified_by: {
    id: number;
    email: string;
    role: string;
  };
  verified_at: string;
}

function ReviewItem({ conflict }: { conflict: PendingConflict }) {
  const queryClient = useQueryClient();

  const mutation = useMutation<VerificationResponse, Error, number>({
    mutationFn: (conflictId: number) => 
      fetch(`/api/v1/conflicts/${conflictId}/verify`, { 
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      }).then(res => {
        if (!res.ok) {
          throw new Error('Failed to verify conflict');
        }
        return res.json();
      }),
    onSuccess: (data: VerificationResponse) => {
      // Automatically refreshes the queue and the dashboard summary!
      queryClient.invalidateQueries({ queryKey: ['validation-summary'] });
      queryClient.invalidateQueries({ queryKey: ['pending-conflicts'] });
      console.log('Conflict verified successfully:', data);
    },
    onError: (error: Error) => {
      console.error('Failed to verify conflict:', error);
      // You could show a toast notification here
    },
  });

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown date';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return 'Invalid date';
    }
  };

  return (
    <div className="flex items-center justify-between p-4 border-b border-white/10 hover:bg-tactical-slate-light/20 transition-colors">
      <div className="max-w-[70%]">
        <h4 className="typography-label font-bold text-tactical-e-ink uppercase text-xs tracking-tight">
          {conflict.conflict_type} • {formatDate(conflict.incidence_date)}
          {conflict.state_name && ` • ${conflict.state_name}`}
        </h4>
        <p className="typography-body text-sm text-tactical-e-ink/80 truncate mt-1">
          {conflict.description}
        </p>
        <div className="flex gap-2 mt-2 flex-wrap">
          {conflict.total_deaths > 0 && (
            <span className="typography-mono text-[10px] signal_critical px-2 py-0.5 rounded font-medium">
              💀 {conflict.total_deaths} Fatalities
            </span>
          )}
          {conflict.total_kidnapped > 0 && (
            <span className="typography-mono text-[10px] signal_high px-2 py-0.5 rounded font-medium">
              👤 {conflict.total_kidnapped} Kidnapped
            </span>
          )}
        </div>
      </div>
      
      <button 
        disabled={mutation.isPending}
        onClick={() => mutation.mutate(conflict.id)}
        className="px-4 py-2 bg-tactical-blue text-tactical-e-ink typography-label text-xs font-bold rounded hover:bg-tactical-blue/80 disabled:opacity-50 disabled:cursor-not-allowed transition-all active:scale-[0.98] min-w-[80px]"
      >
        {mutation.isPending ? (
          <span className="flex items-center justify-center">
            <svg className="animate-spin h-3 w-3 mr-1" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
            </svg>
            Verifying
          </span>
        ) : (
          'Verify'
        )}
      </button>
    </div>
  );
}

export default function ReviewQueue() {
  const { data, isLoading, error, refetch } = useQuery<PendingConflict[]>({
    queryKey: ['pending-conflicts'],
    queryFn: () => 
      fetch('/api/v1/conflicts/pending?limit=20', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        }
      }).then(res => {
        if (!res.ok) {
          throw new Error('Failed to fetch pending conflicts');
        }
        return res.json();
      }),
    refetchInterval: 30000, // Refresh every 30 seconds
    staleTime: 25000,
  });

  if (isLoading) {
    return (
      <div className="glass-card rounded-xl border border-white/10 overflow-hidden font-sans">
        <div className="p-4 border-b border-white/10">
          <h3 className="typography-heading font-bold text-tactical-e-ink flex items-center gap-2">
            <span>🔍</span> Review Queue
          </h3>
        </div>
        <div className="divide-y divide-white/10">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="p-4 animate-pulse">
              <div className="flex justify-between">
                <div className="flex-1">
                  <div className="h-3 bg-slate-200 rounded w-3/4 mb-2"></div>
                  <div className="h-2 bg-slate-200 rounded w-1/2 mb-2"></div>
                  <div className="flex gap-2">
                    <div className="h-4 bg-slate-200 rounded w-16"></div>
                    <div className="h-4 bg-slate-200 rounded w-12"></div>
                  </div>
                </div>
                <div className="h-8 bg-slate-200 rounded w-16"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glass-card rounded-xl border border-white/10 overflow-hidden font-sans">
        <div className="p-4 border-b border-red-500/30">
          <h3 className="typography-heading font-bold text-tactical-e-ink flex items-center gap-2">
            <span>🔍</span> Review Queue
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-red-400 mb-2">⚠️</div>
          <p className="typography-body text-tactical-e-ink/70 font-medium">Unable to load review queue</p>
          <button 
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-tactical-blue text-tactical-e-ink typography-label text-sm rounded hover:bg-tactical-blue/80"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="glass-card rounded-xl border border-white/10 overflow-hidden font-sans">
        <div className="p-4 border-b border-green-500/30">
          <h3 className="typography-heading font-bold text-tactical-e-ink flex items-center gap-2">
            <span>🔍</span> Review Queue
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-green-400 mb-2 text-4xl">✅</div>
          <p className="typography-body text-tactical-e-ink/70 font-medium">All caught up!</p>
          <p className="typography-body text-tactical-e-ink/50 text-sm mt-1">No incidents pending verification</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl border border-white/10 overflow-hidden font-sans">
      <div className="p-4 border-b border-white/10 flex justify-between items-center">
        <h3 className="typography-heading font-bold text-tactical-e-ink flex items-center gap-2">
          <span>🔍</span> Review Queue
          <span className="typography-mono text-xs bg-tactical-blue/20 text-tactical-blue px-2 py-0.5 rounded-full">
            {data.length} pending
          </span>
        </h3>
        <button
          onClick={() => refetch()}
          className="typography-body text-xs text-tactical-e-ink/50 hover:text-tactical-e-ink transition-colors"
        >
          Refresh
        </button>
      </div>
      
      <div className="max-h-96 overflow-y-auto">
        {data.map((conflict) => (
          <ReviewItem key={conflict.id} conflict={conflict} />
        ))}
      </div>
      
      {data.length >= 20 && (
        <div className="p-3 bg-tactical-slate-light/10 text-center">
          <p className="typography-body text-xs text-tactical-e-ink/50">
            Showing first 20 of many pending incidents
          </p>
        </div>
      )}
    </div>
  );
}
