import React, { useState, useMemo, useEffect } from 'react';
import type { ComponentType } from 'react';
import type AIPredictionsType from './AIPredictions';
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
import { ConflictAnalysisReport } from '../reports/ConflictAnalysisReport';
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

  // Fetch dashboard stats from API with retry logic
  useEffect(() => {
    const fetchStats = async (retryCount = 0, maxRetries = 5) => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/analytics/dashboard-summary`, {
          signal: AbortSignal.timeout(10000) // 10s timeout
        });
        
        if (!response.ok) {
          // Backend might still be deploying, retry
          if (retryCount < maxRetries && (response.status === 404 || response.status === 500 || response.status === 502 || response.status === 503)) {
            const waitTime = Math.min(1000 * Math.pow(2, retryCount), 10000); // Exponential backoff, max 10s
            console.log(`Backend not ready (${response.status}), retrying in ${waitTime}ms... (${retryCount + 1}/${maxRetries})`);
            setError(`Waiting for backend deployment... (attempt ${retryCount + 1}/${maxRetries})`);
            await new Promise(resolve => setTimeout(resolve, waitTime));
            return fetchStats(retryCount + 1, maxRetries);
          }
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setStats({
          ...data,
          riskLevel: calculateRiskLevel(data.totalIncidents, data.fatalities)
        });
        setError(null);
      } catch (err) {
        if (retryCount < maxRetries && (err instanceof TypeError || (err as any)?.name === 'TimeoutError')) {
          // Network error or timeout, retry
          const waitTime = Math.min(1000 * Math.pow(2, retryCount), 10000);
          console.log(`Network error, retrying in ${waitTime}ms... (${retryCount + 1}/${maxRetries})`);
          setError(`Connecting to backend... (attempt ${retryCount + 1}/${maxRetries})`);
          await new Promise(resolve => setTimeout(resolve, waitTime));
          return fetchStats(retryCount + 1, maxRetries);
        }
        
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
    const interval = setInterval(() => fetchStats(), 5 * 60 * 1000);
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
        {/* Hero Section - CrisisWatch Inspired */}
        <div className="bg-white border-b border-gray-200">
          <div className="container mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-semibold text-gray-900 mb-2">Nigeria Conflict Tracker</h1>
                <p className="text-base text-gray-600">
                  Real-time monitoring and predictive analysis of conflicts across Nigeria
                </p>
              </div>
              <div className="flex items-center gap-3">
                {/* Live Indicator */}
                <div className="flex items-center gap-2 px-3 py-1.5 bg-white rounded border border-gray-300">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                  </span>
                  <span className="text-sm font-medium text-gray-700">Live</span>
                </div>

                {/* Risk Level Badge - CrisisWatch colors */}
                {stats && (
                  <div className={`px-4 py-1.5 rounded border ${
                    stats.riskLevel === 'critical' ? 'bg-red-50 border-red-200' :
                    stats.riskLevel === 'high' ? 'bg-orange-50 border-orange-200' :
                    stats.riskLevel === 'medium' ? 'bg-yellow-50 border-yellow-200' :
                    'bg-green-50 border-green-200'
                  }`}>
                    <span className={`text-sm font-semibold ${
                      stats.riskLevel === 'critical' ? 'text-red-700' :
                      stats.riskLevel === 'high' ? 'text-orange-700' :
                      stats.riskLevel === 'medium' ? 'text-yellow-600' :
                      'text-green-700'
                    }`}>
                      {stats.riskLevel === 'critical' ? '🔴 Critical Risk' :
                       stats.riskLevel === 'high' ? '🟠 High Risk' :
                       stats.riskLevel === 'medium' ? '🟡 Medium Risk' :
                       '🟢 Low Risk'}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Dashboard Content - CrisisWatch clean background */}
        <div className="bg-gray-50 min-h-screen">
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {/* Incident Card - Red for deteriorated situations */}
            <Card className="border-l-4 border-l-red-500 hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Total Incidents</p>
                    <p className="text-3xl font-semibold text-gray-900">{stats.totalIncidents}</p>
                    <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                  </div>
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                </div>
                {stats.totalIncidentsChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.totalIncidentsChange > 0 ? 'text-red-600' : 
                    stats.totalIncidentsChange < 0 ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {stats.totalIncidentsChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.totalIncidentsChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium">
                      {stats.totalIncidentsChange > 0 ? '+' : ''}{stats.totalIncidentsChange}%
                    </span>
                    <span className="text-gray-500">vs previous period</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Fatalities Card - Orange for high alert */}
            <Card className="border-l-4 border-l-orange-500 hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Fatalities</p>
                    <p className="text-3xl font-semibold text-gray-900">{stats.fatalities}</p>
                    <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                  </div>
                  <Users className="h-5 w-5 text-orange-500" />
                </div>
                {stats.fatalitiesChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.fatalitiesChange > 0 ? 'text-red-600' : 
                    stats.fatalitiesChange < 0 ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {stats.fatalitiesChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.fatalitiesChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium">
                      {stats.fatalitiesChange > 0 ? '+' : ''}{stats.fatalitiesChange}%
                    </span>
                    <span className="text-gray-500">vs previous period</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Hotspots Card - Yellow for tension */}
            <Card className="border-l-4 border-l-yellow-500 hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">Active Hotspots</p>
                    <p className="text-3xl font-semibold text-gray-900">{stats.activeHotspots}</p>
                    <p className="text-xs text-gray-500 mt-1">High risk areas</p>
                  </div>
                  <MapPin className="h-5 w-5 text-yellow-600" />
                </div>
                {stats.activeHotspotsChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.activeHotspotsChange > 0 ? 'text-red-600' : 
                    stats.activeHotspotsChange < 0 ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {stats.activeHotspotsChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.activeHotspotsChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium">
                      {stats.activeHotspotsChange > 0 ? '+' : ''}{stats.activeHotspotsChange}%
                    </span>
                    <span className="text-gray-500">vs previous period</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* States Card - Green for stability context */}
            <Card className="border-l-4 border-l-green-500 hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">States Affected</p>
                    <p className="text-3xl font-semibold text-gray-900">{stats.statesAffected}</p>
                    <p className="text-xs text-gray-500 mt-1">Out of {stats.totalStates || 36} states</p>
                  </div>
                  <Globe className="h-5 w-5 text-green-600" />
                </div>
                {stats.statesAffectedChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.statesAffectedChange > 0 ? 'text-red-600' : 
                    stats.statesAffectedChange < 0 ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {stats.statesAffectedChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.statesAffectedChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium">
                      {stats.statesAffectedChange > 0 ? '+' : ''}{stats.statesAffectedChange}%
                    </span>
                    <span className="text-gray-500">vs previous period</span>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

          {/* Main Dashboard Tabs - CrisisWatch Style */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full" aria-label="Dashboard Navigation">
            <TabsList className="inline-flex h-11 items-center justify-start rounded-none border-b border-gray-200 bg-transparent p-0 mb-6" role="tablist">
              <TabsTrigger 
                value="overview" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'overview'}>
                Overview
              </TabsTrigger>
              <TabsTrigger 
                value="mapping" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'mapping'}>
                Map
              </TabsTrigger>
              <TabsTrigger 
                value="pipeline" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'pipeline'}>
                Data Pipeline
              </TabsTrigger>
              <TabsTrigger 
                value="analytics" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'analytics'}>
                Analytics
              </TabsTrigger>
              <TabsTrigger 
                value="reports" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-gray-600 hover:text-gray-900 data-[state=active]:border-blue-600 data-[state=active]:text-blue-600 data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'reports'}>
                Reports
              </TabsTrigger>
            </TabsList>

          <TabsContent value="overview" className="space-y-8">
            {/* Hero Map Section - CrisisWatch map-first approach */}
            <div>
              <Card className="border border-gray-200 shadow-sm">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-semibold text-gray-900">Conflict Map Overview</CardTitle>
                      <CardDescription className="text-sm text-gray-600 mt-1">
                        Real-time geographic distribution of conflicts across Nigeria
                      </CardDescription>
                    </div>
                    <Globe className="w-5 h-5 text-gray-400" />
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="h-[650px] overflow-hidden">
                    <ConflictMap />
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Risk Assessment */}
              <div>
                <RiskAssessment />
              </div>

              {/* Monthly Trends */}
              <div className="lg:col-span-2">
                <TrendChart />
              </div>

              {/* Recent Incidents */}
              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-xl font-semibold text-gray-900">Recent Incidents</CardTitle>
                      <CardDescription className="text-sm text-gray-600 mt-1">
                        Latest verified events
                      </CardDescription>
                    </div>
                    <Calendar className="w-5 h-5 text-gray-400" />
                  </div>
                </CardHeader>
                <CardContent>
                  <RecentIncidents />
                </CardContent>
              </Card>
            </div>

            {/* State Analysis */}
            <Card className="border border-gray-200 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold text-gray-900">Conflicts by State</CardTitle>
                    <CardDescription className="text-sm text-gray-600 mt-1">
                      Comparative analysis across Nigerian states
                    </CardDescription>
                  </div>
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                </div>
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

          <TabsContent value="analytics" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TrendChart />
              <RiskAssessment />
            </div>
            
            <AIPredictions />
          </TabsContent>

          <TabsContent value="mapping" className="space-y-6">
            <Card className="border border-gray-200 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold text-gray-900">Advanced Geospatial Intelligence</CardTitle>
                    <CardDescription className="text-sm text-gray-600 mt-1">
                      Spatial analysis with hierarchical drill-down and diffusion metrics
                    </CardDescription>
                  </div>
                  <Globe className="w-5 h-5 text-gray-400" />
                </div>
              </CardHeader>
              <CardContent>
                <AdvancedConflictMap />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">Spatial Queries</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Proximity Search</p>
                    <p className="text-gray-600">Find conflicts within radius of any location</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Hierarchical Drill-down</p>
                    <p className="text-gray-600">State → LGA → Ward automatic transitions</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Real-time Analysis</p>
                    <p className="text-gray-600">Dynamic spatial queries and calculations</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">Diffusion Metrics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Grid Analysis</p>
                    <p className="text-gray-600">10km × 10km cell methodology</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">ACLED Standard</p>
                    <p className="text-gray-600">Percentage of cells experiencing violence</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Temporal Tracking</p>
                    <p className="text-gray-600">Monitor diffusion changes over time</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">Population Exposure</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Buffer Zones</p>
                    <p className="text-gray-600">2km and 5km radius analysis</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Risk Assessment</p>
                    <p className="text-gray-600">Population exposure calculations</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">WorldPop Integration</p>
                    <p className="text-gray-600">High-resolution population data</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="pipeline" className="space-y-6">
            <Card className="border border-gray-200 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold text-gray-900">Real-Time Data Pipeline Monitor</CardTitle>
                    <CardDescription className="text-sm text-gray-600 mt-1">
                      Automated pipeline processing 15+ news sources every 6 hours
                    </CardDescription>
                  </div>
                  <Activity className="w-5 h-5 text-gray-400" />
                </div>
              </CardHeader>
              <CardContent>
                <PipelineMonitor />
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">Scraping Engine</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Multi-Source Collection</p>
                    <p className="text-gray-600">15+ Nigerian news sources</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Automated Schedule</p>
                    <p className="text-gray-600">Every 6 hours</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Smart Filtering</p>
                    <p className="text-gray-600">Conflict keyword detection</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">Data Processing</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">NLP Analysis</p>
                    <p className="text-gray-600">Event classification & extraction</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Geocoding Pipeline</p>
                    <p className="text-gray-600">Location coordinate mapping</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Quality Validation</p>
                    <p className="text-gray-600">Multi-source verification</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border border-gray-200 shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold text-gray-900">System Health</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Real-Time Monitoring</p>
                    <p className="text-gray-600">Pipeline health tracking</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Alert System</p>
                    <p className="text-gray-600">Automatic anomaly detection</p>
                  </div>
                  <div className="text-sm">
                    <p className="font-medium text-gray-900">Performance Metrics</p>
                    <p className="text-gray-600">Resource usage optimization</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <ConflictAnalysisReport />
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

        {/* Footer - CrisisWatch minimalist style */}
        <div className="mt-12 pt-6 border-t border-gray-200 bg-white rounded-lg shadow-sm px-6 py-4">
          <div className="flex flex-col md:flex-row items-center justify-between text-sm text-gray-600 gap-4">
            <div>
              © {isClient ? new Date().getFullYear() : 2026} Nextier Nigeria Conflict Tracker
            </div>
            <div className="flex flex-col md:flex-row items-center gap-4">
              <span className="text-gray-500">Data sources: ACLED, news media, official reports</span>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-green-600 border-green-300 bg-green-50">
                  <Eye className="w-3 h-3 mr-1" />
                  Live
                </Badge>
                <span className="text-gray-500">
                  Updated: {isClient && stats?.lastUpdated ? new Date(stats.lastUpdated).toLocaleDateString() : 'Loading...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
        </div>
    </div>
    </div>
  );
};

export default ConflictDashboard;
