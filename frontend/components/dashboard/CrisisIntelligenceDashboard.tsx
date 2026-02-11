import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Shield, 
  TrendingUp, 
  TrendingDown, 
  MapPin, 
  Users, 
  Activity,
  Target,
  Eye,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

interface CrisisMetrics {
  incidents: number;
  fatalities: number;
  displaced: number;
  injuries: number;
  crisis_index_score: number;
  risk_level: string;
}

interface StateHotspot {
  state: string;
  total_incidents: number;
  total_fatalities: number;
  total_displaced: number;
  crisis_index_score: number;
  risk_level: string;
  recent_incidents: number;
  recent_fatalities: number;
  crisis_types_count: number;
}

interface ActorThreat {
  actor: string;
  actor_type: string;
  event_type: string;
  incidents: number;
  total_fatalities: number;
  total_displaced: number;
  threat_score: number;
  threat_level: string;
  states_affected: number;
}

interface CrisisType {
  event_type: string;
  conflict_type: string;
  total_incidents: number;
  total_fatalities: number;
  total_displaced: number;
  states_affected: number;
  trend_direction: string;
  recent_incidents: number;
}

interface CrisisIntelligenceData {
  current_period: CrisisMetrics;
  state_hotspots: StateHotspot[];
  actor_threats: ActorThreat[];
  crisis_types: CrisisType[];
  monthly_trends: Array<{
    month: string;
    incidents: number;
    fatalities: number;
    displaced: number;
    crisis_score: number;
  }>;
  last_updated: string;
}

