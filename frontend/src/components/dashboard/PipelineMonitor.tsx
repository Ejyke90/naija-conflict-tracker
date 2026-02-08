import React from 'react';
import { Activity, CheckCircle, Clock, AlertTriangle, Database, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { StatCard } from '@/components/ui/stat-card';
import { Progress } from '@/components/ui/progress';

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
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {/* Pipeline Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          title="Status"
          value={pipelineStatus.status}
          subtitle={`Last run: ${new Date(pipelineStatus.lastRun).toLocaleString()}`}
          icon={Activity}
          variant="primary"
        />

        <StatCard
          title="Sources"
          value={`${pipelineStatus.sourcesProcessed}/${pipelineStatus.totalSources}`}
          subtitle="News sources processed"
          icon={Database}
          variant="success"
        />

        <StatCard
          title="Events"
          value={pipelineStatus.eventsExtracted}
          subtitle="Verified conflict events"
          icon={CheckCircle}
          variant="primary"
        />
      </div>

      {/* Pipeline Steps */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Execution Steps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {pipelineSteps.map((step, index) => {
              const IconComponent = step.icon;
              const StatusIcon = getStatusIcon(step.status);

              return (
                <motion.div
                  key={step.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover:shadow-md transition-shadow">
                    <CardContent className="pt-4 pb-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-lg ${
                            step.status === 'completed' ? 'bg-green-100' :
                            step.status === 'running' ? 'bg-blue-100 animate-pulse' :
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
                            <div className="text-sm text-muted-foreground">
                              {step.items} / {step.total} items • {step.duration}
                            </div>
                          </div>
                        </div>

                        <Badge variant={
                          step.status === 'completed' ? 'default' :
                          step.status === 'running' ? 'outline' :
                          'secondary'
                        } className={`${
                          step.status === 'completed' ? 'bg-green-500 hover:bg-green-600' :
                          step.status === 'running' ? 'border-blue-500 text-blue-700' :
                          ''
                        }`}>
                          {step.status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Processing Metrics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Geocoding Success Rate</span>
                <span className="font-medium">{pipelineStatus.geocodingSuccess}%</span>
              </div>
              <Progress value={pipelineStatus.geocodingSuccess} className="h-2" />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Validation Pass Rate</span>
                <span className="font-medium">
                  {Math.round((pipelineStatus.validationPassed / pipelineStatus.eventsExtracted) * 100)}%
                </span>
              </div>
              <Progress
                value={(pipelineStatus.validationPassed / pipelineStatus.eventsExtracted) * 100}
                className="h-2"
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Health</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Redis Queue</span>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                Healthy
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Database Connection</span>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                Active
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">API Endpoints</span>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                Responsive
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Memory Usage</span>
              <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
                67%
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
};

export default PipelineMonitor;
