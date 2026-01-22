import React, { useEffect } from 'react';
import dynamic from 'next/dynamic';
import L from 'leaflet';

// Dynamically import MapContainer and related components with SSR disabled
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });

// Leaflet CSS must be imported in _app.tsx or globals.css in Next.js
// Removing it from here to avoid "Global CSS cannot be imported from files other than your Custom <App>" error.

// Fix Leaflet default marker icon issue
if (typeof window !== 'undefined') {
    // @ts-ignore
  delete (L.Icon.Default.prototype)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

// Define props for the map
interface MinimalMapProps {
  incidents?: any[];
}

const MinimalMap: React.FC<MinimalMapProps> = ({ incidents = [] }) => {
    // Custom styled tiles (CartoDB Voyager) for a cleaner look that fits the dashboard
    // or standard OSM. Carbon/Dark styles look good for "Command Centers" but user asked for "bg-slate-50"/light theme mostly.
    // Let's stick to a clean light map.

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer 
        center={[9.0820, 8.6753]} 
        zoom={6} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={false} // clean look, user can scroll or we add custom controls
        className="z-0"
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        {/* Render dynamically passed incidents if available, otherwise fall back to demo markers */}
        {incidents.length > 0 ? (
           incidents.map((incident) => {
             // Simple geocoding fallback for demo if coordinates missing (replace with real lat/lng from API)
             // For now we assume some incidents might not have lat/lng until geocoding is perfect
             // We'll distribute them randomly around center for visual demo if real coords missing
             return (
               <Marker 
                  key={incident.id} 
                  position={[
                      // Use incident coordinates if available, else random offset from Abuja
                      incident.lat || 9.0820 + (Math.random() - 0.5) * 5, 
                      incident.lng || 8.6753 + (Math.random() - 0.5) * 5
                  ]}
                >
                <Popup>
                   <div className="text-sm font-semibold">{incident.type}</div>
                   <div className="text-xs">{incident.location}</div>
                   <div className="text-xs text-slate-500 mt-1">{incident.details}</div>
                </Popup>
              </Marker>
             );
           })
        ) : (
          <>
            <Marker position={[9.0820, 8.6753]}>
            <Popup>
                <div className="text-sm font-semibold">Incident Cluster</div>
                <div className="text-xs">Abuja Central Area</div>
            </Popup>
            </Marker>
            <Marker position={[6.5244, 3.3792]}>
            <Popup>
                <div className="text-sm font-semibold">Lagos Report</div>
            </Popup>
            </Marker>
          </>
        )}
      </MapContainer>
    </div>
  );
};

export default MinimalMap;
