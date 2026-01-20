import React, { useState, useMemo, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  AlertTriangle, 
  MapPin, 
  Users, 
  Calendar,
  Download,
  Filter,
  Eye,
  BarChart3,
  Globe
} from 'lucide-react';
import * as d3 from 'd3';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Activity } from 'lucide-react';
import dynamic from 'next/dynamic';

const ConflictMap = dynamic(() => import('./ConflictMap'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading map...</div>
});

const AdvancedConflictMap = dynamic(() => import('../mapping/AdvancedConflictMap'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading advanced map...</div>
});
// Dynamic imports for components that may cause hydration issues
const TrendChart = dynamic(() => import('./TrendChart'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading chart...</div>
});

const RiskAssessment = dynamic(() => import('./RiskAssessment'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading assessment...</div>
});

const RecentIncidents = dynamic(() => import('./RecentIncidents'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading incidents...</div>
});

const StateAnalysis = dynamic(() => import('./StateAnalysis'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading analysis...</div>
});

const PipelineMonitor = dynamic(() => import('./PipelineMonitor'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading monitor...</div>
});

interface ConflictStats {
  totalIncidents: number;
  fatalities: number;
  activeHotspots: number;
  statesAffected: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  lastUpdated: string;
}

interface ConflictDashboardProps {
  data?: any;
}

