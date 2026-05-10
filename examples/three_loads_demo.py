"""
Minimal end-to-end demo. Runs three simulated loads through pickup/drop
geofences without any external API calls — proves the geofencing math
and event dispatch work end-to-end.

Run with:  python examples/three_loads_demo.py
"""
from __future__ import annotations
import sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from geofence import CircleZone, ZoneTracker  # noqa: E402


# Three fake pickups + drops scattered around the GTA
LOADS = [
    {
        "load_id": "AVX-1001",
        "pickup": CircleZone("pickup-1001", 43.6532, -79.3832, 500, "Toronto Pearson Cargo"),
        "drop":   CircleZone("drop-1001",   43.5890, -79.6441, 500, "Mississauga DC"),
    },
    {
        "load_id": "AVX-1002",
        "pickup": CircleZone("pickup-1002", 43.7315, -79.7624, 500, "Brampton Yard"),
        "drop":   CircleZone("drop-1002",   43.2557, -79.8711, 500, "Hamilton Receiver"),
    },
    {
        "load_id": "AVX-1003",
        "pickup": CircleZone("pickup-1003", 43.8563, -79.5085, 500, "Vaughan Cross-Dock"),
        "drop":   CircleZone("drop-1003",   43.0896, -79.0849, 500, "St. Catharines"),
    },
]


# Fake GPS trajectories — each truck approaches pickup, sits, departs, drives to drop, arrives
TRAJECTORIES = {
    "AVX-1001": [
        (43.7000, -79.4500), (43.6700, -79.4000), (43.6532, -79.3832),  # at pickup
        (43.6500, -79.3900), (43.6200, -79.4500), (43.5890, -79.6441),  # at drop
    ],
    "AVX-1002": [
        (43.7800, -79.7200), (43.7400, -79.7500), (43.7315, -79.7624),
        (43.6800, -79.8000), (43.5000, -79.9000), (43.2557, -79.8711),
    ],
    "AVX-1003": [
        (43.9000, -79.5500), (43.8700, -79.5200), (43.8563, -79.5085),
        (43.7000, -79.3500), (43.4000, -79.2000), (43.0896, -79.0849),
    ],
}


def main():
    tracker = ZoneTracker()

    for step in range(6):
        print(f"\n--- Tick {step + 1} ---")
        for load in LOADS:
            lid = load["load_id"]
            lat, lon = TRAJECTORIES[lid][step]

            for zone, kind in [(load["pickup"], "PICKUP"), (load["drop"], "DROP")]:
                event = tracker.update(lid, zone, lat, lon)
                if event:
                    print(f"  [{lid}] {event.upper()} {kind} ({zone.label}) at ({lat:.4f}, {lon:.4f})")
        time.sleep(0.4)

    print("\nDemo complete. In production, each transition fires a Twilio SMS alert.")


if __name__ == "__main__":
    main()
