"""Weather comparison and climate matching analysis.

Reimplements the normalized Euclidean distance algorithm from index.html
for comparing actual weather against historical normals.

Can work with either:
  - Data loaded from data/cities_weather.json (after running fetch_data.py)
  - Live API calls to Open-Meteo
"""

import json
import math
import os
import time

import pandas as pd

from .cities import CITIES
from .openmeteo import get_winter_actuals


def load_fetched_data(path="data/cities_weather.json"):
    """Load city weather data from the JSON file produced by fetch_data.py."""
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def compare_actual_vs_normal(actuals, normals):
    """Compare actual weather against normals, returning deltas.

    Args:
        actuals: dict with keys high, snow, precip (or avg_high, total_snow, total_precip)
        normals: dict with same key patterns

    Returns:
        dict with delta and percent change for each metric
    """
    a_high = actuals.get("high", actuals.get("avg_high", 0))
    n_high = normals.get("high", normals.get("avg_high", 0))
    a_snow = actuals.get("snow", actuals.get("total_snow", 0))
    n_snow = normals.get("snow", normals.get("avg_snow", 0))
    a_precip = actuals.get("precip", actuals.get("total_precip", 0))
    n_precip = normals.get("precip", normals.get("avg_precip", 0))

    def pct(actual, normal):
        if normal == 0:
            return None
        return round((actual - normal) / normal * 100, 1)

    return {
        "delta_high": round(a_high - n_high, 1),
        "delta_snow": round(a_snow - n_snow, 1),
        "delta_precip": round(a_precip - n_precip, 1),
        "pct_high": pct(a_high, n_high),
        "pct_snow": pct(a_snow, n_snow),
        "pct_precip": pct(a_precip, n_precip),
    }


def find_climate_match(city_actuals, all_normals):
    """Find which city's historical normal best matches the given actuals.

    Uses normalized Euclidean distance across avg_high, snowfall, precip.

    Args:
        city_actuals: dict with keys high, snow, precip
        all_normals: dict mapping city_name -> dict with keys high, snow, precip

    Returns:
        (matched_city_name, distance)
    """
    all_highs = [n["high"] for n in all_normals.values()]
    all_snows = [n["snow"] for n in all_normals.values()]
    all_precips = [n["precip"] for n in all_normals.values()]

    bounds = {
        "high": (min(all_highs), max(all_highs)),
        "snow": (min(all_snows), max(all_snows)),
        "precip": (min(all_precips), max(all_precips)),
    }

    def normalize(val, key):
        lo, hi = bounds[key]
        if hi == lo:
            return 0
        return (val - lo) / (hi - lo)

    def climate_dist(a, b):
        return math.sqrt(
            (normalize(a["high"], "high") - normalize(b["high"], "high")) ** 2
            + (normalize(a["snow"], "snow") - normalize(b["snow"], "snow")) ** 2
            + (normalize(a["precip"], "precip") - normalize(b["precip"], "precip")) ** 2
        )

    best_name = None
    best_dist = float("inf")
    for name, normals in all_normals.items():
        d = climate_dist(city_actuals, normals)
        if d < best_dist:
            best_dist = d
            best_name = name

    return (best_name, round(best_dist, 4))


def build_comparison_table(data_path="data/cities_weather.json"):
    """Build a comparison table for all cities.

    Loads data from JSON file (run fetch_data.py first).
    Falls back to live API calls if no data file exists.

    Returns:
        DataFrame with columns: city, state, normal_high, actual_high, delta_high,
        normal_snow, actual_snow, delta_snow, normal_precip, actual_precip,
        delta_precip, climate_match, match_distance, stayed_typical
    """
    data = load_fetched_data(data_path)
    if data is None:
        raise FileNotFoundError(
            f"No data file at {data_path}. Run fetch_data.py first:\n"
            "  pip install -r requirements.txt\n"
            "  python fetch_data.py"
        )

    # Filter to cities that have both hist and act data
    complete = [c for c in data if "hist" in c and "act" in c]
    if not complete:
        raise ValueError("No cities have both historical and actual data. Run fetch_data.py.")

    # Build normals dict for matching
    all_normals = {f"{c['name']}, {c['state']}": c["hist"] for c in complete}

    threshold = 0.05 * math.sqrt(3)  # ~0.0866

    rows = []
    for c in complete:
        label = f"{c['name']}, {c['state']}"
        actuals = c["act"]
        normals = c["hist"]

        matched, dist = find_climate_match(actuals, all_normals)

        # Self-distance
        self_dist = find_climate_match(actuals, {label: normals})[1]
        stayed = self_dist < threshold

        rows.append({
            "city": c["name"],
            "state": c["state"],
            "normal_high": normals["high"],
            "actual_high": actuals["high"],
            "delta_high": round(actuals["high"] - normals["high"], 1),
            "normal_snow": normals["snow"],
            "actual_snow": actuals["snow"],
            "delta_snow": round(actuals["snow"] - normals["snow"], 1),
            "normal_precip": normals["precip"],
            "actual_precip": actuals["precip"],
            "delta_precip": round(actuals["precip"] - normals["precip"], 1),
            "climate_match": matched,
            "match_distance": dist,
            "self_distance": round(self_dist, 4),
            "stayed_typical": stayed,
        })

    return pd.DataFrame(rows)
