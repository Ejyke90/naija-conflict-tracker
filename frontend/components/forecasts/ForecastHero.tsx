import React from 'react';
import { Activity, TrendingUp, Target } from 'lucide-react';

interface ForecastHeroProps {
  selectedState: string;
  onStateChange: (state: string) => void;
  currentMonthSummary: {
    incidents: number;
    change: number;
    accuracy: number;
  };
  states: string[];
}

interface MetricCardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: 'up' | 'down';
}

const MetricCard: React.FC<MetricCardProps> = ({ label, value, icon, trend }) => {
  return (
    <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6 border border-white/20">
      <div className="flex items-center justify-between mb-2">
        <span className="text-purple-200 text-sm font-medium">{label}</span>
        <div className="text-white">{icon}</div>
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-white">{value}</span>
        {trend && (
          <span className={`text-sm ${trend === 'up' ? 'text-red-300' : 'text-green-300'}`}>
            {trend === 'up' ? '↑' : '↓'}
          </span>
        )}
      </div>
    </div>
  );
};

export const ForecastHero: React.FC<ForecastHeroProps> = ({
  selectedState,
  onStateChange,
  currentMonthSummary,
  states
}) => {
  return (
    <div className="bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 rounded-xl p-8 text-white shadow-2xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">Nigeria Conflict Forecasting</h1>
        <p className="text-purple-200">AI-powered conflict incident predictions with 92% accuracy</p>
      </div>

      {/* State Selector */}
      <div className="mb-8">
        <label className="block text-sm font-medium text-purple-200 mb-2">
          Select Region/State
        </label>
        <div className="relative">
          <select
            value={selectedState}
            onChange={(e) => onStateChange(e.target.value)}
            className="w-full md:w-96 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent backdrop-blur-sm appearance-none cursor-pointer"
          >
            <option value="Nigeria" className="bg-gray-900">All Nigeria</option>
            <optgroup label="High Risk States" className="bg-gray-900">
              {states.slice(0, 5).map((state) => (
                <option key={state} value={state} className="bg-gray-900">
                  {state}
                </option>
              ))}
            </optgroup>
            <optgroup label="Other States" className="bg-gray-900">
              {states.slice(5).map((state) => (
                <option key={state} value={state} className="bg-gray-900">
                  {state}
                </option>
              ))}
            </optgroup>
          </select>
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Current Month Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          label="Incidents This Month"
          value={currentMonthSummary.incidents}
          icon={<Activity size={24} />}
        />
        <MetricCard
          label="vs Last Month"
          value={`${currentMonthSummary.change > 0 ? '+' : ''}${currentMonthSummary.change}%`}
          icon={<TrendingUp size={24} />}
          trend={currentMonthSummary.change > 0 ? 'up' : 'down'}
        />
        <MetricCard
          label="Model Accuracy"
          value={`${currentMonthSummary.accuracy}%`}
          icon={<Target size={24} />}
        />
      </div>

      {/* Info Notice */}
      <div className="mt-6 p-4 bg-white/5 border border-white/10 rounded-lg">
        <p className="text-sm text-purple-200">
          <span className="font-semibold">💡 About Forecasts:</span> Predictions generated using ensemble ML models (Prophet, ARIMA, LSTM). 
          Confidence intervals represent 95% probability ranges. Models retrained daily with latest conflict data.
        </p>
      </div>
    </div>
  );
};

export default ForecastHero;
