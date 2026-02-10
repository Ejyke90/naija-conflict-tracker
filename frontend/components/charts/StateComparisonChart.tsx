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
import { AlertTriangle, TrendingUp, MapPin, Package, ChevronDown, ChevronUp } from 'lucide-react';
import { ApiResponse, formatCachedTime } from '@/types/api';

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
  maxStates?: number;
  allowUserSelection?: boolean;
  defaultToSmartSelection?: boolean;
}

const STATE_COLORS = [
  '#3b82f6', // blue
  '#ef4444', // red
  '#10b981', // green
  '#f59e0b', // amber
  '#8b5cf6', // purple
];

export default function StateComparisonChart({
  states = ['Borno', 'Zamfara', 'Kaduna', 'Plateau', 'Niger'],
  monthsBack = 12,
  maxStates = 5,
  allowUserSelection = true,
  defaultToSmartSelection = true,
}: StateComparisonChartProps) {
  const [data, setData] = useState<TrendComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'trends' | 'totals'>('trends');
  const [metric, setMetric] = useState<'incidents' | 'fatalities'>('incidents');
  const [selectedStates, setSelectedStates] = useState<string[]>(states.slice(0, maxStates));
  const [selectedMonths, setSelectedMonths] = useState<number>(monthsBack);
  const [showControls, setShowControls] = useState(false);
  const [initialStatesLoaded, setInitialStatesLoaded] = useState(false);
  const [isCached, setIsCached] = useState(false);
  const [cachedAt, setCachedAt] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'ok' | 'degraded' | 'error'>('ok');

  // Available Nigerian states for selection
  const availableStates = [
    'Abia', 'Adamawa', 'Akwa Ibom', 'Anambra', 'Bauchi', 'Bayelsa', 'Benue', 'Borno',
    'Cross River', 'Delta', 'Ebonyi', 'Edo', 'Ekiti', 'Enugu', 'Gombe', 'Imo',
    'Jigawa', 'Kaduna', 'Kano', 'Katsina', 'Kebbi', 'Kogi', 'Kwara', 'Lagos',
    'Nasarawa', 'Niger', 'Ogun', 'Ondo', 'Osun', 'Oyo', 'Plateau', 'Rivers',
    'Sokoto', 'Taraba', 'Yobe', 'Zamfara', 'FCT'
  ];

  // Available time periods
  const timePeriods = [
    { label: '6 months', value: 6 },
    { label: '12 months', value: 12 },
    { label: '18 months', value: 18 },
    { label: '24 months', value: 24 },
  ];

  // Fetch smart default states (3 hot, 1 medium, 1 safe)
  useEffect(() => {
    const loadSmartDefaults = async () => {
      try {
        // Check cache first (24 hour TTL)
        const cacheKey = 'smart_default_states_v2';
        const cached = localStorage.getItem(cacheKey);
        if (cached) {
          const { states: cachedStates, timestamp } = JSON.parse(cached);
          const age = Date.now() - timestamp;
          if (age < 24 * 60 * 60 * 1000) { // 24 hours
            setSelectedStates(cachedStates);
            setInitialStatesLoaded(true);
            return;
          }
        }

        // Fetch state statistics from API
        const response = await fetch(`/api/v1/analytics/states?months_back=${monthsBack}`);
        
        if (!response.ok) {
          // Fallback to provided states if API fails
          setSelectedStates(defaultToSmartSelection ? states.slice(0, maxStates) : states);
          setInitialStatesLoaded(true);
          return;
        }

        const apiResponse = await response.json();
        const stateStats = apiResponse.data || []; // Extract data from response
        
        console.log('StateComparisonChart - API Response:', apiResponse);
        console.log('StateComparisonChart - StateStats:', stateStats);
        
        // Sort by fatalities to identify hot, medium, and safe states
        const sorted = [...stateStats].sort((a, b) => b.fatalities - a.fatalities);
        
        if (sorted.length >= 5) {
          // Top 3 hot states (highest fatalities)
          const hotStates = sorted.slice(0, 3).map(s => s.state);
          
          // 1 medium state (middle range)
          const midIndex = Math.floor(sorted.length / 2);
          const mediumState = sorted[midIndex]?.state;
          
          // 1 safe state (bottom 25%, but not zero)
          const safeIndex = Math.floor(sorted.length * 0.75);
          const safeState = sorted[safeIndex]?.state;
          
          const smartDefaults = [...hotStates, mediumState, safeState]
            .filter(Boolean)
            .slice(0, maxStates); // Ensure exactly 5 states
          
          console.log('StateComparisonChart - Smart defaults:', smartDefaults);
          
          // Cache the results
          localStorage.setItem(cacheKey, JSON.stringify({
            states: smartDefaults,
            timestamp: Date.now()
          }));
          
          setSelectedStates(smartDefaults);
        } else {
          console.log('StateComparisonChart - Not enough states, using fallback');
          // Fallback if not enough data
          setSelectedStates(defaultToSmartSelection ? states.slice(0, maxStates) : states);
        }
        
        setInitialStatesLoaded(true);
      } catch (err) {
        console.error('Failed to load smart defaults:', err);
        console.log('StateComparisonChart - Using fallback states:', states.slice(0, maxStates));
        // Fallback to provided states
        setSelectedStates(defaultToSmartSelection ? states.slice(0, maxStates) : states);
        setInitialStatesLoaded(true);
      }
    };

    if (!initialStatesLoaded && defaultToSmartSelection) {
      console.log('StateComparisonChart - Loading smart defaults...');
      loadSmartDefaults();
    } else if (!initialStatesLoaded) {
      console.log('StateComparisonChart - Using initial states:', states.slice(0, maxStates));
      setSelectedStates(states.slice(0, maxStates));
      setInitialStatesLoaded(true);
    }
  }, [initialStatesLoaded, states, maxStates, monthsBack, defaultToSmartSelection]);

  useEffect(() => {
    const fetchData = async () => {
      // Wait for initial states to be loaded first
      if (!initialStatesLoaded) return;
      
      try {
        setLoading(true);
        
        // TODO: Temporarily disabled to prevent 500 error loops
        // const params = new URLSearchParams({
        //   states: selectedStates.slice(0, maxStates).join(','),
        //   months_back: selectedMonths.toString(),
        // });

        // const response = await fetch(`/api/v1/timeseries/trend-comparison?${params}`);
        
        // if (!response.ok) {
        //   throw new Error(`Failed to fetch comparison data: ${response.statusText}`);
        // }

        // const responseData: any = await response.json();
        
        // if (responseData && responseData.comparison) {
        //   // API returns data directly, not wrapped in an array
        //   const result: TrendComparisonData = {
        //     comparison: responseData.comparison,
        //     timeRange: responseData.timeRange || '',
        //     generatedAt: responseData.generatedAt || new Date().toISOString(),
        //   };
          
        //   setData(result);
        //   setIsCached(responseData.cached);
        //   setCachedAt(responseData.cached_at);
        //   setApiStatus(responseData.status as 'ok' | 'degraded' | 'error');
        //   setError(null);
        // } else {
        //   // No data - show graceful message
        //   setError(responseData.message || 'No comparison data available for selected states');
        //   setData(null);
        //   setApiStatus(responseData.status as 'ok' | 'degraded' | 'error');
        //   setIsCached(responseData.cached);
        //   setCachedAt(responseData.cached_at);
        // }
        
        // Set loading to false by default
        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
        setApiStatus('error');
      } finally {
        setLoading(false);
      }
    };

    if (selectedStates.length > 0) {
      fetchData();
    }
  }, [selectedStates, selectedMonths, maxStates, initialStatesLoaded]);

  const toggleStateSelection = (state: string) => {
    if (selectedStates.includes(state)) {
      // Don't allow removing if only 1 state left
      if (selectedStates.length > 1) {
        setSelectedStates(selectedStates.filter(s => s !== state));
      }
    } else {
      // Don't allow adding if already at max
      if (selectedStates.length < maxStates) {
        setSelectedStates([...selectedStates, state]);
      }
    }
  };

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
      <div className={`w-full h-96 flex items-center justify-center rounded-lg ${
        apiStatus === 'degraded' ? 'bg-yellow-50' : 'bg-red-50'
      }`}>
        <div className={`text-center ${
          apiStatus === 'degraded' ? 'text-yellow-600' : 'text-red-600'
        }`}>
          {apiStatus === 'degraded' && <span className="text-2xl mb-2 block">⚠️</span>}
          {apiStatus === 'error' && <AlertTriangle className="h-12 w-12 mx-auto mb-4" />}
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
      <div className={`bg-white rounded-lg p-6 shadow-sm border ${
        apiStatus === 'degraded' ? 'border-yellow-200 bg-yellow-50/30' : 'border-gray-200'
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <MapPin className="h-5 w-5 text-green-600" />
              Regional Conflict Analysis
            </h3>
            <p className="text-sm text-gray-600 mt-1">
              {defaultToSmartSelection ? 
                `Smart selection: 3 hot states, 1 medium, 1 safe (${stateNames.length} of ${maxStates} max)` :
                `Comparing ${stateNames.length} state${stateNames.length !== 1 ? 's' : ''} over ${selectedMonths} months (up to ${maxStates} states supported)`
              }
            </p>
            {/* Cached Data Badge */}
            {isCached && cachedAt && (
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium mt-2 w-fit ${
                apiStatus === 'degraded'
                  ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                  : 'bg-blue-100 text-blue-800 border border-blue-300'
              }`}>
                <Package className="h-3 w-3" />
                <span>Cached • {formatCachedTime(cachedAt)}</span>
                {apiStatus === 'degraded' && <span>⚠️ Degraded</span>}
              </div>
            )}
          </div>

          <div className="flex items-center gap-2">
            {allowUserSelection && (
              <>
                <button
                  onClick={() => setShowControls(!showControls)}
                  className="px-4 py-2 rounded-lg text-sm font-medium bg-purple-600 text-white hover:bg-purple-700 transition-colors flex items-center gap-2"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  Select States & Period
                </button>
                <div className="h-8 w-px bg-gray-300"></div>
              </>
            )}
            
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

        {/* Configuration Panel */}
        {allowUserSelection && showControls && (
          <div className="mb-6 p-4 bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg border-2 border-purple-200">
            <h4 className="font-semibold text-purple-900 mb-3 flex items-center gap-2">
              ⚙️ Comparison Settings
            </h4>
            
            {/* Time Period Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Period
              </label>
              <div className="flex gap-2">
                {timePeriods.map((period) => (
                  <button
                    key={period.value}
                    onClick={() => setSelectedMonths(period.value)}
                    className={`px-3 py-1.5 rounded text-sm font-medium transition-colors ${
                      selectedMonths === period.value
                        ? 'bg-purple-600 text-white'
                        : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
                    }`}
                  >
                    {period.label}
                  </button>
                ))}
              </div>
            </div>

            {/* State Selector */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select States (max {maxStates}) - Currently: {selectedStates.length}
              </label>
              <div className="grid grid-cols-4 md:grid-cols-6 lg:grid-cols-9 gap-2 max-h-48 overflow-y-auto p-2 bg-white rounded border border-gray-200">
                {availableStates.map((state) => {
                  const isSelected = selectedStates.includes(state);
                  const isDisabled = !isSelected && selectedStates.length >= maxStates;
                  
                  return (
                    <button
                      key={state}
                      onClick={() => toggleStateSelection(state)}
                      disabled={isDisabled}
                      className={`px-2 py-1.5 rounded text-xs font-medium transition-all ${
                        isSelected
                          ? 'bg-green-600 text-white shadow-md'
                          : isDisabled
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-gray-50 text-gray-700 hover:bg-gray-200 border border-gray-300'
                      }`}
                    >
                      {state}
                    </button>
                  );
                })}
              </div>
              <p className="text-xs text-gray-600 mt-2">
                💡 Click states to add/remove from comparison. Green = selected, Gray = disabled (limit reached)
              </p>
            </div>
          </div>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {stateNames.map((state, index) => {
            const stateData = data.comparison[state];
            const color = STATE_COLORS[index % STATE_COLORS.length];
            
            // Determine state risk level based on fatalities
            const avgFatalities = stateData.fatalities.reduce((a: number, b: number) => a + b, 0) / stateData.fatalities.length;
            let riskLevel = 'Safe';
            let riskColor = 'text-green-600';
            let bgColor = 'bg-green-50 border-green-200';
            
            if (avgFatalities > 20) {
              riskLevel = 'Hot';
              riskColor = 'text-red-600';
              bgColor = 'bg-red-50 border-red-200';
            } else if (avgFatalities > 10) {
              riskLevel = 'Medium';
              riskColor = 'text-orange-600';
              bgColor = 'bg-orange-50 border-orange-200';
            }
            
            return (
              <div
                key={state}
                className={`bg-gradient-to-br from-gray-50 to-white p-4 rounded-lg border-2 transition-all hover:shadow-md ${bgColor}`}
                style={{ borderColor: color }}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    ></div>
                    <p className="text-sm font-semibold text-gray-900">{state}</p>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${riskColor} ${bgColor}`}>
                    {riskLevel}
                  </span>
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
