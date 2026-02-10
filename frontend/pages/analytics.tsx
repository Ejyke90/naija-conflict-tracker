import React, { useState, lazy, Suspense } from 'react';
import { TrendingUp, Settings, Sparkles } from 'lucide-react';
import ProtectedRoute from '../components/ProtectedRoute';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent } from '@/components/ui/card';
import { ThemeToggle } from '@/components/ui/theme-toggle';

// Lazy load chart components for better performance
const MonthlyTrendsChart = lazy(() => import('../components/charts/MonthlyTrendsChart'));
const IntelligenceGrid = lazy(() => import('../components/intelligence/IntelligenceGrid'));

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

function AnalyticsPageContent() {
  const [monthsBack, setMonthsBack] = useState<number>(6);
  const [comparisonStates, setComparisonStates] = useState<string[]>([
    'Borno',
    'Zamfara',
    'Kaduna',
  ]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Conflict Analytics Dashboard
              </h1>
              <p className="mt-1 sm:mt-2 text-xs sm:text-sm text-gray-600">
                Time-series analysis, forecasting, and seasonal patterns for conflict data
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4" role="region" aria-label="Dashboard controls">
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
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
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
              includeForecast={true}
            />
          </Suspense>
        </section>


        {/* Section 2: Intelligence Grid */}
        <section aria-labelledby="intelligence-grid-heading">
          <div className="flex items-center gap-2 mb-4">
            <Sparkles className="h-6 w-6 text-indigo-600" aria-hidden="true" />
            <h2 id="intelligence-grid-heading" className="text-xl font-semibold text-gray-900">
              High-Signal Intelligence Metrics
            </h2>
          </div>
          <Suspense fallback={<ChartSkeleton />}>
            <IntelligenceGrid />
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
                <p>
                  <strong>Forecasting:</strong> Simple linear regression on the most recent 6-month
                  window. Predictions are short-term (3 months) and assume linear continuation of
                  recent trends.
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

export default function AnalyticsPage() {
  return (
    <ProtectedRoute requiredRole="viewer">
      <AnalyticsPageContent />
    </ProtectedRoute>
  );
}
