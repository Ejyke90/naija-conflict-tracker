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
import { TrendingUp, TrendingDown, AlertTriangle, Calendar, Package } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Skeleton } from '../ui/skeleton';
import { Button } from '../ui/button';

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
  monthsBack?: number;
  state?: string | null;
  includeForecast?: boolean;
}

export default function MonthlyTrendsChart({
  monthsBack = 12,  // Changed back to 12 months for reasonable default
  state = null,
  includeForecast = true,
}: MonthlyTrendsChartProps) {
  const [data, setData] = useState<MonthlyTrendsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'incidents' | 'fatalities'>('incidents');
  const [isCached, setIsCached] = useState(false);
  const [cachedAt, setCachedAt] = useState<string | null>(null);
  const [apiStatus, setApiStatus] = useState<'ok' | 'degraded' | 'error'>('ok');
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 20000); // Increased to 20 second timeout
        
        const params = new URLSearchParams({
          months_back: monthsBack.toString(),
          include_forecast: includeForecast.toString(),
        });

        if (state) {
          params.append('state', state);
        }

        const response = await fetch(`/api/v1/timeseries/monthly-trends?${params}`, {
          signal: controller.signal,
        });
        clearTimeout(timeout);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch trends: ${response.statusText}`);
        }

        let responseData: any = await response.json();
        
        // Enhanced validation with multiple fallback strategies
        let isValidData = false;
        let validationReason = '';
        
        // Strategy 1: Check standard response format
        if (responseData && responseData.data && Array.isArray(responseData.data) && responseData.data.length > 0) {
          isValidData = true;
          validationReason = 'Standard format with data array';
        }
        // Strategy 2: Check if data is directly an array (some endpoints might return this)
        else if (Array.isArray(responseData) && responseData.length > 0) {
          // Wrap direct array in expected format
          responseData = {
            data: responseData,
            state: state || 'Nigeria',
            timeRange: { start: '', end: '', totalMonths: responseData.length },
            summary: {
              avgIncidentsPerMonth: responseData.reduce((sum: number, item: any) => sum + (item.incidents || 0), 0) / responseData.length,
              avgFatalitiesPerMonth: responseData.reduce((sum: number, item: any) => sum + (item.fatalities || 0), 0) / responseData.length,
              totalIncidents: responseData.reduce((sum: number, item: any) => sum + (item.incidents || 0), 0),
              totalFatalities: responseData.reduce((sum: number, item: any) => sum + (item.fatalities || 0), 0),
              peakMonth: responseData[0]?.month || '',
              peakIncidents: Math.max(...responseData.map((item: any) => item.incidents || 0)),
              anomalyCount: 0,
              trendDirection: 'decreasing' as const,
            }
          };
          isValidData = true;
          validationReason = 'Direct array format wrapped';
        }
        // Strategy 3: Check if response has any data-like property
        else if (responseData && typeof responseData === 'object') {
          const possibleDataKeys = ['data', 'results', 'items', 'records', 'monthlyData'];
          for (const key of possibleDataKeys) {
            if (responseData[key] && Array.isArray(responseData[key]) && responseData[key].length > 0) {
              responseData.data = responseData[key];
              isValidData = true;
              validationReason = `Found data in '${key}' property`;
              break;
            }
          }
        }
        
        console.log('MonthlyTrendsChart - Validation Result:', {
          isValidData,
          validationReason,
          responseKeys: Object.keys(responseData || {}),
          hasData: !!responseData?.data,
          dataType: Array.isArray(responseData?.data) ? 'array' : typeof responseData?.data,
          dataLength: responseData?.data?.length
        });
        
        if (isValidData) {
          // API returns data directly, not wrapped in an array
          const result: MonthlyTrendsData = {
            state: responseData.state || 'Nigeria',
            timeRange: responseData.timeRange || { start: '', end: '', totalMonths: 0 },
            data: responseData.data,
            summary: responseData.summary || {
              avgIncidentsPerMonth: 0,
              avgFatalitiesPerMonth: 0,
              totalIncidents: 0,
              totalFatalities: 0,
              peakMonth: '',
              peakIncidents: 0,
              anomalyCount: 0,
              trendDirection: 'decreasing' as const,
            },
            forecast: responseData.forecast,
          };
          
          setData(result);
          setIsCached(responseData.cached || false);
          setCachedAt(responseData.cached_at || null);
          setApiStatus(responseData.status as 'ok' | 'degraded' | 'error' || 'ok');
          setError(null);
        } else {
          // No data available, show graceful message with detailed error info
          const errorDetails = {
            responseData,
            hasResponse: !!responseData,
            hasData: !!responseData?.data,
            isArray: Array.isArray(responseData?.data),
            length: responseData?.data?.length,
            responseKeys: Object.keys(responseData || {}),
            validationReason: 'No valid data format found'
          };
          console.error('MonthlyTrendsChart - Data validation failed:', errorDetails);
          
          // Provide a more user-friendly error message
          let errorMessage = 'No conflict data available for this period';
          if (responseData?.message) {
            errorMessage = responseData.message;
          } else if (!responseData) {
            errorMessage = 'Unable to connect to the server';
          } else if (Object.keys(responseData).length === 0) {
            errorMessage = 'Server returned empty response';
          } else if (!responseData.data) {
            errorMessage = 'Server response missing data field';
          } else if (!Array.isArray(responseData.data)) {
            errorMessage = 'Server returned invalid data format';
          } else if (responseData.data.length === 0) {
            errorMessage = 'No conflict records found in database';
          }
          
          setError(errorMessage);
          setData(null);
          setApiStatus(responseData?.status as 'ok' | 'degraded' | 'error' || 'ok');
          setIsCached(responseData?.cached || false);
          setCachedAt(responseData?.cached_at || null);
        }
      } catch (err) {
        if (err instanceof Error && err.name === 'AbortError') {
          setError('Request timed out - data is taking too long to load');
          setApiStatus('degraded');
        } else {
          setError(err instanceof Error ? err.message : 'Failed to load data');
          setApiStatus('error');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [monthsBack, state, includeForecast, retryCount]);

  if (loading) {
    return (
      <div className="w-full space-y-4">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-64" />
            <Skeleton className="h-4 w-48 mt-2" />
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-24 w-full" />
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-96 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !data) {
    return (
      <Card className="border-orange-200">
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Calendar className="h-5 w-5 text-orange-600" />
            Monthly Trends & Forecasting
          </CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Historical patterns and predictive analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-orange-500 mb-4" />
            <p className="text-orange-700 font-medium text-center mb-2">
              {error || 'No data available'}
            </p>
            
            {/* Retry button for transient errors */}
            {(error?.includes('timed out') || error?.includes('Failed to fetch') || error?.includes('connect')) && (
              <div className="text-center text-sm text-gray-600 mt-4">
                <p className="mb-2">Suggestions:</p>
                <ul className="text-left space-y-1 mb-4">
                  <li>• Try reducing the time range</li>
                  <li>• Check your internet connection</li>
                  <li>• Refresh the page and try again</li>
                </ul>
                <div className="flex gap-2 justify-center">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => setRetryCount(prev => prev + 1)}
                    disabled={loading}
                  >
                    Retry ({retryCount})
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => window.location.reload()}
                  >
                    Refresh Page
                  </Button>
                </div>
              </div>
            )}
            
            {/* Show data details for debugging */}
            {process.env.NODE_ENV === 'development' && error?.includes('No conflict data') && (
              <div className="text-center text-xs text-gray-500 mt-4">
                <details className="cursor-pointer">
                  <summary>Debug Info</summary>
                  <div className="text-left mt-2 p-2 bg-gray-100 rounded">
                    <p>Backend: http://localhost:8000</p>
                    <p>Endpoint: /api/v1/timeseries/monthly-trends</p>
                    <p>Params: months_back={monthsBack}, include_forecast={includeForecast}</p>
                    {state && <p>State: {state}</p>}
                  </div>
                </details>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
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
        incidentsTrend: isNaN(forecast.predictedIncidents) ? 0 : forecast.predictedIncidents,
        fatalitiesTrend: isNaN(forecast.predictedFatalities) ? 0 : forecast.predictedFatalities,
        isAnomalousIncidents: false,
        isAnomalousFatalities: false,
      });
    });
  }

  // Validate and clean data to prevent NaN values
  const cleanedData = combinedData.map(item => ({
    ...item,
    incidents: isNaN(item.incidents) ? 0 : item.incidents,
    fatalities: isNaN(item.fatalities) ? 0 : item.fatalities,
    civilianCasualties: isNaN(item.civilianCasualties) ? 0 : item.civilianCasualties,
    geographicSpread: isNaN(item.geographicSpread) ? 0 : item.geographicSpread,
    incidentsTrend: isNaN(item.incidentsTrend) ? 0 : item.incidentsTrend,
    fatalitiesTrend: isNaN(item.fatalitiesTrend) ? 0 : item.fatalitiesTrend,
  }));

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
    <motion.div
      className="w-full space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Summary Stats */}
      <Card className={apiStatus === 'degraded' ? 'border-yellow-200 bg-yellow-50/30' : ''}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">
                Monthly Conflict Trends - {data.state}
              </CardTitle>
              <CardDescription>
                {data.timeRange.start} to {data.timeRange.end} ({data.timeRange.totalMonths} months)
              </CardDescription>
            </div>
            
            <div className="flex items-center gap-2 flex-col">
              {/* Cached Data Badge */}
              {isCached && cachedAt && (
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                  apiStatus === 'degraded'
                    ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                    : 'bg-blue-100 text-blue-800 border border-blue-300'
                }`}>
                  <Package className="h-3 w-3" />
                  <span>Cached • {cachedAt ? new Date(cachedAt).toLocaleDateString() : 'Unknown'}</span>
                  {apiStatus === 'degraded' && <span>⚠️ Degraded</span>}
                </div>
              )}

              <div className="flex items-center gap-2">
                <Button
                  onClick={() => setViewMode('incidents')}
                  variant={viewMode === 'incidents' ? 'default' : 'outline'}
                  size="sm"
                >
                  Incidents
                </Button>
                <Button
                  onClick={() => setViewMode('fatalities')}
                  variant={viewMode === 'fatalities' ? 'default' : 'outline'}
                  size="sm"
                  className={viewMode === 'fatalities' ? 'bg-destructive hover:bg-destructive/90' : ''}
                >
                  Fatalities
                </Button>
              </div>
            </div>
          </div>
        </CardHeader>
        <CardContent>

          {/* Summary Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card className="border-l-4 border-l-primary">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Avg Incidents/Month</div>
                  <div className="text-2xl font-bold">
                    {data.summary.avgIncidentsPerMonth.toFixed(1)}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="border-l-4 border-l-destructive">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Avg Fatalities/Month</div>
                  <div className="text-2xl font-bold">
                    {data.summary.avgFatalitiesPerMonth.toFixed(1)}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="border-l-4 border-l-orange-500">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2">Peak Month</div>
                  <div className="text-lg font-bold">{data.summary.peakMonth}</div>
                  <div className="text-xs text-muted-foreground">{data.summary.peakIncidents} incidents</div>
                </CardContent>
              </Card>
            </motion.div>
            
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
              <Card className="border-l-4 border-l-purple-500">
                <CardContent className="pt-6">
                  <div className="text-sm font-medium text-muted-foreground mb-2 flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    Trend Direction
                  </div>
                  <div className="flex items-center gap-2">
                    <div className={`flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                      data.summary.trendDirection === 'increasing' 
                        ? 'bg-red-100 text-red-700' 
                        : 'bg-green-100 text-green-700'
                    }`}>
                      {data.summary.trendDirection === 'increasing' ? (
                        <TrendingUp className="h-3 w-3" />
                      ) : (
                        <TrendingDown className="h-3 w-3" />
                      )}
                      <span>{data.summary.trendDirection}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>

          {data.summary.anomalyCount > 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mt-4"
            >
              <Card className="border-yellow-200 bg-yellow-50">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start gap-2">
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
                </CardContent>
              </Card>
            </motion.div>
          )}
        </CardContent>
      </Card>

      {/* Chart */}
      <Card>
        <CardContent className="pt-6">
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={cleanedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
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
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <Card className="border-primary bg-primary/5">
              <CardContent className="pt-4 pb-4">
                <p className="text-sm font-medium mb-1">
                  📈 AI-Powered Conflict Forecasting
                </p>
                <p className="text-xs text-muted-foreground">{data.forecast.note}</p>
                <div className="mt-2 grid grid-cols-3 gap-2">
                  {data.forecast.data.map((f) => (
                    <Card key={f.month}>
                      <CardContent className="pt-3 pb-3 text-center">
                        <p className="text-xs font-medium text-muted-foreground">{f.month}</p>
                        <p className="text-sm font-bold">
                          {viewMode === 'incidents'
                            ? f.predictedIncidents.toFixed(1)
                            : f.predictedFatalities.toFixed(1)}
                        </p>
                        <Badge variant="outline" className="text-xs mt-1">{f.confidence}</Badge>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
