import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, MapPin, Users, AlertTriangle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface StateData {
  state: string;
  conflicts: number;
  fatalities: number;
  incidents: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  change: number;
  population: number;
}

interface StateAnalysisProps {
  detailed?: boolean;
}

export const StateAnalysis: React.FC<StateAnalysisProps> = ({ detailed = false }) => {
  const [sortBy, setSortBy] = useState<'conflicts' | 'fatalities' | 'incidents'>('conflicts');
  const [viewType, setViewType] = useState<'bar' | 'pie'>('bar');

  // Mock data - replace with real API data
  const stateData: StateData[] = [
    { state: 'Borno', conflicts: 45, fatalities: 156, incidents: 67, riskLevel: 'critical', change: 12, population: 5860000 },
    { state: 'Kaduna', conflicts: 38, fatalities: 124, incidents: 52, riskLevel: 'high', change: -8, population: 6113000 },
    { state: 'Plateau', conflicts: 32, fatalities: 98, incidents: 45, riskLevel: 'high', change: 15, population: 3178000 },
    { state: 'Katsina', conflicts: 28, fatalities: 87, incidents: 39, riskLevel: 'high', change: -5, population: 7831000 },
    { state: 'Niger', conflicts: 25, fatalities: 76, incidents: 34, riskLevel: 'medium', change: 8, population: 5556000 },
    { state: 'Zamfara', conflicts: 23, fatalities: 69, incidents: 31, riskLevel: 'medium', change: -12, population: 3838000 },
    { state: 'Sokoto', conflicts: 19, fatalities: 54, incidents: 26, riskLevel: 'medium', change: 3, population: 4998000 },
    { state: 'Yobe', conflicts: 17, fatalities: 48, incidents: 23, riskLevel: 'medium', change: -7, population: 2321000 },
    { state: 'Adamawa', conflicts: 15, fatalities: 42, incidents: 21, riskLevel: 'medium', change: 6, population: 4248000 },
    { state: 'Bauchi', conflicts: 12, fatalities: 35, incidents: 18, riskLevel: 'low', change: -3, population: 4676000 }
  ];

  const sortedData = [...stateData].sort((a, b) => b[sortBy] - a[sortBy]);

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'critical': return '#ef4444';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#22c55e';
      default: return '#6b7280';
    }
  };

  const getRiskBadgeColor = (level: string) => {
    switch (level) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <TrendingUp className="w-4 h-4 text-red-500" />;
    if (change < 0) return <TrendingDown className="w-4 h-4 text-green-500" />;
    return <div className="w-4 h-4" />;
  };

  const pieData = stateData.slice(0, 5).map(state => ({
    name: state.state,
    value: state[sortBy],
    fill: getRiskColor(state.riskLevel)
  }));

  const totalConflicts = stateData.reduce((sum, state) => sum + state.conflicts, 0);
  const totalFatalities = stateData.reduce((sum, state) => sum + state.fatalities, 0);

  if (detailed) {
    return (
      <div className="space-y-6">
        {/* Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">Sort by:</span>
            <div className="flex space-x-1">
              {(['conflicts', 'fatalities', 'incidents'] as const).map((option) => (
                <Button
                  key={option}
                  variant={sortBy === option ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSortBy(option)}
                >
                  {option.charAt(0).toUpperCase() + option.slice(1)}
                </Button>
              ))}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium">View:</span>
            <div className="flex space-x-1">
              <Button
                variant={viewType === 'bar' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewType('bar')}
              >
                Bar Chart
              </Button>
              <Button
                variant={viewType === 'pie' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setViewType('pie')}
              >
                Pie Chart
              </Button>
            </div>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white p-6 rounded-lg border">
          <ResponsiveContainer width="100%" height={400}>
            {viewType === 'bar' ? (
              <BarChart data={sortedData.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="state" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey={sortBy} 
                  fill="#3b82f6"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            ) : (
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            )}
          </ResponsiveContainer>
        </div>

        {/* Detailed Table */}
        <div className="bg-white rounded-lg border overflow-hidden">
          <div className="px-6 py-4 border-b bg-gray-50">
            <h3 className="font-medium">State-by-State Analysis</h3>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">State</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Conflicts</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fatalities</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Incidents</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {sortedData.map((state, index) => (
                  <tr key={state.state} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 text-gray-400 mr-2" />
                        <span className="font-medium">{state.state} State</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge 
                        variant="outline"
                        className={getRiskBadgeColor(state.riskLevel)}
                      >
                        {state.riskLevel.toUpperCase()}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      {state.conflicts}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {state.fatalities}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      {state.incidents}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-1">
                        {getTrendIcon(state.change)}
                        <span className={`text-sm ${state.change > 0 ? 'text-red-600' : state.change < 0 ? 'text-green-600' : 'text-gray-600'}`}>
                          {Math.abs(state.change)}%
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={sortedData.slice(0, 6)}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="state" 
            tick={{ fontSize: 11 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip 
            contentStyle={{
              backgroundColor: 'white',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
            }}
          />
          <Bar 
            dataKey="conflicts" 
            fill="#3b82f6"
            radius={[2, 2, 0, 0]}
            name="Conflicts"
          />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Summary Stats */}
      <div className="mt-4 grid grid-cols-2 gap-4 text-center">
        <div>
          <p className="text-lg font-bold text-blue-600">{totalConflicts}</p>
          <p className="text-xs text-gray-600">Total Conflicts</p>
        </div>
        <div>
          <p className="text-lg font-bold text-red-600">{totalFatalities}</p>
          <p className="text-xs text-gray-600">Total Fatalities</p>
        </div>
      </div>
      
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500">
          Interactive chart visualization with Recharts
        </p>
      </div>
    </div>
  );
};

export default StateAnalysis;
