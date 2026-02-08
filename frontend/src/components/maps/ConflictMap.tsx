import React, { useEffect } from 'react';
import dynamic from 'next/dynamic';
import L from 'leaflet';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MapPin, Filter, Download, Clock } from 'lucide-react';

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

interface ConflictMapProps {
  fullscreen?: boolean;
}

const ConflictMap: React.FC<ConflictMapProps> = ({ fullscreen = false }) => {
  const [geoJsonData, setGeoJsonData] = React.useState(null);

  useEffect(() => {
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
    fillColor: '#3b82f6',
    weight: 1,
    opacity: 1,
    color: '#3b82f6',
    dashArray: '3',
    fillOpacity: 0.1,
  };

  if (fullscreen) {
    return (
      <div className="h-full w-full">
        <MapContainer center={[9.0820, 8.6753]} zoom={6} style={{ height: '100%', width: '100%' }}>
          {geoJsonData && <GeoJSON data={geoJsonData} style={geoJSONStyle} />}
          <TileLayer
            url={`https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`}
            attribution='&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <Marker position={[9.0820, 8.6753]}>
            <Popup>
              A sample marker. Replace with real conflict data.
            </Popup>
          </Marker>
        </MapContainer>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5 text-blue-600" />
                Conflict Map
              </CardTitle>
              <CardDescription className="mt-1">
                Geographic distribution of conflict incidents
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" aria-label="Filter map data">
                <Filter className="h-4 w-4 mr-1" />
                Filter
              </Button>
              <Button variant="default" size="sm" aria-label="Export map data">
                <Download className="h-4 w-4 mr-1" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <motion.div
            className="bg-muted rounded-lg h-96 overflow-hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <MapContainer 
              center={[9.0820, 8.6753]} 
              zoom={6} 
              style={{ height: '100%', width: '100%' }}
              aria-label="Interactive map showing conflict locations in Nigeria"
            >
              {geoJsonData && <GeoJSON data={geoJsonData} style={geoJSONStyle} />}
              <TileLayer
                url={`https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`}
                attribution='&copy; <a href="https://www.mapbox.com/about/maps/">Mapbox</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              />
              <Marker position={[9.0820, 8.6753]}>
                <Popup>
                  A sample marker. Replace with real conflict data.
                </Popup>
              </Marker>
            </MapContainer>
          </motion.div>
          
          <div className="mt-4 flex justify-between items-center text-sm">
            <div className="flex items-center gap-2 text-muted-foreground">
              <MapPin className="h-4 w-4" />
              <span>Click markers for details</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="secondary" className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                Updated 2 mins ago
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ConflictMap;
