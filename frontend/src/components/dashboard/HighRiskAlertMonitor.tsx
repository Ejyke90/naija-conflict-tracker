'use client';

import React, { useState, useEffect, useRef, useMemo } from 'react';
import { AlertTriangle, Bell, BellOff, Check, X, MapPin, Calendar } from 'lucide-react';

interface Alert {
  id: number;
  alert_type: string;
  priority: number;
  risk_score: number;
  status: string;
  title: string;
  summary: string;
  location: {
    state: string;
    lga?: string;
  };
  conflict_category: string;
  conflict_event_id: number;
  created_at: string;
  acknowledged_at?: string;
  resolved_at?: string;
}

interface HighRiskAlertMonitorProps {
  maxVisible?: number;
  showResolved?: boolean;
  enableSound?: boolean;
  refreshInterval?: number;  // milliseconds
}

export default function HighRiskAlertMonitor({
  maxVisible = 5,
  showResolved = false,
  enableSound = true,
  refreshInterval = 30000  // 30 seconds (was 5 seconds - too aggressive)
}: HighRiskAlertMonitorProps) {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastPollTime, setLastPollTime] = useState<string>(new Date().toISOString());
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(enableSound);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [toastAlert, setToastAlert] = useState<Alert | null>(null);
  const [consecutiveFailures, setConsecutiveFailures] = useState(0);
  const [adaptiveInterval, setAdaptiveInterval] = useState(refreshInterval);

  // Static demo data from database - Coming Live Soon
  const demoAlerts = useMemo<Alert[]>(() => [
    {
      id: 1,
      alert_type: 'CRITICAL',
      priority: 1,
      risk_score: 98,
      status: 'ACTIVE',
      title: 'Mass Casualty Event - Zamfara Banditry',
      summary: '205 fatalities in Maradun LGA from banditry attack',
      location: { state: 'Zamfara', lga: 'Maradun' },
      conflict_category: 'Banditry',
      conflict_event_id: 1,
      created_at: '2021-06-16T10:00:00Z'
    },
    {
      id: 2,
      alert_type: 'CRITICAL',
      priority: 1,
      risk_score: 96,
      status: 'ACTIVE',
      title: 'Farmer-Herder Conflict - Benue',
      summary: '204 fatalities and 105 injuries in Guma LGA from suspected herder attack',
      location: { state: 'Benue', lga: 'Guma' },
      conflict_category: 'Farmer - Herder Conflict',
      conflict_event_id: 2,
      created_at: '2025-06-13T14:30:00Z'
    },
    {
      id: 3,
      alert_type: 'CRITICAL',
      priority: 1,
      risk_score: 95,
      status: 'ACKNOWLEDGED',
      title: 'Terrorism Attack - Borno',
      summary: '200 fatalities in Guzamala LGA from ISWAP attack',
      location: { state: 'Borno', lga: 'Guzamala' },
      conflict_category: 'Terrorism',
      conflict_event_id: 3,
      created_at: '2023-03-05T08:15:00Z',
      acknowledged_at: '2023-03-05T12:00:00Z'
    },
    {
      id: 4,
      alert_type: 'HIGH',
      priority: 2,
      risk_score: 92,
      status: 'ACTIVE',
      title: 'Banditry Attack - Niger',
      summary: '200 bandits killed in military airstrike in Mariga LGA',
      location: { state: 'Niger', lga: 'Mariga' },
      conflict_category: 'Banditry',
      conflict_event_id: 4,
      created_at: '2022-03-04T16:45:00Z'
    },
    {
      id: 5,
      alert_type: 'HIGH',
      priority: 2,
      risk_score: 89,
      status: 'RESOLVED',
      title: 'Banditry Clash - Plateau',
      summary: '149 fatalities in Kanam LGA from bandits and vigilantes clash',
      location: { state: 'Plateau', lga: 'Kanam' },
      conflict_category: 'Banditry',
      conflict_event_id: 5,
      created_at: '2025-07-06T11:20:00Z',
      resolved_at: '2025-07-07T09:00:00Z'
    }
  ], []);

  // Initialize with demo data
  useEffect(() => {
    setAlerts(demoAlerts);
    setLoading(false);
  }, [demoAlerts]);

  // Initialize audio
  useEffect(() => {
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQ');
    }
  }, []);

  // Fetch alerts with exponential backoff
  const fetchAlerts = async () => {
    try {
      const response = await fetch(`/api/v1/alerts/poll?since=${lastPollTime}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch alerts: ${response.status}`);
      }

      const data = await response.json();
      
      // Reset failure count on success
      setConsecutiveFailures(0);
      
      // Reduce interval on success (back to normal)
      if (adaptiveInterval > refreshInterval) {
        setAdaptiveInterval(refreshInterval);
      }
      
      // Check for new alerts
      if (data.alerts && data.alerts.length > 0) {
        // Play sound for critical alerts
        if (soundEnabled) {
          const hasCritical = data.alerts.some((a: Alert) => a.alert_type === 'CRITICAL');
          if (hasCritical && audioRef.current) {
            audioRef.current.play().catch(() => {
              // Ignore audio play errors (autoplay policy)
            });
          }
        }

        // Show toast for first new alert
        setToastAlert(data.alerts[0]);
        setTimeout(() => setToastAlert(null), 5000);  // Hide after 5 seconds

        // Merge with existing alerts
        setAlerts((prev) => {
          const merged = [...data.alerts, ...prev];
          // Remove duplicates
          const unique = merged.filter((alert, index, self) =>
            index === self.findIndex((a) => a.id === alert.id)
          );
          // Sort by created_at descending
          return unique.sort((a, b) => 
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
          ).slice(0, 50);  // Keep max 50 alerts
        });
      }

      setLastPollTime(data.server_time);
      setError(null);
    } catch (err) {
      // Increment failure count
      setConsecutiveFailures(prev => prev + 1);
      
      // Exponential backoff: increase interval on failures
      const newInterval = Math.min(
        refreshInterval * Math.pow(2, consecutiveFailures),
        300000 // Max 5 minutes
      );
      setAdaptiveInterval(newInterval);
      
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Poll for alerts with adaptive interval
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, adaptiveInterval);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [adaptiveInterval, lastPollTime]);

  // Acknowledge alert
  const handleAcknowledge = async (alertId: number) => {
    try {
      const response = await fetch(`/api/v1/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ notes: 'Acknowledged from dashboard' })
      });

      if (!response.ok) {
        throw new Error('Failed to acknowledge alert');
      }

      // Update local state
      setAlerts((prev) => prev.map((alert) =>
        alert.id === alertId
          ? { ...alert, status: 'ACKNOWLEDGED', acknowledged_at: new Date().toISOString() }
          : alert
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to acknowledge alert');
    }
  };

  // Resolve alert
  const handleResolve = async (alertId: number) => {
    try {
      const response = await fetch(`/api/v1/alerts/${alertId}/resolve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ resolution_notes: 'Resolved from dashboard' })
      });

      if (!response.ok) {
        throw new Error('Failed to resolve alert');
      }

      // Update local state
      setAlerts((prev) => prev.map((alert) =>
        alert.id === alertId
          ? { ...alert, status: 'RESOLVED', resolved_at: new Date().toISOString() }
          : alert
      ));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to resolve alert');
    }
  };

  // Get priority color
  const getPriorityColor = (alertType: string): string => {
    switch (alertType) {
      case 'CRITICAL':
        return 'bg-red-50 border-red-200 text-red-800';
      case 'HIGH':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      default:
        return 'bg-yellow-50 border-yellow-200 text-yellow-800';
    }
  };

  // Get risk trend indicator
  const getRiskTrend = (riskScore: number) => {
    // Mock trend data - in real implementation this would come from historical data
    const trend = Math.random() > 0.5 ? 'up' : 'down';
    const change = Math.floor(Math.random() * 10) + 1;
    return { trend, change };
  };

  // Get risk gauge color
  const getRiskGaugeColor = (score: number) => {
    if (score >= 95) return 'bg-red-500';
    if (score >= 85) return 'bg-orange-500';
    return 'bg-yellow-500';
  };

  // Get status badge
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <span className="px-2 py-1 text-xs font-medium signal-critical rounded">Active</span>;
      case 'ACKNOWLEDGED':
        return <span className="px-2 py-1 text-xs font-medium bg-tactical-slate-dark text-tactical-slate-light rounded">Acknowledged</span>;
      case 'RESOLVED':
        return <span className="px-2 py-1 text-xs font-medium signal-low rounded">Resolved</span>;
      default:
        return null;
    }
  };

  // Filter alerts
  const visibleAlerts = showResolved 
    ? alerts.slice(0, maxVisible)
    : alerts.filter((a) => a.status !== 'RESOLVED').slice(0, maxVisible);

  if (loading && alerts.length === 0) {
    return (
      <div className="glass-card rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-tactical-e-ink typography-heading">High-Risk Alerts</h3>
        </div>
        <p className="text-tactical-slate-medium">Loading alerts...</p>
      </div>
    );
  }

  return (
    <>
      {/* Toast Notification */}
      {toastAlert && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in-right">
          <div className={`${getPriorityColor(toastAlert.alert_type)} border-l-4 rounded-lg shadow-lg p-4 max-w-md`}>
            <div className="flex items-start">
              <AlertTriangle className="w-5 h-5 mr-3 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm mb-1">New {toastAlert.alert_type} Alert</h4>
                <p className="text-sm">{toastAlert.title}</p>
                <p className="text-xs mt-1 opacity-75">
                  {toastAlert.location.state} • Risk Score: {toastAlert.risk_score}
                </p>
              </div>
              <button
                onClick={() => setToastAlert(null)}
                className="ml-2 text-gray-500 hover:text-gray-700"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Alert Panel */}
      <div className="glass-card rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-signal-critical mr-2" />
            <h3 className="text-lg font-semibold text-tactical-e-ink typography-heading">High-Risk Alerts</h3>
            <span className="ml-2 px-2 py-1 text-xs font-medium bg-tactical-slate-dark text-tactical-slate-light rounded-full">
              🚀 Coming Live Soon
            </span>
            {alerts.filter((a) => a.status === 'ACTIVE').length > 0 && (
              <span className="ml-2 px-2 py-1 text-xs font-bold signal-critical text-white rounded-full">
                {alerts.filter((a) => a.status === 'ACTIVE').length}
              </span>
            )}
          </div>
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="text-tactical-slate-medium hover:text-tactical-e-ink"
            title={soundEnabled ? 'Mute alerts' : 'Unmute alerts'}
          >
            {soundEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
          </button>
        </div>

        <div className="mb-4 p-3 bg-tactical-slate-dark text-tactical-slate-light rounded-lg text-sm border border-tactical-slate-medium">
          <strong>Live demo data</strong> • Real-time alert monitoring for conflict events exceeding risk thresholds. Currently showing sample data for demonstration purposes.
        </div>

        {error && (
          <div className="mb-4 p-3 signal-critical border rounded-lg text-sm">
            {error}
          </div>
        )}

        {visibleAlerts.length === 0 ? (
          <div className="text-center py-8 text-tactical-slate-medium">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p>No active high-risk alerts</p>
          </div>
        ) : (
          <div className="space-y-2">
            {visibleAlerts.map((alert) => {
              const riskTrend = getRiskTrend(alert.risk_score);
              return (
                <div
                  key={alert.id}
                  className={`group ${getPriorityColor(alert.alert_type)} border-l-2 rounded-lg p-3 transition-all hover:shadow-md hover:scale-[1.02]`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-black tracking-wider">{alert.alert_type}</span>
                        {getStatusBadge(alert.status)}
                        <div className="flex items-center gap-1">
                          <span className="text-xs font-mono font-bold">{alert.risk_score}</span>
                          <div className="flex items-center gap-0.5">
                            <div className={`w-8 h-1 ${getRiskGaugeColor(alert.risk_score)} rounded-full`}></div>
                            {riskTrend.trend === 'up' ? (
                              <span className="text-xs text-red-600">↑{riskTrend.change}</span>
                            ) : (
                              <span className="text-xs text-green-600">↓{riskTrend.change}</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <h4 className="font-semibold text-sm mb-1 truncate">{alert.title}</h4>
                      <p className="text-xs opacity-90 line-clamp-2 mb-2">{alert.summary}</p>
                      <div className="flex items-center gap-3 text-xs opacity-75">
                        <div className="flex items-center gap-1">
                          <MapPin className="w-3 h-3" />
                          <span className="font-mono">{alert.location.lga}, {alert.location.state}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          <span className="font-mono">{new Date(alert.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    
                    {/* Hover Actions */}
                    <div className="flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {alert.status === 'ACTIVE' && (
                        <button
                          onClick={() => handleAcknowledge(alert.id)}
                          className="px-2 py-1 text-xs bg-tactical-slate-dark text-tactical-e-ink rounded hover:bg-tactical-slate-medium transition-colors whitespace-nowrap"
                          title="Acknowledge alert"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                      )}
                      {alert.status === 'ACKNOWLEDGED' && (
                        <button
                          onClick={() => handleResolve(alert.id)}
                          className="px-2 py-1 text-xs signal-low text-white rounded hover:bg-opacity-80 transition-colors whitespace-nowrap"
                          title="Resolve alert"
                        >
                          <Check className="w-3 h-3" />
                        </button>
                      )}
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        className="px-2 py-1 text-xs bg-tactical-charcoal bg-opacity-70 rounded hover:bg-opacity-100 transition-colors"
                        title="View details"
                      >
                        <span className="text-xs">⋯</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {alerts.filter((a) => !showResolved ? a.status !== 'RESOLVED' : true).length > maxVisible && (
          <div className="mt-4 text-center">
            <a href="/alerts" className="text-sm text-blue-600 hover:underline">
              View all {alerts.filter((a) => !showResolved ? a.status !== 'RESOLVED' : true).length} alerts →
            </a>
          </div>
        )}
      </div>

      {/* Alert Detail Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 flex items-center justify-center glass-overlay" onClick={() => setSelectedAlert(null)}>
          <div className="glass-card rounded-lg shadow-xl max-w-2xl w-full m-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-tactical-e-ink typography-heading">Alert Details</h3>
                <button onClick={() => setSelectedAlert(null)} className="text-tactical-slate-medium hover:text-tactical-e-ink">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Alert Type:</span>
                  <span className={`ml-2 px-2 py-1 text-sm font-bold rounded ${selectedAlert.alert_type === 'CRITICAL' ? 'signal-critical text-white' : 'signal-high text-white'}`}>
                    {selectedAlert.alert_type}
                  </span>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Risk Score:</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-lg font-mono font-bold text-tactical-e-ink">{selectedAlert.risk_score}</span>
                    <div className={`w-12 h-2 ${getRiskGaugeColor(selectedAlert.risk_score)} rounded-full`}></div>
                  </div>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Title:</span>
                  <p className="mt-1 text-tactical-e-ink">{selectedAlert.title}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Summary:</span>
                  <p className="mt-1 text-tactical-slate-light">{selectedAlert.summary}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Location:</span>
                  <p className="mt-1 text-tactical-e-ink">{selectedAlert.location.lga}, {selectedAlert.location.state}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Conflict Category:</span>
                  <p className="mt-1 text-tactical-e-ink">{selectedAlert.conflict_category}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-tactical-slate-light">Created:</span>
                  <p className="mt-1 font-mono text-tactical-e-ink">{new Date(selectedAlert.created_at).toLocaleString()}</p>
                </div>
                
                {selectedAlert.acknowledged_at && (
                  <div>
                    <span className="text-sm font-medium text-tactical-slate-light">Acknowledged:</span>
                    <p className="mt-1 font-mono text-tactical-e-ink">{new Date(selectedAlert.acknowledged_at).toLocaleString()}</p>
                  </div>
                )}
                
                {selectedAlert.resolved_at && (
                  <div>
                    <span className="text-sm font-medium text-tactical-slate-light">Resolved:</span>
                    <p className="mt-1 font-mono text-tactical-e-ink">{new Date(selectedAlert.resolved_at).toLocaleString()}</p>
                  </div>
                )}
              </div>
              
              <div className="mt-6 flex items-center space-x-3">
                <a
                  href={`/conflicts/${selectedAlert.conflict_event_id}`}
                  className="px-4 py-2 bg-tactical-slate-dark text-tactical-e-ink rounded-lg hover:bg-tactical-slate-medium transition-colors"
                >
                  View Conflict Event
                </a>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-4 py-2 bg-tactical-charcoal text-tactical-slate-light rounded-lg hover:bg-tactical-slate-medium transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
