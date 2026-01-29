import React, { useState } from 'react';
import useSWR from 'swr';
import Link from 'next/link';

interface PredictionData {
  state: string;
  rank: number;
  risk_level: string;
  risk_score: number;
  next_30_days: {
    predicted_incidents: number;
    incidents_ci_lower: number;
    incidents_ci_upper: number;
    predicted_fatalities: number;
    fatalities_ci_lower: number;
    fatalities_ci_upper: number;
  };
  model: string;
  mape?: number;
  accuracy_percent?: number;
  last_trained?: string;
}

interface PredictionsResponse {
  timestamp: string;
  predictions: PredictionData[];
  metadata: {
    total_states_analyzed: number;
    top_states_returned: number;
    analysis_period_days: number;
    forecast_horizon_days: number;
    refresh_interval_hours: number;
  };
}

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error('Failed to fetch predictions');
  }
  return res.json();
};

const getRiskColor = (riskLevel: string): string => {
  switch (riskLevel) {
    case 'CRITICAL':
      return 'bg-red-50 border-red-200';
    case 'HIGH':
      return 'bg-orange-50 border-orange-200';
    case 'MEDIUM':
      return 'bg-yellow-50 border-yellow-200';
    case 'LOW':
      return 'bg-green-50 border-green-200';
    default:
      return 'bg-gray-50 border-gray-200';
  }
};

const getRiskBadgeColor = (riskLevel: string): string => {
  switch (riskLevel) {
    case 'CRITICAL':
      return 'bg-red-100 text-red-800 border border-red-300';
    case 'HIGH':
      return 'bg-orange-100 text-orange-800 border border-orange-300';
    case 'MEDIUM':
      return 'bg-yellow-100 text-yellow-800 border border-yellow-300';
    case 'LOW':
      return 'bg-green-100 text-green-800 border border-green-300';
    default:
      return 'bg-gray-100 text-gray-800';
  }
};

const getRiskEmoji = (riskLevel: string): string => {
  switch (riskLevel) {
    case 'CRITICAL':
      return '🔴';
    case 'HIGH':
      return '🟠';
    case 'MEDIUM':
      return '🟡';
    case 'LOW':
      return '🟢';
    default:
      return '⚪';
  }
};

const formatLastUpdated = (isoString: string): string => {
  const now = new Date();
  const lastUpdate = new Date(isoString);
  const diffMs = now.getTime() - lastUpdate.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMins = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

  if (diffHours > 0) {
    return `${diffHours}h ${diffMins}m ago`;
  } else if (diffMins > 0) {
    return `${diffMins}m ago`;
  } else {
    return 'just now';
  }
};

interface PredictionCardProps {
  prediction: PredictionData;
}

