'use client';

import { useState } from 'react';
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

interface BulkVerificationResponse {
  success: boolean;
  message: string;
  count: number;
  verified_by: {
    id: number;
    email: string;
    role: string;
  };
  verified_ids: number[];
  verified_at: string;
}

export default function BulkReviewQueue() {
  const [selected, setSelected] = useState<number[]>([]);
  const queryClient = useQueryClient();

  // Get current user ID from localStorage or context
  const getCurrentUserId = () => {
    // In a real app, you'd get this from auth context
    // For now, we'll let the backend use the authenticated user
    return null;
  };

  const { data, isLoading, error, refetch } = useQuery<PendingConflict[]>({
    queryKey: ['pending-conflicts'],
    queryFn: () => 
      fetch('/api/v1/conflicts/pending?limit=50', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
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

  const bulkMutation = useMutation<BulkVerificationResponse, Error, number[]>({
    mutationFn: (ids: number[]) => 
      fetch('/api/v1/conflicts/bulk-verify', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          ids, 
          userId: getCurrentUserId()
        })
      }).then(res => {
        if (!res.ok) {
          throw new Error('Failed to bulk verify conflicts');
        }
        return res.json();
      }),
    onSuccess: (data: BulkVerificationResponse) => {
      setSelected([]);
      queryClient.invalidateQueries({ queryKey: ['validation-summary'] });
      queryClient.invalidateQueries({ queryKey: ['pending-conflicts'] });
      console.log('Bulk verification successful:', data);
    },
    onError: (error: Error) => {
      console.error('Failed to bulk verify conflicts:', error);
    },
  });

  const toggleSelect = (id: number) => {
    setSelected(prev => 
      prev.includes(id) 
        ? prev.filter(i => i !== id) 
        : [...prev, id]
    );
  };

  const toggleSelectAll = () => {
    if (data && data.length > 0) {
      setSelected(
        selected.length === data.length 
          ? [] 
          : data.map(item => item.id)
      );
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Unknown date';
    try {
      return format(new Date(dateString), 'MMM d, yyyy');
    } catch {
      return 'Invalid date';
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
        <div className="p-4 border-b bg-slate-50">
          <h3 className="font-bold text-slate-700 flex items-center gap-2">
            <span>📋</span> Bulk Review Queue
          </h3>
        </div>
        <div className="divide-y">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="p-4 animate-pulse">
              <div className="flex items-center gap-4">
                <div className="w-5 h-5 bg-slate-200 rounded"></div>
                <div className="flex-1">
                  <div className="h-3 bg-slate-200 rounded w-3/4 mb-2"></div>
                  <div className="h-2 bg-slate-200 rounded w-1/2"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
        <div className="p-4 border-b bg-red-50">
          <h3 className="font-bold text-slate-700 flex items-center gap-2">
            <span>📋</span> Bulk Review Queue
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-red-600 mb-2">⚠️</div>
          <p className="text-slate-500 font-medium">Unable to load review queue</p>
          <button 
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
        <div className="p-4 border-b bg-green-50">
          <h3 className="font-bold text-slate-700 flex items-center gap-2">
            <span>📋</span> Bulk Review Queue
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-green-600 mb-2 text-4xl">✅</div>
          <p className="text-slate-500 font-medium">All caught up!</p>
          <p className="text-slate-400 text-sm mt-1">No incidents pending verification</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
      {/* Header with controls */}
      <div className="p-4 border-b bg-slate-50 flex justify-between items-center sticky top-0 bg-white z-10">
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSelectAll}
            className="text-xs text-slate-600 hover:text-slate-800 transition-colors"
          >
            {selected.length === data.length ? 'Deselect All' : 'Select All'}
          </button>
          <span className="text-sm font-medium text-slate-700">
            {selected.length} of {data.length} selected
          </span>
        </div>
        
        <button 
          onClick={() => bulkMutation.mutate(selected)}
          disabled={selected.length === 0 || bulkMutation.isPending}
          className="px-4 py-2 bg-blue-600 text-white text-sm font-bold rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all active:scale-[0.98] min-w-[120px]"
        >
          {bulkMutation.isPending ? (
            <span className="flex items-center justify-center">
              <svg className="animate-spin h-3 w-3 mr-1" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Processing...
            </span>
          ) : (
            `Verify Selected (${selected.length})`
          )}
        </button>
      </div>

      {/* Success message */}
      {bulkMutation.data && (
        <div className="p-3 bg-green-50 border-l-4 border-green-500">
          <p className="text-sm text-green-700">
            ✅ Successfully verified {bulkMutation.data.count} incidents
          </p>
        </div>
      )}

      {/* Conflict list */}
      <div className="divide-y max-h-[500px] overflow-y-auto">
        {data.map((item) => (
          <div key={item.id} className="p-4 flex items-center gap-4 hover:bg-slate-50 transition-colors">
            <input 
              type="checkbox" 
              checked={selected.includes(item.id)}
              onChange={() => toggleSelect(item.id)}
              className="w-5 h-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500 focus:ring-2"
            />
            
            <div className="flex-1 min-w-0">
              <p className="text-xs font-bold text-blue-600 uppercase tracking-tight truncate">
                {item.conflict_type} • {formatDate(item.incidence_date)}
                {item.state_name && ` • ${item.state_name}`}
              </p>
              <p className="text-sm text-slate-700 leading-tight truncate mt-1">
                {item.description}
              </p>
              <div className="flex gap-2 mt-2 flex-wrap">
                {item.total_deaths > 0 && (
                  <span className="text-[10px] bg-red-100 text-red-700 px-2 py-0.5 rounded font-medium">
                    💀 {item.total_deaths} Fatalities
                  </span>
                )}
                {item.total_kidnapped > 0 && (
                  <span className="text-[10px] bg-purple-100 text-purple-700 px-2 py-0.5 rounded font-medium">
                    👤 {item.total_kidnapped} Kidnapped
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
      
      {data.length >= 50 && (
        <div className="p-3 bg-slate-50 text-center">
          <p className="text-xs text-slate-500">
            Showing first 50 of many pending incidents
          </p>
        </div>
      )}
    </div>
  );
}
