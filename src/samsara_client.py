"""
Thin Samsara fleet API client.

Samsara has a clean REST API and is generally the easier of the three big telematics
platforms to integrate with. Generate an API token at
https://cloud.samsara.com/o/<your-org>/settings/api-tokens
"""
from __future__ import annotations
import os
import requests
from dataclasses import dataclass

SAMSARA_BASE = "https://api.samsara.com"


@dataclass
class SamsaraVehicle:
    vehicle_id: str
    name: str
    lat: float
    lon: float
    speed_kmh: float
    odometer_km: float | None
    timestamp: str


class SamsaraClient:
    def __init__(self, token: str | None = None):
        self.token = token or os.environ["SAMSARA_API_TOKEN"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def list_vehicles(self) -> list[dict]:
        r = requests.get(f"{SAMSARA_BASE}/fleet/vehicles", headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.json().get("data", [])

    def get_locations(self) -> list[SamsaraVehicle]:
        r = requests.get(
            f"{SAMSARA_BASE}/fleet/vehicles/locations",
            headers=self.headers,
            timeout=15,
        )
        r.raise_for_status()
        out = []
        for v in r.json().get("data", []):
            loc = v.get("location") or {}
            out.append(SamsaraVehicle(
                vehicle_id=str(v.get("id", "")),
                name=v.get("name", ""),
                lat=float(loc.get("latitude", 0)),
                lon=float(loc.get("longitude", 0)),
                speed_kmh=float(loc.get("speed", 0)),
                odometer_km=loc.get("odometer"),
                timestamp=loc.get("time", ""),
            ))
        return out


if __name__ == "__main__":
    client = SamsaraClient()
    for v in client.get_locations()[:10]:
        print(f"{v.name:30s}  ({v.lat:.5f}, {v.lon:.5f})  {v.speed_kmh:.0f} km/h  {v.timestamp}")
