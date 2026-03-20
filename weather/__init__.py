"""Weird Weather toolkit — programmatic access to weather data.

Wraps free, no-API-key weather APIs (Open-Meteo, Meteostat) for
fetching historical weather data, climate normals, and running
comparison analysis.

Quick start:
    from weather import get_winter_actuals, find_city, build_comparison_table

    # Get winter 2025-2026 actuals for Boston
    lat, lon = get_coords("Boston")
    actuals = get_winter_actuals(lat, lon, year=2025)

    # Build full comparison table (uses built-in reference data)
    table = build_comparison_table()
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
    find_climate_match_from_registry,
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
    "find_climate_match_from_registry",
    "build_comparison_table",
]
