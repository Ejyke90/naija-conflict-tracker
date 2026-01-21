import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Globe, 
  TrendingUp, 
  Activity, 
  FileText,
  AlertTriangle,
  Users,
  MapPin
} from 'lucide-react';
import dynamic from 'next/dynamic';

interface ConflictDashboardProps {
  activeView?: string;
}

export const ConflictDashboard: React.FC<ConflictDashboardProps> = ({ activeView = 'overview' }) => {
  const [activeTab, setActiveTab] = useState(activeView);
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) return null;

  // Mock data for demonstration
  const stats = {
    totalIncidents: 1234,
    fatalities: 567,
    activeHotspots: 23,
    statesAffected: 18
  };

  const AIPredictions = dynamic(() => import('./AIPredictions'), {
    ssr: false,
    loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading AI predictions...</div>
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Conflict Intelligence Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-1">
            Real-time monitoring and predictive analysis for Nigeria
          </p>
        </div>
        <span className="px-3 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded-full text-sm font-semibold">
          Risk Level: HIGH
        </span>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Incidents</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalIncidents.toLocaleString()}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Last 30 days</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-red-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Fatalities</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.fatalities.toLocaleString()}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">Confirmed deaths</p>
            </div>
            <Users className="h-8 w-8 text-orange-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Hotspots</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.activeHotspots}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">High-risk areas</p>
            </div>
            <MapPin className="h-8 w-8 text-amber-500" />
          </div>
        </div>

        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600 dark:text-gray-400">States Affected</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{stats.statesAffected}/36</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">States monitored</p>
            </div>
            <Globe className="h-8 w-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Main Content Tabs */}
      <div className="w-full">
        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-slate-800 p-1 rounded-lg mb-6">
          {[
            { id: 'overview', label: 'Overview', icon: Activity },
            { id: 'mapping', label: 'Mapping', icon: Globe },
            { id: 'analytics', label: 'Analytics', icon: TrendingUp },
            { id: 'reports', label: 'Reports', icon: BarChart3 },
            { id: 'alerts', label: 'Alerts', icon: AlertTriangle }
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-white dark:bg-slate-700 text-gray-900 dark:text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="bg-white dark:bg-slate-800 rounded-lg p-6 shadow-lg border border-gray-200 dark:border-slate-700">
          {activeTab === 'overview' && (
            <div>
              <div className="flex items-center mb-4">
                <Activity className="w-5 h-5 mr-2 text-blue-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Real-Time Overview</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Current conflict situation and key metrics. Dashboard content for overview tab. This will include maps, charts, and key metrics.
              </p>
            </div>
          )}

          {activeTab === 'mapping' && (
            <div>
              <div className="flex items-center mb-4">
                <Globe className="w-5 h-5 mr-2 text-green-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Advanced Mapping</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Interactive conflict mapping with clustering and heatmaps. Interactive map component will be displayed here.
              </p>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div>
              <div className="flex items-center mb-4">
                <TrendingUp className="w-5 h-5 mr-2 text-purple-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">AI-Powered Analytics</h3>
              </div>
              <AIPredictions />
            </div>
          )}

          {activeTab === 'reports' && (
            <div>
              <div className="flex items-center mb-4">
                <BarChart3 className="w-5 h-5 mr-2 text-indigo-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Conflict Reports</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Comprehensive analysis and exportable reports. Report generation and export functionality will be available here.
              </p>
            </div>
          )}

          {activeTab === 'alerts' && (
            <div>
              <div className="flex items-center mb-4">
                <AlertTriangle className="w-5 h-5 mr-2 text-red-500" />
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Early Warning System</h3>
              </div>
              <p className="text-gray-600 dark:text-gray-300">
                Critical alerts and risk notifications. Real-time alerts and notifications will be displayed here.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
