import type { NextPage } from 'next';
import Head from 'next/head';
import { Suspense } from 'react';
import { CommandCenterDashboard } from '../../components/dashboard/CommandCenterDashboard';

// Loading component for Suspense fallback
const DashboardLoading = () => (
  <div className="min-h-screen flex items-center justify-center command-center-bg">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
      <p className="text-slate-300">Loading Command Center...</p>
    </div>
  </div>
);

const CommandCenter: NextPage = () => {
  return (
    <>
      <Head>
        <title>Command Center - Naija Conflict Tracker</title>
        <meta name="description" content="High-fidelity command center for real-time conflict monitoring and predictive analytics" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* <Suspense fallback={<DashboardLoading />}> */}
        <CommandCenterDashboard />
      {/* </Suspense> */}
    </>
  );
};

export default CommandCenter;