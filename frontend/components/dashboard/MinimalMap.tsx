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

// State Coordinates Dictionary for Geocoding Fallback
const NIGERIA_STATES: { [key: string]: [number, number] } = {
  "Abia": [5.4527, 7.5248],
  "Adamawa": [9.3265, 12.3984],
  "Akwa Ibom": [5.0515, 7.8567],
  "Anambra": [6.2209, 7.0684],
  "Bauchi": [10.7761, 9.7709],
  "Bayelsa": [4.7719, 6.0699],
  "Benue": [7.3307, 8.2176],
  "Borno": [11.8333, 13.1500],
  "Cross River": [5.8702, 8.5988],
  "Delta": [5.8904, 5.6806],
  "Ebonyi": [6.2649, 8.0137],
  "Edo": [6.5438, 5.8963],
  "Ekiti": [7.6674, 5.3783],
  "Enugu": [6.5364, 7.4356],
  "FCT": [9.0765, 7.3986],
  "Abuja": [9.0765, 7.3986],
  "Gombe": [10.2897, 11.1712],
  "Imo": [5.5720, 7.0588],
  "Jigawa": [12.2280, 9.5616],
  "Kaduna": [10.6093, 7.4295],
  "Kano": [11.9961, 8.5167],
  "Katsina": [12.9616, 7.6223],
  "Kebbi": [11.4942, 4.2302],
  "Kogi": [7.7337, 6.6906],
  "Kwara": [8.9669, 4.6031],
  "Lagos": [6.5244, 3.3792],
  "Nasarawa": [8.5381, 8.5721],
  "Niger": [9.9309, 5.5983],
  "Ogun": [7.1604, 3.3483],
  "Ondo": [7.2508, 5.1931],
  "Osun": [7.5629, 4.5200],
  "Oyo": [8.1574, 3.6147],
  "Plateau": [9.2182, 9.1107],
  "Rivers": [4.8156, 7.0498],
  "Sokoto": [13.0627, 5.2432],
  "Taraba": [8.8937, 11.3614],
  "Yobe": [12.0000, 11.5000],
  "Zamfara": [12.1222, 6.2236]
};

// Define props for the map
interface MinimalMapProps {
  incidents?: any[];
}

const MinimalMap: React.FC<MinimalMapProps> = ({ incidents = [] }) => {
    // Helper to get coordinates from location string
    const getCoords = (location: string, id: string | number): [number, number] => {
        // Try to find state name in location string
        const stateEntry = Object.entries(NIGERIA_STATES).find(([state]) => 
            location.toLowerCase().includes(state.toLowerCase())
        );

        if (stateEntry) {
            const [baseLat, baseLng] = stateEntry[1];
            // Deterministic jitter based on ID to prevent exact overlap
            const idNum = typeof id === 'string' ? parseInt(id.replace(/\D/g, '') || '0') : id;
            const jitterLat = (idNum % 100 - 50) / 1000;
            const jitterLng = (idNum % 100 - 50) / 1000;
            return [baseLat + jitterLat, baseLng + jitterLng];
        }
        
        // Default fallback (Abuja)
        return [9.0765, 7.3986];
    };

  return (
    <div style={{ height: '100%', width: '100%' }}>
      <MapContainer 
        center={[9.0820, 8.6753]} 
        zoom={6} 
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
        className="z-0"
      >
        <TileLayer
          url={`https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`}
          attribution='&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        {/* Render dynamically passed incidents if available */}
        {incidents.length > 0 ? (
           incidents.map((incident) => (
             <Marker 
                key={incident.id} 
                position={getCoords(incident.location, incident.id)}
            >
            <Popup>
                <div className="text-sm font-semibold">{incident.type}</div>
                <div className="text-xs font-medium text-slate-700">{incident.location}</div>
                <div className="text-xs text-slate-500 mt-1">{incident.details}</div>
                <div className="text-[10px] text-slate-400 mt-1">{incident.time}</div>
            </Popup>
            </Marker>
           ))
        ) : (
          /* Demo Marker if no data */
          <Marker position={[9.0765, 7.3986]}>
            <Popup>
                <div className="text-sm font-semibold">Incident Cluster</div>
                <div className="text-xs">Abuja Central Area</div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
};

export default MinimalMap;