const PredictionCard: React.FC<PredictionCardProps> = ({ prediction }) => {
  return (
    <div className={`rounded-lg p-5 border ${getRiskColor(prediction.risk_level)} shadow-sm hover:shadow-md transition-shadow`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="text-lg font-bold text-gray-900">{prediction.state}</h4>
          <p className="text-xs text-gray-500">Rank #{prediction.rank}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getRiskBadgeColor(prediction.risk_level)}`}>
          {getRiskEmoji(prediction.risk_level)} {prediction.risk_level}
        </span>
      </div>

      {/* Risk Score */}
      <div className="mb-4 pb-3 border-b border-current border-opacity-10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Risk Score:</span>
          <span className="font-semibold text-gray-900">{prediction.risk_score.toFixed(1)}/10</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
          <div
            className="bg-gradient-to-r from-green-500 to-red-500 h-1.5 rounded-full"
            style={{ width: `${(prediction.risk_score / 10) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Predictions */}
      <div className="space-y-3 mb-4">
        {/* Incidents Prediction */}
        <div>
          <div className="flex justify-between items-baseline mb-1">
            <label className="text-sm font-medium text-gray-700">Predicted Incidents (30 days)</label>
            <span className="text-sm text-gray-600">
              {prediction.next_30_days.predicted_incidents}
            </span>
          </div>
          <p className="text-xs text-gray-500">
            95% CI: {prediction.next_30_days.incidents_ci_lower} - {prediction.next_30_days.incidents_ci_upper}
          </p>
          <div className="w-full bg-gray-100 rounded h-2 mt-1">
            <div
              className="bg-indigo-500 h-2 rounded"
              style={{
                width: `${Math.min(
                  (prediction.next_30_days.predicted_incidents / 100) * 100,
                  100
                )}%`,
              }}
            ></div>
          </div>
        </div>

        {/* Fatalities Prediction */}
        <div>
          <div className="flex justify-between items-baseline mb-1">
            <label className="text-sm font-medium text-gray-700">Predicted Fatalities (30 days)</label>
            <span className="text-sm text-gray-600">
              {prediction.next_30_days.predicted_fatalities}
            </span>
          </div>
          <p className="text-xs text-gray-500">
            95% CI: {prediction.next_30_days.fatalities_ci_lower} - {prediction.next_30_days.fatalities_ci_upper}
          </p>
          <div className="w-full bg-gray-100 rounded h-2 mt-1">
            <div
              className="bg-red-500 h-2 rounded"
              style={{
                width: `${Math.min(
                  (prediction.next_30_days.predicted_fatalities / 500) * 100,
                  100
                )}%`,
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="pt-3 border-t border-current border-opacity-10 space-y-1">
        <div className="flex justify-between text-xs">
          <span className="text-gray-600">Model:</span>
          <span className="font-medium text-gray-900 capitalize">{prediction.model}</span>
        </div>
        {prediction.accuracy_percent && (
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">Accuracy:</span>
            <span className="font-medium text-gray-900">{prediction.accuracy_percent}%</span>
          </div>
        )}
        {prediction.last_trained && (
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">Last trained:</span>
            <span className="font-medium text-gray-900">
              {new Date(prediction.last_trained).toLocaleDateString()}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default function AIPredictions() {
  const [manualRefreshTrigger, setManualRefreshTrigger] = useState(0);

  const { data, error, isLoading, mutate } = useSWR(
    '/api/v1/predictions/next-30-days',
    fetcher,
    {
      refreshInterval: 6 * 60 * 60 * 1000, // 6 hours
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  const handleManualRefresh = () => {
    setManualRefreshTrigger(prev => prev + 1);
    mutate();
  };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-2xl font-bold text-gray-900">AI Predictions</h3>
          <p className="text-sm text-gray-600 mt-1">Next 30-day conflict forecasts for top at-risk states</p>
        </div>
        <button
          onClick={handleManualRefresh}
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
        >
          {isLoading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Last Updated */}
      {data && (
        <div className="mb-4 text-xs text-gray-500">
          Last updated: {formatLastUpdated(data.timestamp)}
        </div>
      )}

      {/* Loading State */}
      {isLoading && !data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="bg-gray-200 rounded-lg h-80 animate-pulse"></div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
          <div className="flex items-start">
            <svg className="h-5 w-5 text-red-500 mt-0.5 mr-3" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <h4 className="font-medium text-red-900">Failed to load predictions</h4>
              <p className="text-sm text-red-700 mt-1">{error.message}</p>
              <button
                onClick={handleManualRefresh}
                className="text-sm text-red-600 hover:text-red-800 font-medium mt-2 underline"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {data && data.predictions.length === 0 && !isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <svg className="h-12 w-12 text-blue-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h4 className="text-lg font-semibold text-blue-900 mb-2">No predictions available</h4>
          <p className="text-blue-700 text-sm mb-4">Insufficient conflict data to generate predictions</p>
          <p className="text-blue-600 text-xs">Predictions will appear here once enough historical data is available</p>
        </div>
      )}

      {/* Predictions Grid */}
      {data && data.predictions.length > 0 && !isLoading && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {data && data.predictions && data.predictions.map((prediction: PredictionData) => (
              <PredictionCard key={prediction.state} prediction={prediction} />
            ))}
          </div>

          {/* Metadata */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div>
                <p className="text-gray-600">States Analyzed</p>
                <p className="font-semibold text-gray-900">{data.metadata.total_states_analyzed}</p>
              </div>
              <div>
                <p className="text-gray-600">Predictions Shown</p>
                <p className="font-semibold text-gray-900">{data.metadata.top_states_returned}</p>
              </div>
              <div>
                <p className="text-gray-600">Analysis Period</p>
                <p className="font-semibold text-gray-900">{data.metadata.analysis_period_days} days</p>
              </div>
              <div>
                <p className="text-gray-600">Refresh Interval</p>
                <p className="font-semibold text-gray-900">{data.metadata.refresh_interval_hours}h</p>
              </div>
            </div>
          </div>

          {/* Footer Note */}
          <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-xs text-blue-700">
            <p>
              <strong>Disclaimer:</strong> These predictions are experimental and based on historical patterns. Confidence intervals (CI) represent the range of likely outcomes. Actual outcomes may vary due to unforeseen events.{' '}
              <Link href="/docs" className="font-semibold hover:underline">
                Learn more about our models
              </Link>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

