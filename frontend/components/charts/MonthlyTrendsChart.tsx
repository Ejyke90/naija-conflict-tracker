'use client';

import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot,
  Area,
  ComposedChart,
} from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, Calendar } from 'lucide-react';

interface MonthlyDataPoint {
  month: string;
  incidents: number;
  fatalities: number;
  civilianCasualties: number;
  geographicSpread: number;
  incidentsTrend: number;
  fatalitiesTrend: number;
  isAnomalousIncidents: boolean;
  isAnomalousFatalities: boolean;
}

interface ForecastDataPoint {
  month: string;
  predictedIncidents: number;
  predictedFatalities: number;
  confidence: string;
}

interface MonthlyTrendsData {
  timeRange: {
    start: string;
    end: string;
    totalMonths: number;
  };
  state: string;
  data: MonthlyDataPoint[];
  summary: {
    avgIncidentsPerMonth: number;
    avgFatalitiesPerMonth: number;
    totalIncidents: number;
    totalFatalities: number;
    peakMonth: string;
    peakIncidents: number;
    anomalyCount: number;
    trendDirection: 'increasing' | 'decreasing';
  };
  forecast?: {
    method: string;
    periods: number;
    data: ForecastDataPoint[];
    note: string;
  };
}

interface MonthlyTrendsChartProps {
  state?: string;
  monthsBack?: number;
  includeForecast?: boolean;
}

