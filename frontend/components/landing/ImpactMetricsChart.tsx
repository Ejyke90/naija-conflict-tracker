import React from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { Activity } from 'lucide-react';

interface ImpactMetricsChartProps {
  totalIncidents: number;
  totalFatalities: number;
  activeHotspots: number;
  statesAffected: number;
}

export const ImpactMetricsChart: React.FC<ImpactMetricsChartProps> = ({
  totalIncidents,
  totalFatalities,
  activeHotspots,
  statesAffected
}) => {
  const chartData = [
    {
      name: 'Incidents',
      value: totalIncidents,
      color: '#ef4444'
    },
    {
      name: 'Fatalities',
      value: totalFatalities,
      color: '#f97316'
    },
    {
      name: 'Hotspots',
      value: activeHotspots,
      color: '#fbbf24'
    },
    {
      name: 'States',
      value: statesAffected,
      color: '#60a5fa'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
      className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6"
    >
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-blue-400" />
        <div>
          <h3 className="text-lg font-semibold text-white">Impact Overview</h3>
          <p className="text-sm text-gray-400">Key conflict metrics (Last 30 days)</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="name" 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="#9ca3af"
            style={{ fontSize: '12px' }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#fff'
            }}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Bar
            dataKey="value"
            fill="#ef4444"
            radius={[8, 8, 0, 0]}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 pt-4 border-t border-gray-700 grid grid-cols-2 gap-3">
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Avg Fatalities/Incident</p>
          <p className="text-lg font-bold text-orange-400">
            {totalIncidents > 0 ? (totalFatalities / totalIncidents).toFixed(1) : '0'}
          </p>
        </div>
        <div className="text-center">
          <p className="text-xs text-gray-500 mb-1">Geographic Spread</p>
          <p className="text-lg font-bold text-blue-400">
            {((statesAffected / 36) * 100).toFixed(0)}% of Nigeria
          </p>
        </div>
      </div>
    </motion.div>
  );
};
