import React from 'react';
import { AlertTriangle, MapPin, Users } from 'lucide-react';

const RecentIncidents: React.FC = () => {
  // Sample incident data
  const incidents = [
    {
      id: 1,
      title: 'Armed Robbery in Lagos',
      location: 'Lagos, Lagos State',
      date: '2026-01-20',
      fatalities: 2,
      type: 'Criminal',
      severity: 'high'
    },
    {
      id: 2,
      title: 'Community Clash in Kaduna',
      location: 'Kaduna, Kaduna State',
      date: '2026-01-19',
      fatalities: 0,
      type: 'Communal',
      severity: 'medium'
    },
    {
      id: 3,
      title: 'Kidnapping Incident in Zamfara',
      location: 'Zamfara State',
      date: '2026-01-18',
      fatalities: 1,
      type: 'Criminal',
      severity: 'high'
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high': return 'signal_critical';
      case 'medium': return 'signal_medium';
      case 'low': return 'signal_low';
      default: return 'default';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'Criminal': return 'signal_critical';
      case 'Communal': return 'signal_medium';
      case 'Political': return 'signal_high';
      default: return 'default';
    }
  };

  return (
    <div className="space-y-4">
      {incidents.map((incident) => (
        <div key={incident.id} className="glass-card border border-tactical-slate-light/30 rounded-lg p-4 hover:bg-tactical-slate-medium/10 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className={`w-4 h-4 ${
                  incident.severity === 'high' ? 'text-red-400' :
                  incident.severity === 'medium' ? 'text-amber-400' : 'text-green-400'
                }`} />
                <h3 className="typography-body font-medium text-tactical-e-ink">{incident.title}</h3>
                <span className={`px-2 py-1 text-xs rounded-full typography-label ${getTypeColor(incident.type)}`}>
                  {incident.type}
                </span>
              </div>

              <div className="flex items-center gap-4 typography-body text-sm text-tactical-e-ink/70 mb-2">
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {incident.location}
                </div>
                <span>{new Date(incident.date).toLocaleDateString()}</span>
              </div>

              {incident.fatalities > 0 && (
                <div className="flex items-center gap-1 typography-body text-sm text-red-400">
                  <Users className="w-4 h-4" />
                  {incident.fatalities} {incident.fatalities === 1 ? 'fatality' : 'fatalities'}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      <div className="text-center pt-4">
        <button className="typography-body text-blue-400 hover:text-blue-300 text-sm font-medium">
          View all incidents →
        </button>
      </div>
    </div>
  );
};

export default RecentIncidents;
