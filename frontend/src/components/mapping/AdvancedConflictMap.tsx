import React from 'react';
import dynamic from 'next/dynamic';
import L from 'leaflet';

// Dynamically import MapContainer and related components with SSR disabled
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });
const GeoJSON = dynamic(() => import('react-leaflet').then(mod => mod.GeoJSON), { ssr: false });

import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon issue
if (typeof window !== 'undefined') {
  delete (L.Icon.Default.prototype as any)._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

const AdvancedConflictMap: React.FC = () => {
  const [geoJsonData, setGeoJsonData] = React.useState(null);

  React.useEffect(() => {
    fetch('/data/nigeria-states.json')
      .then((res) => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => setGeoJsonData(data))
      .catch((err) => console.error('Error loading GeoJSON:', err));
  }, []);

  const geoJSONStyle = {
    fillColor: '#ef4444',
    weight: 1,
    opacity: 1,
    color: '#ef4444',
    dashArray: '3',
    fillOpacity: 0.1,
  };

  return (
    <div className="card">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold text-gray-900">Advanced Conflict Map</h2>
        <div className="flex space-x-2">
          <button className="btn btn-secondary text-sm">Spatial Analysis</button>
          <button className="btn btn-secondary text-sm">Heatmap</button>
          <button className="btn btn-primary text-sm">Export</button>
        </div>
      </div>

      <div className="bg-gray-100 rounded-lg h-96">
        <MapContainer center={[9.0820, 8.6753]} zoom={6} style={{ height: '100%', width: '100%' }}>
          {geoJsonData && <GeoJSON data={geoJsonData} style={geoJSONStyle} />}
          <TileLayer
            url={`https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`}
            attribution='&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <Marker position={[9.0820, 8.6753]}>
            <Popup>
              Advanced conflict data visualization with spatial analysis capabilities.
            </Popup>
          </Marker>
        </MapContainer>
      </div>

      <div className="mt-4 flex justify-between text-sm text-gray-600">
        <span>📍 Advanced spatial queries enabled</span>
        <span>🔄 PostGIS integration active</span>
      </div>
    </div>
  );
};

export default AdvancedConflictMap;
