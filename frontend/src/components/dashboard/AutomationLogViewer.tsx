'use client';

import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, Download, Filter, RefreshCw } from 'lucide-react';

interface AutomationLog {
  timestamp: string;
  job_id: string;
  status: string;
  duration_seconds: number;
  events_processed?: number;
  errors?: string[];
  metadata?: {
    sources_scraped?: number;
    events_created?: number;
    events_updated?: number;
  };
}

interface AutomationLogViewerProps {
  refreshInterval?: number;  // milliseconds, 0 = no auto-refresh
}

export default function AutomationLogViewer({
  refreshInterval = 30000  // 30 seconds
}: AutomationLogViewerProps) {
  const [logs, setLogs] = useState<AutomationLog[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<AutomationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('24h');
  const [currentPage, setCurrentPage] = useState(1);
  const logsPerPage = 10;

  // Fetch automation logs
  const fetchLogs = async () => {
    try {
      const params = new URLSearchParams();
      if (dateFilter !== 'all') {
        const hours = dateFilter === '24h' ? 24 : dateFilter === '7d' ? 168 : dateFilter === '30d' ? 720 : 0;
        if (hours > 0) {
          const since = new Date(Date.now() - hours * 3600000).toISOString();
          params.append('since', since);
        }
      }
      params.append('limit', '100');

      const response = await fetch(`/api/v1/system/automation/logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch automation logs');
      }

      const data = await response.json();
      setLogs(data.logs || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchLogs();
    if (refreshInterval > 0) {
      const interval = setInterval(fetchLogs, refreshInterval);
      return () => clearInterval(interval);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshInterval, dateFilter]);

  // Apply filters
  useEffect(() => {
    let filtered = logs;

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((log) => log.status === statusFilter);
    }

    setFilteredLogs(filtered);
    setCurrentPage(1);  // Reset to first page when filters change
  }, [logs, statusFilter]);

  // Pagination
  const totalPages = Math.ceil(filteredLogs.length / logsPerPage);
  const paginatedLogs = filteredLogs.slice(
    (currentPage - 1) * logsPerPage,
    currentPage * logsPerPage
  );

  // Download logs as CSV
  const downloadCSV = () => {
    const headers = ['Timestamp', 'Job ID', 'Status', 'Duration (s)', 'Events Processed', 'Errors'];
    const rows = filteredLogs.map((log) => [
      new Date(log.timestamp).toISOString(),
      log.job_id,
      log.status,
      log.duration_seconds.toFixed(2),
      log.events_processed || 0,
      log.errors?.join('; ') || ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.map((cell) => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `automation_logs_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Format duration
  const formatDuration = (seconds: number): string => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  // Calculate statistics
  const stats = {
    total: filteredLogs.length,
    success: filteredLogs.filter((l) => l.status === 'success').length,
    failed: filteredLogs.filter((l) => l.status === 'failed').length,
    avgDuration: filteredLogs.length > 0
      ? filteredLogs.reduce((sum, l) => sum + l.duration_seconds, 0) / filteredLogs.length
      : 0
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">Automation Log</h3>
        <p className="text-gray-500">Loading logs...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Automation Execution Log</h3>
        <div className="flex items-center space-x-3">
          <button
            onClick={fetchLogs}
            className="px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors flex items-center"
          >
            <RefreshCw className="w-4 h-4 mr-1" />
            Refresh
          </button>
          <button
            onClick={downloadCSV}
            disabled={filteredLogs.length === 0}
            className="px-3 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 transition-colors flex items-center"
          >
            <Download className="w-4 h-4 mr-1" />
            Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Total Runs</div>
          <div className="text-2xl font-bold text-gray-800">{stats.total}</div>
        </div>
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Successful</div>
          <div className="text-2xl font-bold text-green-600">{stats.success}</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Failed</div>
          <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
        </div>
        <div className="bg-blue-50 rounded-lg p-3">
          <div className="text-sm text-gray-600">Avg Duration</div>
          <div className="text-2xl font-bold text-blue-600">{formatDuration(stats.avgDuration)}</div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4 mb-4 pb-4 border-b">
        <div className="flex items-center">
          <Filter className="w-4 h-4 text-gray-500 mr-2" />
          <span className="text-sm text-gray-600 mr-2">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">All</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="flex items-center">
          <Clock className="w-4 h-4 text-gray-500 mr-2" />
          <span className="text-sm text-gray-600 mr-2">Period:</span>
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>

      {/* Log Table */}
      {filteredLogs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Clock className="w-12 h-12 mx-auto mb-2 opacity-20" />
          <p>No automation logs found</p>
        </div>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b bg-gray-50">
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Timestamp</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Job</th>
                  <th className="px-4 py-3 text-center font-medium text-gray-700">Status</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Duration</th>
                  <th className="px-4 py-3 text-right font-medium text-gray-700">Events</th>
                  <th className="px-4 py-3 text-left font-medium text-gray-700">Details</th>
                </tr>
              </thead>
              <tbody>
                {paginatedLogs.map((log, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 text-gray-700">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {log.job_id.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </td>
                    <td className="px-4 py-3 text-center">
                      {log.status === 'success' ? (
                        <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 rounded-full">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Success
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 bg-red-100 text-red-800 rounded-full">
                          <XCircle className="w-3 h-3 mr-1" />
                          Failed
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {formatDuration(log.duration_seconds)}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-700">
                      {log.events_processed || 0}
                    </td>
                    <td className="px-4 py-3 text-gray-700">
                      {log.metadata && (
                        <div className="text-xs">
                          <div>Scraped: {log.metadata.sources_scraped || 0}</div>
                          <div>Created: {log.metadata.events_created || 0}</div>
                          {log.metadata.events_updated !== undefined && (
                            <div>Updated: {log.metadata.events_updated}</div>
                          )}
                        </div>
                      )}
                      {log.errors && log.errors.length > 0 && (
                        <div className="text-xs text-red-600 mt-1">
                          {log.errors[0].substring(0, 50)}...
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <div className="text-sm text-gray-600">
                Showing {(currentPage - 1) * logsPerPage + 1} to {Math.min(currentPage * logsPerPage, filteredLogs.length)} of {filteredLogs.length} logs
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                <span className="text-sm text-gray-600">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
