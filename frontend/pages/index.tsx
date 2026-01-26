import type { NextPage } from 'next';
import Head from 'next/head';
import { ProfessionalLayout } from '../components/layouts/ProfessionalLayout';
import { ConflictDashboard } from '../components/dashboard/ConflictDashboard';
import ProtectedRoute from '../components/ProtectedRoute';

const Home: NextPage = () => {
  return (
    <ProtectedRoute requiredRole="analyst">
      <Head>
        <title>Nextier Nigeria Conflict Tracker</title>
        <meta name="description" content="Nextier's real-time conflict tracking and forecasting for Nigeria" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <ProfessionalLayout>
        <ConflictDashboard />
      </ProfessionalLayout>
    </ProtectedRoute>
  );
};

export default Home;
