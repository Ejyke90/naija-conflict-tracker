'use client';

import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';

interface ValidationSummary {
  pendingCount: number;
  isUrgent: boolean;
  highPriorityCount: number;
  lastActivity: string | null;
  totalVerified: number;
  oldestItem: string | null;
  status: 'ok' | 'error' | 'no_data';
  timestamp: string;
}

export default function ValidationQueueCard() {
  const { data, isLoading, error } = useQuery<ValidationSummary>({
    queryKey: ['validation-summary'],
    queryFn: () => fetch('/api/v1/system/validation/summary').then(res => res.json()),
    refetchInterval: 30000, // 30 seconds
    staleTime: 25000, // Consider data stale after 25 seconds
    gcTime: 300000, // Cache for 5 minutes (gcTime replaced cacheTime in v5)
  });

  if (isLoading) {
    return (
      <div className="h-64 animate-pulse bg-slate-50 rounded-xl border border-slate-200" />
    );
  }

  if (error || !data) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
        <div className="p-4 border-b bg-red-50">
          <h3 className="font-bold text-slate-700 flex items-center gap-2">
            <span>📊</span> Data Validation Queue
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-red-600 mb-2">⚠️</div>
          <p className="text-slate-500 font-medium">Unable to load validation data</p>
        </div>
      </div>
    );
  }

  const handleOpenReview = () => {
    // Navigate to review interface
    window.location.href = '/dashboard/review';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
      {/* Header Area */}
      <div className={`p-4 border-b flex justify-between items-center ${
        data.isUrgent ? 'bg-red-50' : 'bg-slate-50'
      }`}>
        <h3 className="font-bold text-slate-700 flex items-center gap-2">
          <span>📊</span> Data Validation Queue
        </h3>
        {data.isUrgent && (
          <span className="text-[10px] font-black tracking-widest text-red-600 bg-white border border-red-200 px-2 py-0.5 rounded">
            URGENT
          </span>
        )}
      </div>

      {/* Main Metric */}
      <div className="p-8 text-center">
        <div className={`text-6xl font-black mb-2 ${
          data.isUrgent ? 'text-red-600' : 'text-amber-500'
        }`}>
          {data.pendingCount}
        </div>
        <p className="text-slate-500 font-medium">Events awaiting verification</p>
        
        {data.highPriorityCount > 0 && (
          <div className="mt-4 inline-flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full border border-red-200 animate-bounce">
            ⚠️ {data.highPriorityCount} High-Impact Incidents
          </div>
        )}
      </div>

      {/* Meta Stats */}
      <div className="grid grid-cols-2 divide-x border-t text-[11px] text-slate-400 uppercase tracking-tighter">
        <div className="p-3 text-center">
          <p className="font-bold text-slate-600 uppercase">Database Size</p>
          <p>{Number(data.totalVerified).toLocaleString()} Verified</p>
        </div>
        <div className="p-3 text-center">
          <p className="font-bold text-slate-600 uppercase">Last Activity</p>
          <p>
            {data.lastActivity 
              ? formatDistanceToNow(new Date(data.lastActivity)) + ' ago'
              : 'Never'
            }
          </p>
        </div>
      </div>

      {/* Action */}
      <div className="p-4 bg-slate-50">
        <button
          onClick={handleOpenReview}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-all shadow-md active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={data.pendingCount === 0}
        >
          {data.pendingCount === 0 ? 'Queue Empty' : 'Open Review Interface →'}
        </button>
      </div>
    </div>
  );
}
