import React, { useState, useEffect } from 'react';
import { 
  Users, 
  TrendingUp, 
  TrendingDown,
  Minus,
  AlertTriangle, 
  MapPin, 
  Shield,
  Eye
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';

interface KidnappingStats {
  current_period: {
    victims: number;
    incidents: number;
    victims_change: number;
    incidents_change: number;
  };
  by_state: Array<{
    state: string;
    victims: number;
    incidents: number;
  }>;
  monthly_trends: Array<{
    month: string;
    victims: number;
    incidents: number;
  }>;
  last_updated: string;
}

export const KidnappingOverview: React.FC = () => {
  const [stats, setStats] = useState<KidnappingStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchKidnappingStats = async () => {
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
        
        const response = await fetch(`/api/v1/conflicts/stats/kidnapping`, {
          headers,
          signal: AbortSignal.timeout(10000) // 10s timeout
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        setStats(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching kidnapping stats:', err);
        setError(err instanceof Error ? err.message : 'Failed to load kidnapping statistics');
        // Set default values on error
        setStats({
          current_period: {
            victims: 0,
            incidents: 0,
            victims_change: 0,
            incidents_change: 0
          },
          by_state: [],
          monthly_trends: [],
          last_updated: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    fetchKidnappingStats();
    // Refresh every 5 minutes
    const interval = setInterval(fetchKidnappingStats, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getRiskLevel = (victims: number, incidents: number): 'low' | 'medium' | 'high' | 'critical' => {
    const score = incidents + (victims * 0.5);
    if (score > 50) return 'critical';
    if (score > 25) return 'high';
    if (score > 10) return 'medium';
    return 'low';
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-4 w-4" />;
    if (change < 0) return <TrendingDown className="h-4 w-4" />;
    return <Minus className="h-4 w-4" />;
  };

  const getTrendColor = (change: number) => {
    if (change > 0) return 'text-red-600';
    if (change < 0) return 'text-green-600';
    return 'text-gray-600';
  };

  const getRiskBadgeColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading kidnapping statistics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 text-red-800">
          <AlertTriangle className="h-5 w-5" />
          <p className="font-medium">Error loading kidnapping statistics: {error}</p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  const riskLevel = getRiskLevel(stats.current_period.victims, stats.current_period.incidents);

  return (
    <div className="space-y-6">
      {/* Header with Risk Level */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Shield className="h-6 w-6 text-purple-600" />
            Kidnapping Victims Analysis
          </h2>
          <p className="text-gray-600 mt-1">
            Comprehensive tracking of kidnapping incidents and victims across Nigeria
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge className={getRiskBadgeColor(riskLevel)}>
            {riskLevel === 'critical' ? '🔴 Critical Risk' :
             riskLevel === 'high' ? '🟠 High Risk' :
             riskLevel === 'medium' ? '🟡 Medium Risk' :
             '🟢 Low Risk'}
          </Badge>
          <div className="text-sm text-gray-500">
            Last updated: {new Date(stats.last_updated).toLocaleDateString()}
          </div>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Total Victims Card */}
        <Card className="border-l-4 border-l-purple-500 hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Total Victims</p>
                <p className="text-3xl font-semibold text-gray-900">{stats.current_period.victims}</p>
                <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
              </div>
              <Users className="h-5 w-5 text-purple-500" />
            </div>
            <div className={`flex items-center gap-1 mt-3 text-sm ${getTrendColor(stats.current_period.victims_change)}`}>
              {getTrendIcon(stats.current_period.victims_change)}
              <span className="font-medium">
                {stats.current_period.victims_change > 0 ? '+' : ''}{stats.current_period.victims_change}%
              </span>
              <span className="text-gray-500">vs previous period</span>
            </div>
          </CardContent>
        </Card>

        {/* Kidnapping Incidents Card */}
        <Card className="border-l-4 border-l-indigo-500 hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Kidnapping Incidents</p>
                <p className="text-3xl font-semibold text-gray-900">{stats.current_period.incidents}</p>
                <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
              </div>
              <AlertTriangle className="h-5 w-5 text-indigo-500" />
            </div>
            <div className={`flex items-center gap-1 mt-3 text-sm ${getTrendColor(stats.current_period.incidents_change)}`}>
              {getTrendIcon(stats.current_period.incidents_change)}
              <span className="font-medium">
                {stats.current_period.incidents_change > 0 ? '+' : ''}{stats.current_period.incidents_change}%
              </span>
              <span className="text-gray-500">vs previous period</span>
            </div>
          </CardContent>
        </Card>

        {/* Average Victims per Incident */}
        <Card className="border-l-4 border-l-blue-500 hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Avg Victims/Incident</p>
                <p className="text-3xl font-semibold text-gray-900">
                  {stats.current_period.incidents > 0 
                    ? (stats.current_period.victims / stats.current_period.incidents).toFixed(1)
                    : '0.0'
                  }
                </p>
                <p className="text-xs text-gray-500 mt-1">Victims per incident</p>
              </div>
              <Eye className="h-5 w-5 text-blue-500" />
            </div>
            <div className="mt-3 text-sm text-gray-600">
              <span className="font-medium">Analysis metric</span>
            </div>
          </CardContent>
        </Card>

        {/* Most Affected State */}
        <Card className="border-l-4 border-l-orange-500 hover:shadow-md transition-shadow">
          <CardContent className="pt-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Most Affected State</p>
                <p className="text-xl font-semibold text-gray-900">
                  {stats.by_state.length > 0 ? stats.by_state[0].state : 'N/A'}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {stats.by_state.length > 0 ? `${stats.by_state[0].victims} victims` : 'No data'}
                </p>
              </div>
              <MapPin className="h-5 w-5 text-orange-500" />
            </div>
            <div className="mt-3 text-sm text-gray-600">
              <span className="font-medium">Hotspot analysis</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Affected States */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">Most Affected States</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            States with highest kidnapping victim counts in the last 30 days
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {stats.by_state.slice(0, 5).map((state, index) => (
              <div key={state.state} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold ${
                    index === 0 ? 'bg-red-100 text-red-700' :
                    index === 1 ? 'bg-orange-100 text-orange-700' :
                    index === 2 ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {index + 1}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{state.state}</p>
                    <p className="text-sm text-gray-600">{state.incidents} incidents</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-semibold text-gray-900">{state.victims}</p>
                  <p className="text-sm text-gray-600">victims</p>
                </div>
              </div>
            ))}
            {stats.by_state.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <Shield className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                <p>No kidnapping data available for the selected period</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
