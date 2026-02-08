import React, { useEffect, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';

interface MetricDisplayProps {
  value: number;
  duration?: number;
  suffix?: string;
  prefix?: string;
  formatLarge?: boolean;
  className?: string;
  decimals?: number;
  colorByValue?: {
    threshold: number;
    above: string;
    below: string;
  };
}

export function MetricDisplay({
  value,
  duration = 1000,
  suffix = '',
  prefix = '',
  formatLarge = false,
  className = '',
  decimals = 0,
  colorByValue,
}: MetricDisplayProps) {
  const [displayValue, setDisplayValue] = useState(0);

  // Format large numbers (1000 -> 1K, 1000000 -> 1M)
  const formatNumber = (num: number): string => {
    if (!formatLarge) {
      return num.toFixed(decimals);
    }

    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toFixed(decimals);
  };

  // Animate the counter
  useEffect(() => {
    let startTime: number;
    let animationFrame: number;

    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);

      // Easing function (ease-out)
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = Math.floor(easeOut * value);

      setDisplayValue(current);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [value, duration]);

  const getColor = () => {
    if (!colorByValue) return '';
    return displayValue >= colorByValue.threshold
      ? colorByValue.above
      : colorByValue.below;
  };

  return (
    <motion.span
      className={`font-bold tabular-nums ${getColor()} ${className}`}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
    >
      {prefix}
      {formatNumber(displayValue)}
      {suffix}
    </motion.span>
  );
}
