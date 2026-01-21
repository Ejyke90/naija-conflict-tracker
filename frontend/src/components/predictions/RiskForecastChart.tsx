import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine,
} from 'recharts';
import { RiskPrediction } from '@/types/predictions';

interface RiskForecastChartProps {
  predictions: RiskPrediction[];
  selectedLocation?: string;
}

export function RiskForecastChart({
  predictions,
  selectedLocation,
}: RiskForecastChartProps) {
  // Transform predictions into chart data
  const chartData = React.useMemo(() => {
    const filteredPredictions = selectedLocation
      ? predictions.filter((p) => p.lga === selectedLocation)
      : predictions.slice(0, 10);

    return filteredPredictions.map((pred) => ({
      name: pred.lga,
      current: pred.currentRisk,
      day7: pred.predicted7Day,
      day14: pred.predicted14Day,
      day30: pred.predicted30Day,
      confidence: pred.confidence,
    }));
  }, [predictions, selectedLocation]);

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
      <div className="mb-6">
        <h3 className="text-lg font-bold text-gray-900 mb-1">
          Risk Forecast Timeline
        </h3>
        <p className="text-sm text-gray-600">
          AI-predicted conflict risk levels across time horizons
        </p>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData}>
          <defs>
            <linearGradient id="currentGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
          />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            label={{
              value: 'Risk Score',
              angle: -90,
              position: 'insideLeft',
              style: { fontSize: 12 },
            }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />

          <ReferenceLine
            y={75}
            stroke="#dc2626"
            strokeDasharray="3 3"
            label={{ value: 'High Risk Threshold', fontSize: 11 }}
          />

          <Area
            type="monotone"
            dataKey="current"
            stroke="#3b82f6"
            fill="url(#currentGradient)"
            name="Current Risk"
          />
          <Area
            type="monotone"
            dataKey="day7"
            stroke="#f59e0b"
            fill="url(#forecastGradient)"
            strokeDasharray="5 5"
            name="7-Day Forecast"
          />
          <Line
            type="monotone"
            dataKey="day14"
            stroke="#ef4444"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
            name="14-Day Forecast"
          />
          <Line
            type="monotone"
            dataKey="day30"
            stroke="#dc2626"
            strokeWidth={2}
            strokeDasharray="10 5"
            dot={false}
            name="30-Day Forecast"
          />
        </AreaChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="text-center p-3 bg-blue-50 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Avg Current Risk</div>
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(
              chartData.reduce((sum, d) => sum + d.current, 0) /
                chartData.length
            )}
          </div>
        </div>
        <div className="text-center p-3 bg-orange-50 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">7-Day Forecast</div>
          <div className="text-2xl font-bold text-orange-600">
            {Math.round(
              chartData.reduce((sum, d) => sum + d.day7, 0) / chartData.length
            )}
          </div>
        </div>
        <div className="text-center p-3 bg-red-50 rounded-lg">
          <div className="text-xs text-gray-600 mb-1">Avg Confidence</div>
          <div className="text-2xl font-bold text-red-600">
            {Math.round(
              chartData.reduce((sum, d) => sum + d.confidence, 0) /
                chartData.length
            )}
            %
          </div>
        </div>
      </div>
    </div>
  );
}
