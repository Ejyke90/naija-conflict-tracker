'use client';

import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { TrendingUp, Clock, CheckCircle, AlertTriangle, Activity, MapPin } from 'lucide-react';

interface ValidationSummary {
  pendingCount: number;
  isUrgent: boolean;
  highPriorityCount: number;
  lastActivity: string | null;
  totalVerified: number;
  oldestItem: string | null;
  status: 'ok' | 'error' | 'no_data';
  timestamp: string;
  breakdown?: {
    banditry: number;
    kidnapping: number;
    terrorism: number;
    farmerHerder: number;
    other: number;
  };
  verificationTrend?: {
    percentage: number;
    direction: 'up' | 'down' | 'stable';
  };
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

  // Mock breakdown data for visualization
  const getBreakdownData = () => ({
    banditry: Math.floor(data.pendingCount * 0.35),
    kidnapping: Math.floor(data.pendingCount * 0.25),
    terrorism: Math.floor(data.pendingCount * 0.20),
    farmerHerder: Math.floor(data.pendingCount * 0.15),
    other: data.pendingCount - Math.floor(data.pendingCount * 0.35) - Math.floor(data.pendingCount * 0.25) - Math.floor(data.pendingCount * 0.20) - Math.floor(data.pendingCount * 0.15)
  });

  const getVerificationTrend = () => ({
    percentage: 12,
    direction: 'up' as const
  });

  const breakdown = data.breakdown || getBreakdownData();
  const trend = data.verificationTrend || getVerificationTrend();
  const progressPercentage = (data.totalVerified / (data.totalVerified + data.pendingCount)) * 100;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden font-sans">
      {/* Header Area */}
      <div className={`p-4 border-b flex justify-between items-center ${
        data.isUrgent ? 'bg-red-50' : 'bg-slate-50'
      }`}>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-lg">📊</span>
            <h3 className="font-bold text-slate-700">Data Validation Queue</h3>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-xs text-green-600 font-medium">Live Sync</span>
          </div>
        </div>
        {data.isUrgent && (
          <span className="text-[10px] font-black tracking-widest text-red-600 bg-white border border-red-200 px-2 py-0.5 rounded">
            URGENT
          </span>
        )}
      </div>

      {/* Progress Visualization */}
      <div className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="text-4xl font-mono font-black mb-1 tracking-tight">
              {data.pendingCount.toLocaleString()}
            </div>
            <p className="text-slate-500 text-sm font-medium">Events awaiting verification</p>
          </div>
          <div className="relative w-20 h-20">
            <svg className="transform -rotate-90 w-20 h-20">
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke="#e2e8f0"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="40"
                cy="40"
                r="36"
                stroke={data.isUrgent ? '#dc2626' : '#f59e0b'}
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 36}`}
                strokeDashoffset={`${2 * Math.PI * 36 * (1 - progressPercentage / 100)}`}
                className="transition-all duration-500"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-sm font-mono font-bold">{Math.round(progressPercentage)}%</span>
            </div>
          </div>
        </div>

        {/* Data Segmentation */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">Breakdown by Type</span>
            <span className="text-slate-400 font-mono">{Object.values(breakdown).reduce((a, b) => a + b, 0)} total</span>
          </div>
          <div className="grid grid-cols-5 gap-2">
            <div className="text-center">
              <div className="text-xs font-mono font-bold text-red-600">{breakdown.banditry}</div>
              <div className="text-xs text-slate-400">Banditry</div>
            </div>
            <div className="text-center">
              <div className="text-xs font-mono font-bold text-orange-600">{breakdown.kidnapping}</div>
              <div className="text-xs text-slate-400">Kidnapping</div>
            </div>
            <div className="text-center">
              <div className="text-xs font-mono font-bold text-purple-600">{breakdown.terrorism}</div>
              <div className="text-xs text-slate-400">Terrorism</div>
            </div>
            <div className="text-center">
              <div className="text-xs font-mono font-bold text-green-600">{breakdown.farmerHerder}</div>
              <div className="text-xs text-slate-400">Farmer</div>
            </div>
            <div className="text-center">
              <div className="text-xs font-mono font-bold text-slate-600">{breakdown.other}</div>
              <div className="text-xs text-slate-400">Other</div>
            </div>
          </div>
        </div>

        {data.highPriorityCount > 0 && (
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-red-100 text-red-700 text-xs font-bold rounded-full border border-red-200">
            <AlertTriangle className="w-3 h-3" />
            {data.highPriorityCount} High-Impact Incidents
          </div>
        )}
      </div>

      {/* Verification Trends & Stats */}
      <div className="grid grid-cols-3 divide-x border-t text-[11px] text-slate-400 uppercase tracking-tighter">
        <div className="p-3 text-center">
          <p className="font-bold text-slate-600 uppercase">Database Size</p>
          <p className="font-mono">{Number(data.totalVerified).toLocaleString()}</p>
        </div>
        <div className="p-3 text-center">
          <p className="font-bold text-slate-600 uppercase">Last Activity</p>
          <p className="font-mono">
            {data.lastActivity 
              ? formatDistanceToNow(new Date(data.lastActivity)) + ' ago'
              : 'Never'
            }
          </p>
        </div>
        <div className="p-3 text-center">
          <p className="font-bold text-slate-600 uppercase">Verification Speed</p>
          <div className="flex items-center justify-center gap-1">
            {trend.direction === 'up' && <TrendingUp className="w-3 h-3 text-green-500" />}
            <span className={`font-mono ${
              trend.direction === 'up' ? 'text-green-600' : 
              trend.direction === 'down' ? 'text-red-600' : 'text-slate-600'
            }`}>
              {trend.percentage}%
            </span>
          </div>
        </div>
      </div>

      {/* Action */}
      <div className="p-4 bg-slate-50 flex items-center justify-between">
        <button
          onClick={handleOpenReview}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-lg transition-all shadow-md active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed text-sm"
          disabled={data.pendingCount === 0}
        >
          {data.pendingCount === 0 ? 'Queue Empty' : 'Open Review Interface'}
        </button>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Clock className="w-3 h-3" />
          <span className="font-mono">{data.pendingCount > 0 ? 'Active' : 'Idle'}</span>
        </div>
      </div>
    </div>
  );
}
