import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

interface StateData {
  state: string;
  incidents: number;
  fatalities: number;
  injuries?: number;
  kidnapped?: number;
  affectedLGAs?: number;
  trend?: 'increasing' | 'decreasing' | 'stable';
  trendPercent?: number;
  riskLevel?: 'critical' | 'high' | 'medium' | 'low';
}

const MiniSparkline: React.FC<{ state: string }> = ({ state }) => {
  const [trendData, setTrendData] = useState<number[]>([]);
  
  useEffect(() => {
    const fetchTrend = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://naija-conflict-tracker-production.up.railway.app';
        const response = await fetch(
          `${apiUrl}/api/v1/timeseries/monthly-trends?state=${state}&months_back=3&include_forecast=false`
        );
        
        if (response.ok) {
          const data = await response.json();
          const incidents = data.monthly_data?.map((d: any) => d.incidents) || [];
          setTrendData(incidents.slice(-3));
        }
      } catch (err) {
        console.error(`Error fetching trend for ${state}:`, err);
      }
    };
    
    fetchTrend();
  }, [state]);
  
  if (trendData.length === 0) return <span className="text-gray-400">—</span>;
  
  return (
    <div className="inline-flex items-center">
      <svg width="60" height="20" className="inline-block">
        <polyline
          points={trendData.map((val, i) => `${i * 30},${20 - (val / Math.max(...trendData)) * 18}`).join(' ')}
          fill="none"
          stroke="#3b82f6"
          strokeWidth="2"
        />
      </svg>
    </div>
  );
};

const TrendIndicator: React.FC<{ trend: string; percent: number }> = ({ trend, percent }) => {
  const getIcon = () => {
    if (trend === 'increasing') return '↑';
    if (trend === 'decreasing') return '↓';
    return '→';
  };
  
  const getColor = () => {
    if (trend === 'increasing') return 'text-red-600';
    if (trend === 'decreasing') return 'text-green-600';
    return 'text-gray-500';
  };
  
  return (
    <span className={`flex items-center gap-1 ${getColor()} font-medium`}>
      <span className="text-lg">{getIcon()}</span>
      <span className="text-sm">{Math.abs(percent)}%</span>
    </span>
  );
};

