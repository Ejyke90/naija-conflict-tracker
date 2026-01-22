import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, FileText, FileSpreadsheet, Calendar, Filter } from 'lucide-react';

interface ReportData {
  summary: {
    total_incidents: number;
    total_fatalities: number;
    total_injuries: number;
    states_affected: number;
    active_hotspots: number;
    period: {
      start: string;
      end: string;
    };
  };
  regional_distribution: Array<{
    region: string;
    incidents: number;
    fatalities: number;
    risk_level: string;
  }>;
  temporal_trends: Array<{
    month: string;
    incidents: number;
    fatalities: number;
  }>;
  conflict_types: Array<{
    type: string;
    count: number;
    fatalities: number;
  }>;
  top_perpetrators: Array<{
    group: string;
    incidents: number;
  }>;
}

const RISK_COLORS = {
  Critical: '#dc2626',
  High: '#f97316',
  Medium: '#fbbf24',
  Low: '#22c55e',
};

const CHART_COLORS = [
  '#3b82f6',
  '#8b5cf6',
  '#ec4899',
  '#f59e0b',
  '#10b981',
  '#06b6d4',
  '#6366f1',
  '#f43f5e'
];

export const ConflictAnalysisReport: React.FC = () => {
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState({
    start: '',
    end: ''
  });

  useEffect(() => {
    fetchReportData();
  }, []);

  const fetchReportData = async (params?: { start_date?: string; end_date?: string }) => {
    setLoading(true);
    setError(null);
    
    try {
      const queryParams = new URLSearchParams();
      if (params?.start_date) queryParams.append('start_date', params.start_date);
      if (params?.end_date) queryParams.append('end_date', params.end_date);
      
      const response = await fetch(`/api/dashboard/report/analysis?${queryParams}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch report data');
      }
      
      const data = await response.json();
      setReportData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const exportToPDF = async () => {
    // TODO: Implement PDF export
    alert('PDF export will be implemented with backend PDF generation endpoint');
  };

  const exportToExcel = () => {
    if (!reportData) return;
    
    // Convert data to CSV format
    const csvData = [
      ['Nigeria Conflict Analysis Report'],
      [''],
      ['Summary Statistics'],
      ['Total Incidents', reportData.summary.total_incidents],
      ['Total Fatalities', reportData.summary.total_fatalities],
      ['Total Injuries', reportData.summary.total_injuries],
      ['States Affected', reportData.summary.states_affected],
      ['Active Hotspots', reportData.summary.active_hotspots],
      [''],
      ['Regional Distribution'],
      ['State', 'Incidents', 'Fatalities', 'Risk Level'],
      ...reportData.regional_distribution.map(r => [r.region, r.incidents, r.fatalities, r.risk_level]),
      [''],
      ['Conflict Types'],
      ['Type', 'Count', 'Fatalities'],
      ...reportData.conflict_types.map(c => [c.type, c.count, c.fatalities])
    ];
    
    const csv = csvData.map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conflict-report-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const applyFilters = () => {
    fetchReportData({
      start_date: dateRange.start,
      end_date: dateRange.end
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading report data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold">Error Loading Report</h3>
        <p className="text-red-600 mt-2">{error}</p>
        <Button onClick={() => fetchReportData()} className="mt-4">
          Retry
        </Button>
      </div>
    );
  }

  if (!reportData) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header with filters and export buttons */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Conflict Analysis Report</h2>
            <p className="text-gray-600 mt-1">
              Comprehensive analysis for {reportData.summary.period.start} to {reportData.summary.period.end}
            </p>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <Button 
              onClick={exportToPDF}
              variant="outline"
              className="flex items-center gap-2"
            >
              <FileText className="w-4 h-4" />
              Export PDF
            </Button>
            <Button 
              onClick={exportToExcel}
              variant="outline"
              className="flex items-center gap-2"
            >
              <FileSpreadsheet className="w-4 h-4" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Date Range Filters */}
        <div className="mt-4 flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Start Date
            </label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              className="border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              End Date
            </label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              className="border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <Button onClick={applyFilters} className="flex items-center gap-2">
            <Filter className="w-4 h-4" />
            Apply Filters
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Incidents</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {reportData.summary.total_incidents.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Fatalities</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {reportData.summary.total_fatalities.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Injuries</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600">
              {reportData.summary.total_injuries.toLocaleString()}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>States Affected</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600">
              {reportData.summary.states_affected}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Hotspots</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-yellow-600">
              {reportData.summary.active_hotspots}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Temporal Trends Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Temporal Trends</CardTitle>
          <CardDescription>Monthly incident and fatality trends over time</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={reportData.temporal_trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="incidents" 
                stackId="1"
                stroke="#3b82f6" 
                fill="#3b82f6" 
                fillOpacity={0.6}
                name="Incidents"
              />
              <Area 
                type="monotone" 
                dataKey="fatalities" 
                stackId="2"
                stroke="#ef4444" 
                fill="#ef4444" 
                fillOpacity={0.6}
                name="Fatalities"
              />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Regional Distribution and Conflict Types */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Regional Distribution Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Regional Distribution</CardTitle>
            <CardDescription>Top 10 states by incident count</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={reportData.regional_distribution.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="region" 
                  angle={-45} 
                  textAnchor="end" 
                  height={100}
                  interval={0}
                  fontSize={12}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="incidents" fill="#3b82f6" name="Incidents" />
                <Bar dataKey="fatalities" fill="#ef4444" name="Fatalities" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Conflict Types Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Conflict Types Distribution</CardTitle>
            <CardDescription>Breakdown by conflict archetype</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={reportData.conflict_types}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  outerRadius={120}
                  label={({type, count}) => `${type}: ${count}`}
                  labelLine={false}
                >
                  {reportData.conflict_types.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Risk Level Table */}
      <Card>
        <CardHeader>
          <CardTitle>State Risk Assessment</CardTitle>
          <CardDescription>Detailed regional breakdown with risk levels</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">State</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Incidents</th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-900">Fatalities</th>
                  <th className="px-4 py-3 text-center text-sm font-semibold text-gray-900">Risk Level</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {reportData.regional_distribution.map((region, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{region.region}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 text-right">{region.incidents}</td>
                    <td className="px-4 py-3 text-sm text-gray-700 text-right">{region.fatalities}</td>
                    <td className="px-4 py-3 text-center">
                      <span
                        className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold"
                        style={{
                          backgroundColor: RISK_COLORS[region.risk_level as keyof typeof RISK_COLORS] + '20',
                          color: RISK_COLORS[region.risk_level as keyof typeof RISK_COLORS]
                        }}
                      >
                        {region.risk_level}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Top Perpetrators */}
      <Card>
        <CardHeader>
          <CardTitle>Top Perpetrator Groups</CardTitle>
          <CardDescription>Most active armed groups and actors</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={reportData.top_perpetrators} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="group" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="incidents" fill="#8b5cf6" name="Incidents" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Methodology Footer */}
      <Card className="bg-gray-50">
        <CardHeader>
          <CardTitle className="text-lg">Methodology & Data Sources</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-gray-700 space-y-2">
          <p>
            <strong>Risk Level Classification:</strong> Critical (20+ incidents or 100+ fatalities), 
            High (10+ incidents or 50+ fatalities), Medium (5+ incidents or 20+ fatalities), 
            Low (below Medium thresholds)
          </p>
          <p>
            <strong>Data Sources:</strong> ACLED, Nigerian news media (Premium Times, Punch, Vanguard, Daily Trust), 
            official government reports, and community-based reporting networks
          </p>
          <p className="text-gray-500 italic">
            Report generated on {new Date().toLocaleDateString()} by Nextier Conflict Monitoring System
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
