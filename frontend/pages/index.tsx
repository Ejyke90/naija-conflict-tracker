import type { NextPage } from 'next';
import Head from 'next/head';
import { useAuth } from '../contexts/AuthContext';
import { ProfessionalLayout } from '../components/layouts/ProfessionalLayout';
import { ConflictDashboard } from '../components/dashboard/ConflictDashboard';
import { LandingPage } from '../components/landing/LandingPage';
import ProtectedRoute from '../components/ProtectedRoute';

const Home: NextPage = () => {
  const { user, isLoading } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Show landing page for unauthenticated users
  if (!user) {
    return (
      <>
        <Head>
          <title>Nextier Nigeria Conflict Tracker</title>
          <meta name="description" content="Real-time monitoring and predictive analytics for conflict incidents across Nigeria" />
          <meta name="viewport" content="width=device-width, initial-scale=1.0" />
          <link rel="icon" href="/favicon.ico" />
        </Head>
        <LandingPage />
      </>
    );
  }

  // Show protected dashboard for authenticated users
  return (
    <ProtectedRoute requiredRole="analyst">
      <Head>
        <title>Dashboard - Nextier Nigeria Conflict Tracker</title>
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
