import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MonthlyTrendChartProps {
  data: number[];
}

export const MonthlyTrendChart: React.FC<MonthlyTrendChartProps> = ({ data }) => {
  // Convert sparkline data to chart format
  const months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const chartData = data.map((value, index) => ({
    month: months[index] || `M${index + 1}`,
    incidents: value
  }));

  // Calculate trend
  const firstHalf = data.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
  const secondHalf = data.slice(3).reduce((a, b) => a + b, 0) / 3;
  const isIncreasing = secondHalf > firstHalf;
  const changePercent = ((secondHalf - firstHalf) / firstHalf * 100).toFixed(1);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6"
    >
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">6-Month Incident Trend</h3>
          <p className="text-sm text-gray-400">Monthly conflict frequency</p>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
          isIncreasing ? 'bg-red-500/10' : 'bg-green-500/10'
        }`}>
          {isIncreasing ? (
            <TrendingUp className="w-4 h-4 text-red-400" />
          ) : (
            <TrendingDown className="w-4 h-4 text-green-400" />
          )}
          <span className={`text-sm font-semibold ${
            isIncreasing ? 'text-red-400' : 'text-green-400'
          }`}>
            {isIncreasing ? '+' : ''}{changePercent}%
          </span>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="month" 
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
          <Line
            type="monotone"
            dataKey="incidents"
            stroke="#ef4444"
            strokeWidth={2}
            dot={{ fill: '#ef4444', r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-xs text-gray-400">
          {isIncreasing ? (
            <>
              <span className="text-red-400 font-semibold">Escalation Alert:</span> Incidents increased by {changePercent}% 
              in recent months compared to earlier period
            </>
          ) : (
            <>
              <span className="text-green-400 font-semibold">De-escalation:</span> Violence decreased by {Math.abs(parseFloat(changePercent))}% 
              showing positive security improvements
            </>
          )}
        </p>
      </div>
    </motion.div>
  );
};
