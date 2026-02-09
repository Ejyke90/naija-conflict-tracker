import type { NextPage } from 'next';
import Head from 'next/head';
import React from 'react';
import ProtectedRoute from '../components/ProtectedRoute';

const ConflictDashboardPage: NextPage = () => {
  React.useEffect(() => {
    // Redirect to main dashboard since kidnapping analytics are now integrated
    window.location.href = '/dashboard#kidnapping';
  }, []);

  return (
    <ProtectedRoute requiredRole="viewer">
      <Head>
        <title>Redirecting to Dashboard...</title>
        <meta name="description" content="Redirecting to main dashboard" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to main dashboard...</p>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default ConflictDashboardPage;
