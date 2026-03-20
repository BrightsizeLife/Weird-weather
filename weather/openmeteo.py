"""Open-Meteo Archive API client for historical weather data.

No API key required. Data available from 1940 onwards.
https://open-meteo.com/en/docs/historical-weather-api
"""

import time

import pandas as pd
import requests

from .utils import winter_date_range

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARS = "temperature_2m_max,temperature_2m_min,precipitation_sum,snowfall_sum"


def get_daily_weather(lat, lon, start_date, end_date):
    """Fetch daily weather data from Open-Meteo archive.

    Args:
        lat: Latitude
        lon: Longitude
        start_date: Start date as "YYYY-MM-DD"
        end_date: End date as "YYYY-MM-DD"

    Returns:
        DataFrame with columns: date, temp_max_f, temp_min_f, precip_in, snowfall_in
    """
    resp = requests.get(
        ARCHIVE_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": DAILY_VARS,
            "temperature_unit": "fahrenheit",
            "precipitation_unit": "inch",
            "timezone": "America/New_York",
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    daily = data.get("daily", {})
    if not daily or not daily.get("time"):
        return pd.DataFrame(columns=["date", "temp_max_f", "temp_min_f", "precip_in", "snowfall_in"])

    df = pd.DataFrame({
        "date": pd.to_datetime(daily["time"]),
        "temp_max_f": daily["temperature_2m_max"],
        "temp_min_f": daily["temperature_2m_min"],
        "precip_in": daily["precipitation_sum"],
        "snowfall_in": daily["snowfall_sum"],
    })
    return df


def get_winter_actuals(lat, lon, year=2025):
    """Get winter season summary for a location.

    Args:
        lat: Latitude
        lon: Longitude
        year: Start year of winter (Dec of this year through Feb of next year)

    Returns:
        dict with keys: avg_high, total_snow, total_precip
    """
    start, end = winter_date_range(year)
    df = get_daily_weather(lat, lon, start, end)

    if df.empty:
        return {"avg_high": None, "total_snow": None, "total_precip": None}

    return {
        "avg_high": round(df["temp_max_f"].mean(), 1),
        "total_snow": round(df["snowfall_in"].sum(), 1),
        "total_precip": round(df["precip_in"].sum(), 1),
    }


def compute_normals(lat, lon, start_year=1991, end_year=2020, months=None):
    """Compute climate normals by averaging across multiple winters.

    Fetches daily data for each winter from start_year to end_year-1
    (since winter spans two calendar years), then averages.

    Args:
        lat: Latitude
        lon: Longitude
        start_year: First year of normal period (default: 1991)
        end_year: Last year of normal period (default: 2020)
        months: Which months to include (default: [12, 1, 2] for winter)

    Returns:
        dict with keys: avg_high, avg_snow, avg_precip
    """
    if months is None:
        months = [12, 1, 2]

    all_highs = []
    all_snow = []
    all_precip = []

    for year in range(start_year, end_year):
        start, end = winter_date_range(year)
        try:
            df = get_daily_weather(lat, lon, start, end)
        except requests.RequestException:
            continue  # skip years with API errors

        if df.empty:
            continue

        all_highs.append(df["temp_max_f"].mean())
        all_snow.append(df["snowfall_in"].sum())
        all_precip.append(df["precip_in"].sum())

        # Be polite to the API
        time.sleep(0.1)

    if not all_highs:
        return {"avg_high": None, "avg_snow": None, "avg_precip": None}

    return {
        "avg_high": round(sum(all_highs) / len(all_highs), 1),
        "avg_snow": round(sum(all_snow) / len(all_snow), 1),
        "avg_precip": round(sum(all_precip) / len(all_precip), 1),
    }


def get_multi_city_weather(cities, start_date, end_date, delay=0.2):
    """Fetch weather for multiple cities, returns combined DataFrame.

    Args:
        cities: List of dicts with at least 'name', 'lat', 'lon' keys
        start_date: Start date as "YYYY-MM-DD"
        end_date: End date as "YYYY-MM-DD"
        delay: Seconds to wait between API calls (default: 0.2)

    Returns:
        DataFrame with a 'city' column plus all daily weather columns
    """
    frames = []
    for city in cities:
        try:
            df = get_daily_weather(city["lat"], city["lon"], start_date, end_date)
            df["city"] = city["name"]
            df["state"] = city.get("state", "")
            frames.append(df)
        except requests.RequestException as e:
            print(f"Warning: failed to fetch {city['name']}: {e}")
        time.sleep(delay)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)