export const ConflictDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [currentTime, setCurrentTime] = useState<string>('');
  const [isClient, setIsClient] = useState(false);

  // Handle client-side rendering to prevent hydration mismatches
  useEffect(() => {
    setIsClient(true);
    setCurrentTime(new Date().toISOString());
  }, []);

  // Mock data - replace with real API data
  const stats: ConflictStats = {
    totalIncidents: 1234,
    fatalities: 567,
    activeHotspots: 23,
    statesAffected: 18,
    riskLevel: 'high',
    lastUpdated: currentTime || '2026-01-19T00:00:00.000Z'
  };

  const riskLevelColor = {
    low: 'bg-green-100 text-green-800 border-green-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    high: 'bg-orange-100 text-orange-800 border-orange-200',
    critical: 'bg-red-100 text-red-800 border-red-200'
  };

  const statCards = [
    {
      title: 'Total Incidents',
      value: stats.totalIncidents.toLocaleString(),
      change: '+12%',
      trend: 'up',
      icon: AlertTriangle,
      description: 'Last 30 days',
      color: 'text-blue-600'
    },
    {
      title: 'Fatalities',
      value: stats.fatalities.toLocaleString(),
      change: '-8%',
      trend: 'down',
      icon: Users,
      description: 'Last 30 days',
      color: 'text-red-600'
    },
    {
      title: 'Active Hotspots',
      value: stats.activeHotspots.toString(),
      change: '+5',
      trend: 'up',
      icon: MapPin,
      description: 'High risk areas',
      color: 'text-orange-600'
    },
    {
      title: 'States Affected',
      value: `${stats.statesAffected}/36`,
      change: 'Stable',
      trend: 'stable',
      icon: Globe,
      description: 'Out of 36 states',
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Nextier Nigeria Conflict Tracker
              </h1>
              <p className="mt-2 text-gray-600">
                Real-time monitoring and analysis of conflicts across Nigeria
              </p>
            </div>
            
            <div className="flex items-center space-x-4">
              <Badge 
                className={`${riskLevelColor[stats.riskLevel]} border`}
                variant="outline"
              >
                Risk Level: {stats.riskLevel.toUpperCase()}
              </Badge>
              
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Export Data
              </Button>
              
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {statCards.map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">
                        {stat.title}
                      </p>
                      <p className="text-3xl font-bold text-gray-900 mt-2">
                        {stat.value}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        {stat.description}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg bg-gray-50 ${stat.color}`}>
                      <stat.icon className="w-6 h-6" />
                    </div>
                  </div>
                  
                  <div className="mt-4 flex items-center">
                    <span className={`text-sm font-medium ${
                      stat.trend === 'up' ? 'text-red-600' : 
                      stat.trend === 'down' ? 'text-green-600' : 
                      'text-gray-600'
                    }`}>
                      {stat.change}
                    </span>
                    <span className="text-sm text-gray-500 ml-2">
                      vs previous period
                    </span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="mapping">Advanced Mapping</TabsTrigger>
            <TabsTrigger value="pipeline">Pipeline Monitor</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Conflict Map */}
              <Card className="lg:col-span-1">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MapPin className="w-5 h-5 mr-2" />
                    Conflict Map
                  </CardTitle>
                  <CardDescription>
                    Geographic distribution of conflicts with risk assessment
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ConflictMap />
                </CardContent>
              </Card>

              {/* Risk Assessment */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Risk Assessment
                  </CardTitle>
                  <CardDescription>
                    Current risk levels across monitored areas
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <RiskAssessment />
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Monthly Trends */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Monthly Conflict Trends
                  </CardTitle>
                  <CardDescription>
                    Interactive chart visualization with Recharts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TrendChart />
                </CardContent>
              </Card>

              {/* Recent Incidents */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="w-5 h-5 mr-2" />
                    Recent Incidents
                  </CardTitle>
                  <CardDescription>
                    Latest verified conflict events
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <RecentIncidents />
                </CardContent>
              </Card>
            </div>

            {/* State Analysis */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Conflicts by State
                </CardTitle>
                <CardDescription>
                  Comparative analysis across Nigerian states
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StateAnalysis />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="map">
            <Card>
              <CardHeader>
                <CardTitle>Interactive Conflict Map</CardTitle>
                <CardDescription>
                  Advanced mapping with layers, clustering, and spatial analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="h-[600px]">
                  <ConflictMap fullscreen />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Trend Analysis</CardTitle>
                </CardHeader>
                <CardContent>
                  <TrendChart />
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Predictive Models</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-gray-500">
                    Advanced analytics coming soon
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="mapping" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Globe className="w-5 h-5 mr-2" />
                  Advanced Geospatial Intelligence
                </CardTitle>
                <CardDescription>
                  ACLED-level spatial analysis with hierarchical drill-down, diffusion metrics, and buffer zone analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <AdvancedConflictMap />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Spatial Queries</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">Proximity Search</p>
                    <p className="text-gray-600">Find conflicts within radius of any location</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Hierarchical Drill-down</p>
                    <p className="text-gray-600">State → LGA → Ward automatic transitions</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Real-time Analysis</p>
                    <p className="text-gray-600">Dynamic spatial queries and calculations</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Diffusion Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">Grid Analysis</p>
                    <p className="text-gray-600">10km × 10km cell methodology</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">ACLED Standard</p>
                    <p className="text-gray-600">Percentage of cells experiencing violence</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Temporal Tracking</p>
                    <p className="text-gray-600">Monitor diffusion changes over time</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Population Exposure</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">Buffer Zones</p>
                    <p className="text-gray-600">2km and 5km radius analysis</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Risk Assessment</p>
                    <p className="text-gray-600">Population exposure calculations</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">WorldPop Integration</p>
                    <p className="text-gray-600">High-resolution population data</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="pipeline" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="w-5 h-5 mr-2" />
                  Real-Time Data Pipeline Monitor
                </CardTitle>
                <CardDescription>
                  Monitor automated "Scrape-Clean-Verify" pipeline processing 15+ news sources every 6 hours
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PipelineMonitor />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Scraping Engine</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">Multi-Source Collection</p>
                    <p className="text-gray-600">15+ Nigerian news sources</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Automated Schedule</p>
                    <p className="text-gray-600">Every 6 hours</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Smart Filtering</p>
                    <p className="text-gray-600">Conflict keyword detection</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Data Processing</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">NLP Analysis</p>
                    <p className="text-gray-600">Event classification & extraction</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Geocoding Pipeline</p>
                    <p className="text-gray-600">Location coordinate mapping</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Quality Validation</p>
                    <p className="text-gray-600">Multi-source verification</p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">System Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium">Real-Time Monitoring</p>
                    <p className="text-gray-600">Pipeline health tracking</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Alert System</p>
                    <p className="text-gray-600">Automatic anomaly detection</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium">Performance Metrics</p>
                    <p className="text-gray-600">Resource usage optimization</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reports">
            <Card>
              <CardHeader>
                <CardTitle>Conflict Reports</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  Report generation system coming soon
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts">
            <Card>
              <CardHeader>
                <CardTitle>Early Warning System</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12 text-gray-500">
                  Alert system coming soon
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              © {isClient ? new Date().getFullYear() : 2026} Nextier Nigeria Conflict Tracker. Built for peace and security.
            </div>
            <div className="flex items-center space-x-4">
              <span>Data sources: ACLED, news media, official reports, and community inputs</span>
              <Badge variant="outline" className="text-green-600 border-green-200">
                <Eye className="w-3 h-3 mr-1" />
                Live
              </Badge>
              <span>Last updated: {isClient && stats.lastUpdated ? new Date(stats.lastUpdated).toLocaleString() : 'Loading...'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConflictDashboard;
