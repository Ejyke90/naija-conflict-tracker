import React from 'react';
import { Brain, TrendingUp, AlertTriangle, MapPin } from 'lucide-react';

interface AIForesightCardProps {
  predictedRisk: number; // 0-100
  flaggedLGAs: string[];
  confidence: number; // 0-100
}

export const AIForesightCard: React.FC<AIForesightCardProps> = ({
  predictedRisk = 65,
  flaggedLGAs = ['Borno', 'Kaduna', 'Zamfara'],
  confidence = 87
}) => {
  // Calculate gauge rotation (0 = 0%, 180 = 100%)
  const gaugeRotation = (predictedRisk / 100) * 180 - 90;

  return (
    <div className="ai-insight-card">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 bg-indigo-500/20 rounded-lg flex items-center justify-center">
          <Brain className="w-6 h-6 text-indigo-400" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white">AI Foresight</h3>
          <p className="text-sm text-slate-400">Predicted Risk for Next 24h</p>
        </div>
      </div>

      {/* Radial Gauge */}
      <div className="flex items-center justify-center mb-6">
        <div className="risk-gauge">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
            {/* Background arc */}
            <path
              d="M 10 60 A 50 50 0 0 1 110 60"
              fill="none"
              stroke="rgba(71, 85, 105, 0.3)"
              strokeWidth="8"
              strokeLinecap="round"
            />
            {/* Risk arc */}
            <path
              d="M 10 60 A 50 50 0 0 1 110 60"
              fill="none"
              stroke={predictedRisk > 70 ? '#f43f5e' : predictedRisk > 40 ? '#f59e0b' : '#10b981'}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${(predictedRisk / 100) * 157} 157`}
              className="transition-all duration-1000 ease-out"
            />
            {/* Needle */}
            <line
              x1="60"
              y1="60"
              x2="60"
              y2="20"
              stroke="#e2e8f0"
              strokeWidth="2"
              strokeLinecap="round"
              transform={`rotate(${gaugeRotation} 60 60)`}
              className="transition-transform duration-1000 ease-out"
            />
            {/* Center dot */}
            <circle cx="60" cy="60" r="4" fill="#e2e8f0" />
          </svg>

          {/* Risk Value */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">{predictedRisk}%</div>
              <div className="text-xs text-slate-400">Risk Level</div>
            </div>
          </div>
        </div>
      </div>

      {/* Flagged LGAs */}
      <div className="mb-4">
        <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
          <MapPin className="w-4 h-4" />
          High-Risk Areas Flagged
        </h4>
        <div className="flex flex-wrap gap-2">
          {flaggedLGAs.map((lga, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-full text-xs font-medium"
            >
              {lga}
            </span>
          ))}
        </div>
      </div>

      {/* AI Confidence */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span className="text-sm text-slate-300">AI Confidence</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 transition-all duration-1000"
              style={{ width: `${confidence}%` }}
            />
          </div>
          <span className="text-sm font-mono text-emerald-400">{confidence}%</span>
        </div>
      </div>

      {/* Summary */}
      <div className="mt-4 p-3 bg-slate-800/50 rounded-lg border border-slate-700/30">
        <p className="text-xs text-slate-400 leading-relaxed">
          AI models predict {predictedRisk > 70 ? 'elevated' : predictedRisk > 40 ? 'moderate' : 'low'} conflict risk
          in {flaggedLGAs.length} regions. Monitor these areas closely for emerging threats.
        </p>
      </div>
    </div>
  );
};