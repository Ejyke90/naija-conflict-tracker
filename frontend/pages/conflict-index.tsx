import React, { useState } from 'react';
import dynamic from 'next/dynamic';
import { Calendar, Download, Info, TrendingUp, Users, MapPin, Shield } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

// Dynamic import to avoid SSR issues
const ConflictIndexTable = dynamic(() => import('@/components/dashboard/ConflictIndexTable'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading Conflict Index...</div>
});

const AdvancedConflictMap = dynamic(() => import('@/components/mapping/AdvancedConflictMap'), {
  ssr: false,
  loading: () => <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">Loading map...</div>
});

export default function ConflictIndexPage() {
  const [timeRange, setTimeRange] = useState('12months');

  // Summary statistics
  const stats = {
    totalEvents: 204605,
    fatalities: 24000,
    statesAffected: 18,
    armedGroups: 156,
    conflictTrend: 'stable', // up, down, stable
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white">
        <div className="container mx-auto px-6 py-12">
          <div className="max-w-4xl">
            <h1 className="text-4xl font-bold mb-4">Nigeria Conflict Index</h1>
            <p className="text-xl text-blue-100 mb-6">
              A comprehensive assessment of conflict severity across Nigerian states based on four key indicators: 
              deadliness, danger to civilians, geographic diffusion, and armed group fragmentation.
            </p>
            <div className="flex items-center gap-4">
              <Button variant="outline" className="bg-white text-blue-600 hover:bg-blue-50">
                <Download className="w-4 h-4 mr-2" />
                Download Full Report
              </Button>
              <Button variant="outline" className="bg-transparent border-white text-white hover:bg-blue-700">
                <Info className="w-4 h-4 mr-2" />
                Methodology
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="container mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Key Findings</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 mt-2 rounded-full bg-red-500" />
              <div>
                <p className="text-gray-900 font-medium">
                  <span className="font-bold">Borno</span> remains the most dangerous state with highest conflict intensity
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 mt-2 rounded-full bg-orange-500" />
              <div>
                <p className="text-gray-900 font-medium">
                  <span className="font-bold">18 states</span> experienced significant violent incidents in past 12 months
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-2 h-2 mt-2 rounded-full bg-yellow-500" />
              <div>
                <p className="text-gray-900 font-medium">
                  <span className="font-bold">156+ armed groups</span> active across the country
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Summary Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Total Conflict Events</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <div className="text-3xl font-bold text-gray-900">
                  {stats.totalEvents.toLocaleString()}
                </div>
                <span className="text-sm text-gray-500">past 12 months</span>
              </div>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="w-4 h-4 text-orange-500" />
                <span className="text-sm text-orange-600">+2.3% from previous period</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Fatalities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <div className="text-3xl font-bold text-red-600">
                  {stats.fatalities.toLocaleString()}
                </div>
                <span className="text-sm text-gray-500">deaths</span>
              </div>
              <div className="flex items-center gap-1 mt-2">
                <Users className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">Conservative estimate</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">States Affected</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <div className="text-3xl font-bold text-gray-900">
                  {stats.statesAffected}
                </div>
                <span className="text-sm text-gray-500">of 36 states</span>
              </div>
              <div className="flex items-center gap-1 mt-2">
                <MapPin className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">{((stats.statesAffected/36)*100).toFixed(0)}% coverage</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Armed Groups</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-baseline gap-2">
                <div className="text-3xl font-bold text-gray-900">
                  {stats.armedGroups}+
                </div>
                <span className="text-sm text-gray-500">distinct groups</span>
              </div>
              <div className="flex items-center gap-1 mt-2">
                <Shield className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-600">High fragmentation</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Time Range Selector */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Calendar className="w-5 h-5 text-gray-600" />
            <span className="text-sm font-medium text-gray-700">Time Period:</span>
            <div className="flex gap-2">
              {['6months', '12months', '24months', 'all'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 text-sm rounded-md transition-colors ${
                    timeRange === range
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {range === 'all' ? 'All Time' : range.replace('months', ' Months')}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="rankings" className="space-y-6">
          <TabsList className="bg-white border border-gray-200">
            <TabsTrigger value="rankings">State Rankings</TabsTrigger>
            <TabsTrigger value="map">Geographic View</TabsTrigger>
            <TabsTrigger value="indicators">Index Indicators</TabsTrigger>
            <TabsTrigger value="methodology">Methodology</TabsTrigger>
          </TabsList>

          <TabsContent value="rankings">
            <ConflictIndexTable timeRange={timeRange as '6months' | '12months' | '24months' | 'all'} />
          </TabsContent>

          <TabsContent value="map">
            <Card>
              <CardHeader>
                <CardTitle>Geographic Conflict Distribution</CardTitle>
                <CardDescription>
                  Interactive map showing conflict intensity across Nigerian states
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-[600px] rounded-lg overflow-hidden">
                  <AdvancedConflictMap />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="indicators">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Deadliness Indicator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500" />
                    Deadliness
                  </CardTitle>
                  <CardDescription>
                    Measures conflict-related fatalities and lethality of events
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 mb-4">
                    This indicator ranks states based on total fatalities, average deaths per event, 
                    and the proportion of high-casualty incidents. Higher scores indicate more lethal conflicts.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Top 3 States:</span>
                      <span className="font-medium">Borno, Zamfara, Kaduna</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avg. fatalities per event:</span>
                      <span className="font-medium text-red-600">3.2</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Civilian Danger Indicator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-orange-500" />
                    Danger to Civilians
                  </CardTitle>
                  <CardDescription>
                    Percentage of events targeting civilian populations
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 mb-4">
                    Measures the proportion of violence directed against non-combatants, including 
                    kidnappings, massacres, and attacks on villages. Higher scores indicate greater civilian risk.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Top 3 States:</span>
                      <span className="font-medium">Zamfara, Kaduna, Borno</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avg. civilian targeting:</span>
                      <span className="font-medium text-orange-600">67%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Geographic Diffusion Indicator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-yellow-500" />
                    Geographic Diffusion
                  </CardTitle>
                  <CardDescription>
                    Spread of conflict across administrative regions
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 mb-4">
                    Calculates the percentage of Local Government Areas (LGAs) within a state experiencing 
                    violence. Higher scores indicate widespread, less concentrated conflict.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Top 3 States:</span>
                      <span className="font-medium">Borno, Kaduna, Plateau</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avg. LGA coverage:</span>
                      <span className="font-medium text-yellow-600">58%</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Armed Groups Indicator */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-blue-500" />
                    Armed Group Fragmentation
                  </CardTitle>
                  <CardDescription>
                    Number of distinct armed groups active in the region
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-700 mb-4">
                    Counts unique armed actors involved in violent events. Higher fragmentation makes 
                    conflict resolution more complex and indicates less centralized violence.
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Top 3 States:</span>
                      <span className="font-medium">Borno, Zamfara, Kaduna</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Avg. groups per state:</span>
                      <span className="font-medium text-blue-600">12.4</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="methodology">
            <Card>
              <CardHeader>
                <CardTitle>Conflict Index Methodology</CardTitle>
                <CardDescription>How we calculate and rank conflict severity</CardDescription>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                <h3 className="text-lg font-bold text-gray-900 mb-3">Overview</h3>
                <p className="text-gray-700 mb-4">
                  The Nigeria Conflict Index ranks states according to four weighted indicators that capture 
                  different dimensions of political violence and armed conflict. The index is calculated using 
                  a rolling 12-month window to capture recent trends.
                </p>

                <h3 className="text-lg font-bold text-gray-900 mb-3 mt-6">The Four Indicators</h3>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="font-bold text-gray-900">1. Deadliness (25% weight)</h4>
                    <p className="text-gray-700">
                      Calculated as: (Total fatalities × 0.6) + (Average fatalities per event × 0.4)
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900">2. Danger to Civilians (25% weight)</h4>
                    <p className="text-gray-700">
                      Percentage of total events that directly target civilian populations, including 
                      attacks on civilians, kidnappings, and violence against property.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900">3. Geographic Diffusion (25% weight)</h4>
                    <p className="text-gray-700">
                      The proportion of Local Government Areas within a state that have experienced at 
                      least one conflict event in the assessment period.
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900">4. Armed Group Fragmentation (25% weight)</h4>
                    <p className="text-gray-700">
                      Total count of distinct armed groups identified as perpetrators of violence, 
                      normalized against state population.
                    </p>
                  </div>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-3 mt-6">Severity Classification</h3>
                <ul className="list-disc list-inside space-y-2 text-gray-700">
                  <li><strong>Extreme:</strong> Composite score ≥ 80</li>
                  <li><strong>High:</strong> Composite score 60-79</li>
                  <li><strong>Turbulent:</strong> Composite score 40-59</li>
                  <li><strong>Moderate:</strong> Composite score &lt; 40</li>
                </ul>

                <h3 className="text-lg font-bold text-gray-900 mb-3 mt-6">Data Sources</h3>
                <p className="text-gray-700">
                  The index is based on real-time conflict event data collected from Nigerian news sources, 
                  government reports, and verified social media accounts. All events are manually reviewed 
                  and geocoded to ensure accuracy.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
