"""City registry: 50 US cities with coordinates.

The hist/act weather data starts empty — run fetch_data.py to populate
from the Open-Meteo API. The 30 original cities retain their curated
reference values as fallbacks.
"""

import pandas as pd


CITIES = [
    # ── West Coast ──
    {"name": "Seattle",        "state": "WA", "lat": 47.61, "lon": -122.33},
    {"name": "Portland",       "state": "OR", "lat": 45.52, "lon": -122.68},
    {"name": "San Francisco",  "state": "CA", "lat": 37.77, "lon": -122.42},
    {"name": "Sacramento",     "state": "CA", "lat": 38.58, "lon": -121.49},
    {"name": "Los Angeles",    "state": "CA", "lat": 34.05, "lon": -118.24},
    {"name": "San Diego",      "state": "CA", "lat": 32.72, "lon": -117.16},

    # ── Mountain / Southwest ──
    {"name": "Las Vegas",      "state": "NV", "lat": 36.17, "lon": -115.14},
    {"name": "Reno",           "state": "NV", "lat": 39.53, "lon": -119.81},
    {"name": "Phoenix",        "state": "AZ", "lat": 33.45, "lon": -112.07},
    {"name": "Tucson",         "state": "AZ", "lat": 32.22, "lon": -110.97},
    {"name": "Denver",         "state": "CO", "lat": 39.74, "lon": -104.98},
    {"name": "Salt Lake City", "state": "UT", "lat": 40.76, "lon": -111.89},
    {"name": "Boise",          "state": "ID", "lat": 43.62, "lon": -116.20},
    {"name": "Billings",       "state": "MT", "lat": 45.78, "lon": -108.50},
    {"name": "Albuquerque",    "state": "NM", "lat": 35.08, "lon": -106.65},
    {"name": "El Paso",        "state": "TX", "lat": 31.76, "lon": -106.44},

    # ── Midwest ──
    {"name": "Chicago",        "state": "IL", "lat": 41.88, "lon": -87.63},
    {"name": "Detroit",        "state": "MI", "lat": 42.33, "lon": -83.05},
    {"name": "Minneapolis",    "state": "MN", "lat": 44.98, "lon": -93.27},
    {"name": "Milwaukee",      "state": "WI", "lat": 43.04, "lon": -87.91},
    {"name": "Indianapolis",   "state": "IN", "lat": 39.77, "lon": -86.16},
    {"name": "Cleveland",      "state": "OH", "lat": 41.50, "lon": -81.69},
    {"name": "Cincinnati",     "state": "OH", "lat": 39.10, "lon": -84.51},
    {"name": "St. Louis",      "state": "MO", "lat": 38.63, "lon": -90.20},
    {"name": "Kansas City",    "state": "MO", "lat": 39.10, "lon": -94.58},
    {"name": "Omaha",          "state": "NE", "lat": 41.26, "lon": -95.94},
    {"name": "Oklahoma City",  "state": "OK", "lat": 35.47, "lon": -97.52},

    # ── Northeast ──
    {"name": "New York",       "state": "NY", "lat": 40.71, "lon": -74.01},
    {"name": "Boston",         "state": "MA", "lat": 42.36, "lon": -71.06},
    {"name": "Philadelphia",   "state": "PA", "lat": 39.95, "lon": -75.17},
    {"name": "Pittsburgh",     "state": "PA", "lat": 40.44, "lon": -79.99},
    {"name": "Washington DC",  "state": "DC", "lat": 38.91, "lon": -77.04},
    {"name": "Baltimore",      "state": "MD", "lat": 39.29, "lon": -76.61},
    {"name": "Richmond",       "state": "VA", "lat": 37.54, "lon": -77.44},
    {"name": "Buffalo",        "state": "NY", "lat": 42.89, "lon": -78.88},
    {"name": "Albany",          "state": "NY", "lat": 42.65, "lon": -73.75},
    {"name": "Burlington",     "state": "VT", "lat": 44.48, "lon": -73.21},
    {"name": "Portland",       "state": "ME", "lat": 43.66, "lon": -70.26},

    # ── Southeast ──
    {"name": "Atlanta",        "state": "GA", "lat": 33.75, "lon": -84.39},
    {"name": "Charlotte",      "state": "NC", "lat": 35.23, "lon": -80.84},
    {"name": "Nashville",      "state": "TN", "lat": 36.17, "lon": -86.78},
    {"name": "Memphis",        "state": "TN", "lat": 35.15, "lon": -90.05},
    {"name": "Miami",          "state": "FL", "lat": 25.77, "lon": -80.19},
    {"name": "Tampa",          "state": "FL", "lat": 27.95, "lon": -82.46},
    {"name": "Jacksonville",   "state": "FL", "lat": 30.33, "lon": -81.66},
    {"name": "New Orleans",    "state": "LA", "lat": 29.95, "lon": -90.07},

    # ── South / Texas ──
    {"name": "Dallas",         "state": "TX", "lat": 32.78, "lon": -96.80},
    {"name": "Houston",        "state": "TX", "lat": 29.76, "lon": -95.37},
    {"name": "San Antonio",    "state": "TX", "lat": 29.42, "lon": -98.49},

    # ── Alaska ──
    {"name": "Anchorage",      "state": "AK", "lat": 61.22, "lon": -149.90},
]


def find_city(name):
    """Find a city by name (case-insensitive, partial match).

    Returns the first matching city dict, or None.
    For ambiguous names like 'Portland', use 'Portland, OR' or 'Portland, ME'.
    """
    name_lower = name.lower().strip()
    # Exact match on "Name, ST" first
    for city in CITIES:
        full = f"{city['name']}, {city['state']}".lower()
        if full == name_lower:
            return city
    # Exact name match
    for city in CITIES:
        if city["name"].lower() == name_lower:
            return city
    # Partial match
    for city in CITIES:
        if name_lower in city["name"].lower():
            return city
    # Partial with state
    for city in CITIES:
        full = f"{city['name']}, {city['state']}".lower()
        if name_lower in full:
            return city
    return None


def get_coords(name):
    """Get (lat, lon) for a city by name."""
    city = find_city(name)
    if city:
        return (city["lat"], city["lon"])
    raise ValueError(f"City not found: {name}")


def all_cities():
    """Return all cities as a DataFrame."""
    rows = []
    for c in CITIES:
        rows.append({
            "name": c["name"],
            "state": c["state"],
            "lat": c["lat"],
            "lon": c["lon"],
        })
    return pd.DataFrame(rows)
