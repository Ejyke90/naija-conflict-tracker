import 'leaflet';

declare module 'leaflet' {
  function heatLayer(
    latlngs: Array<[number, number, number]>,
    options?: {
      max?: number;
      maxZoom?: number;
      minOpacity?: number;
      radius?: number;
      blur?: number;
      gradient?: Record<number, string>;
    }
  ): L.Layer;

  namespace heatLayer {
    interface HeatLatLng extends LatLng {
      alt: number;
    }
  }
}
