import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import useSWR from 'swr';

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
    ['/api/v1/predictions/next-30-days', manualRefreshTrigger],
    ([url]) => fetcher(url),
    {
      refreshInterval: 6 * 60 * 60 * 1000, // 6 hours
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  const handleManualRefresh = () => {
    setManualRefreshTrigger((prev) => prev + 1);
    mutate();
  };

  const heroPrediction = useMemo(() => data?.predictions?.[0], [data]);

  return (
    <div className="rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800 p-6 shadow-xl ring-1 ring-slate-800/60 text-white">
      {/* Hero Header */}
      <div className="flex flex-col lg:flex-row lg:items-center gap-4 mb-6">
        <div className="flex-1 space-y-1">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400">AI forecast preview</p>
          <h3 className="text-2xl font-semibold leading-tight">Next 30-day conflict outlook</h3>
          <p className="text-sm text-slate-300">Top at-risk states, confidence bands, refreshed every 6 hours</p>
          {data && (
            <p className="text-xs text-slate-400">Last updated {formatLastUpdated(data.timestamp)}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleManualRefresh}
            disabled={isLoading}
            className="rounded-full border border-slate-700 bg-slate-800/60 px-4 py-2 text-sm font-medium text-white transition hover:border-indigo-400 hover:text-indigo-100 focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isLoading ? 'Refreshing…' : 'Refresh'}
          </button>
          <Link
            href="/forecasts"
            className="inline-flex items-center rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 focus:ring-offset-slate-900"
          >
            View full forecast
          </Link>
        </div>
      </div>

      {/* Hero Metric Strip */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <div className="rounded-xl border border-white/5 bg-white/5 p-4 shadow-sm backdrop-blur">
          <p className="text-sm text-slate-300">Top risk state</p>
          <p className="text-xl font-semibold text-white">{heroPrediction?.state ?? '—'}</p>
          <p className="text-xs text-slate-400 mt-1">Rank #{heroPrediction?.rank ?? '—'} · {heroPrediction?.risk_level ?? '—'}</p>
        </div>
        <div className="rounded-xl border border-white/5 bg-white/5 p-4 shadow-sm backdrop-blur">
          <p className="text-sm text-slate-300">Predicted incidents (30d)</p>
          <p className="text-xl font-semibold text-white">{heroPrediction?.next_30_days?.predicted_incidents ?? '—'}</p>
          <p className="text-xs text-slate-400 mt-1">CI {heroPrediction?.next_30_days ? `${heroPrediction.next_30_days.incidents_ci_lower} – ${heroPrediction.next_30_days.incidents_ci_upper}` : '—'}</p>
        </div>
        <div className="rounded-xl border border-white/5 bg-white/5 p-4 shadow-sm backdrop-blur">
          <p className="text-sm text-slate-300">Model & accuracy</p>
          <p className="text-xl font-semibold text-white capitalize">{heroPrediction?.model ?? '—'}</p>
          <p className="text-xs text-slate-400 mt-1">MAPE {heroPrediction?.mape ? `${Math.round(heroPrediction.mape * 100)}%` : 'n/a'}</p>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && !data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="h-72 rounded-xl bg-white/5 animate-pulse border border-white/10"
            ></div>
          ))}
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="mb-4 flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-100">
          <svg className="h-5 w-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="font-semibold">Failed to load predictions</p>
            <p className="text-red-200 mt-1">{error.message}</p>
            <div className="mt-2 flex gap-3">
              <button
                onClick={handleManualRefresh}
                className="text-sm font-semibold text-red-100 underline decoration-red-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-red-300 focus:ring-offset-2 focus:ring-offset-slate-900"
              >
                Try again
              </button>
              <Link
                href="/forecasts"
                className="text-sm font-semibold text-indigo-100 underline decoration-indigo-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 focus:ring-offset-slate-900"
              >
                Open full forecast
              </Link>
            </div>
          </div>
        </div>
      )}

      {/* Empty State */}
      {data && data.predictions.length === 0 && !isLoading && (
        <div className="mb-4 rounded-xl border border-white/10 bg-white/5 p-6 text-center text-slate-200">
          <svg className="h-12 w-12 text-slate-400 mx-auto mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <h4 className="text-lg font-semibold text-white">No predictions available</h4>
          <p className="text-sm text-slate-300 mt-2">Data is insufficient right now. Forecasts will appear once enough history is available.</p>
          <div className="mt-3">
            <Link
              href="/forecasts"
              className="inline-flex items-center rounded-full bg-indigo-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:bg-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 focus:ring-offset-slate-900"
            >
              View full forecast
            </Link>
          </div>
        </div>
      )}

      {/* Predictions Grid */}
      {data && data.predictions.length > 0 && !isLoading && (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {data.predictions.map((prediction: PredictionData) => (
              <PredictionCard key={prediction.state} prediction={prediction} />
            ))}
          </div>

          {/* Metadata */}
          <div className="mt-6 pt-4 border-t border-white/10 text-slate-200">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div>
                <p className="text-slate-400">States Analyzed</p>
                <p className="font-semibold text-white">{data.metadata.total_states_analyzed}</p>
              </div>
              <div>
                <p className="text-slate-400">Predictions Shown</p>
                <p className="font-semibold text-white">{data.metadata.top_states_returned}</p>
              </div>
              <div>
                <p className="text-slate-400">Analysis Period</p>
                <p className="font-semibold text-white">{data.metadata.analysis_period_days} days</p>
              </div>
              <div>
                <p className="text-slate-400">Refresh Interval</p>
                <p className="font-semibold text-white">{data.metadata.refresh_interval_hours}h</p>
              </div>
            </div>
          </div>

          {/* Footer Note */}
          <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-3 text-xs text-slate-200">
            <p>
              <span className="font-semibold text-white">Disclaimer:</span> These predictions are experimental and based on historical patterns. Confidence intervals (CI) represent the range of likely outcomes. Actual outcomes may vary due to unforeseen events.{' '}
              <Link href="/docs" className="font-semibold text-indigo-200 hover:text-white hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:ring-offset-2 focus:ring-offset-slate-900">
                Learn more about our models
              </Link>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

