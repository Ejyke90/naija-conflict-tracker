import React, { useState, useEffect, useCallback } from 'react';
import { Activity, CheckCircle, Clock, AlertTriangle, Database, Zap, RefreshCw, Wifi, WifiOff } from 'lucide-react';
import { useWebSocket } from '../../hooks/useWebSocket';

// TypeScript interfaces for API response
/** Scraping health metrics from the data collection pipeline */
interface ScrapingHealth {
  sources_processed: number;
  total_sources: number;
  articles_collected: number;
  events_extracted: number;
}

/** Data quality metrics for validation and geocoding */
interface DataQuality {
  geocoding_success_rate: number;
  validation_pass_rate: number;
}

/** Complete pipeline status response from API */
interface PipelineStatus {
  timestamp: string;
  scraping_health: ScrapingHealth;
  data_quality: DataQuality;
  anomalies: any[];
  alerts: any[];
  overall_status: string;
}

/** Individual pipeline execution step */
interface PipelineStep {
  name: string;
  status: 'completed' | 'running' | 'pending' | 'failed';
  duration: string;
  items: number;
  total: number;
  icon: React.ComponentType<any>;
}

/** System health indicators */
interface SystemHealth {
  redis: string;
  database: string;
  api: string;
  memory_usage: number;
}

