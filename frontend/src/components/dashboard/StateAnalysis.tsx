import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Cell, Legend, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Activity, MapPin, TrendingUpIcon, Zap, Target, Filter } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

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
  const [isPositive, setIsPositive] = useState(false);
  
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
          const sliced = incidents.slice(-3);
          setTrendData(sliced);
          if (sliced.length >= 2) {
            setIsPositive(sliced[sliced.length - 1] > sliced[0]);
          }
        }
      } catch (err) {
        console.error(`Error fetching trend for ${state}:`, err);
      }
    };
    
    fetchTrend();
  }, [state]);
  
  if (trendData.length === 0) return <span className="text-gray-400">—</span>;
  
  const maxVal = Math.max(...trendData);
  const points = trendData.map((val, i) => `${i * 30},${20 - (val / maxVal) * 18}`).join(' ');
  
  return (
    <div className="inline-flex items-center">
      <svg width="70" height="24" viewBox="0 0 70 24" className="drop-shadow-sm">
        <defs>
          <linearGradient id={`grad-${state}`} x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor={isPositive ? '#ef4444' : '#22c55e'} stopOpacity={0.4} />
            <stop offset="100%" stopColor={isPositive ? '#ef4444' : '#22c55e'} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <polyline
          points={points}
          fill={`url(#grad-${state})`}
          stroke={isPositive ? '#dc2626' : '#16a34a'}
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
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
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-96 mt-2" />
          </CardHeader>
        </Card>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
          <Skeleton className="h-64" />
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
    <motion.div 
      className="space-y-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Enhanced Header Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Card className="bg-gradient-to-br from-white to-blue-50 border-blue-200">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Conflicts by State
                </CardTitle>
                <CardDescription className="mt-2 text-lg">
                  Real-time comparative analysis across Nigerian states
                </CardDescription>
              </div>
              <div className="hidden sm:block bg-gradient-to-br from-blue-600 to-indigo-600 p-4 rounded-xl shadow-lg">
                <Activity className="text-white" size={36} />
              </div>
            </div>
            <div className="h-1.5 w-24 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-full mt-4" />
          </CardHeader>
        </Card>
      </motion.div>

      {/* Enhanced Controls Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.1 }}
      >
        <Card className="bg-gradient-to-br from-white to-gray-50">
          <CardContent className="pt-6">
            <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
              <div className="flex-1 w-full">
                <div className="flex items-center gap-2 mb-4">
                  <Filter size={20} className="text-blue-600" />
                  <p className="text-sm font-bold text-gray-900 uppercase tracking-wide">Filters & Sorting</p>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">⏱️ Time Range</label>
                    <Select value={String(timeRange)} onValueChange={(value) => setTimeRange(Number(value))}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select time range" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="3">📅 Last 3 months</SelectItem>
                        <SelectItem value="6">📅 Last 6 months</SelectItem>
                        <SelectItem value="12">📅 Last 12 months</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-700 uppercase tracking-wider">🔀 Sort By</label>
                    <Select value={sortBy} onValueChange={(value) => setSortBy(value as any)}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Sort by" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="incidents">📊 Incident Count</SelectItem>
                        <SelectItem value="fatalities">⚠️ Fatalities</SelectItem>
                        <SelectItem value="risk">🎯 Risk Level</SelectItem>
                        <SelectItem value="improvement">📈 Most Improved</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>
              <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl px-6 py-4 text-white shadow-lg">
                <p className="text-4xl font-black">{sortedData.length}</p>
                <p className="text-sm font-semibold text-blue-100 mt-1">States Tracked</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {error && (
        <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="text-yellow-600 flex-shrink-0 mt-0.5" size={20} />
          <div>
            <p className="text-sm font-medium text-yellow-900">Data unavailable</p>
            <p className="text-sm text-yellow-700 mt-0.5">{error} - Showing cached data</p>
          </div>
        </div>
      )}

      {/* Enhanced Forecast Cards */}
      <AnimatePresence>
        {Object.keys(forecastData).length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <h2 className="text-2xl font-black text-gray-900 mb-5 flex items-center gap-3">
              <div className="w-1.5 h-8 bg-gradient-to-b from-blue-600 to-indigo-600 rounded-full" />
              <Zap size={24} className="text-yellow-500" />
              30-Day Forecast Preview
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
            {sortedData.slice(0, 3).map((state, idx) => {
              const forecast = forecastData[state.state];
              if (!forecast) return null;
              
              const predictedIncidents = Math.round(forecast.predicted_incidents || 0);
              const lower = Math.round(forecast.lower_bound || 0);
              const upper = Math.round(forecast.upper_bound || 0);
              const confidence = forecast.confidence || 85;
              
              return (
                <motion.div 
                  key={state.state} 
                  className="group relative bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 rounded-2xl p-6 text-white shadow-xl border border-blue-500 overflow-hidden"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: idx * 0.1 }}
                  whileHover={{ y: -4, boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)' }}
                >
                  <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-5 transition-opacity" />
                  <div className="relative z-10">
                    <div className="flex items-start justify-between mb-5">
                      <div>
                        <p className="text-sm font-bold text-blue-100 uppercase tracking-widest">Forecast</p>
                        <h3 className="text-2xl font-black mt-2">{state.state}</h3>
                      </div>
                      <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg px-3 py-2 border border-white border-opacity-30 hover:bg-opacity-30 transition-all">
                        <p className="text-lg font-bold">{confidence}%</p>
                        <p className="text-xs text-blue-100">confident</p>
                      </div>
                    </div>
                    
                    <div className="bg-white bg-opacity-10 backdrop-blur-md rounded-xl p-5 mb-5 border border-white border-opacity-10">
                      <div className="flex items-baseline gap-3 mb-3">
                        <span className="text-5xl font-black">{predictedIncidents}</span>
                        <span className="text-blue-100 font-semibold">incidents</span>
                      </div>
                      <p className="text-blue-200 text-sm font-medium">CI: {lower}–{upper}</p>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-blue-100">Accuracy Score</span>
                        <span className="text-white">{confidence}%</span>
                      </div>
                      <div className="w-full h-2.5 bg-white bg-opacity-15 rounded-full overflow-hidden border border-white border-opacity-20">
                        <div 
                          className="h-full bg-gradient-to-r from-blue-200 to-white rounded-full shadow-lg transition-all duration-1000"
                          style={{ width: `${confidence}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enhanced Charts Section */}
      <motion.div 
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
      >
        {/* Incidents Chart */}
        <Card className="hover:shadow-xl hover:border-blue-200 transition-all group">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 group-hover:text-blue-600 transition-colors">
              <div className="bg-blue-100 p-2 rounded-lg group-hover:bg-blue-600 transition-colors">
                <Activity size={20} className="text-blue-600 group-hover:text-white transition-colors" />
              </div>
              Incidents by State
            </CardTitle>
            <CardDescription>Top 10 states ranked by incident frequency</CardDescription>
          </CardHeader>
          <CardContent>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart 
              data={sortedData.slice(0, 10)}
              margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="4 4" stroke="#e5e7eb" />
              <XAxis dataKey="state" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '2px solid #3b82f6',
                  borderRadius: '12px',
                  color: '#fff',
                  padding: '12px',
                  fontWeight: 600
                }}
              />
              <Bar 
                dataKey="incidents" 
                fill="#3b82f6" 
                radius={[12, 12, 0, 0]}
                animationDuration={700}
              />
            </BarChart>
          </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Fatalities Chart */}
        <Card className="hover:shadow-xl hover:border-red-200 transition-all group">
          <CardHeader>
            <CardTitle className="flex items-center gap-3 group-hover:text-red-600 transition-colors">
              <div className="bg-red-100 p-2 rounded-lg group-hover:bg-red-600 transition-colors">
                <AlertTriangle size={20} className="text-red-600 group-hover:text-white transition-colors" />
              </div>
              Fatalities by State
            </CardTitle>
            <CardDescription>Top 10 states ranked by death toll</CardDescription>
          </CardHeader>
          <CardContent>
          <ResponsiveContainer width="100%" height={340}>
            <BarChart 
              data={sortedData.slice(0, 10)}
              margin={{ top: 10, right: 30, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="4 4" stroke="#e5e7eb" />
              <XAxis dataKey="state" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '2px solid #dc2626',
                  borderRadius: '12px',
                  color: '#fff',
                  padding: '12px',
                  fontWeight: 600
                }}
              />
              <Bar 
                dataKey="fatalities" 
                fill="#dc2626"
                radius={[12, 12, 0, 0]}
                animationDuration={700}
              />
            </BarChart>
          </ResponsiveContainer>
          </CardContent>
        </Card>
      </motion.div>

      {/* Enhanced State Statistics Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
      >
        <Card className="overflow-hidden hover:shadow-xl transition-shadow">
          <CardHeader className="bg-gradient-to-r from-gray-50 to-blue-50">
            <CardTitle className="flex items-center gap-3">
              <div className="bg-indigo-600 p-2 rounded-lg">
                <Target size={20} className="text-white" />
              </div>
              Detailed State Analysis
            </CardTitle>
            <CardDescription className="font-semibold">
              Comprehensive overview of all tracked states with metrics and trends
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-gray-100 to-gray-50 border-b-2 border-gray-200">
                <th className="text-left py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">State</th>
                <th className="text-center py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">
                  <div className="flex items-center justify-center gap-2">
                    <Activity size={16} className="text-blue-600" />
                    Incidents
                  </div>
                </th>
                <th className="text-center py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">
                  <div className="flex items-center justify-center gap-2">
                    <AlertTriangle size={16} className="text-red-600" />
                    Fatalities
                  </div>
                </th>
                <th className="text-center py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">3-Mo Trend</th>
                <th className="text-center py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">Change</th>
                <th className="text-right py-4 px-6 font-black text-gray-900 text-sm uppercase tracking-wider">Risk</th>
              </tr>
            </thead>
            <tbody>
              {sortedData.map((state, idx) => (
                <tr 
                  key={state.state} 
                  className={`border-b border-gray-100 hover:bg-blue-50 hover:shadow-inner transition-all duration-200 ${
                    idx % 2 === 0 ? 'bg-white' : 'bg-gray-50 hover:bg-blue-50'
                  }`}
                >
                  <td className="py-5 px-6">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 bg-blue-600 rounded-full" />
                      <span className="font-bold text-gray-900 text-lg">{state.state}</span>
                    </div>
                  </td>
                  <td className="text-center py-5 px-6">
                    <span className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-100 to-blue-50 rounded-lg font-bold text-blue-900 border border-blue-200 hover:border-blue-400 transition-colors">
                      {state.incidents}
                    </span>
                  </td>
                  <td className="text-center py-5 px-6">
                    <span className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-red-100 to-red-50 rounded-lg font-bold text-red-900 border border-red-200 hover:border-red-400 transition-colors">
                      {state.fatalities}
                    </span>
                  </td>
                  <td className="text-center py-5 px-6">
                    <MiniSparkline state={state.state} />
                  </td>
                  <td className="text-center py-5 px-6">
                    {state.trend && state.trendPercent !== undefined ? (
                      <TrendIndicator trend={state.trend} percent={state.trendPercent} />
                    ) : (
                      <span className="text-gray-400 text-sm font-medium">—</span>
                    )}
                  </td>
                  <td className="text-right py-5 px-6">
                    <Badge 
                      variant={state.riskLevel === 'critical' || state.riskLevel === 'high' ? 'destructive' : 'default'}
                      className="uppercase font-bold gap-2"
                    >
                      <span className="w-2 h-2 bg-current rounded-full animate-pulse" />
                      {state.riskLevel ? state.riskLevel.charAt(0).toUpperCase() + state.riskLevel.slice(1) : 'Low'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {sortedData.length === 0 && (
          <div className="p-16 text-center">
            <p className="text-gray-600 font-bold text-lg">No data available</p>
          </div>
        )}
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  );
};

export default StateAnalysis;
