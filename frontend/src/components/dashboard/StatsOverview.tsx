import React, { useState, useEffect } from 'react';

interface DashboardStats {
  total_incidents: number;
  total_fatalities: number;
  active_hotspots: number;
  states_affected: number;
  period_days: number;
}

const StatsOverview: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL;
        if (!apiUrl) {
          throw new Error('API URL not configured');
        }

        const response = await fetch(`${apiUrl}/api/dashboard/stats?days=30`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setStats(data);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch stats');
        // Fallback to placeholder data
        setStats({
          total_incidents: 0,
          total_fatalities: 0,
          active_hotspots: 0,
          states_affected: 0,
          period_days: 30
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-grid">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="stat-card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-8 bg-gray-200 rounded w-1/2 mb-1"></div>
            <div className="h-3 bg-gray-200 rounded w-1/3"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="dashboard-grid">
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Total Incidents</h3>
        <p className="text-3xl font-bold text-primary-600">
          {stats?.total_incidents?.toLocaleString() || '0'}
        </p>
        <p className="text-sm text-gray-600">Last {stats?.period_days || 30} days</p>
        {error && <p className="text-xs text-red-500 mt-1">Using fallback data</p>}
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Fatalities</h3>
        <p className="text-3xl font-bold text-danger-600">
          {stats?.total_fatalities?.toLocaleString() || '0'}
        </p>
        <p className="text-sm text-gray-600">Last {stats?.period_days || 30} days</p>
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">Active Hotspots</h3>
        <p className="text-3xl font-bold text-warning-600">
          {stats?.active_hotspots || '0'}
        </p>
        <p className="text-sm text-gray-600">High risk areas</p>
      </div>
      
      <div className="stat-card">
        <h3 className="text-lg font-semibold text-gray-900">States Affected</h3>
        <p className="text-3xl font-bold text-gray-600">
          {stats?.states_affected || '0'}/36
        </p>
        <p className="text-sm text-gray-600">Out of 36 states</p>
      </div>
    </div>
  );
};

export default StatsOverview;
