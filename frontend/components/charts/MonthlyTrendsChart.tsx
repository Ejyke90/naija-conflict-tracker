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
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { StatCard } from '@/components/ui/stat-card';
import { TrendBadge } from '@/components/ui/trend-badge';

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
      <Card className="border-destructive">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center justify-center py-12">
            <AlertTriangle className="h-12 w-12 text-destructive mb-4" />
            <p className="text-destructive font-medium">{error || 'No data available'}</p>
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
    <motion.div
      className="w-full space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Header with Summary Stats */}
      <Card>
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
                    <TrendBadge
                      direction={data.summary.trendDirection === 'increasing' ? 'up' : 'down'}
                      label={data.summary.trendDirection}
                      invertColors={true}
                      size="lg"
                    />
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
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4"
          >
            <Card className="border-primary bg-primary/5">
              <CardContent className="pt-4 pb-4">
                <p className="text-sm font-medium mb-1">
                  📈 {data.forecast.periods}-Month Forecast ({data.forecast.method})
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
