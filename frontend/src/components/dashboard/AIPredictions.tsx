import React from 'react';
import { usePredictions } from '@/hooks/usePredictions';
import { AlertCard } from '@/components/predictions/AlertCard';
import { RiskForecastChart } from '@/components/predictions/RiskForecastChart';
import { Brain, TrendingUp, Target, Lightbulb, Loader2 } from 'lucide-react';

export function AIPredictions() {
  const { data, isLoading, error, isRefetching } = usePredictions();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
        <span className="ml-3 text-gray-600">Loading AI predictions...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <h3 className="text-red-800 font-semibold mb-2">
          Failed to Load Predictions
        </h3>
        <p className="text-red-600 text-sm">
          {error instanceof Error ? error.message : 'An error occurred'}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh indicator */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-blue-500 rounded-lg">
            <Brain className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">
              AI-Powered Predictions
            </h2>
            <p className="text-sm text-gray-600">
              Generated{' '}
              {new Date(data.generatedAt).toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
              {isRefetching && (
                <span className="ml-2 text-blue-600">
                  <Loader2 className="inline w-3 h-3 animate-spin" /> Updating...
                </span>
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-700">Model Accuracy:</span>
            <span className="font-bold text-blue-600">
              {data.metadata.accuracy}%
            </span>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Column - Alerts & Insights */}
        <div className="space-y-6">
          {/* Critical Alerts */}
          <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl p-6 border border-red-200">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-red-600" />
              <h3 className="font-bold text-gray-900">
                Critical Alerts ({data.alerts.filter(a => a.severity === 'critical' || a.severity === 'high').length})
              </h3>
            </div>
            <div className="space-y-3">
              {data.alerts
                .filter(alert => alert.severity === 'critical' || alert.severity === 'high')
                .slice(0, 3)
                .map((alert) => (
                  <AlertCard key={alert.id} alert={alert} />
                ))}
            </div>
          </div>

          {/* Recommendations */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <div className="flex items-center gap-2 mb-4">
              <Target className="w-5 h-5 text-green-600" />
              <h3 className="font-bold text-gray-900">Recommended Actions</h3>
            </div>
            <ol className="space-y-3">
              {data.recommendations.slice(0, 5).map((rec) => (
                <li key={rec.id} className="flex gap-3">
                  <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                    {rec.priority}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {rec.action}
                    </p>
                    <p className="text-xs text-gray-600 mt-1">
                      {rec.rationale}
                    </p>
                    <p className="text-xs text-blue-600 mt-1">
                      Timeframe: {rec.timeframe}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          {/* Pattern Analysis */}
          <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-200">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-gray-900">AI Insights</h3>
            </div>
            <div className="space-y-3 text-sm text-gray-700">
              <p>
                Our AI model has analyzed{' '}
                <span className="font-semibold">
                  {data.metadata.trainingDataPeriod}
                </span>{' '}
                of historical conflict data to generate these predictions.
              </p>
              <p>
                Current monitoring covers{' '}
                <span className="font-semibold">{data.predictions.length}</span>{' '}
                locations with an average confidence of{' '}
                <span className="font-semibold text-blue-600">
                  {Math.round(
                    data.predictions.reduce((sum, p) => sum + p.confidence, 0) /
                      data.predictions.length
                  )}
                  %
                </span>
                .
              </p>
              <div className="pt-3 border-t border-purple-200">
                <p className="text-xs text-gray-500">
                  Model: {data.metadata.modelVersion} • Last validated:{' '}
                  {new Date(data.metadata.lastValidated).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Charts & Analysis */}
        <div className="space-y-6">
          {/* Risk Forecast Chart */}
          <RiskForecastChart predictions={data.predictions} />

          {/* Contributing Factors */}
          <div className="bg-white rounded-xl p-6 border border-gray-200">
            <h3 className="font-bold text-gray-900 mb-4">
              Key Contributing Factors
            </h3>
            <div className="space-y-3">
              {data.contributingFactors
                .sort((a, b) => b.weight - a.weight)
                .slice(0, 6)
                .map((factor, index) => (
                  <div key={index}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">{factor.name}</span>
                      <span className="font-semibold text-gray-900">
                        {Math.round(factor.weight * 100)}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                        style={{ width: `${factor.weight * 100}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1 capitalize">
                      Category: {factor.category}
                    </p>
                  </div>
                ))}
            </div>
          </div>

          {/* Model Metadata */}
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-6 border border-blue-200">
            <h3 className="font-bold text-gray-900 mb-4">Model Information</h3>
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-600">Version:</dt>
                <dd className="font-semibold">{data.metadata.modelVersion}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Accuracy:</dt>
                <dd className="font-semibold text-green-600">
                  {data.metadata.accuracy}%
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Training Period:</dt>
                <dd className="font-semibold">
                  {data.metadata.trainingDataPeriod}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-600">Last Validated:</dt>
                <dd className="font-semibold">
                  {new Date(data.metadata.lastValidated).toLocaleDateString()}
                </dd>
              </div>
              <div className="pt-2 border-t border-blue-200">
                <dt className="text-gray-600 mb-1">Data Sources:</dt>
                <dd className="flex flex-wrap gap-1">
                  {data.metadata.dataSourcesUsed.map((source, i) => (
                    <span
                      key={i}
                      className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs rounded-full"
                    >
                      {source}
                    </span>
                  ))}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
}
