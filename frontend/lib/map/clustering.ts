/**
 * Marker clustering logic using supercluster
 */

import Supercluster from 'supercluster';
import type { BBox, GeoJsonProperties } from 'geojson';

export interface ConflictEvent {
  id: string;
  latitude: number;
  longitude: number;
  event_type: string;
  fatalities: number;
  injured?: number;
  kidnapped?: number;
  displaced?: number;
  state: string;
  lga?: string;
  community?: string;
  event_date: string;
  description?: string;
  actors?: string[];
  [key: string]: any;
}

export interface ClusterPoint {
  type: 'Feature';
  properties: GeoJsonProperties & {
    cluster?: boolean;
    cluster_id?: number;
    point_count?: number;
    event?: ConflictEvent;
  };
  geometry: {
    type: 'Point';
    coordinates: [number, number];
  };
}

/**
 * Convert conflict events to GeoJSON format for clustering
 */
export function eventsToGeoJSON(events: ConflictEvent[]): ClusterPoint[] {
  return events
    .filter((event) => event.latitude && event.longitude)
    .map((event) => ({
      type: 'Feature' as const,
      properties: {
        cluster: false,
        event,
      },
      geometry: {
        type: 'Point' as const,
        coordinates: [event.longitude, event.latitude],
      },
    }));
}

/**
 * Create and configure a supercluster instance
 */
export function createClusterIndex(
  events: ConflictEvent[],
  options?: Partial<Supercluster.Options<GeoJsonProperties, GeoJsonProperties>>
) {
  const index = new Supercluster<GeoJsonProperties, GeoJsonProperties>({
    radius: 60,
    maxZoom: 16,
    ...options,
  });

  const geoJsonPoints = eventsToGeoJSON(events);
  index.load(geoJsonPoints);

  return index;
}

/**
 * Get clusters and points for current map viewport
 */
export function getClusters(
  index: Supercluster<GeoJsonProperties, GeoJsonProperties>,
  bounds: BBox,
  zoom: number
): ClusterPoint[] {
  return index.getClusters(bounds, Math.floor(zoom)) as ClusterPoint[];
}

/**
 * Get children of a cluster
 */
export function getClusterChildren(
  index: Supercluster<GeoJsonProperties, GeoJsonProperties>,
  clusterId: number
): ClusterPoint[] {
  return index.getChildren(clusterId) as ClusterPoint[];
}

/**
 * Expand a cluster to zoom level where it splits
 */
export function getClusterExpansionZoom(
  index: Supercluster<GeoJsonProperties, GeoJsonProperties>,
  clusterId: number
): number {
  return index.getClusterExpansionZoom(clusterId);
}
