import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
  Legend,
  CartesianGrid,
  Cell
} from 'recharts';

interface ArchetypeItem {
  type: string;
  count: number;
  percentage?: number;
  confidence?: number;
}

interface ArchetypeChartProps {
  data: ArchetypeItem[];
}

const COLORS = ['#f87171', '#fb923c', '#38bdf8', '#a855f7', '#22c55e', '#facc15'];

export const ArchetypeChart: React.FC<ArchetypeChartProps> = ({ data }) => {
  const safeData = data && data.length > 0 ? data : [
    { type: 'Banditry', count: 23, percentage: 40.4, confidence: 0.92 },
    { type: 'Farmer-Herder', count: 15, percentage: 26.3, confidence: 0.88 },
    { type: 'Sectarian', count: 12, percentage: 21.1, confidence: 0.85 },
    { type: 'Kidnapping', count: 7, percentage: 12.3, confidence: 0.90 }
  ];

  return (
    <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8 shadow-2xl shadow-red-900/20">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Archetype Breakdown</p>
          <h3 className="text-xl font-semibold text-white">AI-Categorized Patterns</h3>
        </div>
        <div className="text-sm text-gray-500">Counts with confidence</div>
      </div>
      <div className="h-[320px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={safeData} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis type="number" stroke="#6b7280" />
            <YAxis type="category" dataKey="type" stroke="#6b7280" width={120} />
            <Tooltip contentStyle={{ backgroundColor: '#0b0b0f', borderColor: '#1f2937' }} />
            <Legend />
            <Bar dataKey="count" name="Incidents" radius={[6, 6, 6, 6]}>
              {safeData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
