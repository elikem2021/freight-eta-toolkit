"""
Thin Geotab MyGeotab client. Pulls live vehicle GPS positions for ETA tracking.

Geotab uses a quirky JSON-RPC-over-HTTPS protocol. This client wraps the two
calls a freight broker actually needs: authenticate and get latest GPS.
"""
from __future__ import annotations
import os
import time
import requests
from dataclasses import dataclass


@dataclass
class GeotabPosition:
    vehicle_id: str
    name: str
    lat: float
    lon: float
    speed_kmh: float
    timestamp: str  # ISO8601


class GeotabClient:
    """Minimal Geotab MyGeotab client."""

    def __init__(self, server: str | None = None, database: str | None = None,
                 username: str | None = None, password: str | None = None):
        self.server = server or os.environ.get("GEOTAB_SERVER", "my.geotab.com")
        self.database = database or os.environ["GEOTAB_DATABASE"]
        self.username = username or os.environ["GEOTAB_USERNAME"]
        self.password = password or os.environ["GEOTAB_PASSWORD"]
        self._session_id: str | None = None
        self._authenticated_server: str | None = None

    def _post(self, method: str, params: dict, server: str | None = None) -> dict:
        url = f"https://{server or self.server}/apiv1/"
        body = {"method": method, "params": params}
        r = requests.post(url, json=body, timeout=15)
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"Geotab error: {data['error']}")
        return data["result"]

    def authenticate(self) -> None:
        result = self._post("Authenticate", {
            "database": self.database,
            "userName": self.username,
            "password": self.password,
        })
        creds = result["credentials"]
        self._session_id = creds["sessionId"]
        path = result.get("path") or self.server
        self._authenticated_server = path

    def get_latest_positions(self) -> list[GeotabPosition]:
        if not self._session_id:
            self.authenticate()
        result = self._post(
            "Get",
            {
                "typeName": "DeviceStatusInfo",
                "credentials": {
                    "database": self.database,
                    "userName": self.username,
                    "sessionId": self._session_id,
                },
            },
            server=self._authenticated_server,
        )
        out = []
        for r in result:
            out.append(GeotabPosition(
                vehicle_id=str(r.get("device", {}).get("id", "")),
                name=r.get("device", {}).get("name", ""),
                lat=float(r.get("latitude", 0)),
                lon=float(r.get("longitude", 0)),
                speed_kmh=float(r.get("speed", 0)),
                timestamp=r.get("dateTime", ""),
            ))
        return out


if __name__ == "__main__":
    client = GeotabClient()
    client.authenticate()
    for p in client.get_latest_positions()[:10]:
        print(f"{p.name:30s}  ({p.lat:.5f}, {p.lon:.5f})  {p.speed_kmh:.0f} km/h  {p.timestamp}")
