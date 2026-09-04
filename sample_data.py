"""Generate realistic demo sensor observations for NER locations."""

from __future__ import annotations

from datetime import datetime, timedelta
from math import asin, cos, radians, sin, sqrt

import numpy as np
import pandas as pd


LOCATIONS = [
    ("Sikkim", "Gangtok", 27.3389, 88.6065, 31, 68),
    ("Arunachal Pradesh", "Itanagar", 27.0844, 93.6053, 24, 52),
    ("Assam", "Dima Hasao", 25.3478, 93.0176, 19, 44),
    ("Meghalaya", "Cherrapunji", 25.2840, 91.7210, 36, 82),
    ("Nagaland", "Kohima", 25.6751, 94.1086, 28, 61),
    ("Mizoram", "Aizawl", 23.7271, 92.7176, 34, 73),
    ("Manipur", "Imphal", 24.8170, 93.9368, 22, 48),
    ("Tripura", "Agartala", 23.8315, 91.2868, 12, 31),
]

# Demonstration points only. Replace these with verified district shelter records before deployment.
SAFE_PLACES = [
    ("Gangtok Relief Camp", "Sikkim", 27.3314, 88.6138, "Tadong Community Hall"),
    ("Itanagar Relief Camp", "Arunachal Pradesh", 27.1026, 93.6158, "State Civil Secretariat area"),
    ("Dima Hasao Relief Camp", "Assam", 25.2910, 93.1700, "Haflong Town Hall"),
    ("Cherrapunji Relief Camp", "Meghalaya", 25.2745, 91.7310, "Sohra Community Centre"),
    ("Kohima Relief Camp", "Nagaland", 25.6667, 94.1077, "Kohima Municipal Ground"),
    ("Aizawl Relief Camp", "Mizoram", 23.7360, 92.7176, "Aizawl Sports Complex"),
    ("Imphal Relief Camp", "Manipur", 24.8050, 93.9500, "Khuman Lampak Sports Complex"),
    ("Agartala Relief Camp", "Tripura", 23.8450, 91.2800, "Agartala Town Hall"),
]


def _distance_km(latitude: float, longitude: float, place_latitude: float, place_longitude: float) -> float:
    earth_radius_km = 6371
    lat1, lat2 = radians(latitude), radians(place_latitude)
    delta_lat = radians(place_latitude - latitude)
    delta_lon = radians(place_longitude - longitude)
    value = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(value))


def find_nearest_safe_place(latitude: float, longitude: float) -> dict[str, str | float]:
    """Return the closest demo evacuation point to a monitoring node."""
    nearest = min(SAFE_PLACES, key=lambda place: _distance_km(latitude, longitude, place[2], place[3]))
    return {
        "name": nearest[0],
        "state": nearest[1],
        "latitude": nearest[2],
        "longitude": nearest[3],
        "address": nearest[4],
        "distance_km": round(_distance_km(latitude, longitude, nearest[2], nearest[3]), 1),
    }


def generate_sensor_data(hours: int = 72, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    rows: list[dict] = []
    for hour in range(hours):
        timestamp = now - timedelta(hours=hours - hour - 1)
        for state, district, lat, lon, slope, moisture_base in LOCATIONS:
            rain = max(0, rng.normal(10 if hour % 19 < 12 else 34, 10))
            moisture = np.clip(moisture_base + rain * 0.22 + rng.normal(0, 4), 15, 99)
            displacement = max(0.2, rng.normal(3.5 + moisture / 25, 1.4))
            seismic = max(0.01, rng.normal(0.16, 0.08))
            rows.append({
                "timestamp": timestamp,
                "state": state,
                "district": district,
                "latitude": lat,
                "longitude": lon,
                "rainfall_24h_mm": round(rain, 1),
                "soil_moisture_pct": round(moisture, 1),
                "slope_deg": slope,
                "displacement_mm": round(displacement, 2),
                "seismic_activity": round(seismic, 3),
            })
    return pd.DataFrame(rows)
