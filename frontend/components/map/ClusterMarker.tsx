import React from 'react';
import { Marker } from 'react-map-gl';

interface ClusterMarkerProps {
  longitude: number;
  latitude: number;
  pointCount: number;
  onClick: () => void;
}

/**
 * Cluster marker component for grouped events
 */
export const ClusterMarker: React.FC<ClusterMarkerProps> = ({
  longitude,
  latitude,
  pointCount,
  onClick,
}) => {
  // Size based on point count
  const size = Math.min(50 + (pointCount / 10) * 5, 80);

  return (
    <Marker longitude={longitude} latitude={latitude} anchor="center">
      <div
        className="cursor-pointer transition-transform hover:scale-110"
        onClick={(e) => {
          e.stopPropagation();
          onClick();
        }}
        style={{
          width: size,
          height: size,
        }}
      >
        {/* Outer circle */}
        <div
          className="rounded-full bg-orange-500 opacity-30 absolute inset-0"
          style={{
            width: size,
            height: size,
          }}
        />
        
        {/* Middle circle */}
        <div
          className="rounded-full bg-orange-600 opacity-50 absolute"
          style={{
            width: size * 0.7,
            height: size * 0.7,
            left: size * 0.15,
            top: size * 0.15,
          }}
        />
        
        {/* Inner circle with count */}
        <div
          className="rounded-full bg-orange-700 shadow-lg flex items-center justify-center text-white font-bold absolute"
          style={{
            width: size * 0.5,
            height: size * 0.5,
            left: size * 0.25,
            top: size * 0.25,
            fontSize: size * 0.25,
          }}
        >
          {pointCount}
        </div>
      </div>
    </Marker>
  );
};
