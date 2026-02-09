'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertTriangle, MapPin, TrendingUp, Clock } from 'lucide-react';

interface Hotspot {
  state: string;
  incidents: number;
  fatalities: number;
  incidents_per_day: number;
  severity: 'Critical' | 'High' | 'Moderate';
}

interface HotspotsData {
  hotspots: Hotspot[];
  period: string;
  totalHotspots: number;
  criticalZones: number;
  generatedAt: string;
}

interface RiskHotspotsProps {
  daysBack?: number;
}

const SEVERITY_COLORS = {
  'Critical': 'bg-red-100 text-red-800 border-red-300',
  'High': 'bg-orange-100 text-orange-800 border-orange-300',
  'Moderate': 'bg-yellow-100 text-yellow-800 border-yellow-300',
};

const SEVERITY_BADGES = {
  'Critical': 'destructive',
  'High': 'default',
  'Moderate': 'secondary',
} as const;

export function RiskHotspots({ daysBack = 30 }: RiskHotspotsProps) {
  const [data, setData] = useState<HotspotsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          days_back: daysBack.toString(),
          min_incidents: '3',
        });

        
        const response = await fetch(`/api/v1/intelligence/hotspots?${params}`);
        
        if (!response.ok) throw new Error('Failed to fetch hotspots data');

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [daysBack]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Active Conflict Hotspots</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-32 w-full" />
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

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            Active Conflict Hotspots
          </CardTitle>
          <Badge variant="outline">{data.period}</Badge>
        </div>
        <p className="text-sm text-gray-600 mt-1">
          {data.totalHotspots} active zones • {data.criticalZones} critical
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {data.hotspots.slice(0, 8).map((hotspot, index) => (
            <div
              key={hotspot.state}
              className={`border rounded-lg p-4 ${SEVERITY_COLORS[hotspot.severity]}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-lg">#{index + 1}</span>
                  <MapPin className="h-4 w-4" />
                  <span className="font-semibold">{hotspot.state}</span>
                </div>
                <Badge variant={SEVERITY_BADGES[hotspot.severity]}>
                  {hotspot.severity}
                </Badge>
              </div>

              <div className="grid grid-cols-3 gap-4 text-xs">
                <div>
                  <p className="opacity-75 mb-1">Incidents</p>
                  <p className="font-bold text-lg">{hotspot.incidents}</p>
                </div>
                <div>
                  <p className="opacity-75 mb-1">Fatalities</p>
                  <p className="font-bold text-lg">{hotspot.fatalities}</p>
                </div>
                <div>
                  <p className="opacity-75 mb-1">Per Day</p>
                  <p className="font-bold text-lg">{hotspot.incidents_per_day.toFixed(2)}</p>
                </div>
              </div>

              {/* Progress bar showing activity intensity */}
              <div className="mt-3 pt-3 border-t border-current/20">
                <div className="h-2 bg-white/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-current"
                    style={{ width: `${Math.min((hotspot.incidents / data.hotspots[0].incidents) * 100, 100)}%` }}
                  />
                </div>
              </div>
            </div>
          ))}

          {data.hotspots.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-2 opacity-50" />
              <p>No active hotspots detected in this period</p>
              <p className="text-sm">This is a positive indicator</p>
            </div>
          )}
        </div>

        {/* Summary alert */}
        {data.criticalZones > 0 && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-800 font-semibold flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              ⚠️ {data.criticalZones} critical zone{data.criticalZones > 1 ? 's' : ''} require immediate attention
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
