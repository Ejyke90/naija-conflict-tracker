import React from 'react';
import { Alert } from '@/types/predictions';
import { AlertTriangle, TrendingUp, Activity, Eye } from 'lucide-react';

interface AlertCardProps {
  alert: Alert;
  onViewDetails?: () => void;
}

export function AlertCard({ alert, onViewDetails }: AlertCardProps) {
  const severityConfig = {
    critical: {
      bg: 'bg-red-50',
      border: 'border-red-300',
      text: 'text-red-700',
      badge: 'bg-red-100 text-red-800',
      icon: AlertTriangle,
    },
    high: {
      bg: 'bg-orange-50',
      border: 'border-orange-300',
      text: 'text-orange-700',
      badge: 'bg-orange-100 text-orange-800',
      icon: TrendingUp,
    },
    medium: {
      bg: 'bg-amber-50',
      border: 'border-amber-300',
      text: 'text-amber-700',
      badge: 'bg-amber-100 text-amber-800',
      icon: Activity,
    },
    low: {
      bg: 'bg-blue-50',
      border: 'border-blue-300',
      text: 'text-blue-700',
      badge: 'bg-blue-100 text-blue-800',
      icon: Eye,
    },
  };

  const config = severityConfig[alert.severity];
  const Icon = config.icon;

  return (
    <div
      className={`${config.bg} ${config.border} border rounded-lg p-4 transition-all hover:shadow-md`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${config.badge}`}>
          <Icon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div>
              <span
                className={`inline-block px-2 py-0.5 ${config.badge} text-xs font-semibold rounded uppercase`}
              >
                {alert.severity}
              </span>
              <span className="ml-2 text-sm font-semibold text-gray-900">
                {alert.location}
              </span>
            </div>
            <span className="text-xs text-gray-500 whitespace-nowrap">
              {new Date(alert.timestamp).toLocaleDateString()}
            </span>
          </div>

          <p className={`text-sm ${config.text} mb-2`}>{alert.message}</p>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-gray-600">
              <span>
                Confidence:{' '}
                <span className="font-semibold">{alert.confidence}%</span>
              </span>
              <span className="capitalize">Type: {alert.type}</span>
            </div>

            {onViewDetails && (
              <button
                onClick={onViewDetails}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                View Details →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