const PipelineMonitor: React.FC = () => {
  // State management
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // WebSocket hook for real-time updates
  const { 
    status: wsStatus, 
    lastMessage, 
    isUsingFallback,
    connect,
    disconnect 
  } = useWebSocket({
    endpoint: '/ws/monitoring/pipeline-status',
    onMessage: (data: PipelineStatus) => {
      setStatus(data);
      setError(null);
      setLastUpdate(new Date());
      setLoading(false);
    },
    onStatusChange: (newStatus) => {
      if (newStatus === 'connected' || newStatus === 'polling-fallback') {
        setError(null);
      }
    },
    enableLogging: false, // Set to true for debugging
  });

  // Manual refresh function
  /**
   * Manually fetch pipeline data from HTTP endpoint
   * Used as fallback or for manual refresh
   */
  const refreshData = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/monitoring/pipeline-status');

      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.statusText}`);
      }

      const data = await response.json();
      setStatus(data);
      setError(null);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
      console.error('Refresh error:', err);
    }
  }, []);

  // Fetch data immediately on mount, then rely on polling
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  // Data mapping - generate pipeline steps from API data
  /**
   * Maps API response data to pipeline step display objects
   * Calculates derived metrics like geocoding success counts
   * @returns PipelineStep[] - Array of pipeline steps with computed values
   */
  const getPipelineSteps = (): PipelineStep[] => {
    if (!status) {
      return [];
    }

    const { scraping_health, data_quality } = status;

    return [
      {
        name: 'Data Collection',
        status: 'completed' as const,
        duration: '2m 15s', // This would come from API in a real implementation
        items: scraping_health.sources_processed,
        total: scraping_health.total_sources,
        icon: Database
      },
      {
        name: 'Content Processing',
        status: 'completed' as const,
        duration: '1m 42s',
        items: scraping_health.articles_collected,
        total: scraping_health.articles_collected,
        icon: Activity
      },
      {
        name: 'NLP Analysis',
        status: 'running' as const,
        duration: '45s',
        items: scraping_health.events_extracted,
        total: scraping_health.events_extracted,
        icon: Zap
      },
      {
        name: 'Geocoding',
        status: 'pending' as const,
        duration: '-',
        items: Math.round(scraping_health.events_extracted * data_quality.geocoding_success_rate / 100),
        total: scraping_health.events_extracted,
        icon: CheckCircle
      },
      {
        name: 'Validation',
        status: 'pending' as const,
        duration: '-',
        items: Math.round(scraping_health.events_extracted * data_quality.validation_pass_rate / 100),
        total: scraping_health.events_extracted,
        icon: CheckCircle
      }
    ];
  };

  const pipelineSteps = getPipelineSteps();

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'signal_low';
      case 'running': return 'signal_medium';
      case 'pending': return 'default';
      case 'failed': return 'signal_critical';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'running': return Clock;
      case 'pending': return Clock;
      case 'failed': return AlertTriangle;
      default: return Clock;
    }
  };

  // Loading skeleton component
  const LoadingSkeleton = () => (
    <div className="space-y-6 animate-pulse">
      {/* Pipeline Overview Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <div key={i} className="glass-card text-center p-4">
            <div className="flex items-center justify-center mb-2">
              <div className="w-6 h-6 bg-tactical-slate-medium rounded mr-2"></div>
              <div className="h-4 bg-tactical-slate-medium rounded w-16"></div>
            </div>
            <div className="h-8 bg-tactical-slate-medium rounded w-16 mx-auto mb-2"></div>
            <div className="h-3 bg-tactical-slate-medium rounded w-24 mx-auto"></div>
          </div>
        ))}
      </div>

      {/* Pipeline Steps Skeleton */}
      <div className="glass-card p-6">
        <div className="h-6 bg-tactical-slate-medium rounded w-48 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 border border-tactical-slate-light/30 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-tactical-slate-medium rounded-lg"></div>
                <div>
                  <div className="h-4 bg-tactical-slate-medium rounded w-32 mb-1"></div>
                  <div className="h-3 bg-tactical-slate-medium rounded w-24"></div>
                </div>
              </div>
              <div className="h-6 bg-tactical-slate-medium rounded w-20"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <div className="h-6 bg-tactical-slate-medium rounded w-40 mb-4"></div>
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i}>
                <div className="flex justify-between mb-1">
                  <div className="h-3 bg-tactical-slate-medium rounded w-32"></div>
                  <div className="h-3 bg-tactical-slate-medium rounded w-12"></div>
                </div>
                <div className="w-full bg-tactical-slate-dark rounded-full h-2">
                  <div className="bg-tactical-slate-medium h-2 rounded-full w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="h-6 bg-tactical-slate-medium rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-3 bg-tactical-slate-medium rounded w-24"></div>
                <div className="h-3 bg-tactical-slate-medium rounded w-16"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Show loading skeleton on initial load
  if (loading && !status) {
    return <LoadingSkeleton />;
  }

  // Show error state
  if (error && !status) {
    return (
      <div className="space-y-6">
        <div className="glass-card signal-critical border-red-500/30 p-6">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <div>
              <h3 className="typography-heading text-lg text-tactical-e-ink">Pipeline Status Unavailable</h3>
              <p className="typography-body text-red-300 mt-1">{error}</p>
              {lastUpdate && (
                <p className="typography-body text-sm text-red-400 mt-2">
                  Last successful update: {lastUpdate.toLocaleString()}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={refreshData}
            className="mt-4 px-4 py-2 signal-critical text-white rounded hover:opacity-80 flex items-center gap-2 typography-label"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* WebSocket Connection Status */}
      <div className={`glass-card border-l-4 p-4 ${
        wsStatus === 'connected' ? 'signal-low border-green-500' :
        wsStatus === 'polling-fallback' ? 'signal_medium border-amber-500' :
        wsStatus === 'reconnecting' ? 'border-blue-500' :
        'signal_critical border-red-500'
      }`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {wsStatus === 'connected' ? (
              <Wifi className="w-5 h-5 text-green-400 animate-pulse" />
            ) : (
              <WifiOff className="w-5 h-5 text-red-400" />
            )}
            <div>
              <p className={`typography-body font-medium capitalize ${
                wsStatus === 'connected' ? 'text-green-400' :
                wsStatus === 'polling-fallback' ? 'text-amber-400' :
                'text-red-400'
              }`}>
                {wsStatus === 'connected' ? 'Real-time Updates' : 
                 wsStatus === 'polling-fallback' ? 'Polling Mode (WebSocket unavailable)' :
                 wsStatus === 'reconnecting' ? 'Reconnecting...' : 'Disconnected'}
              </p>
              <p className="typography-body text-xs text-tactical-e-ink/50 mt-1">
                {wsStatus === 'connected' ? 'Receiving live updates via WebSocket' :
                 wsStatus === 'polling-fallback' ? 'Fetching updates every 5 seconds' :
                 'Attempting to establish connection'}
              </p>
            </div>
          </div>
          <button
            onClick={refreshData}
            className="px-3 py-1 text-sm bg-tactical-slate-medium border border-tactical-slate-light/30 rounded hover:bg-tactical-slate-light flex items-center gap-2 typography-label text-tactical-e-ink"
            title="Force refresh"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Error banner for background errors */}
      {error && status && (
        <div className="card border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-600" />
            <div>
              <p className="text-yellow-800 font-medium">Connection issue detected</p>
              <p className="text-yellow-600 text-sm mt-1">{error}</p>
              <p className="text-sm text-yellow-500 mt-1">
                Showing last successful data from {lastUpdate?.toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Pipeline Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Activity className="w-6 h-6 text-blue-400 mr-2" />
            <span className="typography-label text-sm text-tactical-e-ink">Status</span>
          </div>
          <div className="typography-heading text-2xl text-blue-400 capitalize">{status?.overall_status || 'unknown'}</div>
          <div className="typography-body text-xs text-tactical-e-ink/50 mt-1">
            Last run: {status ? new Date(status.timestamp).toLocaleString() : 'Never'}
          </div>
        </div>

        <div className="glass-card text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <Database className="w-6 h-6 text-green-400 mr-2" />
            <span className="typography-label text-sm text-tactical-e-ink">Sources</span>
          </div>
          <div className="typography-heading text-2xl text-green-400">
            {status?.scraping_health.sources_processed || 0}/{status?.scraping_health.total_sources || 0}
          </div>
          <div className="typography-body text-xs text-tactical-e-ink/50 mt-1">News sources processed</div>
        </div>

        <div className="glass-card text-center p-4">
          <div className="flex items-center justify-center mb-2">
            <CheckCircle className="w-6 h-6 text-purple-400 mr-2" />
            <span className="typography-label text-sm text-tactical-e-ink">Events</span>
          </div>
          <div className="typography-heading text-2xl text-purple-400">{status?.scraping_health.events_extracted || 0}</div>
          <div className="typography-body text-xs text-tactical-e-ink/50 mt-1">Verified conflict events</div>
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="glass-card p-6">
        <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">Pipeline Execution Steps</h3>
        <div className="space-y-4">
          {pipelineSteps.map((step, index) => {
            const IconComponent = step.icon;
            const StatusIcon = getStatusIcon(step.status);

            return (
              <div key={step.name} className="flex items-center justify-between p-4 border border-tactical-slate-light/30 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${
                    step.status === 'completed' ? 'signal-low' :
                    step.status === 'running' ? 'signal_medium' :
                    'bg-tactical-slate-medium'
                  }`}>
                    <IconComponent className={`w-5 h-5 ${
                      step.status === 'completed' ? 'text-green-400' :
                      step.status === 'running' ? 'text-amber-400' :
                      'text-tactical-e-ink/50'
                    }`} />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="typography-body font-medium text-tactical-e-ink">{step.name}</h4>
                      <StatusIcon className={`w-4 h-4 ${
                        step.status === 'completed' ? 'text-green-400' :
                        step.status === 'running' ? 'text-amber-400' :
                        step.status === 'failed' ? 'text-red-400' :
                        'text-tactical-e-ink/50'
                      }`} />
                    </div>
                    <div className="typography-body text-sm text-tactical-e-ink/70">
                      {step.items} / {step.total} items • {step.duration}
                    </div>
                  </div>
                </div>

                <div className={`px-3 py-1 text-xs rounded-full typography-label ${
                  step.status === 'completed' ? 'signal_low' :
                  step.status === 'running' ? 'signal_medium' :
                  'bg-tactical-slate-medium text-tactical-e-ink/70'
                }`}>
                  {step.status}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">Processing Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Geocoding Success Rate</span>
              <span className="typography-mono text-sm font-medium text-tactical-e-ink">{status?.data_quality.geocoding_success_rate.toFixed(1) || 0}%</span>
            </div>
            <div className="w-full bg-tactical-slate-dark rounded-full h-2">
              <div
                className="bg-blue-400 h-2 rounded-full"
                style={{ width: `${status?.data_quality.geocoding_success_rate || 0}%` }}
              ></div>
            </div>

            <div className="flex justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Validation Pass Rate</span>
              <span className="typography-mono text-sm font-medium text-tactical-e-ink">
                {status?.data_quality.validation_pass_rate.toFixed(1) || 0}%
              </span>
            </div>
            <div className="w-full bg-tactical-slate-dark rounded-full h-2">
              <div
                className="bg-green-400 h-2 rounded-full"
                style={{ width: `${status?.data_quality.validation_pass_rate || 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="typography-heading text-lg text-tactical-e-ink mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Connection Method</span>
              <span className={`typography-mono text-sm font-medium ${
                isUsingFallback ? 'text-amber-400' : 'text-green-400'
              }`}>
                {isUsingFallback ? 'Polling (5s)' : 'WebSocket'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Connection Status</span>
              <span className={`typography-mono text-sm font-medium capitalize ${
                wsStatus === 'connected' ? 'text-green-400' : 'text-amber-400'
              }`}>
                {wsStatus}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Data Freshness</span>
              <span className="typography-mono text-sm font-medium text-green-400">
                {lastUpdate ? `${Math.floor((Date.now() - lastUpdate.getTime()) / 1000)}s ago` : 'Never'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="typography-body text-sm text-tactical-e-ink/70">Pipeline Status</span>
              <span className={`typography-mono text-sm font-medium ${
                status?.overall_status === 'healthy' ? 'text-green-400' :
                status?.overall_status === 'alert' ? 'text-amber-400' : 'text-tactical-e-ink/50'
              }`}>
                {status?.overall_status || 'Unknown'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineMonitor;
