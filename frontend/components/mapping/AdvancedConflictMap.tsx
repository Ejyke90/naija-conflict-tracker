'use client';

import React, { useState, useEffect, useRef } from 'react';
import dynamic from 'next/dynamic';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.heat';

// Dynamically import MapContainer and related components with SSR disabled
const MapContainer = dynamic(() => import('react-leaflet').then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import('react-leaflet').then(mod => mod.TileLayer), { ssr: false });
const Marker = dynamic(() => import('react-leaflet').then(mod => mod.Marker), { ssr: false });
const Popup = dynamic(() => import('react-leaflet').then(mod => mod.Popup), { ssr: false });

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
  const mapRef = useRef<any>(null);
  const [showHeatmap, setShowHeatmap] = useState(false);
  const [heatmapLayer, setHeatmapLayer] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch heatmap data
  const loadHeatmapData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/v1/conflicts/heatmap/data?days_back=30');
      
      if (!response.ok) {
        throw new Error('Failed to load heatmap data');
      }
      
      const data = await response.json();
      
      // Create heatmap layer
      if (mapRef.current && data.points && data.points.length > 0) {
        // `mapRef.current` is set via MapContainer's `whenCreated` to the Leaflet map instance
        const map = mapRef.current;
        
        // Remove existing heatmap if any
        if (heatmapLayer) {
          map.removeLayer(heatmapLayer);
        }
        
        // Create new heatmap layer with intensity data
        const heat = (L as any).heatLayer(data.points, {
          max: 10,
          maxZoom: 18,
          radius: 50,
          blur: 30,
          gradient: {
            0.0: '#006837',
            0.25: '#1a9850',
            0.5: '#91cf60',
            0.75: '#d9ef8b',
            1.0: '#ff0000'
          }
        });
        
        heat.addTo(map);
        setHeatmapLayer(heat);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error loading heatmap');
      console.error('Error loading heatmap data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Toggle heatmap visibility
  const handleHeatmapToggle = async () => {
    if (!showHeatmap) {
      // Enable heatmap
      await loadHeatmapData();
    } else {
      // Disable heatmap
      if (mapRef.current && heatmapLayer) {
        const map = mapRef.current;
        if (typeof map.removeLayer === 'function') {
          map.removeLayer(heatmapLayer);
        }
        setHeatmapLayer(null);
      }
    }
    setShowHeatmap(!showHeatmap);
  };

  // Export data as GeoJSON
  const handleExport = async () => {
    try {
      const response = await fetch('/api/v1/conflicts/heatmap/data?days_back=30');
      const data = await response.json();
      
      // Convert to GeoJSON FeatureCollection
      const features = data.points.map((point: [number, number, number], idx: number) => ({
        type: 'Feature',
        properties: { intensity: point[2] },
        geometry: {
          type: 'Point',
          coordinates: [point[1], point[0]] // GeoJSON uses [lng, lat]
        }
      }));
      
      const geojson = {
        type: 'FeatureCollection',
        features
      };
      
      const dataStr = JSON.stringify(geojson, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `conflict-heatmap-${new Date().toISOString().split('T')[0]}.geojson`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Error exporting data:', err);
      alert('Failed to export heatmap data');
    }
  };

  return (
    <div className="glass-card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="typography-heading text-xl text-tactical-e-ink">Advanced Conflict Map</h2>
        <div className="flex space-x-2">
          <button 
            className="px-3 py-1.5 bg-tactical-slate-medium border border-tactical-slate-light/30 rounded text-tactical-e-ink typography-label text-sm hover:bg-tactical-slate-light disabled:opacity-50 disabled:cursor-not-allowed"
            title="View spatial analysis metrics"
            disabled
          >
            Spatial Analysis
          </button>
          <button 
            onClick={handleHeatmapToggle}
            disabled={isLoading}
            className={`px-3 py-1.5 rounded typography-label text-sm border border-tactical-slate-light/30 ${
              showHeatmap ? 'signal_high bg-tactical-slate-medium' : 'bg-tactical-slate-medium'
            } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:bg-tactical-slate-light'} text-tactical-e-ink`}
            title={showHeatmap ? 'Hide heatmap layer' : 'Show conflict intensity heatmap'}
          >
            {isLoading ? '⟳ Loading...' : `🔥 Heatmap ${showHeatmap ? '(On)' : ''}`}
          </button>
          <button 
            onClick={handleExport}
            className="px-3 py-1.5 bg-tactical-navy border border-tactical-slate-light/30 rounded text-tactical-e-ink typography-label text-sm hover:bg-tactical-charcoal"
            title="Export heatmap data as GeoJSON"
          >
            ⬇ Export
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-4 p-3 signal-critical border border-red-500/30 rounded-lg typography-body text-sm text-red-300">
          {error}
        </div>
      )}

      <div className="glass-card border border-tactical-slate-light/30 rounded-lg h-96 relative overflow-hidden">
        <MapContainer 
          center={[9.0820, 8.6753]} 
          zoom={6} 
          style={{ height: '100%', width: '100%' }}
          ref={mapRef}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <Marker position={[9.0820, 8.6753]}>
            <Popup>
              Advanced conflict data visualization with spatial analysis and heatmap capabilities.
            </Popup>
          </Marker>
        </MapContainer>
        
        {isLoading && (
          <div className="absolute inset-0 bg-tactical-navy/80 flex items-center justify-center">
            <div className="text-center">
              <div className="animate-spin text-2xl mb-2 text-tactical-e-ink">⟳</div>
              <p className="typography-body text-tactical-e-ink font-medium">Loading heatmap...</p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 flex justify-between typography-body text-sm text-tactical-e-ink/70">
        <span>📍 Advanced spatial queries enabled</span>
        <span>🔄 PostGIS integration active</span>
        {showHeatmap && <span className="text-amber-400 font-medium">🔥 Heatmap layer active</span>}
      </div>

      {showHeatmap && (
        <div className="mt-4 p-3 glass-card border border-tactical-slate-light/30 rounded-lg typography-body text-sm text-tactical-e-ink/80">
          <p className="typography-label font-medium mb-2 text-tactical-e-ink">Heatmap Legend:</p>
          <div className="flex gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gradient-to-r from-green-500 to-green-400"></div>
              <span>Low Intensity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-gradient-to-r from-amber-500 to-orange-500"></div>
              <span>Medium Intensity</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 bg-red-500"></div>
              <span>High Intensity</span>
            </div>
          </div>
          <p className="mt-2 typography-body text-xs text-tactical-e-ink/50">
            Color intensity represents conflict density based on incident count and fatalities over the last 30 days
          </p>
        </div>
      )}
    </div>
  );
};

export default AdvancedConflictMap;
