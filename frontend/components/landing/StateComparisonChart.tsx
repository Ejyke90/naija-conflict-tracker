import React from 'react';
import { motion } from 'framer-motion';
import { MapPin } from 'lucide-react';

interface StateData {
  name: string;
  incidents: number;
  fatalities: number;
  severity: 'low' | 'medium' | 'high';
}

interface StateComparisonChartProps {
  states: StateData[];
  maxIncidents?: number;
}

export const StateComparisonChart: React.FC<StateComparisonChartProps> = ({
  states,
  maxIncidents
}) => {
  const max = maxIncidents || Math.max(...states.map(s => s.incidents));

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'from-red-600 to-red-500';
      case 'medium':
        return 'from-orange-600 to-orange-500';
      case 'low':
        return 'from-yellow-600 to-yellow-500';
      default:
        return 'from-gray-600 to-gray-500';
    }
  };

  const getSeverityBg = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/10';
      case 'medium':
        return 'bg-orange-500/10';
      case 'low':
        return 'bg-yellow-500/10';
      default:
        return 'bg-gray-500/10';
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
      <div className="flex items-center gap-2 mb-6">
        <MapPin className="w-5 h-5 text-red-400" />
        <h3 className="text-lg font-semibold text-white">Most Affected States</h3>
      </div>

      <div className="space-y-4">
        {states.map((state, index) => {
          const percentage = (state.incidents / max) * 100;

          return (
            <motion.div
              key={state.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className={`${getSeverityBg(state.severity)} rounded-lg p-4 border border-gray-700/50`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{state.name}</span>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-400">
                    <span className="text-red-400 font-semibold">{state.incidents}</span> incidents
                  </span>
                  <span className="text-gray-400">
                    <span className="text-orange-400 font-semibold">{state.fatalities}</span> fatalities
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="w-full bg-gray-800 rounded-full h-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ duration: 1, delay: index * 0.1 }}
                  className={`h-full bg-gradient-to-r ${getSeverityColor(state.severity)} rounded-full`}
                />
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-6 pt-4 border-t border-gray-700 flex items-center gap-4 text-xs">
        <span className="text-gray-500">Severity:</span>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-gray-400">High (≥20)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-orange-500" />
          <span className="text-gray-400">Medium (10-19)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-gray-400">Low (&lt;10)</span>
        </div>
      </div>
    </div>
  );
};
