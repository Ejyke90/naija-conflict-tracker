import type { NextPage } from 'next';
import Head from 'next/head';
import LandingPage from '../components/landing/LandingPage';

const Home: NextPage = () => {
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
};

export default Home;
