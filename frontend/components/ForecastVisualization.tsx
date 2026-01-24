import React, { useState, useEffect, useCallback } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Area, AreaChart, ComposedChart
} from 'recharts';
import { Calendar, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';

interface ForecastData {
  date: string;
  predicted_incidents: number;
  lower_bound: number;
  upper_bound: number;
  confidence_interval_width: number;
}

interface ForecastMetadata {
  model: string;
  training_data_points: number;
  trend_direction: string;
  confidence_level: number;
  significant_changepoints?: Array<{
    date: string;
    magnitude: number;
    direction: string;
  }>;
}

interface ForecastResult {
  location: string;
  location_type: string;
  model: string;
  forecast: ForecastData[];
  metadata: ForecastMetadata;
  error?: string;
}

interface Props {
  location: string;
  locationType?: 'state' | 'lga';
  model?: 'prophet' | 'arima' | 'ensemble';
  weeksAhead?: number;
}

const ForecastVisualization: React.FC<Props> = ({
  location,
  locationType = 'state',
  model = 'prophet',
  weeksAhead = 4
}) => {
  const [forecast, setForecast] = useState<ForecastResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState(model);

  const fetchForecast = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${apiUrl}/api/v1/forecasts/advanced/${location}?` +
        `location_type=${locationType}&model=${selectedModel}&weeks_ahead=${weeksAhead}`
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ForecastResult = await response.json();
      
      if (data.error) {
        setError(data.error);
      } else {
        setForecast(data);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load forecast');
    } finally {
      setLoading(false);
    }
  }, [location, locationType, selectedModel, weeksAhead]);

  useEffect(() => {
    fetchForecast();
  }, [fetchForecast]);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'increasing':
        return <TrendingUp className="text-red-500" size={20} />;
      case 'decreasing':
        return <TrendingDown className="text-green-500" size={20} />;
      default:
        return <Minus className="text-gray-500" size={20} />;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const prepareChartData = () => {
    if (!forecast) return [];

    return forecast.forecast.map((item) => ({
      date: formatDate(item.date),
      fullDate: item.date,
      predicted: item.predicted_incidents,
      lower: item.lower_bound,
      upper: item.upper_bound,
      range: [item.lower_bound, item.upper_bound]
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="text-red-500" size={20} />
          <span className="text-red-700 font-medium">Error loading forecast</span>
        </div>
        <p className="text-red-600 text-sm mt-2">{error}</p>
        <button
          onClick={fetchForecast}
          className="mt-3 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-md text-sm transition"
        >
          Retry
        </button>
      </div>
    );
  }

  if (!forecast) return null;

  const chartData = prepareChartData();
  const avgPrediction = chartData.reduce((sum, d) => sum + d.predicted, 0) / chartData.length;

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">
            {location} {locationType === 'state' ? 'State' : 'LGA'} - Conflict Forecast
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            {weeksAhead}-week forecast using {forecast.metadata.model} model
          </p>
        </div>

        {/* Model Selector */}
        <div className="flex space-x-2">
          {['prophet', 'arima', 'ensemble'].map((m) => (
            <button
              key={m}
              onClick={() => setSelectedModel(m as any)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition ${
                selectedModel === m
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Metadata Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-blue-700 text-sm font-medium">Avg. Predicted</span>
            <Calendar size={16} className="text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-blue-900 mt-2">
            {avgPrediction.toFixed(1)}
          </p>
          <p className="text-blue-600 text-xs mt-1">incidents/week</p>
        </div>

        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-purple-700 text-sm font-medium">Trend</span>
            {getTrendIcon(forecast.metadata.trend_direction)}
          </div>
          <p className="text-lg font-bold text-purple-900 mt-2 capitalize">
            {forecast.metadata.trend_direction}
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-4">
          <span className="text-green-700 text-sm font-medium">Training Data</span>
          <p className="text-2xl font-bold text-green-900 mt-2">
            {forecast.metadata.training_data_points}
          </p>
          <p className="text-green-600 text-xs mt-1">weeks</p>
        </div>

        <div className="bg-orange-50 rounded-lg p-4">
          <span className="text-orange-700 text-sm font-medium">Confidence</span>
          <p className="text-2xl font-bold text-orange-900 mt-2">
            {(forecast.metadata.confidence_level * 100).toFixed(0)}%
          </p>
          <p className="text-orange-600 text-xs mt-1">interval</p>
        </div>
      </div>

      {/* Forecast Chart */}
      <div className="border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          Forecast with Confidence Intervals
        </h3>
        <ResponsiveContainer width="100%" height={350}>
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
              label={{ value: 'Predicted Incidents', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '0.5rem',
                padding: '12px'
              }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '8px' }}
            />
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
            />
            
            {/* Confidence Interval Band */}
            <Area
              type="monotone"
              dataKey="range"
              fill="rgba(59, 130, 246, 0.1)"
              stroke="none"
              name="95% Confidence Interval"
            />
            
            {/* Lower Bound */}
            <Line
              type="monotone"
              dataKey="lower"
              stroke="#93c5fd"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="Lower Bound"
            />
            
            {/* Upper Bound */}
            <Line
              type="monotone"
              dataKey="upper"
              stroke="#93c5fd"
              strokeWidth={1}
              strokeDasharray="5 5"
              dot={false}
              name="Upper Bound"
            />
            
            {/* Predicted Values */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ fill: '#2563eb', r: 5 }}
              name="Predicted Incidents"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Forecast Table */}
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Week
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Predicted Incidents
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Confidence Interval
              </th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                Uncertainty
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {forecast.forecast.map((item, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Week {idx + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(item.date)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className="text-sm font-bold text-blue-600">
                    {item.predicted_incidents.toFixed(1)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-600">
                  {item.lower_bound.toFixed(1)} - {item.upper_bound.toFixed(1)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    item.confidence_interval_width < 5 
                      ? 'bg-green-100 text-green-800'
                      : item.confidence_interval_width < 10
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    ±{item.confidence_interval_width.toFixed(1)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Changepoints (if available) */}
      {forecast.metadata.significant_changepoints && forecast.metadata.significant_changepoints.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <h4 className="font-semibold text-yellow-900 mb-2">Significant Trend Changes Detected</h4>
          <div className="space-y-2">
            {forecast.metadata.significant_changepoints.map((cp, idx) => (
              <div key={idx} className="flex items-center space-x-3 text-sm">
                <span className="text-yellow-700">{formatDate(cp.date)}:</span>
                <span className={`font-medium ${
                  cp.direction === 'increase' ? 'text-red-600' : 'text-green-600'
                }`}>
                  {cp.direction === 'increase' ? '↑' : '↓'} {Math.abs(cp.magnitude).toFixed(2)} magnitude change
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ForecastVisualization;
