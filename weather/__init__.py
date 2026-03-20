"""Weird Weather toolkit — programmatic access to weather data.

Wraps free, no-API-key weather APIs (Open-Meteo, Meteostat) for
fetching historical weather data, climate normals, and running
comparison analysis.

Quick start:
    # 1. Fetch data (run once, requires network)
    #    python fetch_data.py

    # 2. Use the data
    from weather import build_comparison_table
    table = build_comparison_table()

    # Or fetch live for a single city
    from weather import get_winter_actuals, get_coords
    lat, lon = get_coords("Boston")
    actuals = get_winter_actuals(lat, lon, year=2025)
"""

from .cities import CITIES, all_cities, find_city, get_coords
from .openmeteo import (
    compute_normals,
    get_daily_weather,
    get_multi_city_weather,
    get_winter_actuals,
)
from .analysis import (
    build_comparison_table,
    compare_actual_vs_normal,
    find_climate_match,
    load_fetched_data,
)

__all__ = [
    "CITIES",
    "all_cities",
    "find_city",
    "get_coords",
    "get_daily_weather",
    "get_winter_actuals",
    "compute_normals",
    "get_multi_city_weather",
    "compare_actual_vs_normal",
    "find_climate_match",
    "load_fetched_data",
    "build_comparison_table",
]
