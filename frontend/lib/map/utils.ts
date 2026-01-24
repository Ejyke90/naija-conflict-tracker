/**
 * Map utility functions for clustering and geospatial operations
 */

export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface Bounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

/**
 * Calculate distance between two coordinates using Haversine formula
 * Returns distance in kilometers
 */
export function calculateDistance(
  coord1: Coordinates,
  coord2: Coordinates
): number {
  const R = 6371; // Earth's radius in km
  const dLat = toRad(coord2.latitude - coord1.latitude);
  const dLon = toRad(coord2.longitude - coord1.longitude);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(coord1.latitude)) *
      Math.cos(toRad(coord2.latitude)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function toRad(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

/**
 * Check if coordinates are within Nigeria's approximate bounds
 */
export function isInNigeria(coords: Coordinates): boolean {
  const nigeriaBounds: Bounds = {
    north: 13.9,
    south: 4.3,
    west: 2.7,
    east: 14.7,
  };

  return (
    coords.latitude >= nigeriaBounds.south &&
    coords.latitude <= nigeriaBounds.north &&
    coords.longitude >= nigeriaBounds.west &&
    coords.longitude <= nigeriaBounds.east
  );
}

/**
 * Nigeria's center coordinates
 */
export const NIGERIA_CENTER: Coordinates = {
  latitude: 9.082,
  longitude: 8.6753,
};

/**
 * Default map bounds for Nigeria
 */
export const NIGERIA_BOUNDS: [[number, number], [number, number]] = [
  [2.7, 4.3], // Southwest [lng, lat]
  [14.7, 13.9], // Northeast [lng, lat]
];

/**
 * Format coordinate for display
 */
export function formatCoordinate(lat: number, lng: number): string {
  const latDir = lat >= 0 ? 'N' : 'S';
  const lngDir = lng >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}°${latDir}, ${Math.abs(lng).toFixed(
    4
  )}°${lngDir}`;
}

/**
 * Determine clustering threshold based on zoom level
 */
export function getClusterRadius(zoom: number): number {
  if (zoom >= 12) return 0; // No clustering at high zoom
  if (zoom >= 10) return 40;
  if (zoom >= 8) return 60;
  if (zoom >= 6) return 80;
  return 100;
}

/**
 * Check if zoom level should show individual markers
 */
export function shouldShowIndividualMarkers(zoom: number): boolean {
  return zoom >= 8;
}
