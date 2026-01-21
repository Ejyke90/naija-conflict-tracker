import React, { useState } from 'react';
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, Bar } from 'recharts';
import { TrendingUp, TrendingDown, Minus, Calendar, AlertTriangle } from 'lucide-react';

interface TrendData {
  month: string;
  conflicts: number;
  fatalities: number;
  incidents: number;
  significant?: boolean;
  event?: string;
}

interface TrendChartProps {
  detailed?: boolean;
  height?: number;
}

const TrendChart: React.FC<TrendChartProps> = ({ detailed = false, height = 300 }) => {
  const [selectedMetric, setSelectedMetric] = useState<'conflicts' | 'fatalities'>('conflicts');

  // Mock data with significant events
  const trendData: TrendData[] = [
    { month: 'Jul 2023', conflicts: 45, fatalities: 120, incidents: 67 },
    { month: 'Aug 2023', conflicts: 52, fatalities: 145, incidents: 78 },
    { month: 'Sep 2023', conflicts: 38, fatalities: 98, incidents: 56 },
    { month: 'Oct 2023', conflicts: 61, fatalities: 178, incidents: 89, significant: true, event: 'Election Period' },
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
    return <Minus className="w-4 h-4 text-slate-500" />;
  };

  const getTrendColor = (change: number) => {
    if (change > 5) return 'text-red-600';
    if (change < -5) return 'text-green-600';
    return 'text-slate-600';
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = trendData.find(d => d.month === label);
      return (
        <div className="bg-white/95 backdrop-blur-sm p-4 rounded-xl shadow-lg border border-white/20 min-w-[200px]">
          <div className="flex items-center space-x-2 mb-3">
            <Calendar className="w-4 h-4 text-slate-600" />
            <p className="font-semibold text-slate-900">{label}</p>
          </div>
          
          <div className="space-y-2">
            {payload.map((entry: any, index: number) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div 
                    className="w-3 h-3 rounded-full" 
                    style={{ backgroundColor: entry.color }}
                  />
                  <span className="text-sm text-slate-700 capitalize">{entry.dataKey}</span>
                </div>
                <span className="font-semibold text-slate-900">{entry.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
          
          {data?.significant && (
            <div className="mt-3 pt-3 border-t border-slate-200">
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-500" />
                <span className="text-sm font-medium text-amber-700">{data.event}</span>
              </div>
            </div>
          )}
        </div>
      );
    }
    return null;
  };

  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    if (payload.significant) {
      return (
        <g>
          <circle cx={cx} cy={cy} r={6} fill="#f59e0b" stroke="#fff" strokeWidth={2} />
          <text x={cx} y={cy - 10} textAnchor="middle" className="text-xs fill-amber-700 font-medium">
            {payload.event}
          </text>
        </g>
      );
    }
    return <circle cx={cx} cy={cy} r={4} fill="#1e293b" stroke="#fff" strokeWidth={2} />;
  };

  return (
    <div className="space-y-4">
      {/* Metric Toggle */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setSelectedMetric('conflicts')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedMetric === 'conflicts' 
                ? 'bg-slate-900 text-white shadow-lg' 
                : 'bg-white text-slate-700 hover:bg-slate-50'
            }`}
          >
            Conflicts
          </button>
          <button
            onClick={() => setSelectedMetric('fatalities')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedMetric === 'fatalities' 
                ? 'bg-slate-900 text-white shadow-lg' 
                : 'bg-white text-slate-700 hover:bg-slate-50'
            }`}
          >
            Fatalities
          </button>
        </div>

        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-1">
            {getTrendIcon(conflictChange)}
            <span className={getTrendColor(conflictChange)}>
              {conflictChange > 0 ? '+' : ''}{conflictChange.toFixed(1)}% conflicts
            </span>
          </div>
          <div className="flex items-center space-x-1">
            {getTrendIcon(fatalityChange)}
            <span className={getTrendColor(fatalityChange)}>
              {fatalityChange > 0 ? '+' : ''}{fatalityChange.toFixed(1)}% fatalities
            </span>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="h-full">
        <ResponsiveContainer width="100%" height={height}>
          <ComposedChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="conflictsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#dc2626" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#dc2626" stopOpacity={0.05}/>
              </linearGradient>
              <linearGradient id="fatalitiesGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ea580c" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ea580c" stopOpacity={0.05}/>
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis 
              dataKey="month" 
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              yAxisId="left"
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickLine={false}
              axisLine={false}
              label={{ value: selectedMetric === 'conflicts' ? 'Conflicts' : 'Fatalities', angle: -90, position: 'insideLeft' }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              tick={{ fontSize: 12, fill: '#64748b' }}
              tickLine={false}
              axisLine={false}
              label={{ value: selectedMetric === 'conflicts' ? 'Fatalities' : 'Conflicts', angle: 90, position: 'insideRight' }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            <Area
              yAxisId="left"
              type="monotone"
              dataKey={selectedMetric}
              stroke="#1e293b"
              strokeWidth={3}
              fill="url(#conflictsGradient)"
              dot={<CustomDot />}
              activeDot={{ r: 6, stroke: '#1e293b', strokeWidth: 2, fill: '#fff' }}
              name={selectedMetric.charAt(0).toUpperCase() + selectedMetric.slice(1)}
            />
            
            <Line
              yAxisId="right"
              type="monotone"
              dataKey={selectedMetric === 'conflicts' ? 'fatalities' : 'conflicts'}
              stroke="#94a3b8"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name={selectedMetric === 'conflicts' ? 'Fatalities' : 'Conflicts'}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="flex items-center justify-center space-x-6 text-xs text-slate-500">
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-slate-900 rounded-full"></div>
          <span>Primary Metric</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-0.5 bg-slate-400"></div>
          <span>Secondary Metric</span>
        </div>
        <div className="flex items-center space-x-1">
          <div className="w-3 h-3 bg-amber-400 rounded-full border-2 border-white"></div>
          <span>Significant Events</span>
        </div>
      </div>
    </div>
  );
};

export default TrendChart;
