"""City registry: 30 US cities with coordinates and reference weather data.

Data extracted from index.html — the same 30 cities used in the
"Weird Weather: Winter 2025-2026" visualization.
"""

import pandas as pd


CITIES = [
    {"name": "Seattle",        "state": "WA", "lat": 47.61, "lon": -122.33,
     "hist": {"high": 46, "snow":  5.3, "precip": 13.8}, "act": {"high": 44, "snow":  8.0, "precip": 12.5}},
    {"name": "Portland",       "state": "OR", "lat": 45.52, "lon": -122.68,
     "hist": {"high": 46, "snow":  4.6, "precip": 12.6}, "act": {"high": 44, "snow":  5.5, "precip": 11.5}},
    {"name": "San Francisco",  "state": "CA", "lat": 37.77, "lon": -122.42,
     "hist": {"high": 57, "snow":  0.0, "precip": 11.5}, "act": {"high": 61, "snow":  0.0, "precip": 10.0}},
    {"name": "Los Angeles",    "state": "CA", "lat": 34.05, "lon": -118.24,
     "hist": {"high": 68, "snow":  0.0, "precip":  8.5}, "act": {"high": 73, "snow":  0.0, "precip":  7.0}},
    {"name": "Las Vegas",      "state": "NV", "lat": 36.17, "lon": -115.14,
     "hist": {"high": 56, "snow":  0.5, "precip":  1.5}, "act": {"high": 63, "snow":  0.0, "precip":  1.0}},
    {"name": "Phoenix",        "state": "AZ", "lat": 33.45, "lon": -112.07,
     "hist": {"high": 65, "snow":  0.0, "precip":  2.1}, "act": {"high": 72, "snow":  0.0, "precip":  1.5}},
    {"name": "Denver",         "state": "CO", "lat": 39.74, "lon": -104.98,
     "hist": {"high": 45, "snow": 21.0, "precip":  2.7}, "act": {"high": 53, "snow":  8.0, "precip":  2.0}},
    {"name": "Salt Lake City", "state": "UT", "lat": 40.76, "lon": -111.89,
     "hist": {"high": 38, "snow": 30.0, "precip":  4.8}, "act": {"high": 46, "snow": 15.0, "precip":  3.5}},
    {"name": "Boise",          "state": "ID", "lat": 43.62, "lon": -116.20,
     "hist": {"high": 38, "snow": 15.0, "precip":  4.0}, "act": {"high": 46, "snow":  8.0, "precip":  3.0}},
    {"name": "Albuquerque",    "state": "NM", "lat": 35.08, "lon": -106.65,
     "hist": {"high": 47, "snow":  6.0, "precip":  1.5}, "act": {"high": 55, "snow":  2.0, "precip":  1.0}},
    {"name": "Chicago",        "state": "IL", "lat": 41.88, "lon": -87.63,
     "hist": {"high": 30, "snow": 22.0, "precip":  5.1}, "act": {"high": 28, "snow": 35.0, "precip":  5.5}},
    {"name": "Detroit",        "state": "MI", "lat": 42.33, "lon": -83.05,
     "hist": {"high": 30, "snow": 22.0, "precip":  5.4}, "act": {"high": 28, "snow": 33.0, "precip":  5.0}},
    {"name": "Minneapolis",    "state": "MN", "lat": 44.98, "lon": -93.27,
     "hist": {"high": 21, "snow": 27.0, "precip":  2.4}, "act": {"high": 20, "snow": 24.0, "precip":  2.0}},
    {"name": "Cleveland",      "state": "OH", "lat": 41.50, "lon": -81.69,
     "hist": {"high": 32, "snow": 27.0, "precip":  6.3}, "act": {"high": 30, "snow": 32.0, "precip":  6.0}},
    {"name": "Pittsburgh",     "state": "PA", "lat": 40.44, "lon": -79.99,
     "hist": {"high": 36, "snow": 20.0, "precip":  8.2}, "act": {"high": 34, "snow": 26.0, "precip":  7.5}},
    {"name": "St. Louis",      "state": "MO", "lat": 38.63, "lon": -90.20,
     "hist": {"high": 39, "snow": 11.0, "precip":  6.9}, "act": {"high": 38, "snow": 16.0, "precip":  6.5}},
    {"name": "Kansas City",    "state": "MO", "lat": 39.10, "lon": -94.58,
     "hist": {"high": 37, "snow": 10.0, "precip":  4.2}, "act": {"high": 36, "snow": 13.0, "precip":  4.0}},
    {"name": "New York",       "state": "NY", "lat": 40.71, "lon": -74.01,
     "hist": {"high": 39, "snow": 17.0, "precip": 11.1}, "act": {"high": 36, "snow": 34.0, "precip":  8.5}},
    {"name": "Boston",         "state": "MA", "lat": 42.36, "lon": -71.06,
     "hist": {"high": 37, "snow": 32.0, "precip": 11.6}, "act": {"high": 34, "snow": 61.0, "precip":  5.7}},
    {"name": "Philadelphia",   "state": "PA", "lat": 39.95, "lon": -75.17,
     "hist": {"high": 42, "snow": 13.0, "precip":  9.7}, "act": {"high": 39, "snow": 28.0, "precip":  8.0}},
    {"name": "Washington DC",  "state": "DC", "lat": 38.91, "lon": -77.04,
     "hist": {"high": 44, "snow": 12.0, "precip":  9.1}, "act": {"high": 41, "snow": 14.0, "precip":  8.5}},
    {"name": "Baltimore",      "state": "MD", "lat": 39.29, "lon": -76.61,
     "hist": {"high": 42, "snow": 12.0, "precip":  9.3}, "act": {"high": 39, "snow": 18.0, "precip":  8.5}},
    {"name": "Burlington",     "state": "VT", "lat": 44.48, "lon": -73.21,
     "hist": {"high": 28, "snow": 51.0, "precip":  6.8}, "act": {"high": 25, "snow": 68.0, "precip":  6.5}},
    {"name": "Portland",       "state": "ME", "lat": 43.66, "lon": -70.26,
     "hist": {"high": 31, "snow": 40.0, "precip": 10.6}, "act": {"high": 28, "snow": 55.0, "precip":  9.5}},
    {"name": "Albany",          "state": "NY", "lat": 42.65, "lon": -73.75,
     "hist": {"high": 31, "snow": 42.6, "precip":  7.8}, "act": {"high": 28, "snow": 48.0, "precip":  7.5}},
    {"name": "Dallas",         "state": "TX", "lat": 32.78, "lon": -96.80,
     "hist": {"high": 57, "snow":  0.7, "precip":  5.3}, "act": {"high": 55, "snow":  1.5, "precip":  5.0}},
    {"name": "Houston",        "state": "TX", "lat": 29.76, "lon": -95.37,
     "hist": {"high": 63, "snow":  0.1, "precip": 10.0}, "act": {"high": 61, "snow":  0.5, "precip":  9.0}},
    {"name": "Atlanta",        "state": "GA", "lat": 33.75, "lon": -84.39,
     "hist": {"high": 51, "snow":  1.7, "precip": 11.5}, "act": {"high": 50, "snow":  5.0, "precip": 11.0}},
    {"name": "Miami",          "state": "FL", "lat": 25.77, "lon": -80.19,
     "hist": {"high": 77, "snow":  0.0, "precip":  5.5}, "act": {"high": 75, "snow":  0.0, "precip":  5.0}},
    {"name": "Nashville",      "state": "TN", "lat": 36.17, "lon": -86.78,
     "hist": {"high": 46, "snow":  5.0, "precip": 11.0}, "act": {"high": 43, "snow":  9.0, "precip": 10.5}},
]


def find_city(name):
    """Find a city by name (case-insensitive, partial match).

    Returns the first matching city dict, or None.
    """
    name_lower = name.lower().strip()
    # Exact match first
    for city in CITIES:
        if city["name"].lower() == name_lower:
            return city
    # Partial match
    for city in CITIES:
        if name_lower in city["name"].lower():
            return city
    # Try with state
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
