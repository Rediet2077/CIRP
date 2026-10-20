import { describe, expect, test } from "bun:test";
import { getCoordinateBounds, isValidGeographicPoint, projectCoordinate } from "./coordinate_projection";

describe("map coordinate projection", () => {
  test("accepts only finite latitude and longitude values in geographic ranges", () => {
    expect(isValidGeographicPoint({ latitude: 9.01, longitude: 38.75 })).toBe(true);
    expect(isValidGeographicPoint({ latitude: 91, longitude: 38.75 })).toBe(false);
    expect(isValidGeographicPoint({ latitude: 9, longitude: Number.NaN })).toBe(false);
  });

  test("projects recorded points inside the padded view bounds", () => {
    const points = [{ latitude: 9.01, longitude: 38.75 }, { latitude: 9.02, longitude: 38.77 }];
    const bounds = getCoordinateBounds(points);
    expect(projectCoordinate(points[0].longitude, bounds.minLng, bounds.maxLng)).toBeGreaterThan(8);
    expect(projectCoordinate(points[1].longitude, bounds.minLng, bounds.maxLng)).toBeLessThan(92);
  });
});
