import type { NextPage } from 'next';
import Head from 'next/head';
import { CommandCenterDashboard } from '../components/dashboard/CommandCenterDashboard';

const Home: NextPage = () => {
  return (
    <>
      <Head>
        <title>Nextier Nigeria Conflict Tracker</title>
        <meta name="description" content="Nextier's real-time conflict tracking and forecasting for Nigeria" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <CommandCenterDashboard />
    </>
  );
};

export default Home;
