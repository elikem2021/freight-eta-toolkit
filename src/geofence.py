"""
Geofence helpers for freight ETA tracking.

Two zone shapes:
  - Circle (lat, lon, radius_m) — fastest, fine for most pickups/drops
  - Polygon (list of [lat, lon] vertices) — for irregular shapes (ports, large yards)

A "zone event" is fired the first time a vehicle transitions across the zone
boundary. We track previous-state per (vehicle_id, zone_id) so we don't spam
"arrived" events every poll.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Iterable


EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in meters between two lat/lon points."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def point_in_polygon(lat: float, lon: float, polygon: Iterable[tuple[float, float]]) -> bool:
    """Ray-casting algorithm. polygon is a sequence of (lat, lon) vertices."""
    pts = list(polygon)
    n = len(pts)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = pts[i]
        yj, xj = pts[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


@dataclass
class CircleZone:
    zone_id: str
    lat: float
    lon: float
    radius_m: float
    label: str = ""

    def contains(self, lat: float, lon: float) -> bool:
        return haversine_m(self.lat, self.lon, lat, lon) <= self.radius_m


@dataclass
class PolygonZone:
    zone_id: str
    vertices: list[tuple[float, float]]
    label: str = ""

    def contains(self, lat: float, lon: float) -> bool:
        return point_in_polygon(lat, lon, self.vertices)


@dataclass
class ZoneTracker:
    """Tracks vehicle-zone state to emit transition events exactly once."""
    state: dict[tuple[str, str], bool] = field(default_factory=dict)

    def update(self, vehicle_id: str, zone, lat: float, lon: float) -> str | None:
        """Returns 'enter', 'exit', or None."""
        key = (vehicle_id, zone.zone_id)
        was_inside = self.state.get(key, False)
        is_inside = zone.contains(lat, lon)
        if is_inside and not was_inside:
            self.state[key] = True
            return "enter"
        if was_inside and not is_inside:
            self.state[key] = False
            return "exit"
        self.state[key] = is_inside
        return None
