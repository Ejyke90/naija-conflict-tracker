import React from 'react';
import { Activity, CheckCircle, Clock, AlertTriangle, Database, Zap } from 'lucide-react';

const PipelineMonitor: React.FC = () => {
  // Sample pipeline data
  const pipelineStatus = {
    lastRun: '2026-01-20T10:30:00Z',
    status: 'running',
    sourcesProcessed: 12,
    totalSources: 15,
    articlesCollected: 247,
    eventsExtracted: 23,
    geocodingSuccess: 95.7,
    validationPassed: 21
  };

  const pipelineSteps = [
    {
      name: 'Data Collection',
      status: 'completed',
      duration: '2m 15s',
      items: pipelineStatus.sourcesProcessed,
      total: pipelineStatus.totalSources,
      icon: Database
    },
    {
      name: 'Content Processing',
      status: 'completed',
      duration: '1m 42s',
      items: pipelineStatus.articlesCollected,
      total: pipelineStatus.articlesCollected,
      icon: Activity
    },
    {
      name: 'NLP Analysis',
      status: 'running',
      duration: '45s',
      items: pipelineStatus.eventsExtracted,
      total: pipelineStatus.eventsExtracted,
      icon: Zap
    },
    {
      name: 'Geocoding',
      status: 'pending',
      duration: '-',
      items: Math.round(pipelineStatus.eventsExtracted * pipelineStatus.geocodingSuccess / 100),
      total: pipelineStatus.eventsExtracted,
      icon: CheckCircle
    },
    {
      name: 'Validation',
      status: 'pending',
      duration: '-',
      items: pipelineStatus.validationPassed,
      total: pipelineStatus.eventsExtracted,
      icon: CheckCircle
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600';
      case 'running': return 'text-blue-600';
      case 'pending': return 'text-gray-400';
      case 'failed': return 'text-red-600';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'running': return Clock;
      case 'pending': return Clock;
      case 'failed': return AlertTriangle;
      default: return Clock;
    }
  };

  return (
    <div className="space-y-6">
      {/* Pipeline Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <Activity className="w-6 h-6 text-blue-600 mr-2" />
            <span className="text-sm font-medium">Status</span>
          </div>
          <div className="text-2xl font-bold text-blue-600 capitalize">{pipelineStatus.status}</div>
          <div className="text-xs text-gray-500 mt-1">
            Last run: {new Date(pipelineStatus.lastRun).toLocaleString()}
          </div>
        </div>

        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <Database className="w-6 h-6 text-green-600 mr-2" />
            <span className="text-sm font-medium">Sources</span>
          </div>
          <div className="text-2xl font-bold text-green-600">
            {pipelineStatus.sourcesProcessed}/{pipelineStatus.totalSources}
          </div>
          <div className="text-xs text-gray-500 mt-1">News sources processed</div>
        </div>

        <div className="card text-center">
          <div className="flex items-center justify-center mb-2">
            <CheckCircle className="w-6 h-6 text-purple-600 mr-2" />
            <span className="text-sm font-medium">Events</span>
          </div>
          <div className="text-2xl font-bold text-purple-600">{pipelineStatus.eventsExtracted}</div>
          <div className="text-xs text-gray-500 mt-1">Verified conflict events</div>
        </div>
      </div>

      {/* Pipeline Steps */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Pipeline Execution Steps</h3>
        <div className="space-y-4">
          {pipelineSteps.map((step, index) => {
            const IconComponent = step.icon;
            const StatusIcon = getStatusIcon(step.status);

            return (
              <div key={step.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`p-2 rounded-lg ${
                    step.status === 'completed' ? 'bg-green-100' :
                    step.status === 'running' ? 'bg-blue-100' :
                    'bg-gray-100'
                  }`}>
                    <IconComponent className={`w-5 h-5 ${
                      step.status === 'completed' ? 'text-green-600' :
                      step.status === 'running' ? 'text-blue-600' :
                      'text-gray-400'
                    }`} />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="font-medium">{step.name}</h4>
                      <StatusIcon className={`w-4 h-4 ${getStatusColor(step.status)}`} />
                    </div>
                    <div className="text-sm text-gray-600">
                      {step.items} / {step.total} items • {step.duration}
                    </div>
                  </div>
                </div>

                <div className={`px-3 py-1 text-xs rounded-full ${
                  step.status === 'completed' ? 'bg-green-100 text-green-800' :
                  step.status === 'running' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {step.status}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Processing Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Geocoding Success Rate</span>
              <span className="text-sm font-medium">{pipelineStatus.geocodingSuccess}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full"
                style={{ width: `${pipelineStatus.geocodingSuccess}%` }}
              ></div>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Validation Pass Rate</span>
              <span className="text-sm font-medium">
                {Math.round((pipelineStatus.validationPassed / pipelineStatus.eventsExtracted) * 100)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-green-600 h-2 rounded-full"
                style={{ width: `${(pipelineStatus.validationPassed / pipelineStatus.eventsExtracted) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-4">System Health</h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Redis Queue</span>
              <span className="text-sm font-medium text-green-600">Healthy</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database Connection</span>
              <span className="text-sm font-medium text-green-600">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">API Endpoints</span>
              <span className="text-sm font-medium text-green-600">Responsive</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Memory Usage</span>
              <span className="text-sm font-medium text-yellow-600">67%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PipelineMonitor;
