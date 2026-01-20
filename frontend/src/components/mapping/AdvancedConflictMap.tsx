import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import PulseMarker from '@/components/ui/PulseMarker';
import { 
  Layers, 
  Filter, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw,
  AlertTriangle,
  Users,
  MapPin,
  Grid3x3,
  Target,
  Radar
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
  event_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  fatalities: number;
  date: string;
  date_occurred: string;
  location: {
    name: string;
    state: string;
    lga?: string;
    ward?: string;
  };
  description?: string;
}

interface HeatmapData {
  state: string;
  conflict_count: number;
  total_fatalities: number;
  center: { lat: number; lng: number };
  intensity: number;
}

interface ClusterData {
  state: string;
  lga: string;
  conflict_count: number;
  total_fatalities: number;
  center: { lat: number; lng: number };
  cluster_size: number;
  event_types: string[];
}

interface DiffusionData {
  analysis_period: string;
  grid_size_km: number;
  metrics: {
    total_cells: number;
    affected_cells: number;
    diffusion_index: number;
    total_conflicts: number;
    total_fatalities: number;
  };
  grid_data: Array<{
    lng: number;
    lat: number;
    conflicts: number;
    fatalities: number;
  }>;
}

interface BufferAnalysis {
  center: { lat: number; lng: number };
  buffer_km: number;
  analysis: {
    conflicts_in_buffer: number;
    total_fatalities: number;
    estimated_exposed_population: number;
    risk_level: 'low' | 'medium' | 'high';
  };
  conflicts: ConflictEvent[];
}

interface AdvancedConflictMapProps {
  apiUrl?: string;
}

// Map Event Handler Component
const MapEventHandler: React.FC<{
  onZoomChange: (zoom: number) => void;
  onBoundsChange: (bounds: L.LatLngBounds) => void;
}> = ({ onZoomChange, onBoundsChange }) => {
  const map = useMapEvents({
    zoomend: () => {
      onZoomChange(map.getZoom());
      onBoundsChange(map.getBounds());
    },
    moveend: () => {
      onBoundsChange(map.getBounds());
    }
  });
  return null;
};

// Heatmap Layer Component
const HeatmapLayer: React.FC<{ data: HeatmapData[] }> = ({ data }) => {
  const map = useMap();

  useEffect(() => {
    if (!data.length) return;

    // Create heatmap circles for state-level data
    const heatmapLayers = data.map(item => {
      const radius = Math.max(20000, item.conflict_count * 5000); // Radius in meters
      const circle = L.circle([item.center.lat, item.center.lng], {
        radius,
        fillColor: item.intensity > 0.7 ? '#ef4444' : 
                   item.intensity > 0.4 ? '#f97316' : 
                   item.intensity > 0.2 ? '#eab308' : '#22c55e',
        fillOpacity: 0.3 + (item.intensity * 0.4),
        color: '#ffffff',
        weight: 2,
        opacity: 0.8
      });

      circle.bindPopup(`
        <div class="p-2">
          <h3 class="font-semibold">${item.state} State</h3>
          <p><strong>${item.conflict_count}</strong> conflicts</p>
          <p><strong>${item.total_fatalities}</strong> fatalities</p>
          <p>Intensity: ${Math.round(item.intensity * 100)}%</p>
        </div>
      `);

      return circle;
    });

    // Add layers to map
    heatmapLayers.forEach(layer => layer.addTo(map));

    // Cleanup function
    return () => {
      heatmapLayers.forEach(layer => map.removeLayer(layer));
    };
  }, [data, map]);

  return null;
};

