import React from 'react';
import dynamic from 'next/dynamic';
import Link from 'next/link';

// Dynamic import for the map to avoid SSR issues
const ConflictMap = dynamic(() => import('./map/ConflictMap'), {
  ssr: false,
  loading: () => (
    <div className="h-96 bg-gray-100 rounded-lg flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
        <p className="text-gray-600 text-sm">Loading interactive map...</p>
      </div>
    </div>
  ),
});

/**
 * Dashboard Map Widget
 * 
 * Embeddable map component for the main dashboard
 * Shows a compact version of the conflict map with basic controls
 */
export const DashboardMapWidget: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Conflict Map</h2>
            <p className="text-sm text-gray-600 mt-1">
              Real-time visualization of conflict events
            </p>
          </div>
          <Link
            href="/map"
            className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline"
          >
            View Fullscreen →
          </Link>
        </div>
      </div>
      
      <div className="h-[500px]">
        <ConflictMap />
      </div>
    </div>
  );
};

export default DashboardMapWidget;
