import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface PerformanceStats {
  status: string;
  message: string;
  endpoints_monitored: number;
  collection_started: string;
}

interface PerformanceHealth {
  status: string;
  monitoring_active: boolean;
  slow_response_threshold: number;
  data_retention_hours: number;
  last_check: string;
}

interface SlowEndpoint {
  threshold: number;
  slow_endpoints: any[];
  message: string;
  checked_at: string;
}

const PerformanceDashboard: React.FC = () => {
  const [stats, setStats] = useState<PerformanceStats | null>(null);
  const [health, setHealth] = useState<PerformanceHealth | null>(null);
  const [slowEndpoints, setSlowEndpoints] = useState<SlowEndpoint | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch performance stats
      const statsResponse = await fetch('/api/v1/performance/stats');
      if (!statsResponse.ok) throw new Error('Failed to fetch performance stats');
      const statsData = await statsResponse.json();
      setStats(statsData);
      
      // Fetch performance health
      const healthResponse = await fetch('/api/v1/performance/health');
      if (!healthResponse.ok) throw new Error('Failed to fetch performance health');
      const healthData = await healthResponse.json();
      setHealth(healthData);
      
      // Fetch slow endpoints
      const slowResponse = await fetch('/api/v1/performance/slow-endpoints?threshold=0.5');
      if (!slowResponse.ok) throw new Error('Failed to fetch slow endpoints');
      const slowData = await slowResponse.json();
      setSlowEndpoints(slowData);
      
      setLastRefresh(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPerformanceData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchPerformanceData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'active':
        return 'signal_low';
      case 'unhealthy':
      case 'warning':
        return 'signal_medium';
      case 'error':
      case 'critical':
        return 'signal_critical';
      default:
        return 'default';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading && !stats) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-tactical-slate-dark rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="h-32 bg-tactical-slate-dark rounded"></div>
            <div className="h-32 bg-tactical-slate-dark rounded"></div>
            <div className="h-32 bg-tactical-slate-dark rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="signal-critical border-red-500/30">
          <CardContent className="p-6">
            <div className="text-tactical-e-ink">
              <h3 className="typography-heading mb-2">Error Loading Performance Data</h3>
              <p className="typography-body text-sm mb-4">{error}</p>
              <Button onClick={fetchPerformanceData} variant="outline" size="sm">
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="typography-heading text-3xl text-tactical-e-ink">Performance Dashboard</h1>
          <p className="typography-body text-tactical-e-ink/70 mt-1">
            Real-time monitoring of API performance and system health
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="typography-body text-sm text-tactical-e-ink/50">
            Last updated: {formatTime(lastRefresh.toISOString())}
          </div>
          <Button onClick={fetchPerformanceData} variant="outline" size="sm">
            Refresh
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Performance Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Performance Status</CardTitle>
          </CardHeader>
          <CardContent>
            {stats && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Status</span>
                  <Badge variant={getStatusColor(stats.status)}>
                    {stats.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Endpoints</span>
                  <span className="typography-mono text-sm text-tactical-e-ink/80">{stats.endpoints_monitored}</span>
                </div>
                <div className="typography-body text-xs text-tactical-e-ink/50 mt-2">
                  {stats.message}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Health Status */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">System Health</CardTitle>
          </CardHeader>
          <CardContent>
            {health && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Health</span>
                  <Badge variant={getStatusColor(health.status)}>
                    {health.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Monitoring</span>
                  <Badge variant={health.monitoring_active ? 'signal_low' : 'signal_critical'}>
                    {health.monitoring_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Threshold</span>
                  <span className="typography-mono text-sm text-tactical-e-ink/80">{health.slow_response_threshold}s</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Slow Endpoints */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Slow Endpoints</CardTitle>
          </CardHeader>
          <CardContent>
            {slowEndpoints && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Threshold</span>
                  <span className="typography-mono text-sm text-tactical-e-ink/80">{slowEndpoints.threshold}s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="typography-body text-sm font-medium text-tactical-e-ink">Count</span>
                  <Badge variant={
                    slowEndpoints.slow_endpoints.length > 0 ? 'signal_medium' : 'signal_low'
                  }>
                    {slowEndpoints.slow_endpoints.length}
                  </Badge>
                </div>
                <div className="typography-body text-xs text-tactical-e-ink/50 mt-2">
                  {slowEndpoints.message}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Additional Information */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Monitoring Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="typography-body font-medium text-tactical-e-ink">Collection Started:</span>
                <span className="typography-mono text-tactical-e-ink/80">{stats ? formatTime(stats.collection_started) : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="typography-body font-medium text-tactical-e-ink">Data Retention:</span>
                <span className="typography-mono text-tactical-e-ink/80">{health ? `${health.data_retention_hours} hours` : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="typography-body font-medium text-tactical-e-ink">Last Check:</span>
                <span className="typography-mono text-tactical-e-ink/80">{health ? formatTime(health.last_check) : 'N/A'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button 
                onClick={fetchPerformanceData} 
                className="w-full" 
                variant="tactical_primary"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </Button>
              <div className="typography-body text-xs text-tactical-e-ink/50 text-center">
                Data refreshes automatically every 30 seconds
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default PerformanceDashboard;
