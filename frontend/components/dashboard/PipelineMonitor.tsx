import React, { useState, useEffect, useCallback } from 'react';
import { Activity, CheckCircle, Clock, AlertTriangle, Database, Zap, RefreshCw } from 'lucide-react';

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

  // API integration function
  /**
   * Fetches pipeline status from the backend API
   * @returns Promise<PipelineStatus> - Complete pipeline status data
   * @throws Error when API request fails
   */
  const fetchPipelineStatus = async (): Promise<PipelineStatus> => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/v1/monitoring/pipeline-status`);

    if (!response.ok) {
      throw new Error(`Failed to fetch pipeline status: ${response.statusText}`);
    }

    return await response.json();
  };

  // Data fetching logic
  /**
   * Fetches pipeline data and updates component state
   * Handles loading states, errors, and success scenarios
   */
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const data = await fetchPipelineStatus();
      setStatus(data);
      setError(null);
      setLastUpdate(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('Failed to fetch pipeline status:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh implementation
  useEffect(() => {
    // Fetch data on component mount
    fetchData();

    // Set up 30-second polling interval
    const interval = setInterval(fetchData, 30000); // 30 seconds

    // Cleanup function to clear interval on unmount
    return () => clearInterval(interval);
  }, [fetchData]);

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
      case 'completed': return 'text-green-600';
      case 'running': return 'text-blue-600';
      case 'pending': return 'text-gray-400';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-400';
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
          <div key={i} className="card text-center">
            <div className="flex items-center justify-center mb-2">
              <div className="w-6 h-6 bg-gray-300 rounded mr-2"></div>
              <div className="h-4 bg-gray-300 rounded w-16"></div>
            </div>
            <div className="h-8 bg-gray-300 rounded w-16 mx-auto mb-2"></div>
            <div className="h-3 bg-gray-300 rounded w-24 mx-auto"></div>
          </div>
        ))}
      </div>

      {/* Pipeline Steps Skeleton */}
      <div className="card">
        <div className="h-6 bg-gray-300 rounded w-48 mb-4"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 bg-gray-300 rounded-lg"></div>
                <div>
                  <div className="h-4 bg-gray-300 rounded w-32 mb-1"></div>
                  <div className="h-3 bg-gray-300 rounded w-24"></div>
                </div>
              </div>
              <div className="h-6 bg-gray-300 rounded w-20"></div>
            </div>
          ))}
        </div>
      </div>

      {/* Performance Metrics Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="h-6 bg-gray-300 rounded w-40 mb-4"></div>
          <div className="space-y-3">
            {[1, 2].map((i) => (
              <div key={i}>
                <div className="flex justify-between mb-1">
                  <div className="h-3 bg-gray-300 rounded w-32"></div>
                  <div className="h-3 bg-gray-300 rounded w-12"></div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-300 h-2 rounded-full w-3/4"></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="h-6 bg-gray-300 rounded w-32 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="h-3 bg-gray-300 rounded w-24"></div>
                <div className="h-3 bg-gray-300 rounded w-16"></div>
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
        <div className="card border-red-200 bg-red-50">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <div>
              <h3 className="text-lg font-semibold text-red-800">Pipeline Status Unavailable</h3>
              <p className="text-red-600 mt-1">{error}</p>
              {lastUpdate && (
                <p className="text-sm text-red-500 mt-2">
                  Last successful update: {lastUpdate.toLocaleString()}
                </p>
              )}
            </div>
          </div>
          <button
            onClick={fetchData}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 flex items-center gap-2"
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
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <Activity className="w-6 h-6 text-blue-600 mr-2" />
            <span className="text-sm font-medium">Status</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 capitalize">{status?.overall_status || 'unknown'}</div>
          <div className="text-xs text-gray-500 mt-1">
            Last run: {status ? new Date(status.timestamp).toLocaleString() : 'Never'}
          </div>
        </div>

        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <Database className="w-6 h-6 text-green-600 mr-2" />
            <span className="text-sm font-medium">Sources</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {status?.scraping_health.sources_processed || 0}/{status?.scraping_health.total_sources || 0}
          </div>
          <div className="text-xs text-gray-500 mt-1">News sources processed</div>
        </div>

        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <CheckCircle className="w-6 h-6 text-purple-600 mr-2" />
            <span className="text-sm font-medium">Events</span>
          </div>
          <div className="text-2xl font-bold text-purple-600">{status?.scraping_health.events_extracted || 0}</div>
          <div className="text-xs text-gray-500 mt-1">Verified conflict events</div>
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Pipeline Execution Steps</h3>
        <div className="space-y-4">
          {pipelineSteps.map((step, index) => {
            const IconComponent = step.icon;
            const StatusIcon = getStatusIcon(step.status);

            return (
              <div key={step.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${
                    step.status === 'completed' ? 'bg-green-100' :
                    step.status === 'running' ? 'bg-blue-100' :
                    'bg-gray-100'
                  }`}>
                    <IconComponent className={`w-5 h-5 ${
                      step.status === 'completed' ? 'text-green-600' :
                      step.status === 'running' ? 'text-blue-600' :
                      'text-gray-400'
                    }`} />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{step.name}</h4>
                      <StatusIcon className={`w-4 h-4 ${getStatusColor(step.status)}`} />
                    </div>
                    <div className="text-sm text-gray-600">
                      {step.items} / {step.total} items • {step.duration}
                    </div>
                  </div>
                </div>

                <div className={`px-3 py-1 text-xs rounded-full ${
                  step.status === 'completed' ? 'bg-green-100 text-green-800' :
                  step.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-600'
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
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Processing Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Geocoding Success Rate</span>
              <span className="text-sm font-medium">{status?.data_quality.geocoding_success_rate.toFixed(1) || 0}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${status?.data_quality.geocoding_success_rate || 0}%` }}
              ></div>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Validation Pass Rate</span>
              <span className="text-sm font-medium">
                {status?.data_quality.validation_pass_rate.toFixed(1) || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${status?.data_quality.validation_pass_rate || 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Connection</span>
              <span className={`text-sm font-medium ${error ? 'text-red-600' : 'text-green-600'}`}>
                {error ? 'Failed' : 'Connected'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Data Freshness</span>
              <span className="text-sm font-medium text-green-600">
                {lastUpdate ? `${Math.floor((Date.now() - lastUpdate.getTime()) / 1000)}s ago` : 'Never'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Auto-refresh</span>
              <span className="text-sm font-medium text-green-600">Active (30s)</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Pipeline Status</span>
              <span className={`text-sm font-medium ${
                status?.overall_status === 'healthy' ? 'text-green-600' :
                status?.overall_status === 'alert' ? 'text-yellow-600' : 'text-gray-600'
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
