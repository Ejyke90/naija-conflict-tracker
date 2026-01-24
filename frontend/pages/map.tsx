import type { NextPage } from 'next';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import { ProfessionalLayout } from '../components/layouts/ProfessionalLayout';

// Dynamic import to avoid SSR issues with mapbox
const ConflictMap = dynamic(() => import('../components/map/ConflictMap'), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-full bg-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-700 font-medium">Loading map...</p>
      </div>
    </div>
  ),
});

const MapPage: NextPage = () => {
  return (
    <>
      <Head>
        <title>Interactive Conflict Map | Nextier Nigeria Conflict Tracker</title>
        <meta
          name="description"
          content="Interactive map of conflict events across Nigeria with real-time data"
        />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      <ProfessionalLayout>
        <div className="h-[calc(100vh-4rem)]">
          <ConflictMap fullscreen />
        </div>
      </ProfessionalLayout>
    </>
  );
};

export default MapPage;
