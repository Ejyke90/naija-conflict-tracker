import type { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';
import React, { useState, useEffect, lazy, Suspense } from 'react';
import { TrendingUp, Calendar, MapPin, Settings, Download, Printer, Wifi, WifiOff, Sparkles, ArrowRight } from 'lucide-react';
import ProtectedRoute from '../../components/ProtectedRoute';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { useConflictUpdates } from '@/hooks/useWebSocket';
import { exportToPDF, printPage } from '@/utils/exportData';
// Lazy load ALL heavy components for better performance
const IntelligenceInsights = lazy(() => import('../../components/intelligence/IntelligenceInsights').then(m => ({ default: m.IntelligenceInsights })));
const RiskHotspots = lazy(() => import('../../components/intelligence/RiskHotspots').then(m => ({ default: m.RiskHotspots })));
const SystemHeartbeat = lazy(() => import('../../src/components/dashboard/SystemHeartbeat'));
const HighRiskAlertMonitor = lazy(() => import('../../src/components/dashboard/HighRiskAlertMonitor'));
const MonthlyTrendsChart = lazy(() => import('../../components/charts/MonthlyTrendsChart'));
const SeasonalPatternChart = lazy(() => import('../../components/charts/SeasonalPatternChart'));
const StateComparisonChart = lazy(() => import('../../components/charts/StateComparisonChart'));

// Loading skeleton for charts
const ChartSkeleton = () => (
  <Card>
    <CardContent className="p-6">
      <div className="space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-64 w-full" />
        <div className="flex gap-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>
    </CardContent>
  </Card>
);

function DashboardContent() {
  const [monthsBack, setMonthsBack] = useState<number>(6);
  const [comparisonStates, setComparisonStates] = useState<string[]>([
    'Borno',
    'Zamfara',
    'Kaduna',
  ]);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [availableStates, setAvailableStates] = useState<Array<{
    id: number;
    name: string;
    conflictCount: number;
    totalFatalities: number;
  }>>([]);

  // WebSocket connection for real-time updates (non-blocking)
  const { isConnected } = useConflictUpdates((data) => {
    console.log('New conflict data:', data);
    setLastUpdate(new Date());
  });

  // Fetch available states for filter
  useEffect(() => {
    const fetchStates = async () => {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/locations/states`);
        if (response.ok) {
          const states = await response.json();
          setAvailableStates(states);
        } else {
          console.warn('Failed to load states for filter');
        }
      } catch (err) {
        console.error('Failed to load states:', err);
        // Fail silently - filter is optional enhancement
      }
    };
    fetchStates();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Nextier Conflict Analytics Dashboard
              </h1>
              <p className="mt-1 sm:mt-2 text-xs sm:text-sm text-gray-600">
                Predictive intelligence empowering peace in Nigeria
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4" role="region" aria-label="Dashboard controls">
              {/* System Heartbeat (Compact) */}
              <Suspense fallback={
                <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 animate-pulse">
                  <div className="h-4 w-4 bg-gray-300 rounded-full" />
                  <div className="h-3 w-16 bg-gray-300 rounded" />
                </div>
              }>
                <SystemHeartbeat compact={true} showControls={false} refreshInterval={10000} />
              </Suspense>
              
              {/* WebSocket Status Indicator */}
              <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 no-print">
                {isConnected ? (
                  <>
                    <Wifi className="h-4 w-4 text-green-600" />
                    <span className="text-xs text-green-600">Live</span>
                  </>
                ) : (
                  <>
                    <WifiOff className="h-4 w-4 text-gray-400" />
                    <span className="text-xs text-gray-400">Offline</span>
                  </>
                )}
              </div>
              
              {/* Export Buttons */}
              <Button
                variant="outline"
                size="sm"
                onClick={printPage}
                className="no-print gap-2"
                aria-label="Print dashboard"
              >
                <Printer className="h-4 w-4" />
                <span className="hidden sm:inline">Print</span>
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={exportToPDF}
                className="no-print gap-2"
                aria-label="Export to PDF"
              >
                <Download className="h-4 w-4" />
                <span className="hidden sm:inline">Export PDF</span>
              </Button>
              
              <ThemeToggle />
              
              <div className="flex-1 sm:flex-none">
                <label htmlFor="time-range" className="block text-xs font-medium text-gray-700 mb-1">
                  Time Range
                </label>
                <select
                  id="time-range"
                  value={monthsBack}
                  onChange={(e) => setMonthsBack(Number(e.target.value))}
                  className="w-full sm:w-auto px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  aria-label="Select time range for analytics"
                >
                  <option value={6}>Last 6 months</option>
                  <option value={12}>Last 12 months</option>
                  <option value={24}>Last 24 months</option>
                  <option value={36}>Last 36 months</option>
                </select>
              </div>

              {/* State Filter Dropdown */}
              <div className="flex-1 sm:flex-none">
                <label htmlFor="state-filter" className="block text-xs font-medium text-gray-700 mb-1">
                  Filter by State
                </label>
                <select
                  id="state-filter"
                  value={selectedState || ''}
                  onChange={(e) => setSelectedState(e.target.value || null)}
                  className="w-full sm:w-auto px-3 sm:px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                  aria-label="Filter dashboard by state"
                >
                  <option value="">All States (National)</option>
                  {availableStates.map((state) => (
                    <option key={state.id} value={state.name}>
                      {state.name} ({state.conflictCount} incidents)
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Section 0: Automation Monitoring (NEW - Phase 1) */}
        <section aria-label="System Automation Status" className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Suspense fallback={<ChartSkeleton />}>
            <SystemHeartbeat compact={false} showControls={true} refreshInterval={10000} />
          </Suspense>
          <Suspense fallback={<ChartSkeleton />}>
            <HighRiskAlertMonitor maxVisible={5} showResolved={false} enableSound={true} refreshInterval={5000} />
          </Suspense>
        </section>

        {/* Section 1: Monthly Trends with Forecast */}
        <section aria-labelledby="monthly-trends-heading">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-6 w-6 text-blue-600" aria-hidden="true" />
            <h2 id="monthly-trends-heading" className="text-xl font-semibold text-gray-900">
              Monthly Trends & Forecasting
            </h2>
          </div>
          <Suspense fallback={<ChartSkeleton />}>
            <MonthlyTrendsChart
              monthsBack={monthsBack}
              state={selectedState}
              includeForecast={true}
            />
          </Suspense>
        </section>

        {/* Section 2: Seasonal Patterns */}
        <section aria-labelledby="seasonal-patterns-heading">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="h-6 w-6 text-purple-600" aria-hidden="true" />
            <h2 id="seasonal-patterns-heading" className="text-xl font-semibold text-gray-900">
              Seasonal Conflict Patterns
            </h2>
          </div>
          <Suspense fallback={<ChartSkeleton />}>
            <SeasonalPatternChart state={selectedState} />
          </Suspense>
        </section>

        {/* Section 3: State Comparison */}
        <section aria-labelledby="state-comparison-heading">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="h-6 w-6 text-green-600" aria-hidden="true" />
            <h2 id="state-comparison-heading" className="text-xl font-semibold text-gray-900">State Comparison</h2>
          </div>
          <Suspense fallback={<ChartSkeleton />}>
            <StateComparisonChart states={comparisonStates} monthsBack={12} />
          </Suspense>
        </section>

        {/* Info Cards */}
        <section aria-label="Analytics features overview" className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <article className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
            <div className="flex items-start gap-3">
              <div className="bg-blue-600 rounded-lg p-3" aria-hidden="true">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">Trend Detection</h3>
                <p className="text-sm text-blue-700">
                  3-month moving averages smooth out noise and reveal underlying conflict patterns
                </p>
              </div>
            </div>
          </article>

          <article className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
            <div className="flex items-start gap-3">
              <div className="bg-purple-600 rounded-lg p-3" aria-hidden="true">
                <Calendar className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-purple-900 mb-1">Seasonal Analysis</h3>
                <p className="text-sm text-purple-700">
                  Identify high-risk months by aggregating historical data across all years
                </p>
              </div>
            </div>
          </article>

          <article className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
            <div className="flex items-start gap-3">
              <div className="bg-green-600 rounded-lg p-3" aria-hidden="true">
                <MapPin className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-green-900 mb-1">State Insights</h3>
                <p className="text-sm text-green-700">
                  Compare conflict trends across multiple states to identify regional patterns
                </p>
              </div>
            </div>
          </article>
        </section>

        {/* Methodology Note */}
        <section aria-labelledby="methodology-heading" className="bg-white rounded-lg p-6 border border-gray-200">
          <div className="flex items-start gap-3">
            <Settings className="h-5 w-5 text-gray-500 mt-0.5" aria-hidden="true" />
            <div>
              <h3 id="methodology-heading" className="font-semibold text-gray-900 mb-2">Methodology</h3>
              <div className="text-sm text-gray-600 space-y-2">
                <p>
                  <strong>Anomaly Detection:</strong> Statistical outlier detection using z-scores
                  (threshold: 2.0 standard deviations). Red markers indicate unusual conflict spikes
                  requiring investigation.
                </p>
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border-l-4 border-indigo-500 rounded-r-lg p-4 -mx-2">
                  <div className="flex items-start gap-3">
                    <Sparkles className="h-5 w-5 text-indigo-600 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="font-semibold text-indigo-900 mb-1">🔮 AI-Powered Forecasting</p>
                      <p className="text-sm text-indigo-700 mb-3">
                        Advanced machine learning models (Prophet, ARIMA, LSTM) deliver precise conflict predictions with confidence intervals, trend decomposition, and risk assessments.
                      </p>
                      <Link href="/forecasts" className="inline-flex items-center gap-2 text-sm font-medium text-indigo-600 hover:text-indigo-800 transition group">
                        Explore AI Forecasts
                        <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                      </Link>
                    </div>
                  </div>
                </div>
                <p>
                  <strong>Seasonal Patterns:</strong> High-risk months show &gt;20% more incidents
                  than the annual average, aggregated across all years in the database.
                </p>
                <p className="text-xs text-gray-500 mt-3">
                  Data source: Nextier Nigeria Violent Conflicts Database (6,580+ events, 2020-2026)
                </p>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

const Dashboard: NextPage = () => {
  return (
    <ProtectedRoute requiredRole="viewer">
      <Head>
        <title>Dashboard - Nextier Nigeria Conflict Tracker</title>
        <meta name="description" content="Nextier's real-time conflict tracking and forecasting for Nigeria" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <DashboardContent />
    </ProtectedRoute>
  );
};

export default Dashboard;
