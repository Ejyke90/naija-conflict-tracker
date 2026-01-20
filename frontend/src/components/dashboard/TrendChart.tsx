import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface TrendData {
  month: string;
  conflicts: number;
  fatalities: number;
  incidents: number;
}

interface TrendChartProps {
  detailed?: boolean;
  height?: number;
}

export const TrendChart: React.FC<TrendChartProps> = ({ detailed = false, height = 300 }) => {
  // Mock data - replace with real API data
  const trendData: TrendData[] = [
    { month: 'Jul 2023', conflicts: 45, fatalities: 120, incidents: 67 },
    { month: 'Aug 2023', conflicts: 52, fatalities: 145, incidents: 78 },
    { month: 'Sep 2023', conflicts: 38, fatalities: 98, incidents: 56 },
    { month: 'Oct 2023', conflicts: 61, fatalities: 178, incidents: 89 },
    { month: 'Nov 2023', conflicts: 47, fatalities: 132, incidents: 71 },
    { month: 'Dec 2023', conflicts: 55, fatalities: 156, incidents: 82 },
    { month: 'Jan 2024', conflicts: 49, fatalities: 142, incidents: 75 }
  ];

  const currentMonth = trendData[trendData.length - 1];
  const previousMonth = trendData[trendData.length - 2];
  
  const conflictChange = ((currentMonth.conflicts - previousMonth.conflicts) / previousMonth.conflicts * 100);
  const fatalityChange = ((currentMonth.fatalities - previousMonth.fatalities) / previousMonth.fatalities * 100);

  const getTrendIcon = (change: number) => {
    if (change > 5) return <TrendingUp className="w-4 h-4 text-red-500" />;
    if (change < -5) return <TrendingDown className="w-4 h-4 text-green-500" />;
    return <Minus className="w-4 h-4 text-gray-500" />;
  };

  const getTrendColor = (change: number) => {
    if (change > 5) return 'text-red-600';
    if (change < -5) return 'text-green-600';
    return 'text-gray-600';
  };

  if (detailed) {
    return (
      <div className="space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Monthly Conflicts</p>
                <p className="text-2xl font-bold">{currentMonth.conflicts}</p>
              </div>
              <div className="flex items-center space-x-1">
                {getTrendIcon(conflictChange)}
                <span className={`text-sm font-medium ${getTrendColor(conflictChange)}`}>
                  {Math.abs(conflictChange).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Monthly Fatalities</p>
                <p className="text-2xl font-bold">{currentMonth.fatalities}</p>
              </div>
              <div className="flex items-center space-x-1">
                {getTrendIcon(fatalityChange)}
                <span className={`text-sm font-medium ${getTrendColor(fatalityChange)}`}>
                  {Math.abs(fatalityChange).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Chart */}
        <div className="bg-white p-4 rounded-lg border">
          <h3 className="text-lg font-semibold mb-4">Detailed Trend Analysis</h3>
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="conflicts" 
                stackId="1"
                stroke="#ef4444" 
                fill="#ef4444" 
                fillOpacity={0.6}
                name="Conflicts"
              />
              <Area 
                type="monotone" 
                dataKey="incidents" 
                stackId="1"
                stroke="#f97316" 
                fill="#f97316" 
                fillOpacity={0.6}
                name="Incidents"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full">
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={trendData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="month" 
            tick={{ fontSize: 12 }}
            tickLine={false}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="conflicts" 
            stroke="#ef4444" 
            strokeWidth={2}
            dot={{ fill: '#ef4444', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#ef4444', strokeWidth: 2 }}
            name="Conflicts"
          />
          <Line 
            type="monotone" 
            dataKey="fatalities" 
            stroke="#f97316" 
            strokeWidth={2}
            dot={{ fill: '#f97316', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#f97316', strokeWidth: 2 }}
            name="Fatalities"
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Interactive chart visualization with Recharts
        </p>
      </div>
    </div>
  );
};

export default TrendChart;
