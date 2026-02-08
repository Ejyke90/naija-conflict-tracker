import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';

interface SparklineData {
  value: number;
  label?: string;
}

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: {
    direction: 'up' | 'down' | 'stable';
    percentage: number;
    label?: string;
  };
  sparklineData?: SparklineData[];
  variant?: 'default' | 'primary' | 'destructive' | 'success';
  className?: string;
}

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  sparklineData,
  variant = 'default',
  className = '',
}: StatCardProps) {
  const getTrendIcon = () => {
    if (!trend) return null;
    switch (trend.direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4" />;
      case 'down':
        return <TrendingDown className="h-4 w-4" />;
      case 'stable':
        return <Minus className="h-4 w-4" />;
    }
  };

  const getTrendColor = () => {
    if (!trend) return '';
    switch (trend.direction) {
      case 'up':
        return 'text-red-600 bg-red-50';
      case 'down':
        return 'text-green-600 bg-green-50';
      case 'stable':
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return 'border-l-4 border-l-primary';
      case 'destructive':
        return 'border-l-4 border-l-destructive';
      case 'success':
        return 'border-l-4 border-l-green-500';
      default:
        return '';
    }
  };

  // Simple sparkline renderer
  const renderSparkline = () => {
    if (!sparklineData || sparklineData.length === 0) return null;

    const max = Math.max(...sparklineData.map((d) => d.value));
    const min = Math.min(...sparklineData.map((d) => d.value));
    const range = max - min || 1;

    return (
      <div className="flex items-end gap-0.5 h-8 mt-2">
        {sparklineData.map((data, index) => {
          const height = ((data.value - min) / range) * 100;
          return (
            <motion.div
              key={index}
              className="flex-1 bg-primary/20 rounded-sm"
              style={{ height: `${height}%`, minHeight: '2px' }}
              initial={{ scaleY: 0 }}
              animate={{ scaleY: 1 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
            />
          );
        })}
      </div>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className={className}
    >
      <Card className={`hover:shadow-lg transition-shadow ${getVariantStyles()}`}>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {title}
            </CardTitle>
            {Icon && (
              <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Icon className="h-4 w-4 text-primary" />
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-1">
            <motion.div
              className="text-3xl font-bold tracking-tight"
              initial={{ scale: 0.5 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            >
              {typeof value === 'number' ? value.toLocaleString() : value}
            </motion.div>
            
            {subtitle && (
              <p className="text-xs text-muted-foreground">{subtitle}</p>
            )}

            {trend && (
              <div className="flex items-center gap-1 pt-1">
                <Badge variant="outline" className={`${getTrendColor()} flex items-center gap-1 px-2 py-0.5`}>
                  {getTrendIcon()}
                  <span className="text-xs font-semibold">
                    {trend.percentage > 0 ? '+' : ''}{trend.percentage.toFixed(1)}%
                  </span>
                </Badge>
                {trend.label && (
                  <span className="text-xs text-muted-foreground ml-1">
                    {trend.label}
                  </span>
                )}
              </div>
            )}

            {renderSparkline()}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
