import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';

interface ThreatMapProps {
  className?: string;
}

export const ThreatMap: React.FC<ThreatMapProps> = ({ className = '' }) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<mapboxgl.Map | null>(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (!mapContainer.current) return;

    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token) {
      console.error('Mapbox token not found');
      return;
    }

    mapboxgl.accessToken = token;

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/dark-v11',
      center: [8.6753, 9.0820], // Nigeria center
      zoom: 6,
      pitch: 0,
      bearing: 0
    });

    map.current.on('load', () => {
      setMapLoaded(true);

      // Add heatmap layer for conflict density
      map.current?.addSource('conflict-heatmap', {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            // Sample conflict data - replace with real data
            {
              type: 'Feature',
              properties: { intensity: 0.8 },
              geometry: { type: 'Point', coordinates: [13.5, 11.85] } // Maiduguri
            },
            {
              type: 'Feature',
              properties: { intensity: 0.6 },
              geometry: { type: 'Point', coordinates: [7.44, 10.52] } // Kaduna
            },
            {
              type: 'Feature',
              properties: { intensity: 0.4 },
              geometry: { type: 'Point', coordinates: [6.55, 12.00] } // Zamfara
            },
            {
              type: 'Feature',
              properties: { intensity: 0.3 },
              geometry: { type: 'Point', coordinates: [3.38, 6.45] } // Lagos
            }
          ]
        }
      });

      map.current?.addLayer({
        id: 'conflict-heatmap-layer',
        type: 'heatmap',
        source: 'conflict-heatmap',
        paint: {
          'heatmap-weight': [
            'interpolate',
            ['linear'],
            ['get', 'intensity'],
            0, 0,
            1, 1
          ],
          'heatmap-intensity': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 1,
            9, 3
          ],
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(9, 9, 11, 0)',
            0.2, 'rgba(16, 185, 129, 0.4)', // emerald-500
            0.4, 'rgba(245, 158, 11, 0.6)', // amber-500
            0.6, 'rgba(249, 115, 22, 0.8)', // orange-600
            1, 'rgba(244, 63, 94, 1)' // rose-500
          ],
          'heatmap-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 2,
            9, 20
          ],
          'heatmap-opacity': 0.7
        }
      });

      // Add glowing effect
      map.current?.addLayer({
        id: 'conflict-heatmap-glow',
        type: 'heatmap',
        source: 'conflict-heatmap',
        paint: {
          'heatmap-weight': [
            'interpolate',
            ['linear'],
            ['get', 'intensity'],
            0, 0,
            1, 1
          ],
          'heatmap-intensity': 0.5,
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(244, 63, 94, 0)',
            0.5, 'rgba(244, 63, 94, 0.3)',
            1, 'rgba(244, 63, 94, 0.6)'
          ],
          'heatmap-radius': [
            'interpolate',
            ['linear'],
            ['zoom'],
            0, 10,
            9, 40
          ],
          'heatmap-opacity': 0.3
        }
      });

      // Add minimal labels
      map.current?.setLayoutProperty('country-label', 'text-field', [
        'format',
        ['get', 'name_en'],
        { 'font-scale': 0.8, 'text-color': '#94a3b8' }
      ]);

      map.current?.setPaintProperty('country-label', 'text-color', '#94a3b8');
      map.current?.setPaintProperty('state-label', 'text-color', '#64748b');

      // Hide unnecessary layers for cleaner look
      const layersToHide = [
        'poi-label',
        'transit-label',
        'waterway-label',
        'natural-point-label',
        'landuse-overlay',
        'building'
      ];

      layersToHide.forEach(layer => {
        if (map.current?.getLayer(layer)) {
          map.current?.setLayoutProperty(layer, 'visibility', 'none');
        }
      });
    });

    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, []);

  return (
    <div className={`threat-map-container ${className}`}>
      <div ref={mapContainer} className="w-full h-full" />
      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 backdrop-blur-sm rounded-xl">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mx-auto mb-4"></div>
            <p className="text-slate-300">Loading threat map...</p>
          </div>
        </div>
      )}
    </div>
  );
};