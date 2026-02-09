import type { NextPage } from 'next';
import Head from 'next/head';
import React from 'react';
import ProtectedRoute from '../components/ProtectedRoute';
import { ConflictDashboard } from '../src/components/dashboard/ConflictDashboard';

const ConflictDashboardPage: NextPage = () => {
  return (
    <ProtectedRoute requiredRole="viewer">
      <Head>
        <title>Conflict Dashboard - Nextier Nigeria Conflict Tracker</title>
        <meta name="description" content="Comprehensive conflict monitoring dashboard with kidnapping analytics" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <ConflictDashboard />
    </ProtectedRoute>
  );
};

export default ConflictDashboardPage;
