import { motion, useAnimation } from 'framer-motion';
import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, AlertTriangle, Users, MapPin, Activity } from 'lucide-react';

interface StatCardProps {
  label: string;
  value: number;
  change: number;
  period?: string;
  color: 'red' | 'purple' | 'blue' | 'green';
  icon: 'incidents' | 'fatalities' | 'hotspots' | 'states';
  sparklineData?: number[];
  index: number;
}

// Easing function for smooth counting
const easeOutQuart = (t: number) => 1 - (--t) * t * t * t;

// Animated counter component
const CountUp = ({ end, duration = 2000 }: { end: number; duration?: number }) => {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      if (progress < 1) {
        setCount(Math.floor(end * easeOutQuart(progress)));
        requestAnimationFrame(animate);
      } else {
        setCount(end);
      }
    };
    requestAnimationFrame(animate);
  }, [end, duration]);
  
  return <span>{count.toLocaleString()}</span>;
};

// Sparkline mini chart
const Sparkline = ({ data }: { data: number[] }) => {
  if (!data || data.length === 0) return null;
  
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  
  const points = data
    .map((value, index) => {
      const x = (index / (data.length - 1)) * 100;
      const y = 30 - ((value - min) / range) * 25;
      return `${x},${y}`;
    })
    .join(' ');
  
  return (
    <svg width="100%" height="30" className="sparkline">
      <motion.polyline
        points={points}
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 0.6 }}
        transition={{ duration: 1.5, delay: 0.5 }}
      />
    </svg>
  );
};

// Get icon component based on type
const getIcon = (type: string) => {
  switch (type) {
    case 'incidents':
      return <AlertTriangle className="w-8 h-8" />;
    case 'fatalities':
      return <Users className="w-8 h-8" />;
    case 'hotspots':
      return <MapPin className="w-8 h-8" />;
    case 'states':
      return <Activity className="w-8 h-8" />;
    default:
      return <Activity className="w-8 h-8" />;
  }
};

// Get color classes
const getColorClasses = (color: string) => {
  const classes = {
    red: {
      bg: 'from-red-500 to-orange-600',
      iconBg: 'bg-red-500/20',
      iconText: 'text-red-600',
      ring: 'ring-red-500/20',
    },
    purple: {
      bg: 'from-purple-500 to-pink-600',
      iconBg: 'bg-purple-500/20',
      iconText: 'text-purple-600',
      ring: 'ring-purple-500/20',
    },
    blue: {
      bg: 'from-blue-500 to-cyan-600',
      iconBg: 'bg-blue-500/20',
      iconText: 'text-blue-600',
      ring: 'ring-blue-500/20',
    },
    green: {
      bg: 'from-green-500 to-emerald-600',
      iconBg: 'bg-green-500/20',
      iconText: 'text-green-600',
      ring: 'ring-green-500/20',
    },
  };
  return classes[color as keyof typeof classes] || classes.blue;
};

export const AnimatedStatCard = ({
  label,
  value,
  change,
  period = 'Last 30 days',
  color,
  icon,
  sparklineData,
  index,
}: StatCardProps) => {
  const colors = getColorClasses(color);
  
  // Animation variants
  const cardVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8, 
      y: 20 
    },
    visible: {
      opacity: 1,
      scale: 1,
      y: 0,
      transition: {
        delay: index * 0.1,
        duration: 0.5,
        ease: [0.25, 0.1, 0.25, 1.0],
      },
    },
  };
  
  return (
    <motion.div
      className="stat-card group"
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ 
        y: -8,
        scale: 1.02,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.15)',
        transition: { duration: 0.2 }
      }}
    >
      <div className="stat-card-inner">
        {/* Background gradient (subtle) */}
        <div className={`stat-card-gradient bg-gradient-to-br ${colors.bg}`} />
        
        {/* Icon container */}
        <div className="stat-icon-container">
          <motion.div
            className={`stat-icon ${colors.iconBg} ${colors.iconText}`}
            whileHover={{ 
              rotate: 5, 
              scale: 1.1,
              transition: { duration: 0.3 }
            }}
          >
            {getIcon(icon)}
          </motion.div>
        </div>
        
        {/* Label */}
        <div className="stat-label">{label}</div>
        
        {/* Value with counter animation */}
        <div className="stat-value">
          <CountUp end={value} duration={2000} />
        </div>
        
        {/* Period */}
        <div className="stat-period">{period}</div>
        
        {/* Sparkline */}
        {sparklineData && sparklineData.length > 0 && (
          <div className="stat-sparkline">
            <Sparkline data={sparklineData} />
          </div>
        )}
        
        {/* Change indicator */}
        <motion.div
          className={`stat-change ${change >= 0 ? 'stat-change-positive' : 'stat-change-negative'}`}
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.1 + 0.5 }}
        >
          <div className="stat-change-content">
            {change >= 0 ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span className="stat-change-value">
              {change >= 0 ? '+' : ''}{change}%
            </span>
          </div>
          <span className="stat-change-label">vs previous period</span>
        </motion.div>
      </div>
      
      <style jsx>{`
        .stat-card {
          position: relative;
          background: white;
          border-radius: 1rem;
          padding: 1.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          overflow: hidden;
          cursor: pointer;
        }
        
        .stat-card-inner {
          position: relative;
          z-index: 1;
        }
        
        .stat-card-gradient {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          height: 4px;
          opacity: 0.8;
        }
        
        .stat-icon-container {
          margin-bottom: 1rem;
        }
        
        .stat-icon {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          padding: 0.75rem;
          border-radius: 0.75rem;
          transition: all 0.3s ease;
        }
        
        .stat-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: #6b7280;
          margin-bottom: 0.5rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        
        .stat-value {
          font-size: 2.5rem;
          font-weight: 700;
          color: #111827;
          line-height: 1;
          margin-bottom: 0.25rem;
        }
        
        .stat-period {
          font-size: 0.75rem;
          color: #9ca3af;
          margin-bottom: 1rem;
        }
        
        .stat-sparkline {
          margin: 1rem 0;
          color: #6b7280;
        }
        
        .stat-change {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        
        .stat-change-content {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
          font-weight: 600;
        }
        
        .stat-change-positive {
          color: #10b981;
        }
        
        .stat-change-negative {
          color: #ef4444;
        }
        
        .stat-change-label {
          font-size: 0.75rem;
          color: #9ca3af;
          font-weight: 400;
        }
        
        .stat-change-value {
          font-weight: 600;
        }
        
        /* Dark mode */
        [data-theme="dark"] .stat-card {
          background: #1e293b;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }
        
        [data-theme="dark"] .stat-label {
          color: #94a3b8;
        }
        
        [data-theme="dark"] .stat-value {
          color: #f1f5f9;
        }
        
        [data-theme="dark"] .stat-period,
        [data-theme="dark"] .stat-change-label {
          color: #64748b;
        }
      `}</style>
    </motion.div>
  );
};

// Grid container for stat cards
export const StatsGrid = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="stats-grid">
      {children}
      <style jsx>{`
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin: 2rem 0;
        }
        
        @media (max-width: 768px) {
          .stats-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};
