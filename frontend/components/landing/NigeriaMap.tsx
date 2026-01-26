import React from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { motion } from 'framer-motion';

// Localized Nigeria ADM1 boundaries (geoBoundaries simplified)
const NIGERIA_TOPO_URL = "/data/nigeria-states.json";

interface NigeriaMapProps {
  stateData?: Array<{
    name: string;
    incidents: number;
    severity: 'low' | 'medium' | 'high';
  }>;
}

export const NigeriaMap: React.FC<NigeriaMapProps> = ({ stateData = [] }) => {
  const getStateColor = (stateName: string) => {
    const state = stateData.find(s => 
      s.name.toLowerCase() === stateName.toLowerCase()
    );
    
    if (!state) return '#E5E7EB'; // Gray for no data
    
    switch (state.severity) {
      case 'high':
        return '#DC2626'; // Red
      case 'medium':
        return '#F59E0B'; // Orange
      case 'low':
        return '#10B981'; // Green
      default:
        return '#E5E7EB';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, delay: 0.6 }}
      className="w-full h-full relative"
    >
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          center: [8, 9],
          scale: 2000
        }}
        className="w-full h-full"
      >
        <Geographies geography={NIGERIA_TOPO_URL}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const stateName = geo.properties.NAME_1 
                || geo.properties.name 
                || geo.properties.shapeName 
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
                  stroke="#FFFFFF"
                  strokeWidth={0.5}
                  className={`cursor-pointer ${severityClass}`}
                  style={{
                    default: {
                      fill: getStateColor(stateName),
                      stroke: '#FFFFFF',
                      strokeWidth: 0.5,
                      outline: 'none',
                      transition: 'all 250ms'
                    },
                    hover: {
                      fill: getStateColor(stateName),
                      stroke: '#1E40AF',
                      strokeWidth: 1.5,
                      outline: 'none',
                      filter: 'brightness(1.1)'
                    },
                    pressed: {
                      fill: getStateColor(stateName),
                      stroke: '#1E40AF',
                      strokeWidth: 1.5,
                      outline: 'none'
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
    </motion.div>
  );
};
