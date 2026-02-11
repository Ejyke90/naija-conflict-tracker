'use client';

import { useQuery } from '@tanstack/react-query';
import { formatDistanceToNow } from 'date-fns';
import { MapPin, Activity, TrendingUp, AlertTriangle, Clock } from 'lucide-react';

interface RecentActivity {
  id: number;
  state: string;
  lga: string;
  event_type: string;
  fatalities: number;
  injuries: number;
  event_date: string;
  created_at: string;
  risk_score?: number;
}

interface ActivityFeedProps {
  maxItems?: number;
}

export default function ActivityFeed({ maxItems = 5 }: ActivityFeedProps) {
  const { data, isLoading, error } = useQuery<RecentActivity[]>({
    queryKey: ['recent-activity'],
    queryFn: () => fetch('/api/v1/conflicts/recent?limit=10').then(res => res.json()),
    refetchInterval: 60000, // 1 minute
    staleTime: 55000,
  });

  // Mock data for demonstration
  const mockData: RecentActivity[] = [
    {
      id: 1,
      state: 'Zamfara',
      lga: 'Maradun',
      event_type: 'Banditry',
      fatalities: 205,
      injuries: 0,
      event_date: '2025-02-08',
      created_at: '2025-02-08T10:30:00Z',
      risk_score: 98
    },
    {
      id: 2,
      state: 'Benue',
      lga: 'Guma',
      event_type: 'Farmer - Herder Conflict',
      fatalities: 204,
      injuries: 105,
      event_date: '2025-02-07',
      created_at: '2025-02-07T14:20:00Z',
      risk_score: 96
    },
    {
      id: 3,
      state: 'Borno',
      lga: 'Guzamala',
      event_type: 'Terrorism',
      fatalities: 200,
      injuries: 0,
      event_date: '2025-02-06',
      created_at: '2025-02-06T08:15:00Z',
      risk_score: 95
    },
    {
      id: 4,
      state: 'Niger',
      lga: 'Mariga',
      event_type: 'Banditry',
      fatalities: 200,
      injuries: 0,
      event_date: '2025-02-05',
      created_at: '2025-02-05T16:45:00Z',
      risk_score: 92
    },
    {
      id: 5,
      state: 'Plateau',
      lga: 'Kanam',
      event_type: 'Banditry',
      fatalities: 149,
      injuries: 9,
      event_date: '2025-02-04',
      created_at: '2025-02-04T11:20:00Z',
      risk_score: 89
    }
  ];

  const activities = data || mockData;

  const getRiskColor = (score?: number) => {
    if (!score) return 'text-tactical-slate-medium';
    if (score >= 95) return 'text-signal-critical';
    if (score >= 85) return 'text-signal-high';
    return 'text-signal-medium';
  };

  const getRiskBg = (score?: number) => {
    if (!score) return 'bg-tactical-slate-dark';
    if (score >= 95) return 'bg-signal-critical';
    if (score >= 85) return 'bg-signal-high';
    return 'bg-signal-medium';
  };

  if (isLoading) {
    return (
      <div className="h-64 loading-skeleton rounded-xl border border-tactical-slate-medium" />
    );
  }

  if (error) {
    return (
      <div className="glass-card rounded-xl shadow-sm border border-tactical-slate-medium overflow-hidden font-sans">
        <div className="p-4 border-b border-tactical-slate-medium signal-critical">
          <h3 className="font-bold text-tactical-e-ink flex items-center gap-2">
            <Activity className="w-4 h-4" />
            Recent Activity Feed
          </h3>
        </div>
        <div className="p-8 text-center">
          <div className="text-signal-critical mb-2">⚠️</div>
          <p className="text-tactical-slate-light font-medium">Unable to load activity data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card rounded-xl shadow-sm border border-tactical-slate-medium overflow-hidden font-sans">
      {/* Header */}
      <div className="p-4 border-b border-tactical-slate-medium bg-tactical-charcoal">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-tactical-slate-light" />
            <h3 className="font-bold text-tactical-e-ink typography-heading">Recent Activity Feed</h3>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-signal-low rounded-full animate-pulse"></div>
            <span className="text-xs text-signal-low font-medium">Live</span>
          </div>
        </div>
      </div>

      {/* Activity List */}
      <div className="divide-y divide-tactical-slate-medium">
        {activities.slice(0, maxItems).map((activity, index) => (
          <div key={activity.id} className="p-3 hover:bg-tactical-slate-dark transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <MapPin className="w-3 h-3 text-tactical-slate-medium flex-shrink-0" />
                  <span className="text-sm font-medium text-tactical-e-ink truncate">
                    {activity.lga}, {activity.state}
                  </span>
                  {activity.risk_score && (
                    <span className={`px-1.5 py-0.5 text-xs font-mono font-bold rounded ${getRiskBg(activity.risk_score)} ${getRiskColor(activity.risk_score)}`}>
                      {activity.risk_score}
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-tactical-slate-medium">
                  <span className="font-medium">{activity.event_type}</span>
                  <span>•</span>
                  <span className="font-mono">
                    {activity.fatalities > 0 && `${activity.fatalities} killed`}
                    {activity.fatalities > 0 && activity.injuries > 0 && ', '}
                    {activity.injuries > 0 && `${activity.injuries} injured`}
                  </span>
                </div>
              </div>
              <div className="text-right text-xs text-tactical-slate-medium">
                <div className="font-mono">
                  {formatDistanceToNow(new Date(activity.created_at), { addSuffix: true })}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 bg-tactical-charcoal border-t border-tactical-slate-medium">
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 text-tactical-slate-medium">
            <TrendingUp className="w-3 h-3" />
            <span className="font-mono">{activities.length} recent events</span>
          </div>
          <button className="text-tactical-slate-light hover:text-tactical-e-ink font-medium">
            View all →
          </button>
        </div>
      </div>
    </div>
  );
}