// Cluster Layer Component
const ClusterLayer: React.FC<{ data: ClusterData[] }> = ({ data }) => {
  const map = useMap();

  useEffect(() => {
    if (!data.length) return;

    const clusterLayers = data.map(item => {
      const marker = L.circleMarker([item.center.lat, item.center.lng], {
        radius: Math.min(30, Math.max(8, item.cluster_size / 2)),
        fillColor: item.conflict_count > 20 ? '#ef4444' : 
                   item.conflict_count > 10 ? '#f97316' : 
                   item.conflict_count > 5 ? '#eab308' : '#22c55e',
        fillOpacity: 0.7,
        color: '#ffffff',
        weight: 2,
        opacity: 1
      });

      // Add cluster count label
      const divIcon = L.divIcon({
        html: `<div style="
          background: rgba(255,255,255,0.9);
          border-radius: 50%;
          width: 24px;
          height: 24px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 12px;
          border: 2px solid #333;
        ">${item.conflict_count}</div>`,
        className: 'cluster-label',
        iconSize: [24, 24],
        iconAnchor: [12, 12]
      });

      const labelMarker = L.marker([item.center.lat, item.center.lng], { icon: divIcon });

      marker.bindPopup(`
        <div class="p-2">
          <h3 class="font-semibold">${item.lga} LGA</h3>
          <p class="text-sm text-gray-600">${item.state} State</p>
          <p><strong>${item.conflict_count}</strong> conflicts</p>
          <p><strong>${item.total_fatalities}</strong> fatalities</p>
          <p class="text-xs mt-1">Types: ${item.event_types.join(', ')}</p>
        </div>
      `);

      return [marker, labelMarker];
    }).flat();

    clusterLayers.forEach(layer => layer.addTo(map));

    return () => {
      clusterLayers.forEach(layer => map.removeLayer(layer));
    };
  }, [data, map]);

  return null;
};

// Diffusion Grid Component
const DiffusionGrid: React.FC<{ data: DiffusionData | null }> = ({ data }) => {
  const map = useMap();

  useEffect(() => {
    if (!data?.grid_data.length) return;

    const gridLayers = data.grid_data
      .filter(cell => cell.conflicts > 0)
      .map(cell => {
        const size = data.grid_size_km * 1000; // Convert to meters
        const bounds = L.latLngBounds(
          [cell.lat, cell.lng],
          [cell.lat + (data.grid_size_km / 111), cell.lng + (data.grid_size_km / 111)]
        );

        const rectangle = L.rectangle(bounds, {
          fillColor: cell.conflicts > 10 ? '#ef4444' : 
                     cell.conflicts > 5 ? '#f97316' : 
                     cell.conflicts > 2 ? '#eab308' : '#22c55e',
          fillOpacity: 0.4,
          color: '#ffffff',
          weight: 1,
          opacity: 0.8
        });

        rectangle.bindPopup(`
          <div class="p-2">
            <h4 class="font-semibold">Grid Cell</h4>
            <p><strong>${cell.conflicts}</strong> conflicts</p>
            <p><strong>${cell.fatalities}</strong> fatalities</p>
            <p class="text-xs">Size: ${data.grid_size_km}km × ${data.grid_size_km}km</p>
          </div>
        `);

        return rectangle;
      });

    gridLayers.forEach(layer => layer.addTo(map));

    return () => {
      gridLayers.forEach(layer => map.removeLayer(layer));
    };
  }, [data, map]);

  return null;
};

