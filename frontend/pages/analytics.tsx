import React, { useState } from 'react';
import MonthlyTrendsChart from '../components/charts/MonthlyTrendsChart';
import SeasonalPatternChart from '../components/charts/SeasonalPatternChart';
import StateComparisonChart from '../components/charts/StateComparisonChart';
import { TrendingUp, Calendar, MapPin, Settings } from 'lucide-react';
import ProtectedRoute from '../components/ProtectedRoute';

function AnalyticsPageContent() {
  const [selectedState, setSelectedState] = useState<string>('');
  const [monthsBack, setMonthsBack] = useState<number>(24);
  const [comparisonStates, setComparisonStates] = useState<string[]>([
    'Borno',
    'Zamfara',
    'Kaduna',
  ]);

  const topStates = [
    'All States',
    'Borno',
    'Zamfara',
    'Kaduna',
    'Plateau',
    'Benue',
    'Taraba',
    'Niger',
    'Katsina',
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Conflict Analytics Dashboard
              </h1>
              <p className="mt-2 text-sm text-gray-600">
                Time-series analysis, forecasting, and seasonal patterns for conflict data
              </p>
            </div>
            
            <div className="flex items-center gap-4" role="region" aria-label="Dashboard controls">
              <div>
                <label htmlFor="state-filter" className="block text-xs font-medium text-gray-700 mb-1">
                  State Filter
                </label>
                <select
                  id="state-filter"
                  value={selectedState}
                  aria-label="Filter analytics by state"
                  onChange={(e) => setSelectedState(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {topStates.map((state) => (
                    <option key={state} value={state === 'All States' ? '' : state}>
                      {state}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="time-range" className="block text-xs font-medium text-gray-700 mb-1">
                  Time Range
                </label>
                <select
                  id="time-range"
                  value={monthsBack}
                  onChange={(e) => setMonthsBack(Number(e.target.value))}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
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
          <MonthlyTrendsChart
            state={selectedState || undefined}
            monthsBack={monthsBack}
            includeForecast={true}
          />
        </section>

        {/* Section 2: Seasonal Patterns */}
        <section aria-labelledby="seasonal-patterns-heading">
          <div className="flex items-center gap-2 mb-4">
            <Calendar className="h-6 w-6 text-purple-600" aria-hidden="true" />
            <h2 id="seasonal-patterns-heading" className="text-xl font-semibold text-gray-900">
              Seasonal Conflict Patterns
            </h2>
          </div>
          <SeasonalPatternChart state={selectedState || undefined} />
        </section>

        {/* Section 3: State Comparison */}
        <section aria-labelledby="state-comparison-heading">
          <div className="flex items-center gap-2 mb-4">
            <MapPin className="h-6 w-6 text-green-600" aria-hidden="true" />
            <h2 id="state-comparison-heading" className="text-xl font-semibold text-gray-900">State Comparison</h2>
          </div>
          <StateComparisonChart states={comparisonStates} monthsBack={12} />
        </section>

        {/* Info Cards */}
        <section aria-label="Analytics features overview" className="grid grid-cols-1 md:grid-cols-3 gap-6">
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
                <p>
                  <strong>Forecasting:</strong> Simple linear regression on the most recent 6-month
                  window. Predictions are short-term (3 months) and assume linear continuation of
                  recent trends.
                </p>
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

export default function AnalyticsPage() {
  return (
    <ProtectedRoute requiredRole="viewer">
      <AnalyticsPageContent />
    </ProtectedRoute>
  );
}
