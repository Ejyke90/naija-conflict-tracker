'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  AlertTriangle, 
  TrendingUp, 
  Map, 
  Calendar,
  Droplet,
  Zap,
  Shield,
  Users
} from 'lucide-react';

interface ConflictArchetype {
  total_incidents: number;
  total_fatalities: number;
  avg_fatalities_per_incident: number;
  percentage: number;
}

interface ArchetypeData {
  summary: Record<string, ConflictArchetype>;
  timeRange: string;
  totalConflicts: number;
  generatedAt: string;
}

interface IntelligenceInsightsProps {
  state?: string;
  monthsBack?: number;
}

const ARCHETYPE_ICONS: Record<string, any> = {
  "Farmer-Herder": Droplet,
  "Banditry": AlertTriangle,
  "Terrorism": Zap,
  "Communal Clash": Users,
  "Resource Conflict": Map,
  "Political Violence": TrendingUp,
  "Security Operations": Shield,
};

const ARCHETYPE_COLORS: Record<string, string> = {
  "Farmer-Herder": "bg-amber-100 text-amber-800 border-amber-300",
  "Banditry": "bg-red-100 text-red-800 border-red-300",
  "Terrorism": "bg-purple-100 text-purple-800 border-purple-300",
  "Communal Clash": "bg-blue-100 text-blue-800 border-blue-300",
  "Resource Conflict": "bg-green-100 text-green-800 border-green-300",
  "Political Violence": "bg-orange-100 text-orange-800 border-orange-300",
  "Security Operations": "bg-gray-100 text-gray-800 border-gray-300",
};

export function IntelligenceInsights({ state, monthsBack = 12 }: IntelligenceInsightsProps) {
  const [data, setData] = useState<ArchetypeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          months_back: monthsBack.toString(),
        });
        if (state) params.append('state', state);

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/intelligence/archetypes?${params}`);
        
        if (!response.ok) throw new Error('Failed to fetch intelligence data');

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [state, monthsBack]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Conflict Intelligence</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error || !data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-red-600">
            <AlertTriangle className="h-12 w-12 mx-auto mb-2" />
            <p>{error || 'No data available'}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Sort archetypes by percentage
  const sortedArchetypes = Object.entries(data.summary)
    .sort(([, a], [, b]) => b.percentage - a.percentage)
    .slice(0, 6); // Top 6 archetypes

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-blue-600" />
            Conflict Intelligence & Archetypes
          </CardTitle>
          <Badge variant="outline">{data.timeRange}</Badge>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          Analysis of {data.totalConflicts} conflicts by type and trigger patterns
        </p>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sortedArchetypes.map(([name, stats]) => {
            const Icon = ARCHETYPE_ICONS[name] || AlertTriangle;
            const colorClass = ARCHETYPE_COLORS[name] || "bg-gray-100 text-gray-800 border-gray-300";
            
            return (
              <div
                key={name}
                className={`border rounded-lg p-4 ${colorClass.split(' ')[0].replace('bg-', 'border-')}`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <div className={`p-2 rounded ${colorClass.split(' ')[0]}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-sm">{name}</h3>
                      <p className="text-xs opacity-75">{stats.percentage.toFixed(1)}% of conflicts</p>
                    </div>
                  </div>
                  <Badge variant={stats.total_incidents > 10 ? "destructive" : "secondary"}>
                    {stats.total_incidents}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div>
                    <p className="opacity-75">Total Fatalities</p>
                    <p className="font-bold text-lg">{stats.total_fatalities}</p>
                  </div>
                  <div>
                    <p className="opacity-75">Avg per Incident</p>
                    <p className="font-bold text-lg">{stats.avg_fatalities_per_incident.toFixed(1)}</p>
                  </div>
                </div>

                {/* Risk indicator */}
                <div className="mt-3 pt-3 border-t border-current/20">
                  <div className="flex items-center justify-between text-xs">
                    <span>Severity:</span>
                    <span className="font-semibold">
                      {stats.avg_fatalities_per_incident > 5 ? 'High' : 
                       stats.avg_fatalities_per_incident > 2 ? 'Medium' : 'Low'}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Key Insights */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-sm text-blue-900 mb-2 flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Key Insights
          </h4>
          <ul className="text-sm text-blue-800 space-y-1">
            {sortedArchetypes[0] && (
              <li>• <strong>{sortedArchetypes[0][0]}</strong> is the dominant conflict archetype ({sortedArchetypes[0][1].percentage.toFixed(1)}%)</li>
            )}
            {sortedArchetypes.filter(([, s]) => s.avg_fatalities_per_incident > 5).length > 0 && (
              <li>• {sortedArchetypes.filter(([, s]) => s.avg_fatalities_per_incident > 5).length} archetype(s) show high lethality ({'>'}5 fatalities/incident)</li>
            )}
            <li>• Monitor seasonal triggers for Farmer-Herder conflicts (peak: Nov-Mar dry season)</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
