import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database, 
  Globe, 
  RefreshCw,
  TrendingUp,
  Users,
  Zap,
  BarChart3
} from 'lucide-react';

interface PipelineStatus {
  timestamp: string;
  scraping_health: {
    overall_status: string;
    total_sources: number;
    failed_sources: number;
    avg_success_rate: number;
    sources: Array<{
      source: string;
      status: string;
      success_rate: number;
      last_run: string;
    }>;
  };
  data_quality: {
    status: string;
    quality_score: number;
    total_events: number;
    verification_rate: number;
    geocoding_rate: number;
  };
  anomalies: Array<{
    type: string;
    severity: string;
    description: string;
    timestamp: string;
  }>;
  alerts: Array<{
    type: string;
    severity: string;
    title: string;
    message: string;
    timestamp: string;
  }>;
}

interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  redis_status: string;
  worker_count: number;
  status: string;
}

const PipelineMonitor: React.FC = () => {
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchPipelineStatus = async () => {
    try {
      const response = await fetch('/api/v1/monitoring/pipeline-status');
      const data = await response.json();
      setPipelineStatus(data);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch pipeline status:', error);
    }
  };

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch('/api/v1/monitoring/system-metrics');
      const data = await response.json();
      setSystemMetrics(data);
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    }
  };

  const refreshData = async () => {
    setIsRefreshing(true);
    await Promise.all([
      fetchPipelineStatus(),
      fetchSystemMetrics()
    ]);
    setIsRefreshing(false);
  };

  const triggerManualScrape = async () => {
    try {
      const response = await fetch('/api/v1/scraping/trigger-manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sources: ['all'] })
      });
      
      if (response.ok) {
        await refreshData();
      }
    } catch (error) {
      console.error('Failed to trigger manual scrape:', error);
    }
  };

  useEffect(() => {
    refreshData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(refreshData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'excellent':
        return 'bg-green-500';
      case 'warning':
      case 'good':
      case 'fair':
        return 'bg-yellow-500';
      case 'unhealthy':
      case 'poor':
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
      case 'excellent':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning':
      case 'good':
      case 'fair':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'unhealthy':
      case 'poor':
      case 'error':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Pipeline Monitor</h2>
          <p className="text-gray-600">
            Real-time monitoring of data collection and processing
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            onClick={triggerManualScrape}
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Trigger Scrape</span>
          </Button>
          <Button
            variant="outline"
            onClick={refreshData}
            disabled={isRefreshing}
            className="flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Scraping Status</p>
                <p className="text-2xl font-bold">
                  {pipelineStatus?.scraping_health.overall_status || 'Unknown'}
                </p>
              </div>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(pipelineStatus?.scraping_health.overall_status || '')}`} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Data Quality</p>
                <p className="text-2xl font-bold">
                  {pipelineStatus?.data_quality.quality_score.toFixed(1) || '0'}%
                </p>
              </div>
              <BarChart3 className="w-6 h-6 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Workers</p>
                <p className="text-2xl font-bold">
                  {systemMetrics?.worker_count || '0'}
                </p>
              </div>
              <Users className="w-6 h-6 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Last Update</p>
                <p className="text-sm font-mono">
                  {lastUpdate.toLocaleTimeString()}
                </p>
              </div>
              <Clock className="w-6 h-6 text-gray-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="scraping" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="scraping">Scraping</TabsTrigger>
          <TabsTrigger value="quality">Data Quality</TabsTrigger>
          <TabsTrigger value="system">System</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
        </TabsList>

        {/* Scraping Tab */}
        <TabsContent value="scraping" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Globe className="w-5 h-5 mr-2" />
                News Source Status
              </CardTitle>
              <CardDescription>
                Real-time status of all news sources being scraped
              </CardDescription>
            </CardHeader>
            <CardContent>
              {pipelineStatus?.scraping_health.sources ? (
                <div className="space-y-3">
                  {pipelineStatus.scraping_health.sources.map((source, index) => (
                    <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center space-x-3">
                        {getStatusIcon(source.status)}
                        <div>
                          <p className="font-medium">{source.source}</p>
                          <p className="text-sm text-gray-600">
                            Last run: {new Date(source.last_run).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="font-medium">{(source.success_rate * 100).toFixed(1)}%</p>
                        <Progress value={source.success_rate * 100} className="w-20" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No scraping data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Data Quality Tab */}
        <TabsContent value="quality" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle>Quality Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Overall Quality Score</span>
                    <span>{pipelineStatus?.data_quality.quality_score.toFixed(1)}%</span>
                  </div>
                  <Progress value={pipelineStatus?.data_quality.quality_score || 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Verification Rate</span>
                    <span>{((pipelineStatus?.data_quality.verification_rate || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={(pipelineStatus?.data_quality.verification_rate || 0) * 100} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Geocoding Rate</span>
                    <span>{((pipelineStatus?.data_quality.geocoding_rate || 0) * 100).toFixed(1)}%</span>
                  </div>
                  <Progress value={(pipelineStatus?.data_quality.geocoding_rate || 0) * 100} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Events</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total Events (24h)</span>
                    <span className="font-bold">{pipelineStatus?.data_quality.total_events || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Verified Events</span>
                    <span className="font-bold text-green-600">
                      {Math.round((pipelineStatus?.data_quality.total_events || 0) * (pipelineStatus?.data_quality.verification_rate || 0))}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Geocoded Events</span>
                    <span className="font-bold text-blue-600">
                      {Math.round((pipelineStatus?.data_quality.total_events || 0) * (pipelineStatus?.data_quality.geocoding_rate || 0))}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Resource Usage
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span>CPU Usage</span>
                    <span>{systemMetrics?.cpu_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemMetrics?.cpu_percent || 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Memory Usage</span>
                    <span>{systemMetrics?.memory_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemMetrics?.memory_percent || 0} />
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span>Disk Usage</span>
                    <span>{systemMetrics?.disk_percent.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemMetrics?.disk_percent || 0} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Database className="w-5 h-5 mr-2" />
                  Services Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Redis</span>
                  <Badge variant={systemMetrics?.redis_status === 'healthy' ? 'default' : 'destructive'}>
                    {systemMetrics?.redis_status || 'Unknown'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Celery Workers</span>
                  <Badge variant="default">
                    {systemMetrics?.worker_count || 0} active
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span>Overall System</span>
                  <Badge variant={systemMetrics?.status === 'healthy' ? 'default' : 'destructive'}>
                    {systemMetrics?.status || 'Unknown'}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Active Alerts & Anomalies
              </CardTitle>
            </CardHeader>
            <CardContent>
              {(pipelineStatus?.alerts.length || 0) > 0 || (pipelineStatus?.anomalies.length || 0) > 0 ? (
                <div className="space-y-3">
                  {pipelineStatus?.alerts.map((alert, index) => (
                    <div key={index} className="p-4 border rounded-lg border-red-200 bg-red-50">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-red-800">{alert.title}</p>
                          <p className="text-sm text-red-600">{alert.message}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(alert.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <Badge variant="destructive">{alert.severity}</Badge>
                      </div>
                    </div>
                  ))}
                  {pipelineStatus?.anomalies.map((anomaly, index) => (
                    <div key={index} className="p-4 border rounded-lg border-yellow-200 bg-yellow-50">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-medium text-yellow-800">{anomaly.type}</p>
                          <p className="text-sm text-yellow-600">{anomaly.description}</p>
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(anomaly.timestamp).toLocaleString()}
                          </p>
                        </div>
                        <Badge variant="secondary">{anomaly.severity}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
                  <p>No active alerts or anomalies</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PipelineMonitor;
