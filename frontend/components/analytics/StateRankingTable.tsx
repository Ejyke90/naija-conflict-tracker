'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { TrendingUp, TrendingDown, Minus, Download, Search } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface StateRankingData {
  state: string;
  incidents: number;
  fatalities: number;
  injuries: number;
  kidnapped: number;
  affectedLGAs: number;
  previousIncidents: number;
  trend: 'increasing' | 'stable' | 'decreasing';
  trendPercent: number;
  riskLevel: 'critical' | 'high' | 'medium' | 'low';
}

interface StateRankingTableProps {
  monthsBack?: number;
  defaultSortBy?: 'incidents' | 'fatalities' | 'injuries';
  limit?: number;
}

const RISK_COLORS = {
  critical: 'bg-red-100 text-red-800 border-red-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  low: 'bg-green-100 text-green-800 border-green-300',
};

export default function StateRankingTable({
  monthsBack = 12,
  defaultSortBy = 'incidents',
  limit = 37
}: StateRankingTableProps) {
  const router = useRouter();
  const [data, setData] = useState<StateRankingData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortBy, setSortBy] = useState(defaultSortBy);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedMonths, setSelectedMonths] = useState(monthsBack);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(
          `${apiUrl}/api/v1/timeseries/state-summary?months_back=${selectedMonths}&limit=${limit}`
        );

        if (!response.ok) throw new Error('Failed to fetch state rankings');

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedMonths, limit]);

  const filteredData = data.filter((row) =>
    row.state.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const sortedData = [...filteredData].sort((a, b) => {
    const aVal = a[sortBy];
    const bVal = b[sortBy];
    return sortOrder === 'desc' ? bVal - aVal : aVal - bVal;
  });

  const exportToCSV = () => {
    const headers = ['State', 'Incidents', 'Fatalities', 'Injuries', 'Kidnapped', 'Affected LGAs', 'Trend', 'Risk Level'];
    const rows = sortedData.map((row) => [
      row.state,
      row.incidents,
      row.fatalities,
      row.injuries,
      row.kidnapped,
      row.affectedLGAs,
      `${row.trend} (${row.trendPercent}%)`,
      row.riskLevel
    ]);

    const csv = [headers, ...rows].map((row) => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `state-rankings-${selectedMonths}months.csv`;
    a.click();
  };

  const handleSort = (column: typeof sortBy) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(column);
      setSortOrder('desc');
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-64 bg-gray-200 rounded"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="text-red-600">Error: {error}</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-xl font-bold text-gray-900">State Rankings</h3>
            <p className="text-sm text-gray-600 mt-1">
              {sortedData.length} states ranked by conflict metrics
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Time Period Selector */}
            <select
              value={selectedMonths}
              onChange={(e) => setSelectedMonths(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value={6}>Last 6 months</option>
              <option value={12}>Last 12 months</option>
              <option value={24}>Last 24 months</option>
            </select>

            {/* Export Button */}
            <Button variant="outline" size="sm" onClick={exportToCSV}>
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search states..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b-2 border-gray-200">
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">Rank</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-700">State</th>
                <th
                  className="px-4 py-3 text-right font-semibold text-gray-700 cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('incidents')}
                >
                  Incidents {sortBy === 'incidents' && (sortOrder === 'desc' ? '↓' : '↑')}
                </th>
                <th
                  className="px-4 py-3 text-right font-semibold text-gray-700 cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('fatalities')}
                >
                  Fatalities {sortBy === 'fatalities' && (sortOrder === 'desc' ? '↓' : '↑')}
                </th>
                <th
                  className="px-4 py-3 text-right font-semibold text-gray-700 cursor-pointer hover:bg-gray-100"
                  onClick={() => handleSort('injuries')}
                >
                  Injuries {sortBy === 'injuries' && (sortOrder === 'desc' ? '↓' : '↑')}
                </th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">Trend</th>
                <th className="px-4 py-3 text-center font-semibold text-gray-700">Risk Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {sortedData.map((row, index) => (
                <tr
                  key={row.state}
                  className="hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => router.push(`/states/${row.state}`)}
                >
                  <td className="px-4 py-3 text-gray-600 font-medium">{index + 1}</td>
                  <td className="px-4 py-3 font-semibold text-gray-900">{row.state}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{row.incidents.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{row.fatalities.toLocaleString()}</td>
                  <td className="px-4 py-3 text-right text-gray-700">{row.injuries.toLocaleString()}</td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1">
                      {row.trend === 'increasing' && <TrendingUp className="h-4 w-4 text-red-600" />}
                      {row.trend === 'decreasing' && <TrendingDown className="h-4 w-4 text-green-600" />}
                      {row.trend === 'stable' && <Minus className="h-4 w-4 text-gray-400" />}
                      <span className={`text-xs ${row.trend === 'increasing' ? 'text-red-600' : row.trend === 'decreasing' ? 'text-green-600' : 'text-gray-600'}`}>
                        {Math.abs(row.trendPercent)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full border ${RISK_COLORS[row.riskLevel]}`}>
                      {row.riskLevel.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
