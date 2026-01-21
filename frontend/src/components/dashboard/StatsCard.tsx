import React, { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: number;
  subtitle: string;
  trend: number;
  trendLabel: string;
  icon: React.ReactNode;
  gradientClass: string;
}

export function StatsCard({ title, value, subtitle, trend, trendLabel, icon, gradientClass }: StatsCardProps) {
  const [displayValue, setDisplayValue] = useState(0);

  // Count-up animation
  useEffect(() => {
    let start = 0;
    const end = value;
    const duration = 2000;
    const increment = end / (duration / 16);

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setDisplayValue(end);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(start));
      }
    }, 16);

    return () => clearInterval(timer);
  }, [value]);

  const getTrendIcon = () => {
    if (trend > 0) return <TrendingUp className="w-4 h-4" />;
    if (trend < 0) return <TrendingDown className="w-4 h-4" />;
    return <Minus className="w-4 h-4" />;
  };

  const getTrendColor = () => {
    if (title.includes('Fatalities')) {
      return trend < 0 ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50';
    }
    return trend > 0 ? 'text-red-600 bg-red-50' : 'text-green-600 bg-green-50';
  };

  return (
    <div className="group relative bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 hover:-translate-y-1 overflow-hidden">
      {/* Gradient background on hover */}
      <div className={`absolute inset-0 ${gradientClass} opacity-0 group-hover:opacity-5 transition-opacity`}></div>

      {/* Icon with gradient background */}
      <div className="relative flex items-start justify-between mb-4">
        <div className={`p-3 rounded-xl ${gradientClass} bg-opacity-10`}>
          <div className="text-2xl">{icon}</div>
        </div>

        {/* Trend indicator */}
        <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${getTrendColor()}`}>
          {getTrendIcon()}
          <span>{Math.abs(trend)}%</span>
        </div>
      </div>

      {/* Main value with count-up */}
      <div className="relative">
        <div className="text-sm text-gray-500 uppercase tracking-wide font-medium mb-2">
          {title}
        </div>
        <div className="text-4xl font-bold text-gray-900 mb-2 tabular-nums">
          {displayValue.toLocaleString()}
        </div>
        <div className="text-sm text-gray-600">
          {subtitle}
        </div>
        <div className="text-xs text-gray-400 mt-2">
          {trendLabel}
        </div>
      </div>

      {/* Mini sparkline chart placeholder */}
      <div className="mt-4 h-12 flex items-end gap-1">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className={`flex-1 ${gradientClass} rounded-t opacity-20 group-hover:opacity-40 transition-opacity`}
            style={{ height: `${Math.random() * 100}%` }}
          />
        ))}
      </div>
    </div>
  );
}

export default StatsCard;
