import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Download, TrendingUp, TrendingDown } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface ConflictIndexData {
  rank: number;
  state: string;
  deadliness: number;
  civilianDanger: number;
  geographicDiffusion: number;
  armedGroups: number;
  totalEvents: number;
  fatalities: number;
  trend: 'up' | 'down' | 'stable';
  severity: 'extreme' | 'high' | 'turbulent' | 'moderate';
}

type SortField = 'rank' | 'state' | 'deadliness' | 'civilianDanger' | 'geographicDiffusion' | 'armedGroups' | 'totalEvents' | 'fatalities';
type SortDirection = 'asc' | 'desc';

const ConflictIndexTable: React.FC = () => {
  const [sortField, setSortField] = useState<SortField>('rank');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);

  // Mock data - replace with API call
  const mockData: ConflictIndexData[] = [
    {
      rank: 1,
      state: 'Borno',
      deadliness: 95,
      civilianDanger: 87,
      geographicDiffusion: 78,
      armedGroups: 23,
      totalEvents: 456,
      fatalities: 1234,
      trend: 'up',
      severity: 'extreme'
    },
    {
      rank: 2,
      state: 'Zamfara',
      deadliness: 89,
      civilianDanger: 92,
      geographicDiffusion: 65,
      armedGroups: 18,
      totalEvents: 378,
      fatalities: 987,
      trend: 'up',
      severity: 'extreme'
    },
    {
      rank: 3,
      state: 'Kaduna',
      deadliness: 82,
      civilianDanger: 75,
      geographicDiffusion: 71,
      armedGroups: 15,
      totalEvents: 342,
      fatalities: 876,
      trend: 'stable',
      severity: 'high'
    },
    {
      rank: 4,
      state: 'Plateau',
      deadliness: 78,
      civilianDanger: 68,
      geographicDiffusion: 58,
      armedGroups: 12,
      totalEvents: 289,
      fatalities: 654,
      trend: 'down',
      severity: 'high'
    },
    {
      rank: 5,
      state: 'Adamawa',
      deadliness: 72,
      civilianDanger: 71,
      geographicDiffusion: 62,
      armedGroups: 14,
      totalEvents: 267,
      fatalities: 589,
      trend: 'up',
      severity: 'high'
    },
    {
      rank: 6,
      state: 'Niger',
      deadliness: 68,
      civilianDanger: 64,
      geographicDiffusion: 54,
      armedGroups: 10,
      totalEvents: 234,
      fatalities: 512,
      trend: 'stable',
      severity: 'turbulent'
    },
    {
      rank: 7,
      state: 'Katsina',
      deadliness: 65,
      civilianDanger: 69,
      geographicDiffusion: 49,
      armedGroups: 9,
      totalEvents: 221,
      fatalities: 478,
      trend: 'up',
      severity: 'turbulent'
    },
    {
      rank: 8,
      state: 'Sokoto',
      deadliness: 61,
      civilianDanger: 58,
      geographicDiffusion: 45,
      armedGroups: 8,
      totalEvents: 198,
      fatalities: 423,
      trend: 'stable',
      severity: 'turbulent'
    },
  ];

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedData = useMemo(() => {
    const sorted = [...mockData].sort((a, b) => {
      const aValue = a[sortField];
      const bValue = b[sortField];
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortDirection === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      return sortDirection === 'asc' 
        ? (aValue as number) - (bValue as number)
        : (bValue as number) - (aValue as number);
    });
    
    return sorted;
  }, [mockData, sortField, sortDirection]);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * rowsPerPage;
    const endIndex = startIndex + rowsPerPage;
    return sortedData.slice(startIndex, endIndex);
  }, [sortedData, currentPage, rowsPerPage]);

  const totalPages = Math.ceil(sortedData.length / rowsPerPage);

  const SortIcon: React.FC<{ field: SortField }> = ({ field }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" />;
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="w-4 h-4 text-blue-600" />
      : <ArrowDown className="w-4 h-4 text-blue-600" />;
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'extreme': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'turbulent': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'moderate': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const exportToCSV = () => {
    const headers = ['Rank', 'State', 'Deadliness', 'Civilian Danger', 'Geographic Diffusion', 'Armed Groups', 'Total Events', 'Fatalities', 'Severity'];
    const rows = sortedData.map(d => [
      d.rank,
      d.state,
      d.deadliness,
      d.civilianDanger,
      d.geographicDiffusion,
      d.armedGroups,
      d.totalEvents,
      d.fatalities,
      d.severity
    ]);
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `nigeria-conflict-index-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Nigeria Conflict Index</h2>
            <p className="text-sm text-gray-600 mt-1">
              Rankings of Nigerian states by conflict severity indicators
            </p>
          </div>
          <Button
            onClick={exportToCSV}
            className="flex items-center gap-2"
            variant="outline"
          >
            <Download className="w-4 h-4" />
            Export CSV
          </Button>
        </div>

        {/* Legend */}
        <div className="mt-4 flex items-center gap-4 text-sm">
          <span className="font-medium text-gray-700">Severity Levels:</span>
          <Badge className="bg-red-100 text-red-800 border border-red-300">Extreme</Badge>
          <Badge className="bg-orange-100 text-orange-800 border border-orange-300">High</Badge>
          <Badge className="bg-yellow-100 text-yellow-800 border border-yellow-300">Turbulent</Badge>
          <Badge className="bg-green-100 text-green-800 border border-green-300">Moderate</Badge>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('rank')}
              >
                <div className="flex items-center gap-2">
                  Rank
                  <SortIcon field="rank" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('state')}
              >
                <div className="flex items-center gap-2">
                  State
                  <SortIcon field="state" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('deadliness')}
              >
                <div className="flex items-center gap-2">
                  Deadliness
                  <SortIcon field="deadliness" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('civilianDanger')}
              >
                <div className="flex items-center gap-2">
                  Civilian Danger
                  <SortIcon field="civilianDanger" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('geographicDiffusion')}
              >
                <div className="flex items-center gap-2">
                  Geo. Diffusion
                  <SortIcon field="geographicDiffusion" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('armedGroups')}
              >
                <div className="flex items-center gap-2">
                  Armed Groups
                  <SortIcon field="armedGroups" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('totalEvents')}
              >
                <div className="flex items-center gap-2">
                  Total Events
                  <SortIcon field="totalEvents" />
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('fatalities')}
              >
                <div className="flex items-center gap-2">
                  Fatalities
                  <SortIcon field="fatalities" />
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Severity
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Trend
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {paginatedData.map((row) => (
              <tr key={row.state} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className={`
                      w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm
                      ${row.rank <= 3 ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'}
                    `}>
                      {row.rank}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{row.state}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className={`h-2 rounded-full ${row.deadliness >= 80 ? 'bg-red-600' : row.deadliness >= 60 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                        style={{ width: `${row.deadliness}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">{row.deadliness}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className={`h-2 rounded-full ${row.civilianDanger >= 80 ? 'bg-red-600' : row.civilianDanger >= 60 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                        style={{ width: `${row.civilianDanger}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">{row.civilianDanger}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div 
                        className={`h-2 rounded-full ${row.geographicDiffusion >= 70 ? 'bg-red-600' : row.geographicDiffusion >= 50 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                        style={{ width: `${row.geographicDiffusion}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-gray-900">{row.geographicDiffusion}%</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm font-medium text-gray-900">{row.armedGroups}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm font-medium text-gray-900">{row.totalEvents.toLocaleString()}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm font-bold text-red-600">{row.fatalities.toLocaleString()}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <Badge className={getSeverityColor(row.severity)}>
                    {row.severity.toUpperCase()}
                  </Badge>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  {row.trend === 'up' && <TrendingUp className="w-5 h-5 text-red-500" />}
                  {row.trend === 'down' && <TrendingDown className="w-5 h-5 text-green-500" />}
                  {row.trend === 'stable' && <div className="w-5 h-0.5 bg-gray-400" />}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-700">Rows per page:</span>
          <select
            value={rowsPerPage}
            onChange={(e) => {
              setRowsPerPage(Number(e.target.value));
              setCurrentPage(1);
            }}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            <option value={10}>10</option>
            <option value={20}>20</option>
            <option value={50}>50</option>
          </select>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-700">
            {(currentPage - 1) * rowsPerPage + 1}–{Math.min(currentPage * rowsPerPage, sortedData.length)} of {sortedData.length}
          </span>
          <div className="flex gap-2">
            <Button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              variant="outline"
              size="sm"
            >
              Previous
            </Button>
            <Button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              variant="outline"
              size="sm"
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConflictIndexTable;
