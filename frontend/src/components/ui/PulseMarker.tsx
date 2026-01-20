import React from 'react';
import { Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { createRoot } from 'react-dom/client';
import PulseAlert from './PulseAlert';

interface ConflictEvent {
  id: string;
  lat: number;
  lng: number;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  fatalities: number;
  date: string;
  location: string;
  description?: string;
}

interface PulseMarkerProps {
  event: ConflictEvent;
}

// Create custom pulse marker icon
const createPulseIcon = (severity: string) => {
  const colorMap = {
    critical: '#ef4444', // Red
    high: '#f97316',    // Orange  
    medium: '#eab308',  // Yellow
    low: '#22c55e'      // Green
  };

  const intensityMap = {
    critical: 'high',
    high: 'high',
    medium: 'medium',
    low: 'low'
  };

  const color = colorMap[severity as keyof typeof colorMap] || '#6b7280';
  const intensity = intensityMap[severity as keyof typeof intensityMap] || 'low';

  // Create a div element for the custom marker
  const div = document.createElement('div');
  div.className = 'pulse-marker-container';
  div.style.cssText = `
    position: relative;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
  `;

  // Only add pulse for high-risk incidents (critical and high)
  if (severity === 'critical' || severity === 'high') {
    const root = createRoot(div);
    root.render(
      <PulseAlert 
        color={color} 
        size="medium" 
        intensity={intensity as 'low' | 'medium' | 'high'} 
      />
    );
  } else {
    // Static marker for low/medium risk
    const staticDot = document.createElement('div');
    staticDot.style.cssText = `
      width: 12px;
      height: 12px;
      background-color: ${color};
      border: 2px solid white;
      border-radius: 50%;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    `;
    div.appendChild(staticDot);
  }

  return L.divIcon({
    html: div.outerHTML,
    className: 'custom-pulse-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20]
  });
};

const PulseMarker: React.FC<PulseMarkerProps> = ({ event }) => {
  const icon = createPulseIcon(event.severity);

  return (
    <Marker
      position={[event.lat, event.lng]}
      icon={icon}
    >
      <Popup>
        <div className="p-2 min-w-[200px]">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-semibold text-gray-900">{event.type}</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${
              event.severity === 'critical' ? 'bg-red-100 text-red-800' :
              event.severity === 'high' ? 'bg-orange-100 text-orange-800' :
              event.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
              'bg-green-100 text-green-800'
            }`}>
              {event.severity.toUpperCase()}
            </span>
          </div>
          
          <div className="space-y-1 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <span>📍</span>
              <span>{event.location}</span>
            </div>
            {event.fatalities > 0 && (
              <div className="flex items-center space-x-2">
                <span>👥</span>
                <span>{event.fatalities} casualties</span>
              </div>
            )}
            <div className="flex items-center space-x-2">
              <span>📅</span>
              <span>{new Date(event.date).toLocaleDateString()}</span>
            </div>
          </div>
          
          {event.description && (
            <p className="mt-2 text-sm text-gray-700">{event.description}</p>
          )}
        </div>
      </Popup>
    </Marker>
  );
};

export default PulseMarker;
