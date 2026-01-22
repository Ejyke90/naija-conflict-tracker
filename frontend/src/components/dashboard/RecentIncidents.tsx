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

  return (
    <div className="space-y-4">
      {incidents.map((incident) => (
        <div key={incident.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <AlertTriangle className={`w-4 h-4 ${
                  incident.severity === 'high' ? 'text-red-500' :
                  incident.severity === 'medium' ? 'text-yellow-500' : 'text-green-500'
                }`} />
                <h3 className="font-medium text-gray-900">{incident.title}</h3>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  incident.type === 'Criminal' ? 'bg-red-100 text-red-800' :
                  incident.type === 'Communal' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {incident.type}
                </span>
              </div>

              <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                <div className="flex items-center gap-1">
                  <MapPin className="w-4 h-4" />
                  {incident.location}
                </div>
                <span>{new Date(incident.date).toLocaleDateString()}</span>
              </div>

              {incident.fatalities > 0 && (
                <div className="flex items-center gap-1 text-sm text-red-600">
                  <Users className="w-4 h-4" />
                  {incident.fatalities} {incident.fatalities === 1 ? 'fatality' : 'fatalities'}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}

      <div className="text-center pt-4">
        <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
          View all incidents →
        </button>
      </div>
    </div>
  );
};

export default RecentIncidents;
