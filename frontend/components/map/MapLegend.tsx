import React from 'react';
import { LEGEND_ITEMS, SIZE_LEGEND } from '../../lib/map/colors';

interface MapLegendProps {
  className?: string;
}

/**
 * Map legend showing event types and fatality size indicators
 */
export const MapLegend: React.FC<MapLegendProps> = ({ className = '' }) => {
  return (
    <div className={`bg-white shadow-lg rounded-lg p-4 ${className}`}>
      <h3 className="font-semibold text-gray-900 text-sm mb-3">Legend</h3>

      {/* Event Types */}
      <div className="mb-4">
        <p className="text-xs font-medium text-gray-700 mb-2">Event Types</p>
        <div className="space-y-1.5">
          {LEGEND_ITEMS.map((item) => (
            <div key={item.label} className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full border border-white shadow-sm flex-shrink-0"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs text-gray-700">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Fatality Size */}
      <div>
        <p className="text-xs font-medium text-gray-700 mb-2">Marker Size (Fatalities)</p>
        <div className="space-y-1.5">
          {SIZE_LEGEND.map((item) => (
            <div key={item.label} className="flex items-center space-x-2">
              <div
                className="rounded-full bg-gray-400 border border-white shadow-sm flex-shrink-0"
                style={{
                  width: item.size,
                  height: item.size,
                }}
              />
              <span className="text-xs text-gray-700">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Cluster Indicator */}
      <div className="mt-4 pt-4 border-t">
        <div className="flex items-center space-x-2">
          <div className="relative" style={{ width: 32, height: 32 }}>
            <div className="absolute inset-0 rounded-full bg-orange-500 opacity-30" />
            <div className="absolute rounded-full bg-orange-700 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: 20, height: 20, left: 6, top: 6 }}>
              5
            </div>
          </div>
          <span className="text-xs text-gray-700">Clustered events</span>
        </div>
      </div>
    </div>
  );
};
