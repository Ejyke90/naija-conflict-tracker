import React, { useState, useEffect, useMemo } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, LayersControl, GeoJSON } from 'react-leaflet';
import { LatLngExpression } from 'leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// import { HeatmapLayer } from 'react-leaflet-heatmap-layer'; // Temporarily disabled for deployment
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import PulseAlert from '@/components/ui/PulseAlert';
import PulseMarker from '@/components/ui/PulseMarker';
import { 
  Layers, 
  Filter, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  AlertTriangle,
  Users,
  MapPin
} from 'lucide-react';

// Fix for default markers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: '/images/marker-icon-2x.png',
  iconUrl: '/images/marker-icon.png',
  shadowUrl: '/images/marker-shadow.png',
});

interface ConflictEvent {
  id: string;
  lat: number;
  lng: number;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  fatalities: number;
  date: string;
  location: string;
  description: string;
}

interface ConflictMapProps {
  fullscreen?: boolean;
  height?: string;
}

export const ConflictMap: React.FC<ConflictMapProps> = ({ 
  fullscreen = false, 
  height = '400px' 
}) => {
  const [mapData, setMapData] = useState<ConflictEvent[]>([]);
  const [activeLayer, setActiveLayer] = useState<'incidents' | 'heatmap' | 'clusters'>('incidents');
  const [selectedFilters, setSelectedFilters] = useState<string[]>([]);
  const [mapRef, setMapRef] = useState<L.Map | null>(null);

  // Nigeria center coordinates
  const nigeriaCenter: LatLngExpression = [9.0820, 8.6753];

  // Mock conflict data - replace with real API data
  const mockConflictData: ConflictEvent[] = useMemo(() => [
    {
      id: '1',
      lat: 11.0937,
      lng: 7.7319,
      type: 'Armed Attack',
      severity: 'high',
      fatalities: 15,
      date: '2024-01-15',
      location: 'Kaduna State',
      description: 'Armed attack on farming community'
    },
    {
      id: '2',
      lat: 6.5244,
      lng: 3.3792,
      type: 'Kidnapping',
      severity: 'medium',
      fatalities: 0,
      date: '2024-01-14',
      location: 'Lagos State',
      description: 'Kidnapping incident reported'
    },
    {
      id: '3',
      lat: 9.0579,
      lng: 7.4951,
      type: 'Communal Conflict',
      severity: 'critical',
      fatalities: 25,
      date: '2024-01-13',
      location: 'Plateau State',
      description: 'Farmer-herder conflict escalation'
    },
    {
      id: '4',
      lat: 12.0022,
      lng: 8.5919,
      type: 'Banditry',
      severity: 'high',
      fatalities: 8,
      date: '2024-01-12',
      location: 'Katsina State',
      description: 'Bandit attack on village'
    },
    {
      id: '5',
      lat: 11.8462,
      lng: 13.1571,
      type: 'Terrorism',
      severity: 'critical',
      fatalities: 32,
      date: '2024-01-11',
      location: 'Borno State',
      description: 'Terrorist attack on military base'
    }
  ], []);

  useEffect(() => {
    setMapData(mockConflictData);
  }, [mockConflictData]);

  // Color coding for conflict severity
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return '#22c55e';
      case 'medium': return '#eab308';
      case 'high': return '#f97316';
      case 'critical': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // Create custom icon based on conflict type and severity
  const createConflictIcon = (event: ConflictEvent) => {
    const color = getSeverityColor(event.severity);
    const size = event.severity === 'critical' ? 25 : event.severity === 'high' ? 20 : 15;
    
    return L.divIcon({
      className: 'custom-conflict-marker',
      html: `
        <div style="
          background-color: ${color};
          border: 2px solid white;
          border-radius: 50%;
          width: ${size}px;
          height: ${size}px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-size: 10px;
          font-weight: bold;
        ">
          ${event.fatalities || '•'}
        </div>
      `,
      iconSize: [size, size],
      iconAnchor: [size/2, size/2]
    });
  };

  // Prepare heatmap data
  const heatmapPoints = mapData.map(event => [
    event.lat,
    event.lng,
    event.severity === 'critical' ? 1.0 : 
    event.severity === 'high' ? 0.7 : 
    event.severity === 'medium' ? 0.4 : 0.2
  ]);

  const resetMap = () => {
    if (mapRef) {
      mapRef.setView(nigeriaCenter, 6);
    }
  };

  return (
    <div className={`relative ${fullscreen ? 'h-full' : ''}`} style={{ height: fullscreen ? '100%' : height }}>
      {/* Map Controls */}
      <div className="absolute top-4 left-4 z-[1000] space-y-2">
        <div className="bg-white rounded-lg shadow-lg p-2 space-y-2">
          <div className="flex space-x-1">
            <Button
              size="sm"
              variant={activeLayer === 'incidents' ? 'default' : 'outline'}
              onClick={() => setActiveLayer('incidents')}
            >
              <MapPin className="w-4 h-4 mr-1" />
              Incidents
            </Button>
            <Button
              size="sm"
              variant={activeLayer === 'heatmap' ? 'default' : 'outline'}
              onClick={() => setActiveLayer('heatmap')}
            >
              <Layers className="w-4 h-4 mr-1" />
              Heatmap
            </Button>
          </div>
          
          <Button size="sm" variant="outline" onClick={resetMap}>
            <RotateCcw className="w-4 h-4 mr-1" />
            Reset View
          </Button>
        </div>
      </div>

      {/* Legend with Pulse Alert Indicators */}
      <div className="absolute bottom-4 left-4 z-[1000]">
        <div className="bg-white rounded-lg shadow-lg p-3">
          <h4 className="font-semibold text-sm mb-2">Conflict Severity</h4>
          <div className="space-y-2">
            {[
              { level: 'Critical', color: '#ef4444', count: mapData.filter(e => e.severity === 'critical').length, pulse: true },
              { level: 'High', color: '#f97316', count: mapData.filter(e => e.severity === 'high').length, pulse: true },
              { level: 'Medium', color: '#eab308', count: mapData.filter(e => e.severity === 'medium').length, pulse: false },
              { level: 'Low', color: '#22c55e', count: mapData.filter(e => e.severity === 'low').length, pulse: false }
            ].map(item => (
              <div key={item.level} className="flex items-center space-x-2 text-xs">
                <div className="flex items-center justify-center w-6 h-6">
                  {item.pulse ? (
                    <PulseAlert color={item.color} size="small" intensity={item.level === 'Critical' ? 'high' : 'medium'} />
                  ) : (
                    <div 
                      className="w-3 h-3 rounded-full border border-white shadow-sm"
                      style={{ backgroundColor: item.color }}
                    />
                  )}
                </div>
                <span>{item.level}</span>
                {item.pulse && <span className="text-orange-500 text-xs">●</span>}
                <Badge variant="outline" className="text-xs">
                  {item.count}
                </Badge>
              </div>
            ))}
          </div>
          <div className="mt-2 pt-2 border-t border-gray-200 text-xs text-gray-500">
            <span className="text-orange-500">●</span> Live pulse alerts for high-risk areas
          </div>
        </div>
      </div>

      {/* Stats Overlay */}
      <div className="absolute top-4 right-4 z-[1000]">
        <div className="bg-white rounded-lg shadow-lg p-3 space-y-2">
          <div className="flex items-center space-x-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <span className="font-semibold">{mapData.length}</span>
            <span className="text-gray-600">Total Incidents</span>
          </div>
          <div className="flex items-center space-x-2 text-sm">
            <Users className="w-4 h-4 text-orange-500" />
            <span className="font-semibold">
              {mapData.reduce((sum, event) => sum + event.fatalities, 0)}
            </span>
            <span className="text-gray-600">Fatalities</span>
          </div>
        </div>
      </div>

      {/* Map Container */}
      <MapContainer
        center={nigeriaCenter}
        zoom={6}
        style={{ height: '100%', width: '100%' }}
        ref={setMapRef}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Conflict Incidents Layer with Professional Pulse Alerts */}
        {activeLayer === 'incidents' && mapData.map(event => (
          <PulseMarker key={event.id} event={event} />
        ))}

        {/* Heatmap Layer - Temporarily disabled for deployment */}
        {activeLayer === 'heatmap' && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-90">
            <p className="text-gray-600">Heatmap visualization coming soon</p>
          </div>
        )}
      </MapContainer>
    </div>
  );
};

export default ConflictMap;
