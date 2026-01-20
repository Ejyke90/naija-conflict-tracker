import React from 'react';
import { motion } from 'framer-motion';

interface PulseAlertProps {
  color?: string;
  size?: 'small' | 'medium' | 'large';
  intensity?: 'low' | 'medium' | 'high';
}

const PulseAlert: React.FC<PulseAlertProps> = ({ 
  color = '#ef4444', 
  size = 'medium',
  intensity = 'medium'
}) => {
  const sizeConfig = {
    small: { container: 'h-4 w-4', dot: 'h-2 w-2', maxExpansion: 32 },
    medium: { container: 'h-6 w-6', dot: 'h-3 w-3', maxExpansion: 48 },
    large: { container: 'h-8 w-8', dot: 'h-4 w-4', maxExpansion: 64 }
  };

  const intensityConfig = {
    low: { duration: 2.5, rings: 2, delay: 1.0 },
    medium: { duration: 2.0, rings: 2, delay: 0.8 },
    high: { duration: 1.5, rings: 3, delay: 0.6 }
  };

  const config = sizeConfig[size];
  const animConfig = intensityConfig[intensity];

  return (
    <div className={`relative flex items-center justify-center ${config.container}`}>
      {/* Central Solid Point */}
      <div 
        className={`relative z-10 ${config.dot} rounded-full`}
        style={{ backgroundColor: color }} 
      />
      
      {/* Animated Rings */}
      {Array.from({ length: animConfig.rings }, (_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{ border: `2px solid ${color}` }}
          initial={{ 
            width: parseInt(config.dot.split('-')[1]) * 4, 
            height: parseInt(config.dot.split('-')[1]) * 4, 
            opacity: 0.8 
          }}
          animate={{
            width: config.maxExpansion,
            height: config.maxExpansion,
            opacity: 0,
          }}
          transition={{
            duration: animConfig.duration,
            repeat: Infinity,
            delay: i * animConfig.delay,
            ease: "easeOut",
          }}
        />
      ))}
    </div>
  );
};

export default PulseAlert;
