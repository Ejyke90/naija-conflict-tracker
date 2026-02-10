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
        return 'bg-green-500';
      case 'unhealthy':
      case 'warning':
        return 'bg-yellow-500';
      case 'error':
      case 'critical':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  if (loading && !stats) {
    return (
      <div className="p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-32 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-6">
            <div className="text-red-800">
              <h3 className="font-semibold mb-2">Error Loading Performance Data</h3>
              <p className="text-sm mb-4">{error}</p>
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
          <h1 className="text-3xl font-bold text-gray-900">Performance Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Real-time monitoring of API performance and system health
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
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
                  <span className="text-sm font-medium">Status</span>
                  <Badge className={getStatusColor(stats.status)}>
                    {stats.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Endpoints</span>
                  <span className="text-sm">{stats.endpoints_monitored}</span>
                </div>
                <div className="text-xs text-gray-500 mt-2">
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
                  <span className="text-sm font-medium">Health</span>
                  <Badge className={getStatusColor(health.status)}>
                    {health.status}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Monitoring</span>
                  <Badge className={health.monitoring_active ? 'bg-green-500' : 'bg-red-500'}>
                    {health.monitoring_active ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Threshold</span>
                  <span className="text-sm">{health.slow_response_threshold}s</span>
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
                  <span className="text-sm font-medium">Threshold</span>
                  <span className="text-sm">{slowEndpoints.threshold}s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Count</span>
                  <Badge className={
                    slowEndpoints.slow_endpoints.length > 0 ? 'bg-yellow-500' : 'bg-green-500'
                  }>
                    {slowEndpoints.slow_endpoints.length}
                  </Badge>
                </div>
                <div className="text-xs text-gray-500 mt-2">
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
                <span className="font-medium">Collection Started:</span>
                <span>{stats ? formatTime(stats.collection_started) : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Data Retention:</span>
                <span>{health ? `${health.data_retention_hours} hours` : 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">Last Check:</span>
                <span>{health ? formatTime(health.last_check) : 'N/A'}</span>
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
                variant="outline"
                disabled={loading}
              >
                {loading ? 'Refreshing...' : 'Refresh Data'}
              </Button>
              <div className="text-xs text-gray-500 text-center">
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
