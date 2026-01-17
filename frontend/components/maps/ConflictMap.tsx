import React from 'react';

const ConflictMap: React.FC = () => {
  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Conflict Map</h2>
        <div className="flex space-x-2">
          <button className="btn btn-secondary text-sm">Filter</button>
          <button className="btn btn-primary text-sm">Export</button>
        </div>
      </div>
      
      <div className="bg-gray-100 rounded-lg h-96 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🗺️</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Interactive Map</h3>
          <p className="text-gray-600 mb-4">
            Map visualization will appear here once Mapbox token is configured
          </p>
          <div className="text-sm text-gray-500">
            Configure NEXT_PUBLIC_MAPBOX_TOKEN in .env.local
          </div>
        </div>
      </div>
      
      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>📍 Click markers for details</span>
        <span>🔄 Last updated: 2 minutes ago</span>
      </div>
    </div>
  );
};

export default ConflictMap;
