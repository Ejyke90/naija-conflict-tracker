import React from 'react';
import { ComposableMap, Geographies, Geography } from 'react-simple-maps';
import { motion } from 'framer-motion';

// Nigeria ADM1 boundaries from geoBoundaries (stable public source)
const NIGERIA_TOPO_URL = "https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/releaseData/gbOpen/NGA/ADM1/geoBoundaries-NGA-ADM1.geojson";

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

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={getStateColor(stateName)}
                  stroke="#FFFFFF"
                  strokeWidth={0.5}
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
                  className="cursor-pointer"
                  onMouseEnter={() => {
                    // Could show tooltip here
                  }}
                />
              );
            })
          }
        </Geographies>
        
        {/* Pulsing hotspot markers */}
        {stateData
          .filter(s => s.severity === 'high')
          .map((state, idx) => (
            <motion.circle
              key={state.name}
              cx={0}
              cy={0}
              r={4}
              fill="#DC2626"
              initial={{ scale: 0 }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.8, 0.4, 0.8]
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: idx * 0.2
              }}
            />
          ))}
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
    </motion.div>
  );
};
