import React from 'react';
import { AlertTriangle, Shield, TrendingUp } from 'lucide-react';

const RiskAssessment: React.FC = () => {
  return (
    <div className="glass-card p-6">
      <h2 className="typography-heading text-xl text-tactical-e-ink mb-6">Risk Assessment</h2>

      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 signal-critical rounded-lg border border-red-500/20">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-3" />
            <div>
              <p className="typography-body font-medium text-tactical-e-ink">High Risk Zone</p>
              <p className="typography-body text-sm text-tactical-e-ink/70">North Central Region</p>
            </div>
          </div>
          <span className="typography-mono text-red-400 font-semibold">85%</span>
        </div>

        <div className="flex items-center justify-between p-4 signal-high rounded-lg border border-amber-500/20">
          <div className="flex items-center">
            <TrendingUp className="h-5 w-5 text-amber-400 mr-3" />
            <div>
              <p className="typography-body font-medium text-tactical-e-ink">Medium Risk Zone</p>
              <p className="typography-body text-sm text-tactical-e-ink/70">South West Region</p>
            </div>
          </div>
          <span className="typography-mono text-amber-400 font-semibold">62%</span>
        </div>

        <div className="flex items-center justify-between p-4 signal-low rounded-lg border border-green-500/20">
          <div className="flex items-center">
            <Shield className="h-5 w-5 text-green-400 mr-3" />
            <div>
              <p className="typography-body font-medium text-tactical-e-ink">Low Risk Zone</p>
              <p className="typography-body text-sm text-tactical-e-ink/70">South East Region</p>
            </div>
          </div>
          <span className="typography-mono text-green-400 font-semibold">23%</span>
        </div>
      </div>

      <div className="mt-6 p-4 glass-card border border-tactical-slate-light/30">
        <p className="typography-body text-sm text-tactical-e-ink/70">
          Risk assessment based on historical data, current trends, and geopolitical factors.
        </p>
      </div>
    </div>
  );
};

export default RiskAssessment;