const StateAnalysis: React.FC = () => {
  const [stateData, setStateData] = useState<StateData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState(6);
  const [sortBy, setSortBy] = useState<'incidents' | 'fatalities' | 'risk' | 'improvement'>('incidents');
  const [forecastData, setForecastData] = useState<Record<string, any>>({});

  const fetchStateData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://naija-conflict-tracker-production.up.railway.app';
      const response = await fetch(
        `${apiUrl}/api/v1/timeseries/state-summary?months_back=${timeRange}&limit=10`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch state data');
      }
      
      const data = await response.json();
      setStateData(data);
    } catch (err) {
      console.error('Error fetching state data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
      
      // Fallback to sample data on error
      setStateData([
        { state: 'Kaduna', incidents: 145, fatalities: 23, trend: 'increasing', trendPercent: 12, riskLevel: 'high' },
        { state: 'Borno', incidents: 98, fatalities: 67, trend: 'decreasing', trendPercent: -8, riskLevel: 'critical' },
        { state: 'Zamfara', incidents: 87, fatalities: 12, trend: 'stable', trendPercent: 2, riskLevel: 'high' }
      ]);
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  useEffect(() => {
    fetchStateData();
  }, [fetchStateData]);

  // Fetch forecasts for top 3 states
  useEffect(() => {
    const fetchForecasts = async () => {
      if (stateData.length === 0) return;
      
      const topStates = stateData.slice(0, 3);
      const forecasts: Record<string, any> = {};
      
      for (const state of topStates) {
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://naija-conflict-tracker-production.up.railway.app';
          const response = await fetch(
            `${apiUrl}/api/v1/timeseries/monthly-trends?state=${state.state}&months_back=12&include_forecast=true`
          );
          
          if (response.ok) {
            const data = await response.json();
            forecasts[state.state] = data.forecast;
          }
        } catch (err) {
          console.error(`Error fetching forecast for ${state.state}:`, err);
        }
      }
      
      setForecastData(forecasts);
    };
    
    fetchForecasts();
  }, [stateData]);

  // Sort data based on selected criteria
  const sortedData = React.useMemo(() => {
    return [...stateData].sort((a, b) => {
      switch (sortBy) {
        case 'incidents':
          return b.incidents - a.incidents;
        case 'fatalities':
          return b.fatalities - a.fatalities;
        case 'risk': {
          const riskOrder = { critical: 4, high: 3, medium: 2, low: 1 };
          const aRisk = riskOrder[a.riskLevel || 'low'];
          const bRisk = riskOrder[b.riskLevel || 'low'];
          return bRisk - aRisk;
        }
        case 'improvement':
          return (a.trendPercent || 0) - (b.trendPercent || 0);
        default:
          return 0;
      }
    });
  }, [stateData, sortBy]);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading state analysis...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Controls Row */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-600">
          Showing data from last {timeRange} months • {sortedData.length} states
        </div>
        <div className="flex gap-3">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="incidents">Sort by Incidents</option>
            <option value="fatalities">Sort by Fatalities</option>
            <option value="risk">Sort by Risk Level</option>
            <option value="improvement">Sort by Improvement</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(Number(e.target.value))}
            className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={3}>Last 3 months</option>
            <option value={6}>Last 6 months</option>
            <option value={12}>Last 12 months</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
          ⚠️ {error} - Showing cached data
        </div>
      )}

      {/* Forecast Preview Cards */}
      {Object.keys(forecastData).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {sortedData.slice(0, 3).map((state) => {
            const forecast = forecastData[state.state];
            if (!forecast) return null;
            
            return (
              <div key={state.state} className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{state.state}</h4>
                  <span className="text-xs text-blue-600 font-medium">30-Day Forecast</span>
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-bold text-blue-900">
                    {Math.round(forecast.predicted_incidents || 0)}
                  </span>
                  <span className="text-sm text-gray-600">incidents</span>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs">
                  <span className="text-blue-700">
                    Range: {Math.round(forecast.lower_bound || 0)}-{Math.round(forecast.upper_bound || 0)}
                  </span>
                  {forecast.confidence && (
                    <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded-full font-medium">
                      {forecast.confidence}% confidence
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top States by Incidents */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">States by Incident Count</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sortedData.slice(0, 10)} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="state" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="incidents" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top States by Fatalities */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">States by Fatalities</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sortedData.slice(0, 10)} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="state" type="category" width={80} />
              <Tooltip />
              <Bar dataKey="fatalities" fill="#dc2626" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* State Statistics Table */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">State Statistics Overview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-medium">State</th>
                <th className="text-right py-3 px-4 font-medium">Incidents</th>
                <th className="text-right py-3 px-4 font-medium">Fatalities</th>
                <th className="text-center py-3 px-4 font-medium">3-Mo Trend</th>
                <th className="text-center py-3 px-4 font-medium">Change</th>
                <th className="text-right py-3 px-4 font-medium">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((state) => (
                <tr key={state.state} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 font-medium">{state.state}</td>
                  <td className="text-right py-3 px-4">{state.incidents}</td>
                  <td className="text-right py-3 px-4 text-red-600 font-semibold">{state.fatalities}</td>
                  <td className="text-center py-3 px-4">
                    <MiniSparkline state={state.state} />
                  </td>
                  <td className="text-center py-3 px-4">
                    {state.trend && state.trendPercent !== undefined ? (
                      <TrendIndicator trend={state.trend} percent={state.trendPercent} />
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                  <td className="text-right py-3 px-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      state.riskLevel === 'critical' ? 'bg-red-100 text-red-800' :
                      state.riskLevel === 'high' ? 'bg-orange-100 text-orange-800' :
                      state.riskLevel === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {state.riskLevel ? state.riskLevel.charAt(0).toUpperCase() + state.riskLevel.slice(1) : 'Low'}
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
};

export default StateAnalysis;
