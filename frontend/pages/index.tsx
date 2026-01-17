import { GetServerSideProps } from 'next';
import type { NextPage } from 'next';
import Head from 'next/head';
import DashboardLayout from '../components/layouts/DashboardLayout';
import StatsOverview from '../components/dashboard/StatsOverview';
import ConflictMap from '../components/maps/ConflictMap';
import RecentIncidents from '../components/dashboard/RecentIncidents';
import TrendsChart from '../components/charts/TrendsChart';
import RiskAssessment from '../components/dashboard/RiskAssessment';

const Home: NextPage = () => {
  return (
    <>
      <Head>
        <title>Nigeria Conflict Tracker</title>
        <meta name="description" content="Real-time conflict tracking and forecasting for Nigeria" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <DashboardLayout>
        <div className="space-y-6">
          {/* Header */}
          <div className="bg-white shadow-sm border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
              <h1 className="text-3xl font-bold text-gray-900">
                Nigeria Conflict Tracker
              </h1>
              <p className="mt-2 text-gray-600">
                Real-time monitoring and analysis of conflicts across Nigeria
              </p>
            </div>
          </div>

          {/* Stats Overview */}
          <StatsOverview />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Map - Takes 2 columns */}
            <div className="lg:col-span-2">
              <ConflictMap />
            </div>

            {/* Side Panel */}
            <div className="space-y-6">
              <RiskAssessment />
              <RecentIncidents />
            </div>
          </div>

          {/* Trends Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TrendsChart title="Monthly Conflict Trends" type="line" />
            <TrendsChart title="Conflicts by State" type="bar" />
          </div>
        </div>
      </DashboardLayout>
    </>
  );
};

export default Home;

export const getServerSideProps: GetServerSideProps = async (context) => {
  // You can fetch initial data here if needed
  return {
    props: {}, // will be passed as props to the page component
  };
};
