import type { NextPage } from 'next';
import Head from 'next/head';
import { Suspense, lazy } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { Skeleton } from '@/components/ui/skeleton';
import { MapPin } from 'lucide-react';

const StateRankingTable = lazy(() => import('@/components/analytics/StateRankingTable'));

const StatesPage: NextPage = () => {
  return (
    <ProtectedRoute requiredRole="viewer">
      <Head>
        <title>State Analysis - Naija Conflict Tracker</title>
        <meta name="description" content="State-level conflict analysis for Nigeria" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center gap-3">
              <MapPin className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">State-Level Analysis</h1>
                <p className="text-sm text-gray-600 mt-1">
                  Comprehensive conflict metrics for all Nigerian states
                </p>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Suspense fallback={
            <div className="space-y-4">
              <Skeleton className="h-96" />
            </div>
          }>
            <StateRankingTable monthsBack={12} limit={37} />
          </Suspense>
        </main>
      </div>
    </ProtectedRoute>
  );
};

export default StatesPage;
