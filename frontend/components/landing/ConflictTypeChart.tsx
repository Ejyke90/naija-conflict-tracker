import React from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { Flame } from 'lucide-react';

interface ConflictType {
  type: string;
  count: number;
  percentage?: number;
}

interface ConflictTypeChartProps {
  data: ConflictType[];
}

const COLORS = ['#ef4444', '#f97316', '#fbbf24', '#fb923c'];

export const ConflictTypeChart: React.FC<ConflictTypeChartProps> = ({ data }) => {
  const chartData = data.map((item) => ({
    name: item.type,
    value: item.count
  }));

  const totalIncidents = data.reduce((sum, item) => sum + item.count, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-xl p-6"
    >
      <div className="flex items-center gap-2 mb-6">
        <Flame className="w-5 h-5 text-red-400" />
        <div>
          <h3 className="text-lg font-semibold text-white">Conflict Type Distribution</h3>
          <p className="text-sm text-gray-400">Primary violence categories</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${(percent * 100).toFixed(0)}%`}
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: '1px solid #374151',
              borderRadius: '8px',
              color: '#fff'
            }}
          />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 space-y-2">
        {data.map((item, index) => (
          <div
            key={item.type}
            className="flex items-center justify-between p-2 bg-gray-800/50 rounded-lg"
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm text-gray-300">{item.type}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-white">{item.count}</span>
              <span className="text-xs text-gray-500">
                {((item.count / totalIncidents) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
};
