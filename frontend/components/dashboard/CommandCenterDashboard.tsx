// frontend/components/dashboard/CommandCenterDashboard.tsx
import React, { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { CommandCenterLayout } from '../layouts/CommandCenterLayout';
import { AIForesightCard } from './AIForesightCard';
import { RealTimeMetrics } from './RealTimeMetrics';
import { IncidentFeed } from './IncidentFeed';

// Dynamic imports for map components
const ThreatMap = dynamic(() => import('../maps/ThreatMap') as any, {
  ssr: false,
  loading: () => (
    <div className="threat-map-container flex items-center justify-center bg-slate-800/50 rounded-xl">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
        <p className="text-slate-300">Loading threat map...</p>
      </div>
    </div>
  )
});

export const CommandCenterDashboard: React.FC = () => {
  const [currentTime, setCurrentTime] = useState<string>('');

  useEffect(() => {
    // Update time every second
    const updateTime = () => {
      setCurrentTime(new Date().toLocaleString());
    };

    updateTime();
    const interval = setInterval(updateTime, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen command-center-bg text-gray-100 p-8">
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">Naija Conflict Tracker</h1>
            <p className="text-slate-400">
              Real-time conflict monitoring and predictive analytics across Nigeria
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400 mb-1">Last Updated</div>
            <div className="text-lg font-mono text-emerald-400">{currentTime}</div>
          </div>
        </div>

        {/* Real-Time Metrics */}
        <RealTimeMetrics />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          {/* Threat Map - Takes up 2 columns on xl screens */}
          <div className="xl:col-span-2">
            <div className="glass-panel p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-slate-700 rounded-lg flex items-center justify-center">
                  <div className="w-6 h-6 bg-rose-500 rounded-full animate-pulse"></div>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Global Threat Map</h3>
                  <p className="text-sm text-slate-400">Live conflict density visualization</p>
                </div>
              </div>

              {/* <ThreatMap /> */}
              <div className="threat-map-container flex items-center justify-center bg-slate-800/50 rounded-xl">
                <div className="text-center">
                  <div className="text-6xl mb-4">🗺️</div>
                  <p className="text-slate-300">Threat Map Placeholder</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            {/* AI Foresight Card */}
            <AIForesightCard
              predictedRisk={68}
              flaggedLGAs={['Borno', 'Kaduna', 'Zamfara', 'Yobe']}
              confidence={89}
            />

            {/* Incident Feed */}
            <IncidentFeed />
          </div>
        </div>

        {/* Footer Stats */}
        <div className="glass-panel p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-2xl font-bold text-emerald-400">23</div>
              <div className="text-sm text-slate-400">Active Monitors</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-400">156</div>
              <div className="text-sm text-slate-400">Data Sources</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-indigo-400">94.2%</div>
              <div className="text-sm text-slate-400">System Uptime</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-rose-400">2.3s</div>
              <div className="text-sm text-slate-400">Avg Response</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CommandCenterDashboard;
