import React, { useEffect, useRef, useState } from 'react';
import { motion, useInView, useMotionValue, useSpring } from 'framer-motion';

interface StatCardProps {
  value: number;
  label: string;
  sublabel: string;
  icon?: React.ReactNode;
  delay?: number;
  trend?: number; // Percentage change
  severity?: 'critical' | 'high' | 'medium' | 'low';
}

const getSeverityColors = (severity?: string) => {
  switch (severity) {
    case 'critical':
      return {
        bg: 'from-red-900/40 to-red-800/20',
        border: 'border-red-500/30',
        glow: 'shadow-red-500/20',
        icon: 'text-red-400',
        text: 'text-red-400',
        pulse: 'bg-red-500/20'
      };
    case 'high':
      return {
        bg: 'from-orange-900/40 to-orange-800/20',
        border: 'border-orange-500/30',
        glow: 'shadow-orange-500/20',
        icon: 'text-orange-400',
        text: 'text-orange-400',
        pulse: 'bg-orange-500/20'
      };
    case 'medium':
      return {
        bg: 'from-blue-900/40 to-blue-800/20',
        border: 'border-blue-500/30',
        glow: 'shadow-blue-500/20',
        icon: 'text-blue-400',
        text: 'text-blue-400',
        pulse: 'bg-blue-500/20'
      };
    default:
      return {
        bg: 'from-green-900/40 to-green-800/20',
        border: 'border-green-500/30',
        glow: 'shadow-green-500/20',
        icon: 'text-green-400',
        text: 'text-green-400',
        pulse: 'bg-green-500/20'
      };
  }
};

export const StatCard: React.FC<StatCardProps> = ({
  value,
  label,
  sublabel,
  icon,
  delay = 0,
  trend,
  severity = 'low'
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    stiffness: 50,
    damping: 30
  });
  const [displayValue, setDisplayValue] = useState(0);
  const colors = getSeverityColors(severity);

  useEffect(() => {
    if (isInView) {
      setTimeout(() => {
        motionValue.set(value);
      }, delay);
    }
  }, [isInView, value, delay, motionValue]);

  useEffect(() => {
    const unsubscribe = springValue.on('change', (latest) => {
      setDisplayValue(Math.floor(latest));
    });
    return unsubscribe;
  }, [springValue]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.6, delay: delay / 1000 }}
      whileHover={{ scale: 1.05, y: -5 }}
      className={`relative p-6 rounded-xl bg-gradient-to-br ${colors.bg} ${colors.border} border backdrop-blur-sm shadow-xl ${colors.glow} hover:shadow-2xl transition-all duration-300 overflow-hidden group`}
    >
      {/* Animated background pulse */}
      <motion.div
        className={`absolute inset-0 ${colors.pulse} opacity-0 group-hover:opacity-100`}
        animate={{
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />
      
      <div className="relative z-10">
        <div className="flex items-start justify-between mb-4">
          {icon && (
            <div className={`p-3 rounded-lg ${colors.pulse} ${colors.border} border`}>
              <div className={colors.icon}>{icon}</div>
            </div>
          )}
          {trend !== undefined && (
            <div className={`flex items-center space-x-1 text-sm font-semibold ${trend >= 0 ? 'text-red-400' : 'text-green-400'}`}>
              <span>{trend >= 0 ? '↑' : '↓'}</span>
              <span>{Math.abs(trend).toFixed(1)}%</span>
            </div>
          )}
        </div>
        
        <div className="space-y-2">
          <div className="flex items-baseline space-x-2">
            <span className={`text-4xl font-bold ${colors.text}`}>
              {displayValue.toLocaleString()}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider">{label}</h3>
          <p className="text-xs text-gray-500">{sublabel}</p>
        </div>
      </div>
    </motion.div>
  );
};
    </motion.div>
  );
};
