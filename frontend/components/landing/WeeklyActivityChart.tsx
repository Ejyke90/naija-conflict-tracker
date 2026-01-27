import React from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Clock } from 'lucide-react';

interface WeeklyActivityChartProps {
  timeline: number[];
}

export const WeeklyActivityChart: React.FC<WeeklyActivityChartProps> = ({ timeline }) => {
  // Generate last 7 days data from timeline
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  const chartData = timeline.slice(-7).map((value, index) => ({
    day: days[index] || `D${index + 1}`,
    incidents: value
  }));

  const maxValue = Math.max(...timeline.slice(-7));
  const minValue = Math.min(...timeline.slice(-7));
  const trend = timeline[timeline.length - 1] > timeline[timeline.length - 2] ? 'up' : 'down';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.1 }}
      className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6"
    >
      <div className="flex items-center gap-2 mb-6">
        <Clock className="w-5 h-5 text-blue-400" />
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-white">7-Day Activity</h3>
          <p className="text-sm text-gray-400">Recent weekly pattern</p>
        </div>
        <div className={`px-3 py-1 rounded-lg ${
          trend === 'up' ? 'bg-red-500/10' : 'bg-green-500/10'
        }`}>
          <span className={`text-xs font-semibold ${
            trend === 'up' ? 'text-red-400' : 'text-green-400'
          }`}>
            {trend === 'up' ? '↑' : '↓'} {trend === 'up' ? 'Rising' : 'Declining'}
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={180}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="day" 
            stroke="#9ca3af"
            style={{ fontSize: '11px' }}
          />
          <YAxis 
            stroke="#9ca3af"
            style={{ fontSize: '11px' }}
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
          <Area
            type="monotone"
            dataKey="incidents"
            stroke="#3b82f6"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorIncidents)"
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="mt-4 pt-4 border-t border-gray-700 grid grid-cols-2 gap-3 text-center">
        <div>
          <p className="text-xs text-gray-500 mb-1">Peak Day</p>
          <p className="text-sm font-bold text-blue-400">{maxValue} incidents</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Low Day</p>
          <p className="text-sm font-bold text-green-400">{minValue} incidents</p>
        </div>
      </div>
    </motion.div>
  );
};
