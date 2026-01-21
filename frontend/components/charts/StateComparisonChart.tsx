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
  BarChart,
  Bar,
} from 'recharts';
import { AlertTriangle, TrendingUp, MapPin } from 'lucide-react';

interface StateData {
  months: string[];
  incidents: number[];
  fatalities: number[];
  total: number;
  avgPerMonth: number;
}

interface TrendComparisonData {
  comparison: Record<string, StateData>;
  timeRange: string;
  generatedAt: string;
}

interface StateComparisonChartProps {
  states?: string[];
  monthsBack?: number;
}

const STATE_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // purple
];

export default function StateComparisonChart({
  states = ['Borno', 'Zamfara', 'Kaduna'],
  monthsBack = 12,
}: StateComparisonChartProps) {
  const [data, setData] = useState<TrendComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'trends' | 'totals'>('trends');
  const [metric, setMetric] = useState<'incidents' | 'fatalities'>('incidents');
  const [selectedStates, setSelectedStates] = useState<string[]>(states);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          states: selectedStates.join(','),
          months_back: monthsBack.toString(),
        });

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/timeseries/trend-comparison?${params}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch comparison data: ${response.statusText}`);
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
  }, [selectedStates, monthsBack]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading state comparison...</p>
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

  // Transform data for charting
  const stateNames = Object.keys(data.comparison);
  const allMonths = data.comparison[stateNames[0]]?.months || [];

  // Combine all states data by month for trends chart
  const trendsData = allMonths.map((month, index) => {
    const point: any = { month };
    stateNames.forEach((state) => {
      const stateData = data.comparison[state];
      point[state] = metric === 'incidents' 
        ? stateData.incidents[index] 
        : stateData.fatalities[index];
    });
    return point;
  });

  // Total comparison data for bar chart
  const totalsData = stateNames.map((state) => ({
    state,
    total: data.comparison[state].total,
    avgPerMonth: data.comparison[state].avgPerMonth,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
        <p className="font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            <span className="font-medium">{entry.name}:</span> {entry.value}
          </p>
        ))}
      </div>
    );
  };

  return (
    <div className="w-full space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <MapPin className="h-5 w-5 text-green-600" />
              State Comparison
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              Comparing {stateNames.length} state{stateNames.length !== 1 ? 's' : ''} over {data.timeRange}
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('trends')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'trends'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Trends
            </button>
            <button
              onClick={() => setViewMode('totals')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                viewMode === 'totals'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Totals
            </button>
            
            <div className="ml-4 h-8 w-px bg-gray-300"></div>
            
            <button
              onClick={() => setMetric('incidents')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                metric === 'incidents'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Incidents
            </button>
            <button
              onClick={() => setMetric('fatalities')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                metric === 'fatalities'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Fatalities
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {stateNames.map((state, index) => {
            const stateData = data.comparison[state];
            const color = STATE_COLORS[index % STATE_COLORS.length];
            
            return (
              <div
                key={state}
                className="bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg border-2 transition-all hover:shadow-md"
                style={{ borderColor: color }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  ></div>
                  <p className="text-sm font-semibold text-gray-900">{state}</p>
                </div>
                <p className="text-2xl font-bold" style={{ color }}>
                  {stateData.total}
                </p>
                <p className="text-xs text-gray-600 mt-1">
                  Avg: {stateData.avgPerMonth.toFixed(1)}/month
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
        {viewMode === 'trends' ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={trendsData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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

              {stateNames.map((state, index) => (
                <Line
                  key={state}
                  type="monotone"
                  dataKey={state}
                  stroke={STATE_COLORS[index % STATE_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name={state}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={totalsData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="state" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              
              <Bar dataKey="total" name={`Total ${metric === 'incidents' ? 'Incidents' : 'Fatalities'}`} radius={[8, 8, 0, 0]}>
                {totalsData.map((entry, index) => (
                  <Bar
                    key={entry.state}
                    dataKey="total"
                    fill={STATE_COLORS[index % STATE_COLORS.length]}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}

        {/* Detailed Table */}
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-gray-700">State</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Total</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Avg/Month</th>
                <th className="px-4 py-2 text-right font-medium text-gray-700">Data Points</th>
                <th className="px-4 py-2 text-center font-medium text-gray-700">Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {stateNames.map((state, index) => {
                const stateData = data.comparison[state];
                const recentValues = metric === 'incidents' 
                  ? stateData.incidents.slice(-3)
                  : stateData.fatalities.slice(-3);
                const isIncreasing = recentValues[2] > recentValues[0];

                return (
                  <tr key={state} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-900 flex items-center gap-2">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: STATE_COLORS[index % STATE_COLORS.length] }}
                      ></div>
                      {state}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-700 font-semibold">
                      {stateData.total}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-700">
                      {stateData.avgPerMonth.toFixed(1)}
                    </td>
                    <td className="px-4 py-2 text-right text-gray-700">
                      {stateData.months.length} months
                    </td>
                    <td className="px-4 py-2 text-center">
                      <TrendingUp
                        className={`h-4 w-4 inline ${
                          isIncreasing ? 'text-red-600' : 'text-green-600 rotate-180'
                        }`}
                      />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
