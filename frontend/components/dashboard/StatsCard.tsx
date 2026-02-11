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
  gradientClass = 'glass-card'
}) => {
  const getSignalColor = (trendValue?: number) => {
    if (!trendValue) return 'text-tactical-e-ink';
    if (trendValue > 10) return 'signal-critical';
    if (trendValue > 5) return 'signal-high';
    if (trendValue > 0) return 'signal-medium';
    return 'signal-low';
  };

  return (
    <div className={`rounded-xl p-6 text-tactical-e-ink shadow-lg border border-white/10 ${gradientClass}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="typography-label text-tactical-e-ink/70 mb-2">{title}</p>
          <p className="typography-heading text-3xl mb-1">{value.toLocaleString()}</p>
          <p className="typography-body text-tactical-e-ink/70 text-sm">{subtitle}</p>
          {trend && trendLabel && (
            <p className={`typography-label text-sm mt-2 ${getSignalColor(trend)}`}>
              {trend > 0 ? '+' : ''}{trend}% {trendLabel}
            </p>
          )}
        </div>
        {icon && <span className="text-4xl text-tactical-e-ink/50">{icon}</span>}
      </div>
    </div>
  );
};
