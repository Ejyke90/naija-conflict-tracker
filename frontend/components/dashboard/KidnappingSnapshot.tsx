import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  Users, 
  TrendingUp, 
  AlertTriangle, 
  MapPin,
  ArrowRight
} from 'lucide-react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

interface KidnappingSnapshotData {
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
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  last_updated: string;
}

export const KidnappingSnapshot: React.FC = () => {
  const [data, setData] = useState<KidnappingSnapshotData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchKidnappingData = async () => {
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
          signal: AbortSignal.timeout(15000) // 15s timeout for snapshot
        });
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        
        // Calculate risk level
        const riskLevel = getRiskLevel(result.current_period.victims, result.current_period.incidents);
        
        setData({
          ...result,
          risk_level: riskLevel
        });
        setError(null);
      } catch (err) {
        console.error('Error fetching kidnapping snapshot:', err);
        setError(err instanceof Error ? err.message : 'Failed to load kidnapping data');
        // Set default values on error
        setData({
          current_period: {
            victims: 0,
            incidents: 0,
            victims_change: 0,
            incidents_change: 0
          },
          by_state: [],
          risk_level: 'low',
          last_updated: new Date().toISOString()
        });
      } finally {
        setLoading(false);
      }
    };

    fetchKidnappingData();
  }, []);

  const getRiskLevel = (victims: number, incidents: number): 'low' | 'medium' | 'high' | 'critical' => {
    const score = incidents + (victims * 0.5);
    if (score > 50) return 'critical';
    if (score > 25) return 'high';
    if (score > 10) return 'medium';
    return 'low';
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

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="h-4 w-4 text-red-600" />;
    if (change < 0) return <TrendingUp className="h-4 w-4 text-green-600 transform rotate-180" />;
    return <div className="h-4 w-4 bg-gray-400 rounded-full" />;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Shield className="h-5 w-5 text-purple-600" />
            Kidnapping Analytics
          </CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Real-time kidnapping incident tracking
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
          <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Shield className="h-5 w-5 text-purple-600" />
            Kidnapping Analytics
          </CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Real-time kidnapping incident tracking
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32 text-orange-600">
            <div className="text-center">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
              <p className="text-sm">Unable to load data</p>
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
            <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <Shield className="h-5 w-5 text-purple-600" />
              Kidnapping Analytics
            </CardTitle>
            <CardDescription className="text-sm text-gray-600">
              Real-time kidnapping incident tracking and analysis
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={getRiskBadgeColor(data.risk_level)}>
              {data.risk_level === 'critical' ? '🔴 Critical' :
               data.risk_level === 'high' ? '🟠 High' :
               data.risk_level === 'medium' ? '🟡 Medium' :
               '🟢 Low'} Risk
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <Users className="h-5 w-5 text-purple-600" />
                <span className="text-2xl font-bold text-purple-700">{data.current_period.victims}</span>
              </div>
              <p className="text-sm text-gray-600">Total Victims</p>
              <div className="flex items-center justify-center gap-1 mt-1">
                {getTrendIcon(data.current_period.victims_change)}
                <span className="text-xs text-gray-500">
                  {data.current_period.victims_change > 0 ? '+' : ''}{data.current_period.victims_change}%
                </span>
              </div>
            </div>
            
            <div className="bg-indigo-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <AlertTriangle className="h-5 w-5 text-indigo-600" />
                <span className="text-2xl font-bold text-indigo-700">{data.current_period.incidents}</span>
              </div>
              <p className="text-sm text-gray-600">Incidents</p>
              <div className="flex items-center justify-center gap-1 mt-1">
                {getTrendIcon(data.current_period.incidents_change)}
                <span className="text-xs text-gray-500">
                  {data.current_period.incidents_change > 0 ? '+' : ''}{data.current_period.incidents_change}%
                </span>
              </div>
            </div>
            
            <div className="bg-orange-50 rounded-lg p-4 text-center">
              <div className="flex items-center justify-center gap-2 mb-2">
                <MapPin className="h-5 w-5 text-orange-600" />
                <span className="text-xl font-bold text-orange-700">
                  {data.by_state.length > 0 ? data.by_state[0].state : 'N/A'}
                </span>
              </div>
              <p className="text-sm text-gray-600">Most Affected State</p>
              <div className="text-xs text-gray-500 mt-1">
                {data.by_state.length > 0 ? `${data.by_state[0].victims} victims` : 'No data'}
              </div>
            </div>
          </div>

          {/* Top 3 States */}
          {data.by_state.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Top Affected States</h4>
              <div className="space-y-2">
                {data.by_state.slice(0, 3).map((state, index) => (
                  <div key={state.state} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center gap-2">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                        index === 0 ? 'bg-red-100 text-red-700' :
                        index === 1 ? 'bg-orange-100 text-orange-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {index + 1}
                      </div>
                      <span className="text-sm font-medium text-gray-900">{state.state}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-gray-900">{state.victims}</span>
                      <span className="text-xs text-gray-500 ml-1">victims</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Expanded Details */}
          {expanded && (
            <div className="space-y-4 pt-4 border-t border-gray-200">
              {/* Detailed Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Monthly Average</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Avg Victims/Month:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {data.current_period.victims > 0 ? Math.round(data.current_period.victims) : 0}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Avg Incidents/Month:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {data.current_period.incidents > 0 ? Math.round(data.current_period.incidents) : 0}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Risk Analysis</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Current Risk Level:</span>
                      <Badge className={getRiskBadgeColor(data.risk_level)}>
                        {data.risk_level.toUpperCase()}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Victims per Incident:</span>
                      <span className="text-sm font-medium text-gray-900">
                        {data.current_period.incidents > 0 
                          ? (data.current_period.victims / data.current_period.incidents).toFixed(1)
                          : '0.0'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Full State Rankings */}
              {data.by_state.length > 0 && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700">Complete State Rankings</h4>
                  <div className="space-y-2">
                    {data.by_state.map((state, index) => (
                      <div key={state.state} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors">
                        <div className="flex items-center gap-3">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold ${
                            index === 0 ? 'bg-red-100 text-red-700' :
                            index === 1 ? 'bg-orange-100 text-orange-700' :
                            index === 2 ? 'bg-yellow-100 text-yellow-700' :
                            index === 3 ? 'bg-green-100 text-green-700' :
                            'bg-gray-100 text-gray-700'
                          }`}>
                            {index + 1}
                          </div>
                          <div>
                            <p className="text-sm font-medium text-gray-900">{state.state}</p>
                            <p className="text-xs text-gray-500">{state.incidents} incidents</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-gray-900">{state.victims}</p>
                          <p className="text-xs text-gray-500">{state.victims === 1 ? 'victim' : 'victims'}</p>
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
              Last updated: {new Date(data.last_updated).toLocaleDateString()}
            </div>
            <div className="flex gap-2">
              <Button 
                variant="outline"
                size="sm"
                onClick={() => setExpanded(!expanded)}
              >
                {expanded ? 'Show Less' : 'Show More'}
              </Button>
              <Button 
                onClick={() => {
                  // Scroll to kidnapping section on main dashboard
                  const element = document.getElementById('kidnapping-analytics-heading');
                  if (element) {
                    element.scrollIntoView({ behavior: 'smooth' });
                  }
                }}
                className="bg-purple-600 hover:bg-purple-700 text-white"
              >
                {expanded ? 'Collapse' : 'Expand Details'}
                <ArrowRight className={`h-4 w-4 ml-2 ${expanded ? 'transform rotate-180' : ''}`} />
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