export const CrisisIntelligenceDashboard: React.FC = () => {
  const [data, setData] = useState<CrisisIntelligenceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchCrisisIntelligence();
  }, []);

  const fetchCrisisIntelligence = async () => {
    try {
      setLoading(true);
      
      const token = localStorage.getItem('access_token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      const response = await fetch(`/api/v1/crisis-intelligence/crisis-intelligence`, {
        headers,
        signal: AbortSignal.timeout(20000)
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      const result = await response.json();
      setData(result);
      setError(null);
    } catch (err) {
      console.error('Error fetching crisis intelligence:', err);
      setError(err instanceof Error ? err.message : 'Failed to load crisis intelligence');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    try {
      const token = localStorage.getItem('access_token');
      const headers: HeadersInit = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
      
      await fetch(`/api/v1/crisis-intelligence/refresh-views`, {
        method: 'POST',
        headers
      });
      
      await fetchCrisisIntelligence();
    } catch (err) {
      console.error('Error refreshing data:', err);
      setRefreshing(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CRITICAL': return 'bg-red-100 text-red-800 border-red-200';
      case 'HIGH': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'MEDIUM': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'LOW': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'INCREASING': return <TrendingUp className="h-4 w-4 text-red-600" />;
      case 'DECREASING': return <TrendingDown className="h-4 w-4 text-green-600" />;
      case 'STABLE': return <Activity className="h-4 w-4 text-blue-600" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-purple-600" />
            Crisis Intelligence Dashboard
          </CardTitle>
          <CardDescription className="text-sm text-gray-300">
            Multi-dimensional security threat analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-purple-600" />
            Crisis Intelligence Dashboard
          </CardTitle>
          <CardDescription className="text-sm text-gray-300">
            Multi-dimensional security threat analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-orange-600">
            <div className="text-center">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
              <p className="text-sm">Unable to load crisis intelligence</p>
              <Button onClick={fetchCrisisIntelligence} variant="outline" size="sm" className="mt-2">
                Retry
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) return null;

  return (
    <Card className="border-purple-200 shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-semibold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-purple-600" />
              Crisis Intelligence Dashboard
            </CardTitle>
            <CardDescription className="text-sm text-gray-300">
              Multi-dimensional security threat analysis and risk assessment
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={getRiskColor(data.current_period.risk_level)}>
              {data.current_period.risk_level} RISK
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
              disabled={refreshing}
              className="flex items-center gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Key Crisis Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-purple-600" />
                <span className="text-2xl font-bold text-purple-700">{data.current_period.incidents}</span>
              </div>
              <p className="text-sm text-gray-600">Total Incidents</p>
            </div>
            
            <div className="bg-red-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Users className="h-5 w-5 text-red-600" />
                <span className="text-2xl font-bold text-red-700">{data.current_period.fatalities}</span>
              </div>
              <p className="text-sm text-gray-600">Fatalities</p>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Eye className="h-5 w-5 text-orange-600" />
                <span className="text-2xl font-bold text-orange-700">{data.current_period.displaced}</span>
              </div>
              <p className="text-sm text-gray-600">Displaced</p>
            </div>
            
            <div className="bg-indigo-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Target className="h-5 w-5 text-indigo-600" />
                <span className="text-2xl font-bold text-indigo-700">{data.current_period.crisis_index_score.toFixed(0)}</span>
              </div>
              <p className="text-sm text-gray-600">Crisis Index</p>
            </div>
          </div>

          {/* Top State Hotspots */}
          {data.state_hotspots.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-white">Crisis Hotspots by State</h4>
              <div className="space-y-2">
                {data.state_hotspots.slice(0, 5).map((state, index) => (
                  <div key={state.state} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                        index === 0 ? 'bg-red-100 text-red-700' :
                        index === 1 ? 'bg-orange-100 text-orange-700' :
                        index === 2 ? 'bg-yellow-100 text-yellow-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium text-gray-900">{state.state}</span>
                      <Badge className={getRiskColor(state.risk_level)} variant="outline">
                        {state.risk_level}
                      </Badge>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-gray-900">{state.crisis_index_score.toFixed(0)}</span>
                      <span className="text-xs text-gray-500 ml-1">score</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Top Actor Threats */}
          {data.actor_threats.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-white">Threat Actors</h4>
              <div className="space-y-2">
                {data.actor_threats.slice(0, 3).map((actor, index) => (
                  <div key={actor.actor} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                        index === 0 ? 'bg-red-100 text-red-700' :
                        index === 1 ? 'bg-orange-100 text-orange-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <span className="text-sm font-medium text-gray-900">{actor.actor}</span>
                        <p className="text-xs text-gray-500">{actor.event_type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={getRiskColor(actor.threat_level)} variant="outline">
                        {actor.threat_level}
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">{actor.states_affected} states</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Crisis Types with Trends */}
          {data.crisis_types.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-white">Crisis Types & Trends</h4>
              <div className="space-y-2">
                {data.crisis_types.slice(0, 4).map((crisis) => (
                  <div key={crisis.event_type} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-900">{crisis.event_type}</span>
                      {getTrendIcon(crisis.trend_direction)}
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-gray-900">{crisis.total_incidents}</span>
                      <span className="text-xs text-gray-500 ml-1">incidents</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Expanded Details */}
          {expanded && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              {/* Full State Rankings */}
              {data.state_hotspots.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Complete State Risk Assessment</h4>
                  <div className="space-y-2">
                    {data.state_hotspots.map((state, index) => (
                      <div key={state.state} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                        <div className="flex items-center gap-3">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                            index === 0 ? 'bg-red-100 text-red-700' :
                            index === 1 ? 'bg-orange-100 text-orange-700' :
                            index === 2 ? 'bg-yellow-100 text-yellow-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {index + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{state.state}</p>
                            <p className="text-xs text-gray-500">{state.crisis_types_count} crisis types, {state.recent_incidents} recent</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-gray-900">{state.crisis_index_score.toFixed(0)}</p>
                          <p className="text-xs text-gray-500">crisis score</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Call to Action */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <div className="text-sm text-gray-600">
              Last updated: {new Date(data.last_updated).toLocaleString()}
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                size="sm"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? 'Show Less' : 'Show More'}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
