import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Calendar,
  Activity,
  Users
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';

interface KidnappingTrendData {
  month: string;
  victims: number;
  incidents: number;
}

interface KidnappingTrendsProps {
  data?: KidnappingTrendData[];
}

export const KidnappingTrends: React.FC<KidnappingTrendsProps> = ({ data: propData }) => {
  const [data, setData] = useState<KidnappingTrendData[]>(propData || []);
  const [loading, setLoading] = useState(!propData);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (propData) {
      setData(propData);
      setLoading(false);
      return;
    }

    const fetchTrendsData = async () => {
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
        
        const result = await response.json();
        setData(result.monthly_trends || []);
        setError(null);
      } catch (err) {
        console.error('Error fetching kidnapping trends:', err);
        setError(err instanceof Error ? err.message : 'Failed to load kidnapping trends');
        setData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTrendsData();
  }, [propData]);

  // Simple SVG chart component
  const SimpleTrendChart = ({ data }: { data: KidnappingTrendData[] }) => {
    if (data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-gray-500">
          <div className="text-center">
            <Activity className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>No trend data available</p>
          </div>
        </div>
      );
    }

    const maxVictims = Math.max(...data.map(d => d.victims));
    const maxIncidents = Math.max(...data.map(d => d.incidents));
    const chartHeight = 200;
    const chartWidth = 600;
    const padding = 40;
    const barWidth = (chartWidth - padding * 2) / (data.length * 2);

    return (
      <div className="w-full overflow-x-auto">
        <svg width={chartWidth} height={chartHeight} className="mx-auto">
          {/* Grid lines */}
          {[0, 1, 2, 3, 4].map(i => (
            <line
              key={i}
              x1={padding}
              y1={padding + (chartHeight - padding * 2) * i / 4}
              x2={chartWidth - padding}
              y2={padding + (chartHeight - padding * 2) * i / 4}
              stroke="#e5e7eb"
              strokeWidth="1"
            />
          ))}
          
          {/* Y-axis labels */}
          {[0, 1, 2, 3, 4].map(i => (
            <text
              key={i}
              x={padding - 10}
              y={padding + (chartHeight - padding * 2) * i / 4 + 5}
              textAnchor="end"
              className="text-xs fill-gray-600"
            >
              {Math.round(maxVictims * (4 - i) / 4)}
            </text>
          ))}

          {/* Bars and labels */}
          {data.map((item, index) => {
            const victimsHeight = (item.victims / maxVictims) * (chartHeight - padding * 2);
            const incidentsHeight = (item.incidents / maxIncidents) * (chartHeight - padding * 2);
            const x = padding + index * barWidth * 2;
            
            return (
              <g key={index}>
                {/* Victims bar */}
                <rect
                  x={x}
                  y={chartHeight - padding - victimsHeight}
                  width={barWidth * 0.8}
                  height={victimsHeight}
                  fill="#8b5cf6"
                  opacity="0.8"
                />
                
                {/* Incidents bar */}
                <rect
                  x={x + barWidth}
                  y={chartHeight - padding - incidentsHeight}
                  width={barWidth * 0.8}
                  height={incidentsHeight}
                  fill="#6366f1"
                  opacity="0.8"
                />
                
                {/* Month label */}
                <text
                  x={x + barWidth}
                  y={chartHeight - padding + 20}
                  textAnchor="middle"
                  className="text-xs fill-gray-600"
                  transform={`rotate(-45, ${x + barWidth}, ${chartHeight - padding + 20})`}
                >
                  {new Date(item.month).toLocaleDateString('en-US', { month: 'short' })}
                </text>
                
                {/* Value labels on top of bars */}
                {item.victims > 0 && (
                  <text
                    x={x + barWidth * 0.4}
                    y={chartHeight - padding - victimsHeight - 5}
                    textAnchor="middle"
                    className="text-xs fill-gray-700 font-medium"
                  >
                    {item.victims}
                  </text>
                )}
                
                {item.incidents > 0 && (
                  <text
                    x={x + barWidth * 1.4}
                    y={chartHeight - padding - incidentsHeight - 5}
                    textAnchor="middle"
                    className="text-xs fill-gray-700 font-medium"
                  >
                    {item.incidents}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
        
        {/* Legend */}
        <div className="flex justify-center gap-6 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-purple-500 opacity-80 rounded"></div>
            <span className="text-sm text-gray-600">Victims</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-indigo-500 opacity-80 rounded"></div>
            <span className="text-sm text-gray-600">Incidents</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">Kidnapping Trends</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Monthly patterns and historical analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-semibold text-gray-900">Kidnapping Trends</CardTitle>
          <CardDescription className="text-sm text-gray-600">
            Monthly patterns and historical analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-red-600">
            <p className="text-center">Error loading trends: {error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Calculate statistics
  const totalVictims = data.reduce((sum, item) => sum + item.victims, 0);
  const totalIncidents = data.reduce((sum, item) => sum + item.incidents, 0);
  const avgVictimsPerIncident = totalIncidents > 0 ? (totalVictims / totalIncidents).toFixed(1) : '0.0';
  const trendDirection = data.length >= 2 
    ? data[data.length - 1].victims > data[data.length - 2].victims ? 'up' : 'down'
    : 'stable';

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-purple-600" />
              Kidnapping Trends
            </CardTitle>
            <CardDescription className="text-sm text-gray-600">
              Monthly patterns and historical analysis (last 6 months)
            </CardDescription>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-purple-500" />
              <span className="font-medium text-gray-700">{totalVictims} victims</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-indigo-500" />
              <span className="font-medium text-gray-700">{totalIncidents} incidents</span>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Summary Statistics */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-purple-50 rounded-lg p-3 text-center">
              <p className="text-sm text-gray-600 mb-1">Total Victims</p>
              <p className="text-2xl font-bold text-purple-700">{totalVictims}</p>
            </div>
            <div className="bg-indigo-50 rounded-lg p-3 text-center">
              <p className="text-sm text-gray-600 mb-1">Total Incidents</p>
              <p className="text-2xl font-bold text-indigo-700">{totalIncidents}</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 text-center">
              <p className="text-sm text-gray-600 mb-1">Avg Victims/Incident</p>
              <p className="text-2xl font-bold text-blue-700">{avgVictimsPerIncident}</p>
            </div>
          </div>

          {/* Trend Chart */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-3">Monthly Kidnapping Trends</h4>
            <SimpleTrendChart data={data} />
          </div>

          {/* Trend Analysis */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Trend Analysis</h4>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex items-center justify-between">
                <span>Current Trend Direction:</span>
                <span className={`font-medium ${
                  trendDirection === 'up' ? 'text-red-600' : 
                  trendDirection === 'down' ? 'text-green-600' : 
                  'text-gray-600'
                }`}>
                  {trendDirection === 'up' ? '📈 Increasing' : 
                   trendDirection === 'down' ? '📉 Decreasing' : 
                   '➡️ Stable'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Data Period:</span>
                <span className="font-medium">Last {data.length} months</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Average Monthly Victims:</span>
                <span className="font-medium">
                  {data.length > 0 ? Math.round(totalVictims / data.length) : 0}
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
