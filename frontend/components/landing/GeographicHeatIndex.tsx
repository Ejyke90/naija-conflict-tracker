import React from 'react';
import { MapPin, TrendingUp, AlertTriangle } from 'lucide-react';

interface GeographicHeatIndexProps {
  topStates: Array<{
    name: string;
    incidents: number;
    fatalities: number;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export const GeographicHeatIndex: React.FC<GeographicHeatIndexProps> = ({ topStates }) => {
  // Calculate total for percentages
  const totalIncidents = topStates.reduce((sum, state) => sum + state.incidents, 0);
  const totalFatalities = topStates.reduce((sum, state) => sum + state.fatalities, 0);

  // Get top 5 most affected states
  const top5States = topStates.slice(0, 5);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500';
      case 'medium':
        return 'bg-orange-500';
      case 'low':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'text-red-400 border-red-400/30 bg-red-400/10';
      case 'medium':
        return 'text-orange-400 border-orange-400/30 bg-orange-400/10';
      case 'low':
        return 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10';
      default:
        return 'text-gray-400 border-gray-400/30 bg-gray-400/10';
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <MapPin className="w-5 h-5 text-red-400" />
          <h3 className="text-lg font-semibold text-white">
            Most Affected States
          </h3>
        </div>
        <div className="text-xs text-gray-500">
          Top 5 by incidents
        </div>
      </div>

      <div className="space-y-4">
        {top5States.map((state, index) => {
          const incidentPct = totalIncidents > 0 
            ? ((state.incidents / totalIncidents) * 100).toFixed(1) 
            : '0';
          const fatalitiesPerIncident = state.incidents > 0 
            ? (state.fatalities / state.incidents).toFixed(1)
            : '0';

          return (
            <div key={state.name} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="flex items-center justify-center w-6 h-6 rounded-full bg-gray-800 border border-gray-600">
                    <span className="text-xs font-medium text-gray-400">
                      {index + 1}
                    </span>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white">
                      {state.name}
                    </div>
                    <div className="text-xs text-gray-500">
                      {state.incidents} incidents • {state.fatalities} fatalities
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-xs px-2 py-1 rounded-md border ${getSeverityBadge(state.severity)}`}>
                    {state.severity.toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="relative h-2 bg-gray-800 rounded-full overflow-hidden">
                <div
                  className={`absolute left-0 top-0 h-full ${getSeverityColor(state.severity)} transition-all duration-500`}
                  style={{ width: `${incidentPct}%` }}
                />
              </div>

              {/* Metrics */}
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">
                  {incidentPct}% of total incidents
                </span>
                <span className="text-gray-400">
                  {fatalitiesPerIncident} fatalities/incident
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary footer */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2 text-gray-400">
            <AlertTriangle className="w-4 h-4 text-yellow-400" />
            <span>Top 5 account for</span>
          </div>
          <div className="text-white font-semibold">
            {top5States.length > 0 
              ? ((top5States.reduce((sum, s) => sum + s.incidents, 0) / totalIncidents) * 100).toFixed(0)
              : '0'}% of incidents
          </div>
        </div>
        {top5States.some(s => s.severity === 'high') && (
          <div className="mt-2 flex items-start space-x-2 text-xs text-yellow-300 bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-2">
            <TrendingUp className="w-3 h-3 mt-0.5 flex-shrink-0" />
            <span>High lethality indicates severe violence requiring urgent intervention</span>
          </div>
        )}
      </div>
    </div>
  );
};
