"""Utility functions: unit conversion, date helpers, geocoding."""

import requests


def celsius_to_fahrenheit(c):
    """Convert Celsius to Fahrenheit."""
    return c * 9 / 5 + 32


def fahrenheit_to_celsius(f):
    """Convert Fahrenheit to Celsius."""
    return (f - 32) * 5 / 9


def mm_to_inches(mm):
    """Convert millimeters to inches."""
    return mm / 25.4


def cm_to_inches(cm):
    """Convert centimeters to inches."""
    return cm / 2.54


def winter_date_range(year):
    """Return (start_date, end_date) for a winter season.

    winter_date_range(2025) -> ("2025-12-01", "2026-02-28")
    """
    end_year = year + 1
    # Handle leap years for February
    import calendar
    feb_days = 29 if calendar.isleap(end_year) else 28
    return (f"{year}-12-01", f"{end_year}-02-{feb_days:02d}")


def geocode_city(city_name):
    """Look up (lat, lon) for a city name.

    Checks the built-in city registry first, then falls back to
    Open-Meteo's free geocoding API.
    """
    # Try built-in registry first (avoid circular import)
    from .cities import find_city
    match = find_city(city_name)
    if match:
        return (match["lat"], match["lon"])

    # Fallback: Open-Meteo geocoding (free, no API key)
    resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city_name, "count": 1, "language": "en", "format": "json"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if "results" in data and data["results"]:
        r = data["results"][0]
        return (r["latitude"], r["longitude"])

    raise ValueError(f"Could not geocode city: {city_name}")
