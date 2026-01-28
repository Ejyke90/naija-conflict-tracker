import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Activity, Brain, MapPin } from 'lucide-react';

interface PulseMetric {
  label: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
  color: string;
}

export const LivePulse: React.FC = () => {
  const [metrics, setMetrics] = useState<PulseMetric[]>([
    {
      label: 'Total Incidents Tracked',
      value: '12,847',
      change: 8.3,
      icon: <Activity className="w-6 h-6" />,
      color: 'text-blue-400'
    },
    {
      label: 'AI Prediction Success Rate',
      value: '94.2%',
      change: 2.1,
      icon: <Brain className="w-6 h-6" />,
      color: 'text-green-400'
    },
    {
      label: 'Current High-Alert Regions',
      value: 'Borno, Kaduna, Zamfara',
      icon: <MapPin className="w-6 h-6" />,
      color: 'text-red-400'
    }
  ]);

  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Set initial time after hydration
  useEffect(() => {
    setLastUpdated(new Date().toLocaleTimeString());
  }, []);

  // Update time every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdated(new Date().toLocaleTimeString());
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => prev.map(metric => ({
        ...metric,
        // Simulate small changes
        change: metric.change ? metric.change + (Math.random() - 0.5) * 2 : undefined
      })));
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <section className="py-20 bg-slate-900/50 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Live Pulse
          </h2>
          <p className="text-xl text-slate-300 max-w-2xl mx-auto">
            Real-time intelligence from across Nigeria&apos;s conflict landscape
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.label}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="group relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-slate-800/50 to-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-700/50 group-hover:border-slate-600/50 transition-all duration-300"></div>

              <div className="relative p-8">
                <div className="flex items-center justify-between mb-6">
                  <div className={`p-3 rounded-lg bg-slate-800/50 ${metric.color}`}>
                    {metric.icon}
                  </div>
                  {metric.change && (
                    <div className={`flex items-center gap-1 text-sm ${
                      metric.change >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {metric.change >= 0 ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <TrendingDown className="w-4 h-4" />
                      )}
                      <span>{Math.abs(metric.change).toFixed(1)}%</span>
                    </div>
                  )}
                </div>

                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-slate-300">
                    {metric.label}
                  </h3>
                  <div className="text-3xl md:text-4xl font-bold text-white">
                    {metric.value}
                  </div>
                </div>

                {/* Pulse animation for live indicator */}
                <div className="absolute top-4 right-4">
                  <div className="relative">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <div className="absolute inset-0 w-2 h-2 bg-green-400 rounded-full animate-ping opacity-75"></div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          viewport={{ once: true }}
          className="text-center mt-12"
        >
          <p className="text-sm text-slate-400">
            Data updates every 30 seconds • Last updated: {lastUpdated}
          </p>
        </motion.div>
      </div>
    </section>
  );
};