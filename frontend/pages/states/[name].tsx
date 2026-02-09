import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { ArrowLeft, TrendingUp, AlertTriangle, MapPin, Users } from 'lucide-react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface StateOverviewData {
  stateName: string;
  metadata: {
    population: number;
    poverty_rate: number;
    unemployment_rate: number;
  };
  monthlyTrends: Array<{
    month: string;
    incidents: number;
    fatalities: number;
  }>;
  hotspots: Array<{
    lga: string;
    incident_count: number;
    fatalities: number;
    displaced: number;
  }>;
  conflictTypes: Array<{
    type_name: string;
    incidents: number;
    fatalities: number;
  }>;
  statistics: {
    total_incidents: number;
    total_fatalities: number;
    total_injuries: number;
    total_kidnapped: number;
    affected_lgas: number;
  };
}

const StateDetailPage = () => {
  const router = useRouter();
  const { name } = router.query;
  const [data, setData] = useState<StateOverviewData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [monthsBack, setMonthsBack] = useState(12);

  useEffect(() => {
    if (!name) return;

    const fetchStateData = async () => {
      try {
        setLoading(true);
        
        const response = await fetch(
          `/api/v1/dashboard/state-overview/${name}?months_back=${monthsBack}`
        );

        if (!response.ok) throw new Error('Failed to fetch state data');

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load state data');
      } finally {
        setLoading(false);
      }
    };

    fetchStateData();
  }, [name, monthsBack]);

  if (loading) {
    return (
      <ProtectedRoute requiredRole="viewer">
        <div className="min-h-screen bg-gray-50 p-8">
          <Skeleton className="h-12 w-1/3 mb-8" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
            <Skeleton className="h-32" />
          </div>
          <Skeleton className="h-96" />
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !data) {
    return (
      <ProtectedRoute requiredRole="viewer">
        <div className="min-h-screen bg-gray-50 p-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <AlertTriangle className="h-8 w-8 text-red-600 mb-2" />
            <p className="text-red-800">Error: {error || 'State not found'}</p>
            <Link href="/states" className="text-blue-600 hover:underline mt-2 inline-block">
              Return to States Overview
            </Link>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute requiredRole="viewer">
      <Head>
        <title>{name} State - Conflict Analysis</title>
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
              <Link href="/dashboard" className="hover:text-blue-600">Dashboard</Link>
              <span>/</span>
              <Link href="/states" className="hover:text-blue-600">States</Link>
              <span>/</span>
              <span className="text-gray-900 font-medium">{name}</span>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Link
                  href="/states"
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <ArrowLeft className="h-4 w-4" />
                  <span className="text-sm">Back to States</span>
                </Link>

                <div>
                  <h1 className="text-3xl font-bold text-gray-900">{name} State</h1>
                  <p className="text-sm text-gray-600 mt-1">
                    Detailed conflict analysis and trends
                  </p>
                </div>
              </div>

              {/* Time Range Selector */}
              <select
                value={monthsBack}
                onChange={(e) => setMonthsBack(Number(e.target.value))}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm"
              >
                <option value={6}>Last 6 months</option>
                <option value={12}>Last 12 months</option>
                <option value={24}>Last 24 months</option>
                <option value={36}>Last 36 months</option>
              </select>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
          {/* Overview KPI Cards */}
          <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-red-100 rounded-lg p-3">
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Incidents</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.statistics.total_incidents.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-orange-100 rounded-lg p-3">
                    <Users className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Total Fatalities</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.statistics.total_fatalities.toLocaleString()}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-blue-100 rounded-lg p-3">
                    <MapPin className="h-6 w-6 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Affected LGAs</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.statistics.affected_lgas}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center gap-3">
                  <div className="bg-purple-100 rounded-lg p-3">
                    <Users className="h-6 w-6 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Population</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {data.metadata.population?.toLocaleString() || 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Hotspot LGAs */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Top Conflict Hotspots (LGAs)</h2>
            <Card>
              <CardContent className="p-6">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left font-semibold text-gray-700">LGA</th>
                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Incidents</th>
                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Fatalities</th>
                        <th className="px-4 py-3 text-right font-semibold text-gray-700">Displaced</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {data.hotspots.map((lga, index) => (
                        <tr key={lga.lga} className="hover:bg-gray-50">
                          <td className="px-4 py-3 font-medium text-gray-900">{lga.lga}</td>
                          <td className="px-4 py-3 text-right text-gray-700">{lga.incident_count}</td>
                          <td className="px-4 py-3 text-right text-gray-700">{lga.fatalities}</td>
                          <td className="px-4 py-3 text-right text-gray-700">{lga.displaced}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </section>

          {/* Conflict Types */}
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Conflict Type Breakdown</h2>
            <Card>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {data.conflictTypes.map((type) => (
                    <div key={type.type_name} className="flex items-center justify-between">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{type.type_name || 'Unknown'}</p>
                        <div className="mt-1 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 rounded-full h-2"
                            style={{
                              width: `${(type.incidents / data.statistics.total_incidents) * 100}%`
                            }}
                          ></div>
                        </div>
                      </div>
                      <div className="ml-4 text-right">
                        <p className="text-sm font-semibold text-gray-900">{type.incidents} incidents</p>
                        <p className="text-xs text-gray-600">{type.fatalities} fatalities</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </section>
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default StateDetailPage;
