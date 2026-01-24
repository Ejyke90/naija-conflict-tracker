import React from 'react';
import { Marker } from 'react-map-gl';
import { getEventColor, getMarkerSize } from '../../lib/map/colors';
import type { ConflictEvent } from '../../lib/map/clustering';

interface EventMarkerProps {
  event: ConflictEvent;
  onClick: (event: ConflictEvent) => void;
}

/**
 * Custom marker component for individual conflict events
 */
export const EventMarker: React.FC<EventMarkerProps> = ({ event, onClick }) => {
  const color = getEventColor(event.event_type);
  const size = getMarkerSize(event.fatalities);

  return (
    <Marker
      longitude={event.longitude}
      latitude={event.latitude}
      anchor="center"
      onClick={(e) => {
        e.originalEvent.stopPropagation();
        onClick(event);
      }}
    >
      <div
        className="cursor-pointer transition-transform hover:scale-125"
        style={{
          width: size,
          height: size,
        }}
      >
        {/* Outer pulse ring for high-fatality events */}
        {event.fatalities >= 10 && (
          <div
            className="absolute inset-0 rounded-full animate-ping opacity-75"
            style={{
              backgroundColor: color,
              width: size + 8,
              height: size + 8,
              left: -4,
              top: -4,
            }}
          />
        )}
        
        {/* Main marker circle */}
        <div
          className="rounded-full shadow-lg border-2 border-white relative z-10"
          style={{
            backgroundColor: color,
            width: size,
            height: size,
          }}
        >
          {/* Inner dot for emphasis */}
          <div
            className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 rounded-full bg-white opacity-30"
            style={{
              width: size / 3,
              height: size / 3,
            }}
          />
        </div>
      </div>
    </Marker>
  );
};
