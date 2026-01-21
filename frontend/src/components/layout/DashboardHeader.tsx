import React from 'react';
import { Zap, Shield, Activity } from 'lucide-react';

export const DashboardHeader: React.FC = () => {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      {/* Animated background particles */}
      <div className="absolute inset-0 opacity-20">
        <div className="animate-pulse-slow absolute top-20 left-10 w-72 h-72 bg-blue-500 rounded-full blur-3xl"></div>
        <div className="animate-pulse-slow animation-delay-2000 absolute bottom-20 right-10 w-96 h-96 bg-purple-500 rounded-full blur-3xl"></div>
      </div>

      <div className="relative container mx-auto px-6 py-12">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-4 mb-4">
              <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-blue-200">
                Nextier Nigeria Conflict Tracker
              </h1>
              {/* Live indicator with pulse */}
              <span className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full border border-green-400/30">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-ping"></span>
                <span className="w-2 h-2 bg-green-400 rounded-full absolute"></span>
                <span className="text-sm font-medium">Live</span>
              </span>
            </div>

            <p className="text-lg text-blue-100 mb-6">
              AI-powered real-time monitoring and predictive analysis of conflicts across Nigeria
            </p>

            {/* AI Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-lg border border-white/20">
              <Zap className="w-5 h-5 text-blue-300 animate-spin-slow" />
              <span className="text-sm font-medium">AI Prediction Engine Active</span>
            </div>
          </div>

          {/* Risk Level Badge - Prominent */}
          <div className="bg-red-500/20 border-2 border-red-400 rounded-2xl px-8 py-6 backdrop-blur-sm">
            <div className="text-xs uppercase tracking-wide text-red-200 mb-2">Current Risk Level</div>
            <div className="text-5xl font-bold text-red-300 mb-2">HIGH</div>
            <div className="text-sm text-red-200">Enhanced monitoring active</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardHeader;
