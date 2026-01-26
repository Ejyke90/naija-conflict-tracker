import React, { useEffect, useState } from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { motion } from 'framer-motion';

const GEO_URL = "/data/nigeria-states.json";

interface NigeriaMapProps {
  stateData?: Array<{
    name: string;
    incidents: number;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export const NigeriaMap: React.FC<NigeriaMapProps> = ({ stateData = [] }) => {
  const [geoData, setGeoData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('Loading map data...');
    fetch(GEO_URL)
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Failed to load geojson: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log('Map data loaded successfully:', {
          type: data.type,
          features: data.features?.length || 0,
          firstFeature: data.features?.[0]?.properties
        });
        setGeoData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error loading map data:", err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const getStateColor = (stateName: string) => {
    const state = stateData.find(s => 
      s.name.toLowerCase() === stateName.toLowerCase()
    );
    
    if (!state) return '#64748B'; // Better visible gray for states without data
    
    switch (state.severity) {
      case 'high':
        return '#DC2626'; // Red
      case 'medium':
        return '#F59E0B'; // Orange
      case 'low':
        return '#10B981'; // Green
      default:
        return '#64748B'; // Slate gray
    }
  };

  if (loading) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-gray-400">Loading map...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-red-400">Error loading map: {error}</div>
      </div>
    );
  }

  if (!geoData) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <div className="text-gray-400">No map data available</div>
      </div>
    );
  }

  return (
    <div
      className="w-full h-full relative"
    >
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          center: [8, 9.5],
          scale: 2200
        }}
        style={{
          width: '100%',
          height: '100%'
        }}
        viewBox="0 0 800 600"
      >
        {geoData && (
          <Geographies geography={geoData}>
            {({ geographies }) =>
              geographies.map((geo) => {
                const stateName = geo.properties.shapeName
                  || geo.properties.NAME_1 
                  || geo.properties.name 
                || geo.properties.state_name 
                || geo.properties.admin1Name;
              const stateInfo = stateData.find(s => 
                s.name.toLowerCase() === stateName?.toLowerCase()
              );
              const severityClass = stateInfo?.severity === 'high'
                ? 'map-pulse-strong'
                : stateInfo?.severity === 'medium'
                ? 'map-pulse-soft'
                : '';

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={getStateColor(stateName)}
                  stroke="#1e293b"
                  strokeWidth={1.5}
                  className={`cursor-pointer transition-colors duration-200 ${severityClass}`}
                  style={{
                    default: {
                      fill: getStateColor(stateName),
                      stroke: '#1e293b',
                      strokeWidth: 1.5,
                      outline: 'none'
                    },
                    hover: {
                      fill: '#f97316',
                      stroke: '#ffffff',
                      strokeWidth: 2
                    },
                    pressed: {
                      fill: '#ea580c',
                      stroke: '#ffffff',
                      strokeWidth: 2
                    }
                  }}
                  onMouseEnter={() => {
                    // Could show tooltip here
                  }}
                />
              );
            })
          }
          </Geographies>
        )}
      </ComposableMap>

      {/* Legend */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg p-4">
        <div className="text-xs font-semibold text-gray-700 mb-2">Risk Level</div>
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-red-600"></div>
            <span className="text-xs text-gray-600">High (&gt;20 incidents)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-orange-500"></div>
            <span className="text-xs text-gray-600">Medium (10-20)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-xs text-gray-600">Low (&lt;10)</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded-full bg-gray-300"></div>
            <span className="text-xs text-gray-600">No data</span>
          </div>
        </div>
      </div>

      <style jsx global>{`
        @keyframes mapPulse {
          0% { filter: drop-shadow(0 0 0 rgba(255, 75, 75, 0.12)); }
          50% { filter: drop-shadow(0 0 14px rgba(255, 75, 75, 0.55)); }
          100% { filter: drop-shadow(0 0 0 rgba(255, 75, 75, 0.12)); }
        }
        .map-pulse-strong {
          animation: mapPulse 2.4s ease-in-out infinite;
        }
        .map-pulse-soft {
          animation: mapPulse 3.2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
};
