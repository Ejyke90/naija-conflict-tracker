import type { NextPage } from 'next';
import Head from 'next/head';
import { Suspense } from 'react';
import { ProfessionalLayout } from '../../components/layouts/ProfessionalLayout';
import { ConflictDashboard } from '../../components/dashboard/ConflictDashboard';
import ProtectedRoute from '../../components/ProtectedRoute';
import ErrorBoundary from '../../components/ErrorBoundary';

// Loading component for Suspense fallback
const DashboardLoading = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <svg
        className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4"
        viewBox="0 0 24 24"
        fill="none"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <p className="text-gray-600">Loading dashboard...</p>
    </div>
  </div>
);

const Dashboard: NextPage = () => {
  return (
    <ErrorBoundary>
      <ProtectedRoute requiredRole="viewer">
        <Head>
          <title>Dashboard - Nextier Nigeria Conflict Tracker</title>
          <meta name="description" content="Nextier's real-time conflict tracking and forecasting for Nigeria" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <ProfessionalLayout>
          <Suspense fallback={<DashboardLoading />}>
            <ConflictDashboard />
          </Suspense>
        </ProfessionalLayout>
      </ProtectedRoute>
    </ErrorBoundary>
  );
};

export default Dashboard;
