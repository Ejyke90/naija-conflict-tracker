import React, { useState, useMemo, useEffect } from 'react';
import type { ComponentType } from 'react';
import type AIPredictionsType from './AIPredictions';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  TrendingUp, 
  TrendingDown,
  Minus,
  AlertTriangle, 
  MapPin, 
  Users, 
  Calendar,
  Download,
  Filter,
  Eye,
  BarChart3,
  Globe,
  Activity,
  Flag
} from 'lucide-react';
import * as d3 from 'd3';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MarkdownReport } from './MarkdownReport';
import dynamic from 'next/dynamic';
import { DashboardHeader } from '../layout/DashboardHeader';
import { StatsCard } from './StatsCard';

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

const AIPredictions = dynamic(() => import('./AIPredictions'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading AI predictions...</div>
}) as typeof AIPredictionsType;

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
    low: 'risk-level-low',
    medium: 'risk-level-medium',
    high: 'risk-level-high',
    critical: 'risk-level-critical'
  };

  return (
    <div className="min-h-screen bg-transparent">
      {/* Hero Header Section */}
      <DashboardHeader />

      {/* Stats Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Incidents"
            value={stats.totalIncidents}
            subtitle="Last 30 days"
            trend={12}
            trendLabel="vs previous period"
            icon="⚠️"
            gradientClass="bg-gradient-to-br from-red-500 to-orange-500"
          />

          <StatsCard
            title="Fatalities"
            value={stats.fatalities}
            subtitle="Last 30 days"
            trend={-8}
            trendLabel="vs previous period"
            icon="👥"
            gradientClass="bg-gradient-to-br from-purple-500 to-pink-500"
          />

          <StatsCard
            title="Active Hotspots"
            value={stats.activeHotspots}
            subtitle="High risk areas"
            trend={5}
            trendLabel="vs previous period"
            icon="📍"
            gradientClass="bg-gradient-to-br from-amber-500 to-yellow-500"
          />

          <StatsCard
            title="States Affected"
            value={stats.statesAffected}
            subtitle="Out of 36 states"
            trend={0}
            trendLabel="Stable vs previous period"
            icon="🗺️"
            gradientClass="bg-gradient-to-br from-blue-500 to-cyan-500"
          />
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full" aria-label="Dashboard Navigation">
          <TabsList className="grid w-full grid-cols-5 mb-8" role="tablist">
            <TabsTrigger value="overview" className="transition-all duration-300" role="tab" aria-selected={activeTab === 'overview'}>Overview</TabsTrigger>
            <TabsTrigger value="mapping" className="transition-all duration-300" role="tab" aria-selected={activeTab === 'mapping'}>Advanced Mapping</TabsTrigger>
            <TabsTrigger value="pipeline" className="transition-all duration-300" role="tab" aria-selected={activeTab === 'pipeline'}>Pipeline Monitor</TabsTrigger>
            <TabsTrigger value="analytics" className="transition-all duration-300" role="tab" aria-selected={activeTab === 'analytics'}>Analytics</TabsTrigger>
            <TabsTrigger value="reports" className="transition-all duration-300" role="tab" aria-selected={activeTab === 'reports'}>Reports</TabsTrigger>
          </TabsList>

          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
            >

          <TabsContent value="overview" className="space-y-12">
            {/* Hero Map Section */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <Card className="card mb-12">
                <CardHeader className="pb-4">
                  <CardTitle className="flex items-center text-2xl">
                    <Globe className="w-6 h-6 mr-3 text-slate-700" />
                    Conflict Map Overview
                  </CardTitle>
                  <CardDescription className="text-base">
                    Real-time geographic distribution of conflicts with interactive risk assessment
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="h-[600px] rounded-b-2xl overflow-hidden">
                    <ConflictMap />
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Risk Assessment */}
              <motion.div 
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
              >
                <RiskAssessment />
              </motion.div>

              {/* Monthly Trends */}
              <motion.div 
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="lg:col-span-2 card"
              >
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-slate-700" />
                    Monthly Conflict Trends
                  </CardTitle>
                  <CardDescription>
                    Interactive visualization with historical patterns and predictions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <TrendChart />
                </CardContent>
              </motion.div>

              {/* Recent Incidents */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.6 }}
                className="card"
              >
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="w-5 h-5 mr-2 text-purple-600" />
                    Recent Incidents
                  </CardTitle>
                  <CardDescription>
                    Latest verified conflict events with details
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <RecentIncidents />
                </CardContent>
              </motion.div>
            </div>

            {/* State Analysis */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="card"
            >
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-indigo-600" />
                  Conflicts by State
                </CardTitle>
                <CardDescription>
                  Comparative analysis across Nigerian states with interactive insights
                </CardDescription>
              </CardHeader>
              <CardContent>
                <StateAnalysis />
              </CardContent>
            </motion.div>
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

          <TabsContent value="analytics" className="space-y-6">
            <AIPredictions />
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

          <TabsContent value="reports" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Conflict Analysis Report
                </CardTitle>
                <CardDescription>
                  Comprehensive analysis of conflict trends and patterns in Nigeria
                </CardDescription>
              </CardHeader>
              <CardContent>
                <MarkdownReport content={`# Nigeria Conflict Analysis Report
## Executive Summary

This report provides a comprehensive analysis of conflict incidents across Nigeria for the period January 2026. The analysis covers spatial distribution, temporal patterns, and key drivers of violence.

## Key Findings

### Incident Overview
- **Total Incidents**: 1,234 verified conflict events
- **Fatalities**: 567 reported deaths
- **States Affected**: 18 out of 36 states
- **Active Hotspots**: 23 high-risk areas identified

### Regional Distribution

| Region | Incidents | Fatalities | Risk Level |
|--------|-----------|------------|------------|
| North West | 456 | 234 | Critical |
| North East | 345 | 189 | High |
| South South | 234 | 87 | Medium |
| North Central | 123 | 45 | High |
| South West | 45 | 12 | Low |
| South East | 31 | 0 | Low |

### Temporal Trends

#### Monthly Distribution
The conflict incidents show seasonal patterns with peaks during:
- Dry season months (November - March)
- Election periods
- Religious holidays

#### Weekly Patterns
- Higher incidents on weekends
- Reduced activity during weekdays in urban areas

## Risk Assessment

### High-Risk Areas
1. **Kaduna State**: Inter-communal clashes
2. **Borno State**: Insurgency-related activities
3. **Rivers State**: Political violence
4. **Zamfara State**: Banditry and kidnapping

### Emerging Threats
- Climate-induced migration conflicts
- Cyber-enabled criminal activities
- Resource scarcity disputes

## Recommendations

### Immediate Actions
1. Enhance community policing in high-risk areas
2. Improve intelligence sharing between security agencies
3. Implement early warning systems for vulnerable communities

### Long-term Strategies
1. Address root causes: poverty, unemployment, and inequality
2. Strengthen conflict resolution mechanisms
3. Promote inter-community dialogue and reconciliation

## Data Sources
- ACLED (Armed Conflict Location & Event Data Project)
- Nigerian news media monitoring
- Official government reports
- Community-based reporting networks

---
*Report generated on ${new Date().toLocaleDateString()} by Nextier Conflict Monitoring System*
`} />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Report Options</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="w-4 h-4 mr-2" />
                    Export as PDF
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="w-4 h-4 mr-2" />
                    Export as CSV
                  </Button>
                  <Button variant="outline" className="w-full justify-start">
                    <Download className="w-4 h-4 mr-2" />
                    Export as JSON
                  </Button>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Custom Reports</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-gray-500">
                    <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p>Advanced report builder coming soon</p>
                    <p className="text-sm mt-2">Create custom reports with specific filters and time ranges</p>
                  </div>
                </CardContent>
              </Card>
            </div>
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

            </motion.div>
          </AnimatePresence>
        </Tabs>

        {/* Footer */}
        <div className="mt-12 pt-8 border-t border-white/20 bg-white/50 backdrop-blur-sm rounded-t-xl">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              © {isClient ? new Date().getFullYear() : 2026} Nextier Nigeria Conflict Tracker. Built for peace and security.
            </div>
            <div className="flex items-center space-x-4">
              <span>Data sources: ACLED, news media, official reports, and community inputs</span>
              <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
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
