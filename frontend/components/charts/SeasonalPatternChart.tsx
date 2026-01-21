'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { AlertTriangle, Calendar, TrendingUp } from 'lucide-react';

interface SeasonalDataPoint {
  month: string;
  monthNumber: number;
  totalIncidents: number;
  totalFatalities: number;
  avgFatalitiesPerIncident: number;
  riskLevel: 'High' | 'Normal';
}

interface SeasonalAnalysisData {
  state: string;
  seasonalPattern: SeasonalDataPoint[];
  analysis: {
    highRiskMonths: string[];
    avgIncidentsPerMonth: number;
    peakMonth: string;
    lowestMonth: string;
  };
}

interface SeasonalPatternChartProps {
  state?: string;
}

export default function SeasonalPatternChart({ state }: SeasonalPatternChartProps) {
  const [data, setData] = useState<SeasonalAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [chartType, setChartType] = useState<'bar' | 'radar'>('bar');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = state ? `?state=${encodeURIComponent(state)}` : '';
        
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/timeseries/seasonal-analysis${params}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch seasonal data: ${response.statusText}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [state]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading seasonal patterns...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-red-50 rounded-lg">
        <div className="text-center text-red-600">
          <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
          <p>{error || 'No data available'}</p>
        </div>
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const dataPoint = payload[0].payload;

    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900 mb-2">
          {label}
          {dataPoint.riskLevel === 'High' && (
            <span className="ml-2 text-red-600 text-xs font-bold">⚠️ HIGH RISK</span>
          )}
        </p>
        <p className="text-sm">
          <span className="font-medium">Total Incidents:</span> {dataPoint.totalIncidents}
        </p>
        <p className="text-sm">
          <span className="font-medium">Total Fatalities:</span> {dataPoint.totalFatalities}
        </p>
        <p className="text-sm">
          <span className="font-medium">Avg Fatalities/Incident:</span>{' '}
          {dataPoint.avgFatalitiesPerIncident.toFixed(2)}
        </p>
      </div>
    );
  };

  // Color coding for bars based on risk level
  const getBarColor = (riskLevel: string) => {
    return riskLevel === 'High' ? '#ef4444' : '#3b82f6';
  };

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Calendar className="h-5 w-5 text-purple-600" />
              Seasonal Conflict Patterns - {data.state}
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Aggregated data across all years to identify high-risk months
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setChartType('bar')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartType === 'bar'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Bar Chart
            </button>
            <button
              onClick={() => setChartType('radar')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                chartType === 'radar'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Radar Chart
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-xs text-purple-600 font-medium mb-1">Avg Incidents/Month</p>
            <p className="text-2xl font-bold text-purple-900">
              {data.analysis.avgIncidentsPerMonth.toFixed(1)}
            </p>
          </div>

          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-xs text-red-600 font-medium mb-1">Peak Month</p>
            <p className="text-xl font-bold text-red-900">{data.analysis.peakMonth}</p>
          </div>

          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-xs text-green-600 font-medium mb-1">Safest Month</p>
            <p className="text-xl font-bold text-green-900">{data.analysis.lowestMonth}</p>
          </div>

          <div className="bg-orange-50 p-4 rounded-lg">
            <p className="text-xs text-orange-600 font-medium mb-1">High Risk Months</p>
            <p className="text-2xl font-bold text-orange-900">
              {data.analysis.highRiskMonths.length}
            </p>
          </div>
        </div>

        {/* High Risk Months Alert */}
        {data.analysis.highRiskMonths.length > 0 && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm font-medium text-red-900 mb-1">High Risk Periods Identified</p>
              <p className="text-sm text-red-700">
                {data.analysis.highRiskMonths.join(', ')} show significantly higher conflict activity
                ({'>'}20% above average)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        {chartType === 'bar' ? (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data.seasonalPattern} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              
              <Bar yAxisId="left" dataKey="totalIncidents" name="Total Incidents" radius={[8, 8, 0, 0]}>
                {data.seasonalPattern.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.riskLevel)} />
                ))}
              </Bar>
              
              <Bar
                yAxisId="right"
                dataKey="totalFatalities"
                name="Total Fatalities"
                fill="#f59e0b"
                opacity={0.6}
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={data.seasonalPattern} margin={{ top: 20, right: 80, bottom: 20, left: 80 }}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="month" tick={{ fontSize: 11 }} />
              <PolarRadiusAxis angle={90} domain={[0, 'auto']} tick={{ fontSize: 10 }} />
              <Radar
                name="Incidents"
                dataKey="totalIncidents"
                stroke="#8b5cf6"
                fill="#8b5cf6"
                fillOpacity={0.5}
              />
              <Radar
                name="Fatalities"
                dataKey="totalFatalities"
                stroke="#f59e0b"
                fill="#f59e0b"
                fillOpacity={0.3}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
            </RadarChart>
          </ResponsiveContainer>
        )}

        {/* Month Details Table */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-700">Month</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Incidents</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Fatalities</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Avg Severity</th>
                <th className="px-4 py-2 text-center font-medium text-gray-700">Risk Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {data.seasonalPattern.map((month) => (
                <tr
                  key={month.monthNumber}
                  className={`hover:bg-gray-50 ${
                    month.riskLevel === 'High' ? 'bg-red-50' : ''
                  }`}
                >
                  <td className="px-4 py-2 font-medium text-gray-900">{month.month}</td>
                  <td className="px-4 py-2 text-right text-gray-700">{month.totalIncidents}</td>
                  <td className="px-4 py-2 text-right text-gray-700">{month.totalFatalities}</td>
                  <td className="px-4 py-2 text-right text-gray-700">
                    {month.avgFatalitiesPerIncident.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-center">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        month.riskLevel === 'High'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-blue-100 text-blue-800'
                      }`}
                    >
                      {month.riskLevel === 'High' && <AlertTriangle className="h-3 w-3 mr-1" />}
                      {month.riskLevel}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
