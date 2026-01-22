import React from 'react';

interface StatsCardProps {
  title: string;
  value: number;
  subtitle: string;
  trend?: number;
  trendLabel?: string;
  icon?: string;
  gradientClass?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  trendLabel,
  icon,
  gradientClass = 'bg-gradient-to-br from-slate-500 to-slate-600'
}) => {
  return (
    <div className={`rounded-xl p-6 text-white shadow-lg ${gradientClass}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium opacity-90">{title}</p>
          <p className="text-3xl font-bold">{value.toLocaleString()}</p>
          <p className="text-sm opacity-75">{subtitle}</p>
          {trend && trendLabel && (
            <p className="text-sm opacity-75 mt-1">
              {trend > 0 ? '+' : ''}{trend}% {trendLabel}
            </p>
          )}
        </div>
        {icon && <span className="text-4xl">{icon}</span>}
      </div>
    </div>
  );
};
