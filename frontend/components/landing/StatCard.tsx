import React, { useEffect, useRef, useState } from 'react';
import { motion, useInView, useMotionValue, useSpring } from 'framer-motion';

interface StatCardProps {
  value: number;
  label: string;
  sublabel: string;
  icon?: React.ReactNode;
  delay?: number;
}

export const StatCard: React.FC<StatCardProps> = ({
  value,
  label,
  sublabel,
  icon,
  delay = 0
}) => {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });
  const motionValue = useMotionValue(0);
  const springValue = useSpring(motionValue, {
    stiffness: 50,
    damping: 30
  });
  const [displayValue, setDisplayValue] = useState(0);

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
      className="bg-white rounded-xl shadow-lg p-6 border border-gray-100 hover:shadow-xl hover:scale-105 transition-all duration-300"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="text-3xl sm:text-4xl font-bold text-gray-900">
          {displayValue.toLocaleString()}
        </div>
        {icon && (
          <div className="text-blue-600">
            {icon}
          </div>
        )}
      </div>
      <div className="text-sm font-semibold text-gray-700 mb-1">
        {label}
      </div>
      <div className="text-xs text-gray-500">
        {sublabel}
      </div>
    </motion.div>
  );
};
