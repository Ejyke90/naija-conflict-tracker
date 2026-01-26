import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';
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
      <div className="min-h-screen flex items-center justify-center bg-[#09090b]">
        <Activity className="w-8 h-8 text-[#ff4b4b] animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#09090b]">
      {/* Header */}
      <header className="bg-black/90 backdrop-blur-md border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex items-center space-x-3"
            >
              <Image 
                src="/nnvcd-logo.png" 
                alt="NNVCD Logo" 
                width={200}
                height={60}
                priority
                className="h-12 w-auto object-contain"
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex space-x-3"
            >
              <Link href="/login">
                <button className="px-4 py-2 text-sm font-medium text-gray-400 hover:text-white transition-colors">
                  Sign In
                </button>
              </Link>
              <Link href="/register">
                <button className="px-6 py-2 bg-[#ff4b4b] text-white text-sm font-medium rounded-lg hover:bg-[#ff3333] transition-all hover:shadow-lg hover:shadow-red-500/50">
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
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex justify-center mb-8"
          >
            <Image 
              src="/nnvcd-logo.png" 
              alt="NNVCD - Nextier Nigeria Violent Conflict Database" 
              width={800}
              height={240}
              priority
              className="h-32 sm:h-40 lg:h-48 w-auto object-contain"
            />
          </motion.div>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-lg sm:text-xl text-gray-400 max-w-3xl mx-auto"
          >
            Real-time monitoring and predictive analytics to prevent violence and save lives across all 36 Nigerian states
          </motion.p>
        </div>

        {/* Map Visualization */}
        <div className="mb-12">
          <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8 shadow-2xl shadow-red-900/20">
            <div className="h-[600px] w-full relative">
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
            severity="critical"
            trend={12.5}
            delay={800}
          />
          <StatCard
            value={stats?.total_fatalities_30d || 0}
            label="Fatalities"
            sublabel="Last 30 days"
            icon={<Users className="w-8 h-8" />}
            severity="high"
            trend={8.3}
            delay={1000}
          />
          <StatCard
            value={stats?.active_hotspots || 0}
            label="Active Hotspots"
            sublabel="High risk areas"
            icon={<MapPin className="w-8 h-8" />}
            severity="medium"
            trend={-2.1}
            delay={1200}
          />
          <StatCard
            value={stats?.states_affected || 0}
            label="States Affected"
            sublabel="Out of 36 states"
            icon={<TrendingUp className="w-8 h-8" />}
            severity="low"
            trend={5.7}
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
            <button className="group inline-flex items-center space-x-2 px-8 py-4 bg-[#ff4b4b] text-white text-lg font-semibold rounded-xl hover:bg-[#ff3333] transition-all hover:shadow-xl hover:shadow-red-500/50 hover:scale-105">
              <span>Get Started</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </Link>
          <p className="mt-4 text-sm text-gray-500">
            Free account • No credit card required
          </p>
        </motion.div>
      </section>

      {/* Features Section */}
      <section className="bg-black/20 backdrop-blur-sm border-y border-gray-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-blue-500/10 border border-blue-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Real-Time Monitoring</h3>
              <p className="text-gray-400">
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
              <div className="w-16 h-16 bg-green-500/10 border border-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-green-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Predictive Analytics</h3>
              <p className="text-gray-400">
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
              <div className="w-16 h-16 bg-purple-500/10 border border-purple-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-8 h-8 text-purple-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Geospatial Intelligence</h3>
              <p className="text-gray-400">
                Advanced mapping and spatial analysis for all 36 states and 774 LGAs
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-600">
            © {new Date().getFullYear()} Nextier. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};
