import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  AlertTriangle, 
  Users, 
  MapPin, 
  TrendingUp,
  ArrowRight,
  Activity
} from 'lucide-react';
import { StatCard } from './StatCard';
import { NigeriaMap } from './NigeriaMap';

interface LandingStats {
  total_incidents_30d: number;
  total_fatalities_30d: number;
  active_hotspots: number;
  states_affected: number;
  last_updated: string;
  timeline_sparkline: number[];
  top_states: Array<{
    name: string;
    incidents: number;
    fatalities: number;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export const LandingPage: React.FC = () => {
  const [stats, setStats] = useState<LandingStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/public/landing-stats`);
        
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (error) {
        console.error('Failed to fetch landing stats:', error);
        // Use fallback data
        setStats({
          total_incidents_30d: 0,
          total_fatalities_30d: 0,
          active_hotspots: 0,
          states_affected: 0,
          last_updated: new Date().toISOString(),
          timeline_sparkline: [0, 0, 0, 0, 0, 0],
          top_states: []
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Refresh every 60 seconds
    const interval = setInterval(fetchStats, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-blue-50">
        <Activity className="w-8 h-8 text-blue-600 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-gray-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center space-x-3"
            >
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <AlertTriangle className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Nextier</h1>
                <p className="text-xs text-gray-600">Conflict Tracker</p>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex space-x-3"
            >
              <Link href="/login">
                <button className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors">
                  Sign In
                </button>
              </Link>
              <Link href="/register">
                <button className="px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-all hover:shadow-lg">
                  Get Access
                </button>
              </Link>
            </motion.div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20">
        <div className="text-center mb-12">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-4"
          >
            Nigeria Conflict Tracker
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto"
          >
            Real-time monitoring and predictive analytics to prevent violence and save lives across all 36 Nigerian states
          </motion.p>
        </div>

        {/* Map Visualization */}
        <div className="mb-12">
          <div className="bg-white rounded-2xl shadow-2xl p-6 lg:p-8">
            <div className="h-[400px] lg:h-[500px]">
              <NigeriaMap stateData={stats?.top_states || []} />
            </div>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard
            value={stats?.total_incidents_30d || 0}
            label="Total Incidents"
            sublabel="Last 30 days"
            icon={<AlertTriangle className="w-8 h-8" />}
            delay={800}
          />
          <StatCard
            value={stats?.total_fatalities_30d || 0}
            label="Fatalities"
            sublabel="Last 30 days"
            icon={<Users className="w-8 h-8" />}
            delay={1000}
          />
          <StatCard
            value={stats?.active_hotspots || 0}
            label="Active Hotspots"
            sublabel="High risk areas"
            icon={<MapPin className="w-8 h-8" />}
            delay={1200}
          />
          <StatCard
            value={stats?.states_affected || 0}
            label="States Affected"
            sublabel="Out of 36 states"
            icon={<TrendingUp className="w-8 h-8" />}
            delay={1400}
          />
        </div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 1.6 }}
          className="text-center"
        >
          <Link href="/register">
            <button className="group inline-flex items-center space-x-2 px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-xl hover:bg-blue-700 transition-all hover:shadow-xl hover:scale-105">
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </Link>
          <p className="mt-4 text-sm text-gray-600">
            Free account • No credit card required
          </p>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="bg-white/50 backdrop-blur-sm py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Real-Time Monitoring</h3>
              <p className="text-gray-600">
                Track conflict incidents as they happen across Nigeria with automated data collection
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Predictive Analytics</h3>
              <p className="text-gray-600">
                ML-powered forecasting to predict conflict hotspots and prevent escalation
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-purple-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Geospatial Intelligence</h3>
              <p className="text-gray-600">
                Advanced mapping and spatial analysis for all 36 states and 774 LGAs
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400">
            © {new Date().getFullYear()} Nextier. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};
