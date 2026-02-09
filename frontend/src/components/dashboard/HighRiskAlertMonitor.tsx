'use client';

import React, { useState, useEffect, useRef } from 'react';
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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastPollTime, setLastPollTime] = useState<string>(new Date().toISOString());
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [soundEnabled, setSoundEnabled] = useState(enableSound);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [toastAlert, setToastAlert] = useState<Alert | null>(null);

  // Initialize audio
  useEffect(() => {
    if (typeof window !== 'undefined') {
      audioRef.current = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBjGH0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQQ0PUrbl7KxYGAg+lNjuxmwiCDGG0fPTgjMGHm7A7+OTQ');
    }
  }, []);

  // Fetch alerts
  const fetchAlerts = async () => {
    try {
      const response = await fetch(`/api/v1/alerts/poll?since=${lastPollTime}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch alerts');
      }

      const data = await response.json();
      
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
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Poll for alerts
  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, refreshInterval);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshInterval, lastPollTime]);

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
        return 'bg-red-100 border-red-500 text-red-800';
      case 'HIGH':
        return 'bg-orange-100 border-orange-500 text-orange-800';
      default:
        return 'bg-yellow-100 border-yellow-500 text-yellow-800';
    }
  };

  // Get status badge
  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return <span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded">Active</span>;
      case 'ACKNOWLEDGED':
        return <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded">Acknowledged</span>;
      case 'RESOLVED':
        return <span className="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 rounded">Resolved</span>;
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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-800">High-Risk Alerts</h3>
        </div>
        <p className="text-gray-500">Loading alerts...</p>
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
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-800">High-Risk Alerts</h3>
            {alerts.filter((a) => a.status === 'ACTIVE').length > 0 && (
              <span className="ml-2 px-2 py-1 text-xs font-bold bg-red-600 text-white rounded-full">
                {alerts.filter((a) => a.status === 'ACTIVE').length}
              </span>
            )}
          </div>
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className="text-gray-500 hover:text-gray-700"
            title={soundEnabled ? 'Mute alerts' : 'Unmute alerts'}
          >
            {soundEnabled ? <Bell className="w-5 h-5" /> : <BellOff className="w-5 h-5" />}
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
            {error}
          </div>
        )}

        {visibleAlerts.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <AlertTriangle className="w-12 h-12 mx-auto mb-2 opacity-20" />
            <p>No active high-risk alerts</p>
          </div>
        ) : (
          <div className="space-y-3">
            {visibleAlerts.map((alert) => (
              <div
                key={alert.id}
                className={`${getPriorityColor(alert.alert_type)} border-l-4 rounded-lg p-4 transition-all hover:shadow-md`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="font-bold text-sm">{alert.alert_type}</span>
                      {getStatusBadge(alert.status)}
                      <span className="text-xs px-2 py-1 bg-white bg-opacity-50 rounded">
                        Risk: {alert.risk_score}
                      </span>
                    </div>
                    <h4 className="font-semibold text-sm mb-1">{alert.title}</h4>
                    <p className="text-xs mb-2 opacity-90">{alert.summary}</p>
                    <div className="flex items-center space-x-4 text-xs opacity-75">
                      <div className="flex items-center">
                        <MapPin className="w-3 h-3 mr-1" />
                        {alert.location.lga}, {alert.location.state}
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {new Date(alert.created_at).toLocaleString()}
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col space-y-2 ml-4">
                    {alert.status === 'ACTIVE' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors whitespace-nowrap"
                      >
                        <Check className="w-3 h-3 inline mr-1" />
                        Acknowledge
                      </button>
                    )}
                    {alert.status === 'ACKNOWLEDGED' && (
                      <button
                        onClick={() => handleResolve(alert.id)}
                        className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors whitespace-nowrap"
                      >
                        <Check className="w-3 h-3 inline mr-1" />
                        Resolve
                      </button>
                    )}
                    <button
                      onClick={() => setSelectedAlert(alert)}
                      className="px-3 py-1 text-xs bg-white bg-opacity-70 rounded hover:bg-opacity-100 transition-colors"
                    >
                      Details
                    </button>
                  </div>
                </div>
              </div>
            ))}
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50" onClick={() => setSelectedAlert(null)}>
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full m-4 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-800">Alert Details</h3>
                <button onClick={() => setSelectedAlert(null)} className="text-gray-500 hover:text-gray-700">
                  <X className="w-6 h-6" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <span className="text-sm font-medium text-gray-600">Alert Type:</span>
                  <span className={`ml-2 px-2 py-1 text-sm font-bold rounded ${selectedAlert.alert_type === 'CRITICAL' ? 'bg-red-600 text-white' : 'bg-orange-600 text-white'}`}>
                    {selectedAlert.alert_type}
                  </span>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Risk Score:</span>
                  <span className="ml-2 text-lg font-bold">{selectedAlert.risk_score}</span>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Title:</span>
                  <p className="mt-1">{selectedAlert.title}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Summary:</span>
                  <p className="mt-1 text-gray-700">{selectedAlert.summary}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Location:</span>
                  <p className="mt-1">{selectedAlert.location.lga}, {selectedAlert.location.state}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Conflict Category:</span>
                  <p className="mt-1">{selectedAlert.conflict_category}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-600">Created:</span>
                  <p className="mt-1">{new Date(selectedAlert.created_at).toLocaleString()}</p>
                </div>
                
                {selectedAlert.acknowledged_at && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Acknowledged:</span>
                    <p className="mt-1">{new Date(selectedAlert.acknowledged_at).toLocaleString()}</p>
                  </div>
                )}
                
                {selectedAlert.resolved_at && (
                  <div>
                    <span className="text-sm font-medium text-gray-600">Resolved:</span>
                    <p className="mt-1">{new Date(selectedAlert.resolved_at).toLocaleString()}</p>
                  </div>
                )}
              </div>
              
              <div className="mt-6 flex items-center space-x-3">
                <a
                  href={`/conflicts/${selectedAlert.conflict_event_id}`}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Conflict Event
                </a>
                <button
                  onClick={() => setSelectedAlert(null)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
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
