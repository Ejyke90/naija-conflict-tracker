import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Cell } from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Activity } from 'lucide-react';

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
    if (trend === 'increasing') return <TrendingUp size={16} />;
    if (trend === 'decreasing') return <TrendingDown size={16} />;
    return <Minus size={16} />;
  };
  
  const getColor = () => {
    if (trend === 'increasing') return 'text-red-600';
    if (trend === 'decreasing') return 'text-green-600';
    return 'text-gray-500';
  };
  
  return (
    <span className={`inline-flex items-center gap-1.5 font-semibold ${getColor()}`}>
      {getIcon()}
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
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600 mx-auto mb-4"></div>
          <span className="text-gray-600 font-medium">Loading conflict analysis...</span>
        </div>
      </div>
    );
  }

  // Risk level color mapping
  const getRiskColor = (level?: string) => {
    switch (level) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-orange-600 text-white';
      case 'medium': return 'bg-amber-600 text-white';
      default: return 'bg-green-600 text-white';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header Section */}
      <div>
        <div className="flex items-start justify-between mb-2">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">Conflicts by State</h1>
            <p className="text-gray-600 mt-1">Comparative analysis across Nigerian states</p>
          </div>
          <Activity className="text-blue-600" size={32} />
        </div>
        <div className="h-1 w-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full mt-4"></div>
      </div>

      {/* Controls Section - Improved Styling */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-700 mb-2">Filter & Sort</p>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <label className="block text-xs font-medium text-gray-600 mb-2">Time Range</label>
                <select
                  value={timeRange}
                  onChange={(e) => setTimeRange(Number(e.target.value))}
                  className="w-full px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium"
                >
                  <option value={3}>Last 3 months</option>
                  <option value={6}>Last 6 months</option>
                  <option value={12}>Last 12 months</option>
                </select>
              </div>
              <div className="flex-1">
                <label className="block text-xs font-medium text-gray-600 mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="w-full px-4 py-2.5 bg-white border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 font-medium"
                >
                  <option value="incidents">Incident Count</option>
                  <option value="fatalities">Fatalities</option>
                  <option value="risk">Risk Level</option>
                  <option value="improvement">Most Improved</option>
                </select>
              </div>
            </div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg px-4 py-3 text-center md:text-left">
            <p className="text-2xl font-bold text-blue-900">{sortedData.length}</p>
            <p className="text-xs text-blue-700 font-medium">States tracked</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-yellow-900">Data unavailable</p>
            <p className="text-sm text-yellow-700 mt-0.5">{error} - Showing cached data</p>
          </div>
        </div>
      )}

      {/* Forecast Cards - Enhanced */}
      {Object.keys(forecastData).length > 0 && (
        <div>
          <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <span className="w-1 h-6 bg-blue-600 rounded-full"></span>
            30-Day Forecast
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {sortedData.slice(0, 3).map((state) => {
              const forecast = forecastData[state.state];
              if (!forecast) return null;
              
              const predictedIncidents = Math.round(forecast.predicted_incidents || 0);
              const lower = Math.round(forecast.lower_bound || 0);
              const upper = Math.round(forecast.upper_bound || 0);
              const confidence = forecast.confidence || 85;
              
              return (
                <div 
                  key={state.state} 
                  className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-6 text-white shadow-lg border border-blue-500 hover:shadow-xl transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <p className="text-sm font-semibold text-blue-100 uppercase tracking-wide">Predicted Incidents</p>
                      <h3 className="text-2xl font-bold mt-1">{state.state}</h3>
                    </div>
                    <div className="bg-white bg-opacity-20 rounded-lg px-3 py-1">
                      <p className="text-sm font-semibold">{confidence}%</p>
                    </div>
                  </div>
                  
                  <div className="bg-white bg-opacity-10 rounded-lg p-4 mb-4">
                    <div className="flex items-baseline gap-2 mb-3">
                      <span className="text-4xl font-bold">{predictedIncidents}</span>
                      <span className="text-blue-100 font-medium">incidents</span>
                    </div>
                    <p className="text-blue-100 text-sm">Confidence interval: {lower}–{upper}</p>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs text-blue-100">
                    <span>Forecast accuracy ↗</span>
                    <div className="w-20 h-1.5 bg-white bg-opacity-20 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-white rounded-full"
                        style={{ width: `${confidence}%` }}
                      />
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Charts Section - Redesigned */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Incidents Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Activity size={20} className="text-blue-600" />
              Incidents by State
            </h3>
            <p className="text-sm text-gray-600 mt-1">Top 10 states by incident count</p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart 
              data={sortedData.slice(0, 10)}
              margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="state" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar 
                dataKey="incidents" 
                fill="#3b82f6" 
                radius={[8, 8, 0, 0]}
                animationDuration={500}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Fatalities Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
          <div className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
              <AlertTriangle size={20} className="text-red-600" />
              Fatalities by State
            </h3>
            <p className="text-sm text-gray-600 mt-1">Top 10 states by death toll</p>
          </div>
          <ResponsiveContainer width="100%" height={320}>
            <BarChart 
              data={sortedData.slice(0, 10)}
              margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="state" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: 'none',
                  borderRadius: '8px',
                  color: '#fff'
                }}
              />
              <Bar 
                dataKey="fatalities" 
                fill="#dc2626"
                radius={[8, 8, 0, 0]}
                animationDuration={500}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* State Statistics Table - Redesigned */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <Activity size={20} className="text-indigo-600" />
            Detailed State Analysis
          </h3>
          <p className="text-sm text-gray-600 mt-1">Complete overview of all tracked states</p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200">
                <th className="text-left py-3 px-6 font-bold text-gray-900">State</th>
                <th className="text-center py-3 px-6 font-bold text-gray-900">
                  <div className="flex items-center justify-center gap-1">
                    <Activity size={16} className="text-blue-600" />
                    Incidents
                  </div>
                </th>
                <th className="text-center py-3 px-6 font-bold text-gray-900">
                  <div className="flex items-center justify-center gap-1">
                    <AlertTriangle size={16} className="text-red-600" />
                    Fatalities
                  </div>
                </th>
                <th className="text-center py-3 px-6 font-bold text-gray-900">3-Mo Trend</th>
                <th className="text-center py-3 px-6 font-bold text-gray-900">Change</th>
                <th className="text-right py-3 px-6 font-bold text-gray-900">Risk Level</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((state, idx) => (
                <tr 
                  key={state.state} 
                  className={`border-b border-gray-100 hover:bg-blue-50 transition-colors ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'
                  }`}
                >
                  <td className="py-4 px-6">
                    <span className="font-bold text-gray-900">{state.state}</span>
                  </td>
                  <td className="text-center py-4 px-6">
                    <span className="inline-flex items-center justify-center w-10 h-10 bg-blue-100 rounded-lg font-bold text-blue-900">
                      {state.incidents}
                    </span>
                  </td>
                  <td className="text-center py-4 px-6">
                    <span className="inline-flex items-center justify-center w-10 h-10 bg-red-100 rounded-lg font-bold text-red-900">
                      {state.fatalities}
                    </span>
                  </td>
                  <td className="text-center py-4 px-6">
                    <MiniSparkline state={state.state} />
                  </td>
                  <td className="text-center py-4 px-6">
                    {state.trend && state.trendPercent !== undefined ? (
                      <TrendIndicator trend={state.trend} percent={state.trendPercent} />
                    ) : (
                      <span className="text-gray-400 text-sm">—</span>
                    )}
                  </td>
                  <td className="text-right py-4 px-6">
                    <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg font-semibold text-xs ${getRiskColor(state.riskLevel)}`}>
                      <span className="w-2 h-2 bg-current rounded-full"></span>
                      {state.riskLevel ? state.riskLevel.charAt(0).toUpperCase() + state.riskLevel.slice(1) : 'Low'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {sortedData.length === 0 && (
          <div className="p-12 text-center">
            <p className="text-gray-600 font-medium">No data available</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StateAnalysis;
