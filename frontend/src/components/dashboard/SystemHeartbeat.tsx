'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Clock, Pause, Play, Zap } from 'lucide-react';

interface SystemStatus {
  enabled: boolean;
  running: boolean;
  next_run?: string;
  countdown_seconds?: number;
  last_run?: {
    timestamp: string;
    status: string;
    duration_seconds: number;
  };
  jobs?: Array<{
    id: string;
    name: string;
    next_run: string;
  }>;
}

interface SystemHeartbeatProps {
  compact?: boolean;
  showControls?: boolean;
  refreshInterval?: number;  // milliseconds
}

export default function SystemHeartbeat({
  compact = false,
  showControls = true,
  refreshInterval = 60000  // 60 seconds (was 10 seconds - too aggressive for background metric)
}: SystemHeartbeatProps) {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [countdown, setCountdown] = useState<number>(0);
  const [isTriggering, setIsTriggering] = useState(false);
  const [isToggling, setIsToggling] = useState(false);

  // Fetch system status
  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/v1/system/scheduler/status', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch system status');
      }

      const data = await response.json();
      setStatus(data);
      setCountdown(data.countdown_seconds || 0);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Trigger manual scraping
  const handleTrigger = async () => {
    setIsTriggering(true);
    try {
      const response = await fetch('/api/v1/system/scheduler/trigger', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ job_id: 'automated_scraping' })
      });

      if (!response.ok) {
        throw new Error('Failed to trigger job');
      }

      // Refresh status after trigger
      await fetchStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to trigger job');
    } finally {
      setIsTriggering(false);
    }
  };

  // Toggle scheduler (pause/resume)
  const handleToggle = async () => {
    if (!status) return;

    setIsToggling(true);
    const action = status.running ? 'pause' : 'resume';

    try {
      const response = await fetch('/api/v1/system/scheduler/control', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action })
      });

      if (!response.ok) {
        throw new Error(`Failed to ${action} scheduler`);
      }

      // Refresh status after toggle
      await fetchStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to ${action} scheduler`);
    } finally {
      setIsToggling(false);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  // Countdown timer
  useEffect(() => {
    if (countdown <= 0) return;

    const timer = setInterval(() => {
      setCountdown((prev) => Math.max(0, prev - 1));
    }, 1000);

    return () => clearInterval(timer);
  }, [countdown]);

  // Format countdown as MM:SS
  const formatCountdown = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Format last run time
  const formatLastRun = (timestamp: string): string => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    const hours = Math.floor(minutes / 60);
    return `${hours}h ${minutes % 60}m ago`;
  };

  if (loading) {
    return (
      <div className={compact ? 'text-sm text-gray-500' : 'p-4 bg-white rounded-lg shadow'}>
        Loading system status...
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className={compact ? 'text-sm text-red-500' : 'p-4 bg-red-50 rounded-lg'}>
        <AlertCircle className="inline w-4 h-4 mr-1" />
        System Status Unavailable
      </div>
    );
  }

  // Compact mode (for header)
  if (compact) {
    return (
      <div className="flex items-center space-x-3 text-sm">
        {status.running ? (
          <div className="flex items-center text-green-600">
            <CheckCircle className="w-4 h-4 mr-1" />
            <span className="font-medium">Active</span>
          </div>
        ) : (
          <div className="flex items-center text-yellow-600">
            <Pause className="w-4 h-4 mr-1" />
            <span className="font-medium">Paused</span>
          </div>
        )}

        {status.running && status.next_run && (
          <div className="flex items-center text-gray-600">
            <Clock className="w-4 h-4 mr-1" />
            <span>Next: {formatCountdown(countdown)}</span>
          </div>
        )}

        {status.last_run && (
          <div className="text-gray-500">
            Last: {formatLastRun(status.last_run.timestamp)}
          </div>
        )}
      </div>
    );
  }

  // Full mode (for dashboard)
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">System Heartbeat</h3>
        {status.running ? (
          <div className="flex items-center text-green-600">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse mr-2"></div>
            <CheckCircle className="w-5 h-5 mr-1" />
            <span className="font-medium">System Active</span>
          </div>
        ) : (
          <div className="flex items-center text-yellow-600">
            <Pause className="w-5 h-5 mr-1" />
            <span className="font-medium">System Paused</span>
          </div>
        )}
      </div>

      <div className="space-y-4">
        {/* Next Run Countdown */}
        {status.running && status.next_run && (
          <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center">
              <Clock className="w-5 h-5 text-blue-600 mr-2" />
              <span className="text-gray-700">Next Automation Run</span>
            </div>
            <div className="text-2xl font-mono font-bold text-blue-600">
              {formatCountdown(countdown)}
            </div>
          </div>
        )}

        {/* Last Run Status */}
        {status.last_run && (
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <Clock className="w-5 h-5 text-gray-600 mr-2" />
              <span className="text-gray-700">Last Run</span>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-800">
                {formatLastRun(status.last_run.timestamp)}
              </div>
              <div className="text-xs text-gray-500">
                {status.last_run.status === 'success' ? '✓ Success' : '✗ Failed'} 
                {' '}({status.last_run.duration_seconds.toFixed(1)}s)
              </div>
            </div>
          </div>
        )}

        {/* Active Jobs */}
        {status.jobs && status.jobs.length > 0 && (
          <div className="border-t pt-3">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Scheduled Jobs</h4>
            <div className="space-y-2">
              {status.jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{job.name}</span>
                  <span className="text-xs text-gray-500">
                    {new Date(job.next_run).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Control Buttons */}
        {showControls && (
          <div className="flex items-center space-x-3 pt-3 border-t">
            <button
              onClick={handleTrigger}
              disabled={isTriggering || !status.enabled}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Zap className="w-4 h-4 mr-2" />
              {isTriggering ? 'Triggering...' : 'Trigger Now'}
            </button>

            <button
              onClick={handleToggle}
              disabled={isToggling || !status.enabled}
              className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed transition-colors"
            >
              {status.running ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  {isToggling ? 'Pausing...' : 'Pause'}
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  {isToggling ? 'Resuming...' : 'Resume'}
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