export const AdvancedConflictMap: React.FC<AdvancedConflictMapProps> = ({ 
  apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}) => {
  const [zoom, setZoom] = useState(6);
  const [bounds, setBounds] = useState<L.LatLngBounds | null>(null);
  const [activeLayer, setActiveLayer] = useState<'hierarchical' | 'diffusion' | 'buffer'>('hierarchical');
  const [mapRef, setMapRef] = useState<L.Map | null>(null);

  // Data states
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([]);
  const [clusterData, setClusterData] = useState<ClusterData[]>([]);
  const [markerData, setMarkerData] = useState<ConflictEvent[]>([]);
  const [diffusionData, setDiffusionData] = useState<DiffusionData | null>(null);
  const [bufferAnalysis, setBufferAnalysis] = useState<BufferAnalysis | null>(null);
  const [selectedPoint, setSelectedPoint] = useState<{ lat: number; lng: number } | null>(null);

  // Loading states
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const nigeriaCenter: [number, number] = [9.0820, 8.6753];

  // Fetch hierarchical data based on zoom level
  const fetchHierarchicalData = useCallback(async (zoomLevel: number, mapBounds: L.LatLngBounds) => {
    if (!mapBounds) return;

    setLoading(true);
    setError(null);

    try {
      const bbox = `${mapBounds.getWest()},${mapBounds.getSouth()},${mapBounds.getEast()},${mapBounds.getNorth()}`;
      const response = await fetch(`${apiUrl}/api/v1/spatial/hierarchical-data/${zoomLevel}?bbox=${bbox}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Clear previous data
      setHeatmapData([]);
      setClusterData([]);
      setMarkerData([]);

      // Set appropriate data based on zoom level
      if (data.data_type === 'state_heatmap') {
        setHeatmapData(data.features);
      } else if (data.data_type === 'lga_clusters') {
        setClusterData(data.features);
      } else if (data.data_type === 'ward_markers') {
        setMarkerData(data.features);
      }

    } catch (err) {
      setError(`Failed to fetch hierarchical data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Fetch diffusion index
  const fetchDiffusionIndex = useCallback(async (mapBounds: L.LatLngBounds) => {
    if (!mapBounds) return;

    setLoading(true);
    try {
      const bbox = `${mapBounds.getWest()},${mapBounds.getSouth()},${mapBounds.getEast()},${mapBounds.getNorth()}`;
      const response = await fetch(`${apiUrl}/api/v1/spatial/diffusion-index?bbox=${bbox}&grid_size_km=10`);
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      setDiffusionData(data);
    } catch (err) {
      setError(`Failed to fetch diffusion data: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Fetch buffer analysis for selected point
  const fetchBufferAnalysis = useCallback(async (lat: number, lng: number, bufferKm: number = 5) => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/api/v1/spatial/buffer-analysis/${lat}/${lng}?buffer_km=${bufferKm}`);
      
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      setBufferAnalysis(data);
    } catch (err) {
      setError(`Failed to fetch buffer analysis: ${err instanceof Error ? err.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  // Handle zoom and bounds changes
  const handleZoomChange = useCallback((newZoom: number) => {
    setZoom(newZoom);
    if (activeLayer === 'hierarchical' && bounds) {
      fetchHierarchicalData(newZoom, bounds);
    }
  }, [activeLayer, bounds, fetchHierarchicalData]);

  const handleBoundsChange = useCallback((newBounds: L.LatLngBounds) => {
    setBounds(newBounds);
    if (activeLayer === 'hierarchical') {
      fetchHierarchicalData(zoom, newBounds);
    } else if (activeLayer === 'diffusion') {
      fetchDiffusionIndex(newBounds);
    }
  }, [activeLayer, zoom, fetchHierarchicalData, fetchDiffusionIndex]);

  // Handle map click for buffer analysis
  const handleMapClick = useCallback((e: L.LeafletMouseEvent) => {
    if (activeLayer === 'buffer') {
      const { lat, lng } = e.latlng;
      setSelectedPoint({ lat, lng });
      fetchBufferAnalysis(lat, lng);
    }
  }, [activeLayer, fetchBufferAnalysis]);

  // Map click handler component
  const MapClickHandler: React.FC = () => {
    useMapEvents({
      click: handleMapClick
    });
    return null;
  };

  // Reset map view
  const resetMap = useCallback(() => {
    if (mapRef) {
      mapRef.setView(nigeriaCenter, 6);
    }
  }, [mapRef]);

  // Current layer display logic
  const currentLayerType = useMemo(() => {
    if (activeLayer === 'diffusion') return 'diffusion';
    if (activeLayer === 'buffer') return 'buffer';
    
    // Hierarchical layer type based on zoom
    if (zoom <= 6) return 'heatmap';
    if (zoom <= 10) return 'clusters';
    return 'markers';
  }, [activeLayer, zoom]);

  return (
    <div className="relative w-full h-96 bg-gray-100 rounded-lg overflow-hidden">
      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-black bg-opacity-20 flex items-center justify-center z-[2000]">
          <div className="bg-white rounded-lg p-4 shadow-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm">Loading spatial data...</span>
            </div>
          </div>
        </div>
      )}

      {/* Error Display */}
      {error && (
        <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[2000]">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-lg text-sm">
            {error}
          </div>
        </div>
      )}

      {/* Layer Controls */}
      <div className="absolute top-4 left-4 z-[1000]">
        <div className="bg-white rounded-lg shadow-lg p-2">
          <div className="flex flex-col space-y-1">
            <Button
              size="sm"
              variant={activeLayer === 'hierarchical' ? 'default' : 'outline'}
              onClick={() => setActiveLayer('hierarchical')}
              className="text-xs"
            >
              <Layers className="w-3 h-3 mr-1" />
              Hierarchical
            </Button>
            <Button
              size="sm"
              variant={activeLayer === 'diffusion' ? 'default' : 'outline'}
              onClick={() => setActiveLayer('diffusion')}
              className="text-xs"
            >
              <Grid3x3 className="w-3 h-3 mr-1" />
              Diffusion
            </Button>
            <Button
              size="sm"
              variant={activeLayer === 'buffer' ? 'default' : 'outline'}
              onClick={() => setActiveLayer('buffer')}
              className="text-xs"
            >
              <Target className="w-3 h-3 mr-1" />
              Buffer
            </Button>
          </div>
        </div>
      </div>

      {/* Map Controls */}
      <div className="absolute top-4 right-4 z-[1000]">
        <div className="bg-white rounded-lg shadow-lg p-2 space-y-1">
          <Button size="sm" variant="outline" onClick={() => mapRef?.zoomIn()}>
            <ZoomIn className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={() => mapRef?.zoomOut()}>
            <ZoomOut className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline" onClick={resetMap}>
            <RotateCcw className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Analysis Panel */}
      {(diffusionData || bufferAnalysis) && (
        <div className="absolute bottom-4 right-4 z-[1000] max-w-sm">
          <div className="bg-white rounded-lg shadow-lg p-4">
            {diffusionData && activeLayer === 'diffusion' && (
              <div>
                <h4 className="font-semibold text-sm mb-2 flex items-center">
                  <Radar className="w-4 h-4 mr-1" />
                  Diffusion Analysis
                </h4>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span>Diffusion Index:</span>
                    <Badge variant="outline">{diffusionData.metrics.diffusion_index}%</Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Affected Cells:</span>
                    <span>{diffusionData.metrics.affected_cells}/{diffusionData.metrics.total_cells}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Total Conflicts:</span>
                    <span>{diffusionData.metrics.total_conflicts}</span>
                  </div>
                </div>
              </div>
            )}

            {bufferAnalysis && activeLayer === 'buffer' && (
              <div>
                <h4 className="font-semibold text-sm mb-2 flex items-center">
                  <Target className="w-4 h-4 mr-1" />
                  Buffer Analysis ({bufferAnalysis.buffer_km}km)
                </h4>
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span>Risk Level:</span>
                    <Badge variant={
                      bufferAnalysis.analysis.risk_level === 'high' ? 'destructive' :
                      bufferAnalysis.analysis.risk_level === 'medium' ? 'default' : 'secondary'
                    }>
                      {bufferAnalysis.analysis.risk_level.toUpperCase()}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Conflicts:</span>
                    <span>{bufferAnalysis.analysis.conflicts_in_buffer}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Exposed Pop:</span>
                    <span>{bufferAnalysis.analysis.estimated_exposed_population.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000]">
        <div className="bg-white rounded-lg shadow-lg p-3">
          <h4 className="font-semibold text-sm mb-2">
            {currentLayerType === 'heatmap' && 'State Heatmap'}
            {currentLayerType === 'clusters' && 'LGA Clusters'}
            {currentLayerType === 'markers' && 'Ward Markers'}
            {currentLayerType === 'diffusion' && 'Diffusion Grid'}
            {currentLayerType === 'buffer' && 'Buffer Analysis'}
          </h4>
          <div className="text-xs text-gray-600">
            {currentLayerType === 'heatmap' && 'Zoom: 0-6 • State-level intensity'}
            {currentLayerType === 'clusters' && 'Zoom: 7-10 • LGA-level clusters'}
            {currentLayerType === 'markers' && 'Zoom: 11+ • Individual incidents'}
            {currentLayerType === 'diffusion' && '10km grid cells • ACLED methodology'}
            {currentLayerType === 'buffer' && 'Click map for exposure analysis'}
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

        {/* Event Handlers */}
        <MapEventHandler onZoomChange={handleZoomChange} onBoundsChange={handleBoundsChange} />
        <MapClickHandler />

        {/* Layer Rendering */}
        {activeLayer === 'hierarchical' && (
          <>
            {currentLayerType === 'heatmap' && <HeatmapLayer data={heatmapData} />}
            {currentLayerType === 'clusters' && <ClusterLayer data={clusterData} />}
            {currentLayerType === 'markers' && markerData.map(event => (
              <PulseMarker key={event.id} event={{
                ...event,
                type: event.event_type,
                date: event.date_occurred,
                location: event.location.name
              }} />
            ))}
          </>
        )}

        {activeLayer === 'diffusion' && <DiffusionGrid data={diffusionData} />}

        {/* Buffer analysis visualization would be added here */}
      </MapContainer>
    </div>
  );
};

export default AdvancedConflictMap;
