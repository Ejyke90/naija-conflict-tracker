import React from 'react';
import Link from 'next/link';
import { TrendingUp, Calendar, Target } from 'lucide-react';

interface ForecastTeaserProps {
  nextWeekPrediction: number;
  trend: number;
  confidence: number;
  previewData?: Array<{ date: string; value: number }>;
}

const MiniSparkline: React.FC<{ data: Array<{ date: string; value: number }> }> = ({ data }) => {
  if (!data || data.length === 0) return null;

  const max = Math.max(...data.map(d => d.value));
  const min = Math.min(...data.map(d => d.value));
  const range = max - min;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 100;
    const y = 100 - ((d.value - min) / range) * 100;
    return `${x},${y}`;
  }).join(' ');

  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" preserveAspectRatio="none" className="opacity-80">
      <polyline
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        points={points}
        vectorEffect="non-scaling-stroke"
      />
      <polygon
        fill="currentColor"
        fillOpacity="0.2"
        points={`0,100 ${points} 100,100`}
      />
    </svg>
  );
};

export const ForecastTeaser: React.FC<ForecastTeaserProps> = ({
  nextWeekPrediction,
  trend,
  confidence,
  previewData = []
}) => {
  return (
    <section className="bg-gradient-to-br from-purple-900 via-indigo-900 to-blue-900 rounded-xl p-8 text-white shadow-2xl">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-8">
        {/* Left Content */}
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-3">
            <TrendingUp className="text-purple-300" size={28} />
            <h3 className="text-2xl md:text-3xl font-bold">
              AI-Powered Conflict Forecasting
            </h3>
          </div>
          
          <p className="text-purple-200 mb-6 text-lg">
            Predict incidents up to 12 weeks ahead with {confidence}% accuracy using advanced machine learning
          </p>

          {/* Mini Preview Chart */}
          {previewData.length > 0 && (
            <div className="h-32 bg-white/10 rounded-lg mb-6 p-4 backdrop-blur-sm border border-white/20">
              <MiniSparkline data={previewData} />
            </div>
          )}

          {/* Quick Stats Grid */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center gap-2 mb-1">
                <Calendar size={16} className="text-purple-200" />
                <p className="text-sm text-purple-200">Next Week</p>
              </div>
              <p className="text-2xl font-bold">{nextWeekPrediction}</p>
              <p className="text-xs text-purple-200 mt-1">incidents</p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp size={16} className="text-purple-200" />
                <p className="text-sm text-purple-200">Trend</p>
              </div>
              <p className={`text-2xl font-bold ${trend > 0 ? 'text-red-300' : 'text-green-300'}`}>
                {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
              </p>
              <p className="text-xs text-purple-200 mt-1">vs last week</p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 border border-white/20">
              <div className="flex items-center gap-2 mb-1">
                <Target size={16} className="text-purple-200" />
                <p className="text-sm text-purple-200">Confidence</p>
              </div>
              <p className="text-2xl font-bold text-green-300">{confidence}%</p>
              <p className="text-xs text-purple-200 mt-1">accuracy</p>
            </div>
          </div>

          {/* Features List */}
          <div className="space-y-2 mb-6">
            <div className="flex items-center gap-2 text-sm text-purple-200">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Ensemble ML models (Prophet + ARIMA + LSTM)</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-purple-200">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>State-by-state predictions with confidence intervals</span>
            </div>
            <div className="flex items-center gap-2 text-sm text-purple-200">
              <svg className="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span>Real-time updates via WebSocket</span>
            </div>
          </div>
        </div>

        {/* Right CTA */}
        <div className="lg:text-right">
          <Link href="/forecasts">
            <button className="bg-white text-purple-900 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-purple-100 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1 duration-200 w-full lg:w-auto">
              View Full Forecast
              <span className="ml-2">→</span>
            </button>
          </Link>
          
          <p className="text-xs text-purple-200 mt-3">
            Interactive charts · Model comparison · Export to PDF
          </p>
        </div>
      </div>
    </section>
  );
};

export default ForecastTeaser;
