import React from 'react';
import { motion } from 'framer-motion';
import { Users, AlertCircle } from 'lucide-react';

interface CasualtyMetricsProps {
  incidents: number;
  fatalities: number;
  statesAffected: number;
}

export const CasualtyMetrics: React.FC<CasualtyMetricsProps> = ({
  incidents,
  fatalities,
  statesAffected
}) => {
  const fatalityRate = incidents > 0 ? (fatalities / incidents).toFixed(1) : '0';
  const avgPerState = statesAffected > 0 ? (fatalities / statesAffected).toFixed(1) : '0';
  const totalCasualties = fatalities; // Can add injuries when available

  // Calculate severity level
  const getSeverityLevel = () => {
    const rate = parseFloat(fatalityRate);
    if (rate > 5) return { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/10' };
    if (rate > 3) return { label: 'High', color: 'text-orange-400', bg: 'bg-orange-500/10' };
    if (rate > 1.5) return { label: 'Moderate', color: 'text-yellow-400', bg: 'bg-yellow-500/10' };
    return { label: 'Low', color: 'text-green-400', bg: 'bg-green-500/10' };
  };

  const severity = getSeverityLevel();

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6"
    >
      <div className="flex items-center gap-2 mb-6">
        <Users className="w-5 h-5 text-orange-400" />
        <div>
          <h3 className="text-lg font-semibold text-white">Casualty Analysis</h3>
          <p className="text-sm text-gray-400">Human impact metrics</p>
        </div>
      </div>

      {/* Main Metric */}
      <div className="mb-6">
        <div className="flex items-baseline gap-2">
          <span className="text-4xl font-bold text-orange-400">{fatalities}</span>
          <span className="text-gray-500 text-sm">total fatalities</span>
        </div>
        <div className={`mt-3 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg ${severity.bg}`}>
          <AlertCircle className={`w-4 h-4 ${severity.color}`} />
          <span className={`text-sm font-semibold ${severity.color}`}>
            {severity.label} Severity
          </span>
        </div>
      </div>

      {/* Key Ratios */}
      <div className="space-y-4">
        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Lethality Rate</span>
            <span className="text-xs text-gray-600">fatalities/incident</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{fatalityRate}</span>
            <span className="text-sm text-gray-500">per incident</span>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-700/50">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-400">Geographic Impact</span>
            <span className="text-xs text-gray-600">fatalities/state</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">{avgPerState}</span>
            <span className="text-sm text-gray-500">avg per state</span>
          </div>
        </div>
      </div>

      {/* Context Footer */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-xs text-gray-500 italic">
          {parseFloat(fatalityRate) > 3 
            ? '⚠️ High lethality indicates severe violence requiring urgent intervention'
            : '✓ Moderate lethality suggests containable conflicts with targeted responses'
          }
        </p>
      </div>
    </motion.div>
  );
};
