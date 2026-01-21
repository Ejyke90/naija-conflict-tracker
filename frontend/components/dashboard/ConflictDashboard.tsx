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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { MarkdownReport } from './MarkdownReport';
import dynamic from 'next/dynamic';
import { StatsCard } from './StatsCard';

const ConflictMap = dynamic(() => import('../maps/ConflictMap'), {
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
  totalIncidentsChange?: number;
  fatalities: number;
  fatalitiesChange?: number;
  activeHotspots: number;
  activeHotspotsChange?: number;
  statesAffected: number;
  totalStates?: number;
  statesAffectedChange?: number;
  riskLevel?: 'low' | 'medium' | 'high' | 'critical';
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
  const [stats, setStats] = useState<ConflictStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handle client-side rendering to prevent hydration mismatches
  useEffect(() => {
    setIsClient(true);
    setCurrentTime(new Date().toISOString());
  }, []);

  // Fetch dashboard stats from API
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/conflicts/summary/dashboard`);
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setStats({
          ...data,
          riskLevel: calculateRiskLevel(data.totalIncidents, data.fatalities)
        });
        setError(null);
      } catch (err) {
        console.error('Error fetching dashboard stats:', err);
        setError(err instanceof Error ? err.message : 'Failed to load statistics');
        // Set default values on error
        setStats({
          totalIncidents: 0,
          totalIncidentsChange: 0,
          fatalities: 0,
          fatalitiesChange: 0,
          activeHotspots: 0,
          activeHotspotsChange: 0,
          statesAffected: 0,
          totalStates: 36,
          statesAffectedChange: 0,
          riskLevel: 'low',
          lastUpdated: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Refresh every 5 minutes
    const interval = setInterval(fetchStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  // Calculate risk level based on incidents and fatalities
  const calculateRiskLevel = (incidents: number, fatalities: number): 'low' | 'medium' | 'high' | 'critical' => {
    const score = incidents + (fatalities * 2);
    if (score > 1000) return 'critical';
    if (score > 500) return 'high';
    if (score > 100) return 'medium';
    return 'low';
  };

  const riskLevelColor = {
    low: 'risk-level-low',
    medium: 'risk-level-medium',
    high: 'risk-level-high',
    critical: 'risk-level-critical'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed Top Navigation Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="container mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">NextierConflictTracker</h1>
                <p className="text-xs text-gray-600">Nigeria Conflict Monitoring</p>
              </div>
            </div>

            {/* Right Side - Live Status and Risk Badge */}
            <div className="flex items-center gap-4">
              {/* Live Indicator */}
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 rounded-full border border-green-200">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                <span className="text-sm font-medium text-green-700">Live</span>
              </div>

              {/* Risk Level Badge */}
              {stats && (
                <div className={`px-4 py-1.5 border rounded-lg ${
                  stats.riskLevel === 'critical' ? 'bg-red-100 border-red-300' :
                  stats.riskLevel === 'high' ? 'bg-orange-100 border-orange-300' :
                  stats.riskLevel === 'medium' ? 'bg-yellow-100 border-yellow-300' :
                  'bg-green-100 border-green-300'
                }`}>
                  <span className={`text-sm font-semibold ${
                    stats.riskLevel === 'critical' ? 'text-red-700' :
                    stats.riskLevel === 'high' ? 'text-orange-700' :
                    stats.riskLevel === 'medium' ? 'text-yellow-700' :
                    'text-green-700'
                  }`}>
                    Risk Level: {stats.riskLevel?.toUpperCase()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add padding-top to account for fixed header */}
      <div className="pt-20">
        {/* Hero Section */}
        <div className="bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
          <div className="container mx-auto px-6 py-12">
            <div className="max-w-4xl">
              <h2 className="text-5xl font-bold mb-4">
                Nextier Nigeria Conflict Tracker
              </h2>
              <p className="text-xl text-blue-100 mb-6">
                AI-powered real-time monitoring and predictive analysis of conflicts across Nigeria
              </p>
              
              {/* AI Engine Badge */}
              <div className="inline-flex items-center gap-3 px-5 py-3 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                <div className="flex items-center justify-center w-8 h-8 bg-blue-500 rounded-lg">
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <span className="text-sm font-medium">AI Prediction Engine Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content */}
        <div className="container mx-auto px-6 py-8">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Loading dashboard statistics...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2 text-red-800">
              <AlertTriangle className="h-5 w-5" />
              <p className="font-medium">Error loading statistics: {error}</p>
            </div>
          </div>
        )}

        {!loading && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              title="Total Incidents"
              value={stats.totalIncidents}
              subtitle="Last 30 days"
              trend={stats.totalIncidentsChange || 0}
              trendLabel="vs previous period"
              icon="⚠️"
              gradientClass="bg-gradient-to-br from-red-500 to-orange-500"
            />

            <StatsCard
              title="Fatalities"
              value={stats.fatalities}
              subtitle="Last 30 days"
              trend={stats.fatalitiesChange || 0}
              trendLabel="vs previous period"
              icon="👥"
              gradientClass="bg-gradient-to-br from-purple-500 to-pink-500"
            />

            <StatsCard
              title="Active Hotspots"
              value={stats.activeHotspots}
              subtitle="High risk areas"
              trend={stats.activeHotspotsChange || 0}
              trendLabel="vs previous period"
              icon="📍"
              gradientClass="bg-gradient-to-br from-blue-500 to-cyan-500"
            />

            <StatsCard
              title="States Affected"
              value={stats.statesAffected}
              subtitle={`Out of ${stats.totalStates || 36} states`}
              trend={stats.statesAffectedChange || 0}
              trendLabel="vs previous period"
              icon="🗺️"
              gradientClass="bg-gradient-to-br from-green-500 to-emerald-500"
            />
          </div>
        )}

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
              <span>Last updated: {isClient && stats?.lastUpdated ? new Date(stats.lastUpdated).toLocaleString() : 'Loading...'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
};

export default ConflictDashboard;
