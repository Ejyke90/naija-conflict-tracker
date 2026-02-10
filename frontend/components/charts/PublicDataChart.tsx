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
import { AlertTriangle, TrendingUp, MapPin, Package } from 'lucide-react';

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

interface PublicDataChartProps {
  type: 'seasonal' | 'state-comparison';
  state?: string | null;
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

export default function PublicDataChart({ 
  type, 
  state = null, 
  states = ['Borno', 'Zamfara', 'Kaduna', 'Plateau', 'Niger'],
  monthsBack = 12 
}: PublicDataChartProps) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // TODO: Temporarily disabled to prevent 500 error loops
        // let url = '';
        // if (type === 'seasonal') {
        //   url = `/api/v1/timeseries/seasonal-analysis${state ? `?state=${state}` : ''}`;
        // } else {
        //   const params = new URLSearchParams({
        //     states: states.join(','),
        //     months_back: monthsBack.toString(),
        //   });
        //   url = `/api/v1/timeseries/trend-comparison?${params}`;
        // }

        // console.log(`PublicDataChart - Fetching from: ${url}`);
        // const response = await fetch(url);

        // if (!response.ok) {
        //   const errorText = await response.text();
        //   console.error(`API Error: ${response.status} - ${errorText}`);
        //   throw new Error(`Failed to fetch data: ${response.statusText}`);
        // }

        // const responseData = await response.json();
        // console.log(`PublicDataChart - Response:`, responseData);

        // setData(responseData);
        
        // Set loading to false by default
        setLoading(false);
      } catch (err) {
        console.error('PublicDataChart - Error:', err);
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [type, state, states, monthsBack]);

  if (loading) {
    return (
      <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading {type === 'seasonal' ? 'seasonal patterns' : 'state comparison'}...</p>
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
          <p className="text-sm mt-2">Try refreshing the page</p>
        </div>
      </div>
    );
  }

  // Return placeholder when API is disabled
  return (
    <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
      <div className="text-center text-gray-600">
        <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
        <p>{type === 'seasonal' ? 'Seasonal analysis' : 'State comparison'} temporarily disabled</p>
      </div>
    </div>
  );

  // Render seasonal pattern chart
  if (type === 'seasonal' && data.seasonalPattern) {
    return (
      <div className="w-full space-y-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <MapPin className="h-5 w-5 text-green-600" />
            Seasonal Conflict Patterns - {data.state || 'All States'}
          </h3>
          
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={data.seasonalPattern} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                content={({ active, payload, label }: any) => {
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
                }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="totalIncidents" fill="#3b82f6" name="Total Incidents" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  // Render state comparison chart
  if (type === 'state-comparison' && data.comparison) {
    const stateNames = Object.keys(data.comparison);
    
    // Handle case where only some states have data
    if (stateNames.length === 0) {
      return (
        <div className="w-full h-96 flex items-center justify-center bg-yellow-50 rounded-lg">
          <div className="text-center text-yellow-700">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4" />
            <p className="font-medium">No data available for selected states</p>
            <p className="text-sm mt-2">Try selecting different states or expanding the time range</p>
          </div>
        </div>
      );
    }
    
    const allMonths = data.comparison[stateNames[0]]?.months || [];

    // Combine all states data by month for trends chart
    const trendsData = allMonths.map((month: string, index: number) => {
      const point: any = { month };
      stateNames.forEach((stateName) => {
        const stateData = data.comparison[stateName];
        point[stateName] = stateData.incidents[index] || 0;
      });
      return point;
    });

    return (
      <div className="w-full space-y-4">
        <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <MapPin className="h-5 w-5 text-green-600" />
            Regional Conflict Analysis
          </h3>
          
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
              <Tooltip 
                content={({ active, payload, label }: any) => {
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
                }}
              />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />

              {stateNames.map((stateName, index) => (
                <Line
                  key={stateName}
                  type="monotone"
                  dataKey={stateName}
                  stroke={STATE_COLORS[index % STATE_COLORS.length]}
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                  name={stateName}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-96 flex items-center justify-center bg-gray-50 rounded-lg">
      <div className="text-center text-gray-600">
        <p>No data available</p>
      </div>
    </div>
  );
}
