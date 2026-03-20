"""Weather comparison and climate matching analysis.

Reimplements the normalized Euclidean distance algorithm from index.html
for comparing actual weather against historical normals.
"""

import math
import time

import pandas as pd

from .cities import CITIES
from .openmeteo import get_winter_actuals


def compare_actual_vs_normal(actuals, normals):
    """Compare actual weather against normals, returning deltas.

    Args:
        actuals: dict with keys avg_high, total_snow, total_precip
        normals: dict with keys avg_high (or avg_high), avg_snow (or total_snow),
                 avg_precip (or total_precip)

    Returns:
        dict with delta and percent change for each metric
    """
    # Normalize key names
    a_high = actuals.get("avg_high", 0)
    n_high = normals.get("avg_high", 0)
    a_snow = actuals.get("total_snow", 0)
    n_snow = normals.get("avg_snow", normals.get("total_snow", 0))
    a_precip = actuals.get("total_precip", 0)
    n_precip = normals.get("avg_precip", normals.get("total_precip", 0))

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

    Uses normalized Euclidean distance across avg_high, snowfall, precip
    (same algorithm as index.html lines 433-444).

    Args:
        city_actuals: dict with keys high, snow, precip
        all_normals: dict mapping city_name -> dict with keys high, snow, precip

    Returns:
        (matched_city_name, distance)
    """
    # Compute bounds for normalization
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


def find_climate_match_from_registry(city_name):
    """Find climate match for a city using the built-in registry data.

    Uses the hardcoded hist/act data from cities.py (same as index.html).
    Returns (matched_city_name, distance, self_distance, is_asterisk).
    """
    # Build normals dict from all cities
    all_normals = {}
    for c in CITIES:
        all_normals[c["name"]] = c["hist"]

    # Find the target city
    target = None
    for c in CITIES:
        if c["name"].lower() == city_name.lower():
            target = c
            break

    if not target:
        raise ValueError(f"City not found: {city_name}")

    matched, dist = find_climate_match(target["act"], all_normals)
    self_dist = find_climate_match(target["act"], {target["name"]: target["hist"]})[1]

    threshold = 0.05 * math.sqrt(3)  # ~0.0866, same as index.html
    is_asterisk = self_dist < threshold

    return {
        "city": city_name,
        "matched_to": matched,
        "match_distance": dist,
        "self_distance": round(self_dist, 4),
        "stayed_typical": is_asterisk,
    }


def build_comparison_table(cities=None, use_registry=True):
    """Build a comparison table for multiple cities.

    Args:
        cities: List of city names (default: all 30 from registry)
        use_registry: If True, use hardcoded data from cities.py.
                      If False, fetch live data from Open-Meteo (slower).

    Returns:
        DataFrame with columns: city, state, normal_high, actual_high, delta_high,
        normal_snow, actual_snow, delta_snow, normal_precip, actual_precip,
        delta_precip, climate_match, match_distance
    """
    if cities is None:
        city_list = CITIES
    else:
        city_list = []
        for name in cities:
            for c in CITIES:
                if c["name"].lower() == name.lower():
                    city_list.append(c)
                    break

    # Build normals dict
    all_normals = {c["name"]: c["hist"] for c in CITIES}

    rows = []
    for c in city_list:
        if use_registry:
            actuals = c["act"]
        else:
            result = get_winter_actuals(c["lat"], c["lon"])
            actuals = {
                "high": result["avg_high"],
                "snow": result["total_snow"],
                "precip": result["total_precip"],
            }
            time.sleep(0.2)

        matched, dist = find_climate_match(
            actuals if "high" in actuals else {
                "high": actuals.get("avg_high", actuals.get("high")),
                "snow": actuals.get("total_snow", actuals.get("snow")),
                "precip": actuals.get("total_precip", actuals.get("precip")),
            },
            all_normals,
        )

        normals = c["hist"]
        rows.append({
            "city": c["name"],
            "state": c["state"],
            "normal_high": normals["high"],
            "actual_high": actuals.get("high", actuals.get("avg_high")),
            "delta_high": round(actuals.get("high", actuals.get("avg_high", 0)) - normals["high"], 1),
            "normal_snow": normals["snow"],
            "actual_snow": actuals.get("snow", actuals.get("total_snow")),
            "delta_snow": round(actuals.get("snow", actuals.get("total_snow", 0)) - normals["snow"], 1),
            "normal_precip": normals["precip"],
            "actual_precip": actuals.get("precip", actuals.get("total_precip")),
            "delta_precip": round(actuals.get("precip", actuals.get("total_precip", 0)) - normals["precip"], 1),
            "climate_match": matched,
            "match_distance": dist,
        })

    return pd.DataFrame(rows)
