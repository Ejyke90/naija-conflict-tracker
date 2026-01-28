import React from 'react';
import { AlertTriangle, CheckCircle, Clock, MapPin } from 'lucide-react';

interface IncidentItem {
  id: string;
  title: string;
  location: string;
  criticality: 'critical' | 'high' | 'medium' | 'low';
  timestamp: string;
  predicted: boolean;
  description: string;
}

interface IncidentFeedProps {
  incidents?: IncidentItem[];
}

export const IncidentFeed: React.FC<IncidentFeedProps> = ({
  incidents = [
    {
      id: '1',
      title: 'Armed Clashes Reported',
      location: 'Maiduguri, Borno',
      criticality: 'critical',
      timestamp: '2026-01-28T14:30:00Z',
      predicted: true,
      description: 'Multiple casualties reported in central district'
    },
    {
      id: '2',
      title: 'Community Tension Rising',
      location: 'Kaduna North, Kaduna',
      criticality: 'high',
      timestamp: '2026-01-28T12:15:00Z',
      predicted: false,
      description: 'Ethnic tensions escalating between communities'
    },
    {
      id: '3',
      title: 'Security Checkpoint Incident',
      location: 'Zaria, Kaduna',
      criticality: 'medium',
      timestamp: '2026-01-28T10:45:00Z',
      predicted: true,
      description: 'Minor altercation at military checkpoint'
    },
    {
      id: '4',
      title: 'Peaceful Protest',
      location: 'Lagos Island, Lagos',
      criticality: 'low',
      timestamp: '2026-01-28T09:20:00Z',
      predicted: false,
      description: 'Labor union demonstration, no violence reported'
    }
  ]
}) => {
  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
      case 'critical': return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'low': return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/30';
    }
  };

  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));

    if (diffMins < 60) {
      return `${diffMins}m ago`;
    } else if (diffMins < 1440) {
      return `${Math.floor(diffMins / 60)}h ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div className="glass-panel p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center">
          <AlertTriangle className="w-6 h-6 text-slate-300" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">Incident Feed</h3>
          <p className="text-sm text-slate-400">Real-time conflict monitoring</p>
        </div>
      </div>

      <div className="space-y-4 max-h-96 overflow-y-auto">
        {incidents.map((incident) => (
          <div key={incident.id} className="incident-feed-item">
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h4 className="font-semibold text-white text-sm">{incident.title}</h4>
                  {incident.predicted && (
                    <div className="flex items-center gap-1 px-2 py-0.5 bg-emerald-500/20 border border-emerald-500/30 rounded-full">
                      <CheckCircle className="w-3 h-3 text-emerald-400" />
                      <span className="text-xs text-emerald-400 font-medium">Predicted</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-4 text-xs text-slate-400 mb-2">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-3 h-3" />
                    <span className="font-mono">{incident.location}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    <span className="font-mono">{formatTime(incident.timestamp)}</span>
                  </div>
                </div>

                <p className="text-sm text-slate-300 leading-relaxed">
                  {incident.description}
                </p>
              </div>

              <div className={`px-3 py-1 rounded-full border text-xs font-semibold ${getCriticalityColor(incident.criticality)}`}>
                {incident.criticality.toUpperCase()}
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700/50">
        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Auto-refreshing every 30 seconds</span>
          <button className="text-emerald-400 hover:text-emerald-300 transition-colors">
            View All Incidents →
          </button>
        </div>
      </div>
    </div>
  );
};