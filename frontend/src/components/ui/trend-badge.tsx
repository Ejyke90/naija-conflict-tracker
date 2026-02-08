import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

export type TrendDirection = 'up' | 'down' | 'stable';

interface TrendBadgeProps {
  direction: TrendDirection;
  value?: number;
  label?: string;
  variant?: 'default' | 'outline' | 'secondary';
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showPercentage?: boolean;
  className?: string;
  invertColors?: boolean; // For cases where up is bad (e.g., fatalities)
}

export function TrendBadge({
  direction,
  value,
  label,
  variant = 'outline',
  size = 'md',
  showIcon = true,
  showPercentage = true,
  className,
  invertColors = false,
}: TrendBadgeProps) {
  const getTrendIcon = () => {
    switch (direction) {
      case 'up':
        return <TrendingUp className={cn(
          size === 'sm' && 'h-3 w-3',
          size === 'md' && 'h-4 w-4',
          size === 'lg' && 'h-5 w-5'
        )} />;
      case 'down':
        return <TrendingDown className={cn(
          size === 'sm' && 'h-3 w-3',
          size === 'md' && 'h-4 w-4',
          size === 'lg' && 'h-5 w-5'
        )} />;
      case 'stable':
        return <Minus className={cn(
          size === 'sm' && 'h-3 w-3',
          size === 'md' && 'h-4 w-4',
          size === 'lg' && 'h-5 w-5'
        )} />;
    }
  };

  const getTrendColor = () => {
    const isPositive = invertColors
      ? direction === 'down'
      : direction === 'up';

    switch (direction) {
      case 'up':
        return isPositive
          ? 'text-green-700 bg-green-50 border-green-200'
          : 'text-red-700 bg-red-50 border-red-200';
      case 'down':
        return isPositive
          ? 'text-green-700 bg-green-50 border-green-200'
          : 'text-red-700 bg-red-50 border-red-200';
      case 'stable':
        return 'text-gray-700 bg-gray-50 border-gray-200';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'text-xs px-2 py-0.5';
      case 'md':
        return 'text-sm px-2.5 py-1';
      case 'lg':
        return 'text-base px-3 py-1.5';
    }
  };

  const formatValue = () => {
    if (value === undefined) return '';
    const sign = value > 0 ? '+' : '';
    return showPercentage ? `${sign}${value.toFixed(1)}%` : `${sign}${value}`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="inline-block"
    >
      <Badge
        variant={variant}
        className={cn(
          getTrendColor(),
          getSizeClasses(),
          'flex items-center gap-1 font-semibold transition-all hover:shadow-sm',
          className
        )}
      >
        {showIcon && getTrendIcon()}
        {value !== undefined && (
          <span className="tabular-nums">{formatValue()}</span>
        )}
        {label && <span className="ml-1 font-normal">{label}</span>}
      </Badge>
    </motion.div>
  );
}
