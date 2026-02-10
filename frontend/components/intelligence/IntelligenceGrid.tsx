'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp, Users, Shield, AlertTriangle, RefreshCw } from 'lucide-react';

// TypeScript interfaces for analytics data
interface AnalyticsStats {
  totalIncidents: number;
  totalIncidentsChange: number;
  fatalities: number;
  fatalitiesChange: number;
  activeHotspots: number;
  activeHotspotsChange: number;
  statesAffected: number;
  totalStates: number;
  statesAffectedChange: number;
  lastUpdated: string;
}

interface StateStats {
  state: string;
  incidents: number;
  fatalities: number;
}

interface IntelligenceCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  colorClass: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  loading?: boolean;
}

const IntelligenceCard: React.FC<IntelligenceCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  colorClass,
  trend,
  loading = false
}) => {
  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="animate-pulse">
          <div className="h-6 w-6 bg-gray-600 rounded mb-4"></div>
          <div className="h-8 w-24 bg-gray-600 rounded mb-2"></div>
          <div className="h-4 w-32 bg-gray-600 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-gray-800 rounded-lg p-6 border ${colorClass}`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-2 rounded-lg ${colorClass.replace('border', 'bg').replace('500', '500/20')}`}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center text-sm ${
            trend.isPositive ? 'text-emerald-400' : 'text-rose-400'
          }`}>
            <TrendingUp className={`h-4 w-4 mr-1 ${
              !trend.isPositive ? 'rotate-180' : ''
            }`} />
            {trend.value > 0 ? '+' : ''}{trend.value}%
          </div>
        )}
      </div>
      <div>
        <h3 className="text-2xl font-bold text-white mb-1">{value}</h3>
        <p className="text-gray-400 text-sm">{title}</p>
        {subtitle && (
          <p className="text-gray-500 text-xs mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  );
};

interface IntelligenceGridProps {
  className?: string;
}

const IntelligenceGrid: React.FC<IntelligenceGridProps> = ({ className = '' }) => {
  const [stats, setStats] = useState<AnalyticsStats | null>(null);
  const [stateStats, setStateStats] = useState<StateStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetch analytics data from API endpoints
   * Retrieves main stats and state-level data for intelligence metrics
   */
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch main stats
      const statsResponse = await fetch('/api/v1/analytics/stats');
      if (!statsResponse.ok) {
        throw new Error(`Failed to fetch stats: ${statsResponse.statusText}`);
      }
      const statsData = await statsResponse.json();

      // Fetch state statistics for leaderboard
      const stateResponse = await fetch('/api/v1/analytics/states?months_back=12');
      if (!stateResponse.ok) {
        throw new Error(`Failed to fetch state stats: ${stateResponse.statusText}`);
      }
      const stateData = await stateResponse.json();

      setStats(statsData);
      setStateStats(stateData.data || []);
    } catch (err) {
      console.error('Failed to fetch intelligence data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  /**
   * Calculate intelligence metrics from raw analytics data
   * @returns Object containing calculated metrics or null if data is unavailable
   */
  const calculateMetrics = () => {
    if (!stats || !stateStats.length) return null;

    // Kinetic Lethality Index: (Total Fatalities / Total Incidents)
    // Measures the average fatality rate per conflict incident
    const lethalityIndex = stats.totalIncidents > 0 
      ? (stats.fatalities / stats.totalIncidents).toFixed(1)
      : '0.0';

    // Displacement Velocity: Use active hotspots as proxy
    // Represents the rate of population displacement due to conflicts
    const displacementVelocity = stats.activeHotspots;

    // Verification Pulse: Use states affected as proxy
    // Indicates the percentage of verified conflict reports
    const verificationPulse = stats.statesAffected;

    // Regional Risk Leaderboard: Top 3 states by incidents
    // Ranks states by conflict incident volume for risk assessment
    const topStates = stateStats.slice(0, 3);

    return {
      lethalityIndex,
      displacementVelocity,
      verificationPulse,
      topStates
    };
  };

  const metrics = calculateMetrics();

  if (error) {
    return (
      <div className={`bg-gray-800 rounded-lg p-6 border border-rose-500 ${className}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center text-rose-400">
            <AlertTriangle className="h-5 w-5 mr-2" />
            <span>Failed to load intelligence data</span>
          </div>
          <button
            onClick={fetchData}
            className="flex items-center text-rose-400 hover:text-rose-300 transition-colors"
          >
            <RefreshCw className="h-4 w-4 mr-1" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (loading || !metrics) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 ${className}`}>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="bg-gray-800 rounded-lg p-6 border border-gray-700">
            <div className="animate-pulse">
              <div className="h-6 w-6 bg-gray-600 rounded mb-4"></div>
              <div className="h-8 w-24 bg-gray-600 rounded mb-2"></div>
              <div className="h-4 w-32 bg-gray-600 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Intelligence Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Kinetic Lethality Index */}
        <IntelligenceCard
          title="National Lethality"
          value={metrics.lethalityIndex}
          subtitle="Conflict intensity is rising in the Middle Belt"
          icon={<AlertTriangle className="h-5 w-5 text-rose-400" />}
          colorClass="border-rose-500"
          trend={{
            value: stats?.fatalitiesChange || 0,
            isPositive: (stats?.fatalitiesChange || 0) < 0
          }}
          loading={loading}
        />

        {/* Displacement Velocity */}
        <IntelligenceCard
          title="IDP Surge"
          value={`+${metrics.displacementVelocity}`}
          subtitle="Primary driver: Resource competition"
          icon={<Users className="h-5 w-5 text-amber-400" />}
          colorClass="border-amber-500"
          trend={{
            value: stats?.activeHotspotsChange || 0,
            isPositive: (stats?.activeHotspotsChange || 0) < 0
          }}
          loading={loading}
        />

        {/* Verification Pulse */}
        <IntelligenceCard
          title="Data Integrity"
          value={`${metrics.verificationPulse}%`}
          subtitle="of reports verified"
          icon={<Shield className="h-5 w-5 text-emerald-400" />}
          colorClass="border-emerald-500"
          loading={loading}
        />
      </div>

      {/* Regional Risk Leaderboard */}
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 text-rose-400 mr-2" />
          Regional Risk Leaderboard
        </h3>
        <div className="space-y-3">
          {metrics.topStates.map((state, index) => (
            <div
              key={state.state}
              className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg"
            >
              <div className="flex items-center">
                <span className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index === 0 ? 'bg-rose-500 text-white' :
                  index === 1 ? 'bg-amber-500 text-white' :
                  index === 2 ? 'bg-orange-500 text-white' :
                  'bg-gray-600 text-gray-300'
                }`}>
                  {index + 1}
                </span>
                <span className="ml-3 text-white font-medium">{state.state}</span>
              </div>
              <div className="text-right">
                <div className="text-white font-semibold">{state.incidents}</div>
                <div className="text-gray-400 text-sm">incidents</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default IntelligenceGrid;
