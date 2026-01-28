import React from 'react';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { Activity, Target, MapPin, Users } from 'lucide-react';

interface MetricTileProps {
  title: string;
  value: string | number;
  change: number;
  changeLabel: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  sparklineData: Array<{ value: number }>;
}

const MetricTile: React.FC<MetricTileProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  color,
  sparklineData
}) => {
  const isPositive = change > 0;

  return (
    <div className="stat-card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-400">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
          </div>
        </div>

        {/* Sparkline */}
        <div className="w-16 h-8">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={sparklineData}>
              <Line
                type="monotone"
                dataKey="value"
                stroke={isPositive ? '#f43f5e' : '#10b981'}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Change Indicator */}
      <div className={`flex items-center gap-1 text-sm ${
        isPositive ? 'text-rose-400' : 'text-emerald-400'
      }`}>
        <span className="font-medium">
          {isPositive ? '+' : ''}{change}%
        </span>
        <span className="text-slate-400">{changeLabel}</span>
      </div>
    </div>
  );
};

interface RealTimeMetricsProps {
  metrics?: {
    totalIncidents24h: number;
    predictionAccuracy: number;
    activeHotspots: number;
    displacementStats: number;
  };
}

export const RealTimeMetrics: React.FC<RealTimeMetricsProps> = ({
  metrics = {
    totalIncidents24h: 23,
    predictionAccuracy: 94,
    activeHotspots: 7,
    displacementStats: 1250
  }
}) => {
  // Sample sparkline data
  const generateSparklineData = (baseValue: number, variance: number = 10) => {
    return Array.from({ length: 12 }, (_, i) => ({
      value: baseValue + Math.random() * variance - variance / 2
    }));
  };

  const metricTiles = [
    {
      title: 'Total Incidents (24h)',
      value: metrics.totalIncidents24h,
      change: 12,
      changeLabel: 'vs yesterday',
      icon: Activity,
      color: 'bg-rose-500',
      sparklineData: generateSparklineData(metrics.totalIncidents24h, 5)
    },
    {
      title: 'Prediction Accuracy',
      value: `${metrics.predictionAccuracy}%`,
      change: -2,
      changeLabel: 'vs last week',
      icon: Target,
      color: 'bg-emerald-500',
      sparklineData: generateSparklineData(metrics.predictionAccuracy, 3)
    },
    {
      title: 'Active Hotspots',
      value: metrics.activeHotspots,
      change: 8,
      changeLabel: 'vs yesterday',
      icon: MapPin,
      color: 'bg-amber-500',
      sparklineData: generateSparklineData(metrics.activeHotspots, 2)
    },
    {
      title: 'Displacement Stats',
      value: `${metrics.displacementStats.toLocaleString()}`,
      change: 15,
      changeLabel: 'vs last month',
      icon: Users,
      color: 'bg-indigo-500',
      sparklineData: generateSparklineData(metrics.displacementStats / 100, 50)
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {metricTiles.map((tile, index) => (
        <MetricTile key={index} {...tile} />
      ))}
    </div>
  );
};