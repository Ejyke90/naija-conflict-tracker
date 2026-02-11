import React, { useState } from 'react';
import {
  LineChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  TooltipProps
} from 'recharts';

interface ForecastDataPoint {
  date: string;
  actual?: number;
  predicted?: number;
  lower?: number;
  upper?: number;
  confidence?: number;
}

interface ForecastMainChartProps {
  data: ForecastDataPoint[];
  selectedModel: string;
  onModelChange: (model: string) => void;
  loading?: boolean;
}

const models = [
  { id: 'ensemble', name: 'Ensemble', description: 'Combined model (Best)' },
  { id: 'prophet', name: 'Prophet', description: 'Seasonal patterns' },
  { id: 'arima', name: 'ARIMA', description: 'Statistical' },
  { id: 'lstm', name: 'LSTM', description: 'Deep learning' }
];

const CustomTooltip: React.FC<TooltipProps<number, string>> = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-lg border border-gray-200">
        <p className="text-sm font-semibold text-gray-900 mb-2">{label}</p>
        {payload.map((entry, index) => {
          const isActual = entry.dataKey === 'actual';
          const isPredicted = entry.dataKey === 'predicted';
          const confidence = entry.payload?.confidence;
          
          return (
            <div key={index} className="text-sm">
              {isActual && (
                <p className="text-blue-600 font-medium">
                  Actual: <span className="font-bold">{entry.value}</span> incidents
                </p>
              )}
              {isPredicted && (
                <>
                  <p className="text-purple-600 font-medium">
                    Forecast: <span className="font-bold">{entry.value}</span> incidents
                  </p>
                  {confidence && (
                    <p className="text-gray-600">
                      Confidence: {((confidence || 0) * 100).toFixed(0)}%
                    </p>
                  )}
                  {entry.payload?.lower && entry.payload?.upper && (
                    <p className="text-gray-500 text-xs">
                      Range: {entry.payload.lower} - {entry.payload.upper}
                    </p>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    );
  }
  return null;
};

export const ForecastMainChart: React.FC<ForecastMainChartProps> = ({
  data,
  selectedModel,
  onModelChange,
  loading = false
}) => {
  const [showConfidenceInterval, setShowConfidenceInterval] = useState(true);

  return (
    <div className="bg-white rounded-lg p-6 shadow-lg">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <div>
          <h3 className="text-xl font-bold text-gray-900">12-Week Forecast</h3>
          <p className="text-sm text-gray-500 mt-1">
            Historical trends and AI-predicted future incidents
          </p>
        </div>

        {/* Model Selector */}
        <div className="flex flex-wrap gap-2">
          {models.map((model) => (
            <button
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
                selectedModel === model.id
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              title={model.description}
            >
              {model.name}
              {model.id === 'ensemble' && (
                <span className="ml-1 text-xs opacity-75">⭐</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Confidence Interval Toggle */}
      <div className="mb-4">
        <label className="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input
            type="checkbox"
            checked={showConfidenceInterval}
            onChange={(e) => setShowConfidenceInterval(e.target.checked)}
            className="rounded text-purple-600 focus:ring-purple-500"
          />
          Show 95% confidence interval
        </label>
      </div>

      {/* Chart */}
      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
            <p className="text-gray-500">Loading forecast data...</p>
          </div>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={400}>
          <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="confidenceGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
            />
            <YAxis
              tick={{ fontSize: 12 }}
              stroke="#9ca3af"
              label={{ value: 'Incidents', angle: -90, position: 'insideLeft', style: { fontSize: 12 } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: 14 }}
              iconType="line"
            />

            {/* Confidence Interval Area */}
            {showConfidenceInterval && (
              <>
                <Area
                  type="monotone"
                  dataKey="upper"
                  stroke="none"
                  fill="url(#confidenceGradient)"
                  name="Upper Bound"
                />
                <Area
                  type="monotone"
                  dataKey="lower"
                  stroke="none"
                  fill="url(#confidenceGradient)"
                  name="Lower Bound"
                />
              </>
            )}

            {/* Historical Actual Line */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4, fill: '#3b82f6' }}
              name="Historical Actual"
              connectNulls={false}
            />

            {/* Forecast Line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#8b5cf6"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ r: 4, fill: '#fff', stroke: '#8b5cf6', strokeWidth: 2 }}
              name="AI Forecast"
              connectNulls={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      )}

      {/* Legend */}
      <div className="mt-6 flex flex-wrap gap-6 text-sm border-t pt-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-1 bg-blue-600 rounded"></div>
          <span className="text-gray-700">Historical Actual</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-1 border-2 border-purple-600 border-dashed rounded"></div>
          <span className="text-gray-700">AI Forecast</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-8 h-4 bg-purple-600/20 rounded"></div>
          <span className="text-gray-700">95% Confidence Interval</span>
        </div>
      </div>

      {/* Model Info */}
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          <span className="font-semibold">Current Model:</span>{' '}
          {models.find(m => m.id === selectedModel)?.description}
          {selectedModel === 'ensemble' && (
            <span className="ml-2 text-purple-600 font-medium">
              (Weighted average: 50% Prophet + 30% ARIMA + 20% LSTM)
            </span>
          )}
        </p>
      </div>
    </div>
  );
};

export default ForecastMainChart;
