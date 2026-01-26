import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';

interface EconomicPoint {
  month: string; // e.g. 2025-08
  incidents: number;
  fuel_price?: number;
  inflation?: number;
}

interface EconomicPulseChartProps {
  data: EconomicPoint[];
}

const formatMonth = (value: string) => {
  if (!value) return '';
  const [year, month] = value.split('-');
  const date = new Date(Number(year), Number(month) - 1, 1);
  return date.toLocaleString('en', { month: 'short' });
};

export const EconomicPulseChart: React.FC<EconomicPulseChartProps> = ({ data }) => {
  const safeData = data && data.length > 0 ? data : [
    { month: '2025-07', incidents: 42, fuel_price: 720, inflation: 22.5 },
    { month: '2025-08', incidents: 48, fuel_price: 750, inflation: 23.1 },
    { month: '2025-09', incidents: 55, fuel_price: 790, inflation: 24.0 },
    { month: '2025-10', incidents: 60, fuel_price: 820, inflation: 24.8 },
    { month: '2025-11', incidents: 58, fuel_price: 815, inflation: 24.5 },
    { month: '2025-12', incidents: 65, fuel_price: 840, inflation: 25.2 },
  ];

  return (
    <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8 shadow-2xl shadow-red-900/20">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Economic Correlation</p>
          <h3 className="text-xl font-semibold text-white">Violence vs Fuel Price / Inflation</h3>
        </div>
        <div className="text-sm text-gray-500">Dual Axis • 12 months</div>
      </div>
      <div className="h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={safeData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
            <XAxis dataKey="month" tickFormatter={formatMonth} stroke="#6b7280" />
            <YAxis yAxisId="left" stroke="#f87171" tick={{ fill: '#6b7280' }} />
            <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" tick={{ fill: '#6b7280' }} />
            <Tooltip contentStyle={{ backgroundColor: '#0b0b0f', borderColor: '#1f2937' }} />
            <Legend />
            <Line yAxisId="left" type="monotone" dataKey="incidents" name="Incidents" stroke="#f87171" strokeWidth={2.2} dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="fuel_price" name="Fuel Price" stroke="#f59e0b" strokeWidth={2} dot={false} />
            <Line yAxisId="right" type="monotone" dataKey="inflation" name="Inflation %" stroke="#38bdf8" strokeWidth={2} dot={false} strokeDasharray="4 3" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
