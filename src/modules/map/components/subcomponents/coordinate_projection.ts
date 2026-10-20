export interface GeographicPoint {
  latitude: number;
  longitude: number;
}

export function isValidGeographicPoint(point: GeographicPoint): boolean {
  return Number.isFinite(point.latitude) &&
    Number.isFinite(point.longitude) &&
    point.latitude >= -90 && point.latitude <= 90 &&
    point.longitude >= -180 && point.longitude <= 180;
}

export function getCoordinateBounds(points: GeographicPoint[]) {
  const latitudes = points.map((point) => point.latitude);
  const longitudes = points.map((point) => point.longitude);
  const latMin = Math.min(...latitudes);
  const latMax = Math.max(...latitudes);
  const lngMin = Math.min(...longitudes);
  const lngMax = Math.max(...longitudes);
  const latPadding = Math.max((latMax - latMin) * 0.1, 0.001);
  const lngPadding = Math.max((lngMax - lngMin) * 0.1, 0.001);

  return {
    minLat: latMin - latPadding,
    maxLat: latMax + latPadding,
    minLng: lngMin - lngPadding,
    maxLng: lngMax + lngPadding,
  };
}

export function projectCoordinate(value: number, min: number, max: number): number {
  return 8 + ((value - min) / (max - min)) * 84;
}
