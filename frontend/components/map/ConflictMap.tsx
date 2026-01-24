import React, { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import Map, { MapRef, NavigationControl, ScaleControl, FullscreenControl } from 'react-map-gl';
import { Filter, Layers, RefreshCw, Download } from 'lucide-react';
import { useMapData } from '../../hooks/useMapData';
import { useMapFilters } from '../../hooks/useMapFilters';
import { EventMarker } from './EventMarker';
import { ClusterMarker } from './ClusterMarker';
import { EventPopup } from './EventPopup';
import { MapFilters } from './MapFilters';
import { MapLegend } from './MapLegend';
import { MapControls } from './MapControls';
import { NIGERIA_CENTER } from '../../lib/map/utils';
import { createClusterIndex, getClusters } from '../../lib/map/clustering';
import type { ConflictEvent } from '../../lib/map/clustering';
import 'mapbox-gl/dist/mapbox-gl.css';

interface ConflictMapProps {
  fullscreen?: boolean;
  className?: string;
}

// Mapbox access token - should be in environment variable
const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN || 'pk.eyJ1IjoibmV4dGllciIsImEiOiJjbTJ1ZGZzNGswMDBzMmlzaGpvN3QybW40In0.placeholder';

/**
 * Interactive Conflict Map with clustering, filtering, and popups
 */
export const ConflictMap: React.FC<ConflictMapProps> = ({ fullscreen = false, className = '' }) => {
  const mapRef = useRef<MapRef>(null);

  // Filter state
  const { filters, activeFilterCount } = useMapFilters();
  const [showFilters, setShowFilters] = useState(false);
  const [showLegend, setShowLegend] = useState(true);

  // Map state
  const [viewState, setViewState] = useState({
    longitude: NIGERIA_CENTER.longitude,
    latitude: NIGERIA_CENTER.latitude,
    zoom: 6,
  });
  const [mapStyle, setMapStyle] = useState<'streets' | 'satellite'>('streets');
  const [selectedEvent, setSelectedEvent] = useState<ConflictEvent | null>(null);

  // Fetch data with filters
  const { events, isLoading, error, refresh, totalCount, lastUpdated } = useMapData({ filters });

  // Create cluster index
  const clusterIndex = useMemo(() => {
    if (events.length === 0) return null;
    return createClusterIndex(events);
  }, [events]);

  // Get clusters for current viewport
  const { clusters, points } = useMemo(() => {
    if (!clusterIndex || events.length === 0) {
      return { clusters: [], points: [] };
    }

    const map = mapRef.current?.getMap();
    if (!map) {
      return { clusters: [], points: [] };
    }

    const bounds = map.getBounds();
    if (!bounds) {
      return { clusters: [], points: [] };
    }

    const bbox: [number, number, number, number] = [
      bounds.getWest(),
      bounds.getSouth(),
      bounds.getEast(),
      bounds.getNorth(),
    ];

    const clusterPoints = getClusters(clusterIndex, bbox, viewState.zoom);

    const clustersArray = clusterPoints.filter((point) => point.properties?.cluster);
    const pointsArray = clusterPoints.filter((point) => !point.properties?.cluster);

    return {
      clusters: clustersArray,
      points: pointsArray,
    };
  }, [clusterIndex, events, viewState.zoom]);

  // Handle cluster click - zoom to expansion zoom
  const handleClusterClick = useCallback(
    (clusterId: number, longitude: number, latitude: number) => {
      if (!clusterIndex) return;

      const expansionZoom = clusterIndex.getClusterExpansionZoom(clusterId);
      setViewState({
        longitude,
        latitude,
        zoom: Math.min(expansionZoom + 1, 20),
      });
    },
    [clusterIndex]
  );

  // Handle location search
  const handleLocationSelect = useCallback((lng: number, lat: number, zoom = 10) => {
    setViewState({ longitude: lng, latitude: lat, zoom });
  }, []);

  // Get map style URL
  const getMapStyleURL = () => {
    if (mapStyle === 'satellite') {
      return 'mapbox://styles/mapbox/satellite-streets-v12';
    }
    return 'mapbox://styles/mapbox/streets-v12';
  };

  // Export data as JSON
  const handleExport = () => {
    const dataStr = JSON.stringify(events, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `conflict-data-${new Date().toISOString()}.json`;
    link.click();
  };

  const containerClass = fullscreen
    ? 'h-screen w-screen'
    : className || 'h-[600px] w-full rounded-lg overflow-hidden shadow-xl';

  return (
    <div className={`relative ${containerClass}`}>
      {/* Map Container */}
      <Map
        ref={mapRef}
        {...viewState}
        onMove={(evt) => setViewState(evt.viewState)}
        mapStyle={getMapStyleURL()}
        mapboxAccessToken={MAPBOX_TOKEN}
        style={{ width: '100%', height: '100%' }}
        attributionControl={false}
      >
        {/* Navigation Controls */}
        <NavigationControl position="top-right" />
        <ScaleControl position="bottom-right" />
        <FullscreenControl position="top-right" />

        {/* Cluster Markers */}
        {clusters.map((cluster) => {
          const [longitude, latitude] = cluster.geometry.coordinates;
          const { cluster_id, point_count } = cluster.properties || {};

          return (
            <ClusterMarker
              key={`cluster-${cluster_id}`}
              longitude={longitude}
              latitude={latitude}
              pointCount={point_count || 0}
              onClick={() => handleClusterClick(cluster_id!, longitude, latitude)}
            />
          );
        })}

        {/* Individual Event Markers */}
        {points.map((point) => {
          const event = point.properties?.event as ConflictEvent;
          if (!event) return null;

          return (
            <EventMarker
              key={`event-${event.id}`}
              event={event}
              onClick={setSelectedEvent}
            />
          );
        })}

        {/* Event Popup */}
        {selectedEvent && (
          <EventPopup event={selectedEvent} onClose={() => setSelectedEvent(null)} />
        )}
      </Map>

      {/* Top Controls Bar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex items-start justify-between gap-4">
        {/* Search */}
        <MapControls
          onLocationSelect={handleLocationSelect}
          mapboxAccessToken={MAPBOX_TOKEN}
          className="flex-1 max-w-md"
        />

        {/* Action Buttons */}
        <div className="flex gap-2">
          {/* Refresh Button */}
          <button
            onClick={() => refresh()}
            disabled={isLoading}
            className="bg-white hover:bg-gray-50 text-gray-700 px-3 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-medium"
            title="Refresh data"
          >
            <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
            <span className="hidden sm:inline">Refresh</span>
          </button>

          {/* Toggle Map Style */}
          <button
            onClick={() => setMapStyle(mapStyle === 'streets' ? 'satellite' : 'streets')}
            className="bg-white hover:bg-gray-50 text-gray-700 px-3 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-medium"
            title="Toggle map style"
          >
            <Layers size={16} />
            <span className="hidden sm:inline">{mapStyle === 'streets' ? 'Satellite' : 'Streets'}</span>
          </button>

          {/* Export Button */}
          <button
            onClick={handleExport}
            disabled={events.length === 0}
            className="bg-white hover:bg-gray-50 text-gray-700 px-3 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-medium disabled:opacity-50"
            title="Export data"
          >
            <Download size={16} />
            <span className="hidden sm:inline">Export</span>
          </button>

          {/* Toggle Filters */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-medium relative"
            title="Toggle filters"
          >
            <Filter size={16} />
            <span className="hidden sm:inline">Filters</span>
            {activeFilterCount > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                {activeFilterCount}
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Filter Sidebar */}
      {showFilters && (
        <div className="absolute top-4 right-4 bottom-4 w-80 z-20">
          <MapFilters onClose={() => setShowFilters(false)} />
        </div>
      )}

      {/* Legend */}
      {showLegend && !showFilters && (
        <div className="absolute bottom-4 left-4 z-10">
          <MapLegend />
        </div>
      )}

      {/* Status Bar */}
      <div className="absolute bottom-4 right-4 bg-white px-4 py-2 rounded-lg shadow-lg text-xs text-gray-600 z-10">
        <div className="flex items-center gap-4">
          <span>
            <span className="font-semibold">{totalCount.toLocaleString()}</span> events shown
          </span>
          <span>•</span>
          <span>
            Updated{' '}
            {new Date(lastUpdated).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </span>
        </div>
      </div>

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center z-30">
          <div className="text-center">
            <RefreshCw size={32} className="animate-spin text-blue-600 mx-auto mb-2" />
            <p className="text-gray-700 font-medium">Loading conflict data...</p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg shadow-lg z-30 max-w-md">
          <p className="font-semibold">Error loading data</p>
          <p className="text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export default ConflictMap;
