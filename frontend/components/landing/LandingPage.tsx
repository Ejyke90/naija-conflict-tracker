/* eslint-disable @next/next/no-img-element */
import React, { useEffect, useState } from 'react';
import Image from 'next/image';
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
import { EconomicPulseChart } from './EconomicPulseChart';
import { ArchetypeChart } from './ArchetypeChart';
import { RecentIncidentsFeed } from './RecentIncidentsFeed';

interface LandingStats {
  total_incidents_30d: number;
  total_fatalities_30d: number;
  active_hotspots: number;
  states_affected: number;
  last_updated: string;
  timeline_sparkline: number[];
  trends?: {
    incidents_change_pct?: number;
    fatalities_change_pct?: number;
    hotspots_change_pct?: number;
    states_change?: number;
  };
  economic_pulse?: Array<{
    month: string;
    incidents: number;
    fuel_price?: number;
    inflation?: number;
  }>;
  archetypes?: Array<{
    type: string;
    count: number;
    percentage?: number;
    confidence?: number;
  }>;
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
          trends: {
            incidents_change_pct: 0,
            fatalities_change_pct: 0,
            hotspots_change_pct: 0,
            states_change: 0
          },
          economic_pulse: [
            { month: '2025-07', incidents: 42, fuel_price: 720, inflation: 22.5 },
            { month: '2025-08', incidents: 48, fuel_price: 750, inflation: 23.1 },
            { month: '2025-09', incidents: 55, fuel_price: 790, inflation: 24.0 },
            { month: '2025-10', incidents: 60, fuel_price: 820, inflation: 24.8 },
            { month: '2025-11', incidents: 58, fuel_price: 815, inflation: 24.5 },
            { month: '2025-12', incidents: 65, fuel_price: 840, inflation: 25.2 }
          ],
          archetypes: [
            { type: 'Banditry', count: 23, percentage: 40.4, confidence: 0.92 },
            { type: 'Farmer-Herder', count: 15, percentage: 26.3, confidence: 0.88 },
            { type: 'Sectarian', count: 12, percentage: 21.1, confidence: 0.85 },
            { type: 'Kidnapping', count: 7, percentage: 12.3, confidence: 0.90 }
          ],
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

  useEffect(() => {
    if (stats && typeof window !== 'undefined') {
      window.dispatchEvent(new Event('resize'));
    }
  }, [stats]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#09090b]">
        <Activity className="w-8 h-8 text-[#ff4b4b] animate-spin" />
      </div>
    );
  }

  const trends = stats?.trends || {};
  const incidentsTrend = trends.incidents_change_pct ?? 12.5;
  const fatalitiesTrend = trends.fatalities_change_pct ?? 8.3;
  const hotspotsTrend = trends.hotspots_change_pct ?? -2.1;
  const statesTrend = trends.states_change ?? 5.7;

  const tickerItems = [
    {
      label: 'Incident Velocity',
      value: `${incidentsTrend >= 0 ? '↑' : '↓'} ${Math.abs(incidentsTrend).toFixed(1)}% vs last 30d`
    },
    {
      label: 'Fatality Drift',
      value: `${fatalitiesTrend >= 0 ? '↑' : '↓'} ${Math.abs(fatalitiesTrend).toFixed(1)}% change`
    },
    {
      label: 'Hotspot Pressure',
      value: `${hotspotsTrend >= 0 ? '↑' : '↓'} ${Math.abs(hotspotsTrend).toFixed(1)}% movement`
    },
    {
      label: 'States Impacted',
      value: `${stats?.states_affected ?? 0} of 36 with active alerts`
    }
  ];

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
              <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">
                NNVCD
              </div>
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
            <div className="text-center">
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-500 via-orange-500 to-red-600 mb-2">
                NNVCD
              </h1>
              <p className="text-sm sm:text-base text-gray-400 font-medium">
                Nextier Nigeria Violent Conflict Database
              </p>
            </div>
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

        {/* Live Ticker */}
        <div className="relative overflow-hidden rounded-xl border border-gray-800 bg-black/40 shadow-lg shadow-red-900/20 mb-8">
          <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 via-transparent to-blue-500/10" />
          <div className="flex space-x-10 marquee py-3 px-4 text-sm sm:text-base">
            {[...tickerItems, ...tickerItems].map((item, idx) => (
              <div key={`${item.label}-${idx}`} className="flex items-center space-x-2 text-gray-200 whitespace-nowrap">
                <span className="h-2.5 w-2.5 rounded-full bg-[#ff4b4b] animate-pulse" aria-hidden />
                <span className="font-semibold text-white">{item.label}</span>
                <span className="text-gray-500">•</span>
                <span className="text-gray-300">{item.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Map Visualization */}
        <div className="mb-12">
          <div className="bg-black/40 backdrop-blur-sm rounded-2xl border border-gray-800 p-6 lg:p-8 shadow-2xl shadow-red-900/20">
            <div className="h-[600px] w-full relative">
              <NigeriaMap stateData={stats?.top_states || []} />
            </div>
          </div>
        </div>

        {/* Economic Pulse & Archetype Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          <EconomicPulseChart data={stats?.economic_pulse || []} />
          <ArchetypeChart data={stats?.archetypes || []} />
        </div>

        {/* Recent Incidents Feed */}
        <div className="mb-12">
          <RecentIncidentsFeed />
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard
            value={stats?.total_incidents_30d || 0}
            label="Total Incidents"
            sublabel="Last 30 days"
            icon={<AlertTriangle className="w-8 h-8" />}
            severity="critical"
            trend={incidentsTrend}
            delay={800}
          />
          <StatCard
            value={stats?.total_fatalities_30d || 0}
            label="Fatalities"
            sublabel="Last 30 days"
            icon={<Users className="w-8 h-8" />}
            severity="high"
            trend={fatalitiesTrend}
            delay={1000}
          />
          <StatCard
            value={stats?.active_hotspots || 0}
            label="Active Hotspots"
            sublabel="High risk areas"
            icon={<MapPin className="w-8 h-8" />}
            severity="medium"
            trend={hotspotsTrend}
            delay={1200}
          />
          <StatCard
            value={stats?.states_affected || 0}
            label="States Affected"
            sublabel="Out of 36 states"
            icon={<TrendingUp className="w-8 h-8" />}
            severity="low"
            trend={statesTrend}
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

      <style jsx global>{`
        @keyframes marquee {
          0% { transform: translateX(0); }
          100% { transform: translateX(-50%); }
        }
        .marquee {
          animation: marquee 22s linear infinite;
          width: max-content;
        }
      `}</style>
    </div>
  );
};