export default function MonthlyTrendsChart({
  state,
  monthsBack = 24,
  includeForecast = true,
}: MonthlyTrendsChartProps) {
  const [data, setData] = useState<MonthlyTrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'incidents' | 'fatalities'>('incidents');

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          months_back: monthsBack.toString(),
          include_forecast: includeForecast.toString(),
        });
        if (state) params.append('state', state);

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/timeseries/monthly-trends?${params}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch trends: ${response.statusText}`);
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
  }, [state, monthsBack, includeForecast]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading trend data...</p>
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

  // Combine historical and forecast data for charting
  const combinedData = [...data.data];
  
  if (data.forecast) {
    data.forecast.data.forEach((forecast) => {
      combinedData.push({
        month: forecast.month,
        incidents: 0, // Will show as gap
        fatalities: 0,
        civilianCasualties: 0,
        geographicSpread: 0,
        incidentsTrend: forecast.predictedIncidents,
        fatalitiesTrend: forecast.predictedFatalities,
        isAnomalousIncidents: false,
        isAnomalousFatalities: false,
      });
    });
  }

  // Find anomalies for highlighting
  const anomalies = data.data.filter((d) =>
    viewMode === 'incidents' ? d.isAnomalousIncidents : d.isAnomalousFatalities
  );

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    const dataPoint = payload[0].payload;
    const isForecast = !dataPoint.incidents && !dataPoint.fatalities;

    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {isForecast ? (
          <>
            <p className="text-sm text-blue-600 mb-1">📈 Forecast</p>
            <p className="text-sm">
              <span className="font-medium">Predicted {viewMode}:</span>{' '}
              {viewMode === 'incidents'
                ? dataPoint.incidentsTrend.toFixed(1)
                : dataPoint.fatalitiesTrend.toFixed(1)}
            </p>
          </>
        ) : (
          <>
            <p className="text-sm">
              <span className="font-medium">Incidents:</span> {dataPoint.incidents}
              {dataPoint.isAnomalousIncidents && (
                <span className="ml-2 text-red-600 font-bold">⚠️ SPIKE</span>
              )}
            </p>
            <p className="text-sm">
              <span className="font-medium">Fatalities:</span> {dataPoint.fatalities}
              {dataPoint.isAnomalousFatalities && (
                <span className="ml-2 text-red-600 font-bold">⚠️ SPIKE</span>
              )}
            </p>
            <p className="text-sm">
              <span className="font-medium">Civilian Deaths:</span> {dataPoint.civilianCasualties}
            </p>
            <p className="text-sm">
              <span className="font-medium">LGAs Affected:</span> {dataPoint.geographicSpread}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              <span className="font-medium">Trend (3mo avg):</span>{' '}
              {viewMode === 'incidents'
                ? dataPoint.incidentsTrend.toFixed(1)
                : dataPoint.fatalitiesTrend.toFixed(1)}
            </p>
          </>
        )}
      </div>
    );
  };

  return (
    <div className="w-full space-y-4">
      {/* Header with Summary Stats */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Monthly Conflict Trends - {data.state}
            </h3>
            <p className="text-sm text-gray-600">
              {data.timeRange.start} to {data.timeRange.end} ({data.timeRange.totalMonths} months)
            </p>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('incidents')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'incidents'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Incidents
            </button>
            <button
              onClick={() => setViewMode('fatalities')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'fatalities'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Fatalities
            </button>
          </div>
        </div>

        {/* Summary Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-xs text-blue-600 font-medium mb-1">Avg Incidents/Month</p>
            <p className="text-2xl font-bold text-blue-900">
              {data.summary.avgIncidentsPerMonth.toFixed(1)}
            </p>
          </div>
          
          <div className="bg-red-50 p-4 rounded-lg">
            <p className="text-xs text-red-600 font-medium mb-1">Avg Fatalities/Month</p>
            <p className="text-2xl font-bold text-red-900">
              {data.summary.avgFatalitiesPerMonth.toFixed(1)}
            </p>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg">
            <p className="text-xs text-orange-600 font-medium mb-1">Peak Month</p>
            <p className="text-lg font-bold text-orange-900">{data.summary.peakMonth}</p>
            <p className="text-xs text-orange-700">{data.summary.peakIncidents} incidents</p>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-xs text-purple-600 font-medium mb-1 flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              Trend Direction
            </p>
            <div className="flex items-center gap-2">
              {data.summary.trendDirection === 'increasing' ? (
                <TrendingUp className="h-6 w-6 text-red-600" />
              ) : (
                <TrendingDown className="h-6 w-6 text-green-600" />
              )}
              <p className="text-lg font-bold text-purple-900 capitalize">
                {data.summary.trendDirection}
              </p>
            </div>
          </div>
        </div>

        {data.summary.anomalyCount > 0 && (
          <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-lg p-3 flex items-start gap-2">
            <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-yellow-900">
                {data.summary.anomalyCount} Anomal{data.summary.anomalyCount === 1 ? 'y' : 'ies'}{' '}
                Detected
              </p>
              <p className="text-xs text-yellow-700">
                Unusual conflict spikes identified using statistical analysis
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={combinedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="incidentsGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="fatalitiesGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />

            {/* Area fill for actual data */}
            {viewMode === 'incidents' && (
              <Area
                type="monotone"
                dataKey="incidents"
                stroke="none"
                fill="url(#incidentsGradient)"
                name="Incidents"
              />
            )}
            {viewMode === 'fatalities' && (
              <Area
                type="monotone"
                dataKey="fatalities"
                stroke="none"
                fill="url(#fatalitiesGradient)"
                name="Fatalities"
              />
            )}

            {/* Actual data line */}
            <Line
              type="monotone"
              dataKey={viewMode === 'incidents' ? 'incidents' : 'fatalities'}
              stroke={viewMode === 'incidents' ? '#3b82f6' : '#ef4444'}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
              name={viewMode === 'incidents' ? 'Incidents' : 'Fatalities'}
            />

            {/* Trend line (moving average) */}
            <Line
              type="monotone"
              dataKey={viewMode === 'incidents' ? 'incidentsTrend' : 'fatalitiesTrend'}
              stroke={viewMode === 'incidents' ? '#1e40af' : '#991b1b'}
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={false}
              name="Trend (3mo avg)"
            />

            {/* Anomaly markers */}
            {anomalies.map((anomaly) => (
              <ReferenceDot
                key={anomaly.month}
                x={anomaly.month}
                y={viewMode === 'incidents' ? anomaly.incidents : anomaly.fatalities}
                r={8}
                fill="#ef4444"
                stroke="#fff"
                strokeWidth={2}
              />
            ))}
          </ComposedChart>
        </ResponsiveContainer>

        {data.forecast && (
          <div className="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-3">
            <p className="text-sm font-medium text-blue-900 mb-1">
              📈 {data.forecast.periods}-Month Forecast ({data.forecast.method})
            </p>
            <p className="text-xs text-blue-700">{data.forecast.note}</p>
            <div className="mt-2 grid grid-cols-3 gap-2">
              {data.forecast.data.map((f) => (
                <div key={f.month} className="bg-white p-2 rounded text-center">
                  <p className="text-xs font-medium text-gray-600">{f.month}</p>
                  <p className="text-sm font-bold text-blue-900">
                    {viewMode === 'incidents'
                      ? f.predictedIncidents.toFixed(1)
                      : f.predictedFatalities.toFixed(1)}
                  </p>
                  <p className="text-xs text-gray-500">{f.confidence}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
