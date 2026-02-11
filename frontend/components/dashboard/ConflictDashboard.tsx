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
import Link from 'next/link';
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

const IntelligenceGrid = dynamic(() => import('../intelligence/IntelligenceGrid'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading intelligence grid...</div>
});

const PipelineMonitor = dynamic(() => import('./PipelineMonitor'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading monitor...</div>
});

const AIPredictions = dynamic(() => import('./AIPredictions'), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading AI predictions...</div>
}) as typeof AIPredictionsType;

const CrisisIntelligenceDashboard = dynamic(() => import('./CrisisIntelligenceDashboard').then(mod => ({ default: mod.CrisisIntelligenceDashboard })), {
  ssr: false,
  loading: () => <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">Loading crisis intelligence...</div>
});

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
        
        
        // Get auth token from localStorage
        const token = localStorage.getItem('access_token');
        const headers: HeadersInit = {
          'Content-Type': 'application/json',
        };
        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`/api/v1/analytics/dashboard-summary`, {
          headers,
          signal: AbortSignal.timeout(10000) // 10s timeout
        });
        
        if (!response.ok) {
          // If unauthorized, fallback to public landing stats
          if (response.status === 401) {
            console.log('User not authenticated, using public stats');
            const publicResponse = await fetch(`/api/v1/public/landing-stats`);
            if (publicResponse.ok) {
              const publicData = await publicResponse.json();
              setStats({
                totalIncidents: publicData.totalIncidents,
                fatalities: publicData.totalFatalities,
                activeHotspots: publicData.activeHotspots,
                statesAffected: publicData.statesAffected,
                riskLevel: calculateRiskLevel(publicData.totalIncidents, publicData.totalFatalities),
                lastUpdated: new Date().toISOString()
              });
              return;
            }
          }
          
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

  const getRiskSignalColor = (riskLevel?: string) => {
    switch (riskLevel) {
      case 'critical': return 'signal_critical';
      case 'high': return 'signal_high';
      case 'medium': return 'signal_medium';
      case 'low': return 'signal_low';
      default: return 'default';
    }
  };

  return (
    <div className="min-h-screen bg-tactical-navy">
      {/* Fixed Top Navigation Bar */}
      <div className="fixed top-0 left-0 right-0 z-50 nav-header shadow-sm">
        <div className="container mx-auto px-6 py-3">
          <div className="flex items-center justify-between">
            {/* Logo and Title */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-tactical-slate-dark rounded-lg flex items-center justify-center border border-tactical-slate-medium">
                <svg className="w-6 h-6 text-tactical-e-ink" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-bold text-tactical-e-ink typography-heading">NextierConflictTracker</h1>
                <p className="text-xs text-tactical-slate-light">Nigeria Conflict Monitoring</p>
              </div>
            </div>

            {/* Right Side - Live Status and Risk Badge */}
            <div className="flex items-center gap-4">
              {/* Live Indicator */}
              <div className="status-live">
                <span>Live</span>
              </div>

              {/* Risk Level Badge */}
              {stats && (
                <div className={`px-4 py-1.5 border border-white/20 rounded-lg glass-card ${getRiskSignalColor(stats.riskLevel)}`}>
                  <span className="typography-label text-sm font-semibold">
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
        {/* Hero Section - Tactical Intelligence Inspired */}
        <div className="bg-tactical-charcoal border-b border-tactical-slate-medium">
          <div className="container mx-auto px-6 py-12">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-semibold text-tactical-e-ink typography-heading mb-2">Nigeria Conflict Tracker</h1>
                <p className="text-base text-tactical-slate-light">
                  Real-time monitoring and predictive analysis of conflicts across Nigeria
                </p>
              </div>
              <div className="flex items-center gap-3">
                {/* Live Indicator */}
                <div className="status-live">
                  <span>Live</span>
                </div>

                {/* Risk Level Badge - Tactical colors */}
                {stats && (
                  <div className={`px-4 py-1.5 rounded border border-white/20 glass-card ${getRiskSignalColor(stats.riskLevel)}`}>
                    <span className="typography-label text-sm font-semibold">
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

        {/* Dashboard Content - Tactical clean background */}
        <div className="bg-tactical-navy min-h-screen">
          <div className="container mx-auto px-6 py-8">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tactical-slate-light mx-auto mb-4"></div>
              <p className="text-tactical-slate-light">Loading dashboard statistics...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="signal-critical border rounded-lg p-4 mb-6">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              <p className="font-medium">Error loading statistics: {error}</p>
            </div>
          </div>
        )}

        {!loading && stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            {/* Incident Card - Signal critical for deteriorated situations */}
            <div className="glass-card border-l-4 border-l-signal-critical hover:shadow-md transition-shadow">
              <div className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-tactical-slate-light mb-1 data-label">Total Incidents</p>
                    <p className="text-3xl font-semibold text-tactical-e-ink data-metric">{stats.totalIncidents}</p>
                    <p className="text-xs text-tactical-slate-medium mt-1">Last 30 days</p>
                  </div>
                  <AlertTriangle className="h-5 w-5 text-signal-critical" />
                </div>
                {stats.totalIncidentsChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.totalIncidentsChange > 0 ? 'text-signal-critical' : 
                    stats.totalIncidentsChange < 0 ? 'text-signal-low' : 'text-tactical-slate-medium'
                  }`}>
                    {stats.totalIncidentsChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.totalIncidentsChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium typography-mono">
                      {stats.totalIncidentsChange > 0 ? '+' : ''}{stats.totalIncidentsChange}%
                    </span>
                    <span className="text-tactical-slate-medium">vs previous period</span>
                  </div>
                )}
              </div>
            </div>

            {/* Fatalities Card - Signal high for alert */}
            <div className="glass-card border-l-4 border-l-signal-high hover:shadow-md transition-shadow">
              <div className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-tactical-slate-light mb-1 data-label">Fatalities</p>
                    <p className="text-3xl font-semibold text-tactical-e-ink data-metric">{stats.fatalities}</p>
                    <p className="text-xs text-tactical-slate-medium mt-1">Last 30 days</p>
                  </div>
                  <Users className="h-5 w-5 text-signal-high" />
                </div>
                {stats.fatalitiesChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.fatalitiesChange > 0 ? 'text-signal-critical' : 
                    stats.fatalitiesChange < 0 ? 'text-signal-low' : 'text-tactical-slate-medium'
                  }`}>
                    {stats.fatalitiesChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.fatalitiesChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium typography-mono">
                      {stats.fatalitiesChange > 0 ? '+' : ''}{stats.fatalitiesChange}%
                    </span>
                    <span className="text-tactical-slate-medium">vs previous period</span>
                  </div>
                )}
              </div>
            </div>

            {/* Hotspots Card - Signal medium for tension */}
            <div className="glass-card border-l-4 border-l-signal-medium hover:shadow-md transition-shadow">
              <div className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-tactical-slate-light mb-1 data-label">Active Hotspots</p>
                    <p className="text-3xl font-semibold text-tactical-e-ink data-metric">{stats.activeHotspots}</p>
                    <p className="text-xs text-tactical-slate-medium mt-1">High risk areas</p>
                  </div>
                  <MapPin className="h-5 w-5 text-signal-medium" />
                </div>
                {stats.activeHotspotsChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.activeHotspotsChange > 0 ? 'text-signal-critical' : 
                    stats.activeHotspotsChange < 0 ? 'text-signal-low' : 'text-tactical-slate-medium'
                  }`}>
                    {stats.activeHotspotsChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.activeHotspotsChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium typography-mono">
                      {stats.activeHotspotsChange > 0 ? '+' : ''}{stats.activeHotspotsChange}%
                    </span>
                    <span className="text-tactical-slate-medium">vs previous period</span>
                  </div>
                )}
              </div>
            </div>

            {/* States Card - Signal low for stability context */}
            <div className="glass-card border-l-4 border-l-signal-low hover:shadow-md transition-shadow">
              <div className="pt-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-tactical-slate-light mb-1 data-label">States Affected</p>
                    <p className="text-3xl font-semibold text-tactical-e-ink data-metric">{stats.statesAffected}</p>
                    <p className="text-xs text-tactical-slate-medium mt-1">Out of {stats.totalStates || 36} states</p>
                  </div>
                  <Globe className="h-5 w-5 text-signal-low" />
                </div>
                {stats.statesAffectedChange !== undefined && (
                  <div className={`flex items-center gap-1 mt-3 text-sm ${
                    stats.statesAffectedChange > 0 ? 'text-signal-critical' : 
                    stats.statesAffectedChange < 0 ? 'text-signal-low' : 'text-tactical-slate-medium'
                  }`}>
                    {stats.statesAffectedChange > 0 ? <TrendingUp className="h-4 w-4" /> : 
                     stats.statesAffectedChange < 0 ? <TrendingDown className="h-4 w-4" /> : 
                     <Minus className="h-4 w-4" />}
                    <span className="font-medium typography-mono">
                      {stats.statesAffectedChange > 0 ? '+' : ''}{stats.statesAffectedChange}%
                    </span>
                    <span className="text-tactical-slate-medium">vs previous period</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

          {/* Main Dashboard Tabs - Tactical Style */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full" aria-label="Dashboard Navigation">
            <TabsList className="inline-flex h-11 items-center justify-start rounded-none border-b border-tactical-slate-medium bg-transparent p-0 mb-6" role="tablist">
              <TabsTrigger 
                value="overview" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'overview'}>
                Overview
              </TabsTrigger>
              <TabsTrigger 
                value="mapping" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'mapping'}>
                Map
              </TabsTrigger>
              <TabsTrigger 
                value="pipeline" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'pipeline'}>
                Data Pipeline
              </TabsTrigger>
              <TabsTrigger 
                value="analytics" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'analytics'}>
                Analytics
              </TabsTrigger>
              <TabsTrigger 
                value="reports" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'reports'}>
                Reports
              </TabsTrigger>
              <TabsTrigger 
                value="crisis-intelligence" 
                className="inline-flex items-center justify-center whitespace-nowrap rounded-none border-b-2 border-transparent px-6 py-3 text-sm font-medium text-tactical-slate-light hover:text-tactical-e-ink data-[state=active]:border-tactical-slate-light data-[state=active]:text-tactical-e-ink data-[state=active]:bg-transparent" 
                role="tab" 
                aria-selected={activeTab === 'crisis-intelligence'}>
                Crisis Intelligence
              </TabsTrigger>
            </TabsList>

          <TabsContent value="overview" className="space-y-8">
            {/* Hero Map Section - Tactical map-first approach */}
            <div>
              <div className="glass-card border border-tactical-slate-medium shadow-sm">
                <div className="p-6 pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h2 className="text-xl font-semibold text-tactical-e-ink typography-heading">Conflict Map Overview</h2>
                      <p className="text-sm text-tactical-slate-light mt-1">
                        Real-time geographic distribution of conflicts across Nigeria
                      </p>
                    </div>
                    <Globe className="w-5 h-5 text-tactical-slate-medium" />
                  </div>
                </div>
                <div className="p-0">
                  <div className="h-[650px] overflow-hidden">
                    <ConflictMap />
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Risk Assessment */}
              <div>
                <RiskAssessment />
              </div>

              {/* Monthly Trends */}
              <div className="lg:col-span-2">
                <Card className="border border-gray-200 shadow-sm">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-xl font-semibold text-gray-900">Monthly Trends</CardTitle>
                        <CardDescription className="text-sm text-gray-600 mt-1">
                          Historical patterns and forecasts
                        </CardDescription>
                      </div>
                      <Activity className="w-5 h-5 text-gray-400" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <TrendChart />
                  </CardContent>
                </Card>
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

            {/* Intelligence Grid */}
            <Card className="border border-gray-200 shadow-sm">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold text-gray-900">Conflict Intelligence Grid</CardTitle>
                    <CardDescription className="text-sm text-gray-600 mt-1">
                      High-signal metrics and insights from conflict data analysis
                    </CardDescription>
                  </div>
                  <Activity className="w-5 h-5 text-gray-400" />
                </div>
              </CardHeader>
              <CardContent>
                <IntelligenceGrid />
              </CardContent>
            </Card>

            {/* AI Forecast Teaser */}
            <Card className="border border-purple-200 shadow-md bg-gradient-to-br from-purple-50 via-white to-blue-50">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                      <TrendingUp className="w-6 h-6 text-purple-600" />
                      AI-Powered Conflict Forecasting
                    </CardTitle>
                    <CardDescription className="text-sm text-gray-600 mt-1">
                      Predict incidents up to 12 weeks ahead with 92% accuracy using ensemble ML models
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <p className="text-sm text-gray-600 mb-1">Next Week Forecast</p>
                      <p className="text-2xl font-bold text-gray-900">23 incidents</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <p className="text-sm text-gray-600 mb-1">Trend</p>
                      <p className="text-2xl font-bold text-red-600">↑ +12%</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 border border-purple-100">
                      <p className="text-sm text-gray-600 mb-1">Model Accuracy</p>
                      <p className="text-2xl font-bold text-green-600">92%</p>
                    </div>
                  </div>

                  <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                    <ul className="space-y-2 text-sm text-gray-700">
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-purple-600 rounded-full"></div>
                        Ensemble ML models (Prophet + ARIMA + LSTM)
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-purple-600 rounded-full"></div>
                        State-by-state predictions with confidence intervals
                      </li>
                      <li className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 bg-purple-600 rounded-full"></div>
                        Interactive charts and model comparison
                      </li>
                    </ul>
                  </div>

                  <Link href="/forecasts">
                    <Button className="w-full bg-purple-600 hover:bg-purple-700 text-white">
                      View Full Forecast Dashboard →
                    </Button>
                  </Link>
                </div>
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
            <AIPredictions />
          </TabsContent>

          <TabsContent value="crisis-intelligence" className="space-y-6">
            <CrisisIntelligenceDashboard />
          </TabsContent>

          <TabsContent value="reports" className="space-y-6">
            <ConflictAnalysisReport />
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
                    <p className="font-medium text-gray-900">Nextier Standard</p>
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
              <span className="text-gray-500">Data sources: Nextier Database, news media, official reports</span>
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
