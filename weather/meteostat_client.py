"""Meteostat wrapper for pre-computed climate normals and daily history.

No API key required. Uses the meteostat Python library (v2 API).
https://dev.meteostat.net/python/
"""

from datetime import datetime

import pandas as pd
from meteostat import daily, normals, Point

from .utils import celsius_to_fahrenheit, cm_to_inches, mm_to_inches


def get_normals(lat, lon, start_year=1991, end_year=2020):
    """Get monthly climate normals from Meteostat.

    Returns DataFrame with columns:
        month, tavg_f, tmin_f, tmax_f, prcp_in, snow_in (where available)

    Note: Meteostat snow normals may not be available for all stations.
    """
    point = Point(lat, lon)
    data = normals(point, start_year, end_year).fetch()

    if data is None or data.empty:
        return pd.DataFrame()

    result = pd.DataFrame({"month": data.index})

    # Temperature: Meteostat returns Celsius
    if "tmax" in data.columns:
        result["tmax_f"] = data["tmax"].values
        result["tmax_f"] = result["tmax_f"].apply(
            lambda x: round(celsius_to_fahrenheit(x), 1) if pd.notna(x) else None
        )
    if "tmin" in data.columns:
        result["tmin_f"] = data["tmin"].values
        result["tmin_f"] = result["tmin_f"].apply(
            lambda x: round(celsius_to_fahrenheit(x), 1) if pd.notna(x) else None
        )
    if "tavg" in data.columns:
        result["tavg_f"] = data["tavg"].values
        result["tavg_f"] = result["tavg_f"].apply(
            lambda x: round(celsius_to_fahrenheit(x), 1) if pd.notna(x) else None
        )

    # Precipitation: Meteostat returns mm
    if "prcp" in data.columns:
        result["prcp_in"] = data["prcp"].values
        result["prcp_in"] = result["prcp_in"].apply(
            lambda x: round(mm_to_inches(x), 2) if pd.notna(x) else None
        )

    # Snow depth: Meteostat returns cm (when available — often NaN)
    if "snow" in data.columns:
        result["snow_in"] = data["snow"].values
        result["snow_in"] = result["snow_in"].apply(
            lambda x: round(cm_to_inches(x), 1) if pd.notna(x) else None
        )

    return result


def get_winter_normals(lat, lon, start_year=1991, end_year=2020):
    """Get winter (Dec-Feb) climate normals summary.

    Returns dict with keys: avg_high, avg_precip_monthly
    Note: snowfall normals are often unavailable in Meteostat.
    """
    df = get_normals(lat, lon, start_year, end_year)
    if df.empty:
        return {"avg_high": None, "avg_precip_monthly": None}

    winter = df[df["month"].isin([12, 1, 2])]
    if winter.empty:
        return {"avg_high": None, "avg_precip_monthly": None}

    result = {}
    if "tmax_f" in winter.columns:
        result["avg_high"] = round(winter["tmax_f"].mean(), 1)
    else:
        result["avg_high"] = None

    if "prcp_in" in winter.columns:
        result["avg_precip_monthly"] = round(winter["prcp_in"].mean(), 2)
    else:
        result["avg_precip_monthly"] = None

    return result


def get_daily_history(lat, lon, start_date, end_date):
    """Fetch daily historical data via Meteostat Point interface.

    Args:
        lat: Latitude
        lon: Longitude
        start_date: Start date as "YYYY-MM-DD"
        end_date: End date as "YYYY-MM-DD"

    Returns:
        DataFrame with daily weather data (units converted to F/inches)
    """
    point = Point(lat, lon)
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    data = daily(point, start, end).fetch()
    if data is None or data.empty:
        return pd.DataFrame()

    result = pd.DataFrame({"date": data.index})

    if "tmax" in data.columns:
        result["temp_max_f"] = data["tmax"].apply(
            lambda x: round(celsius_to_fahrenheit(x), 1) if pd.notna(x) else None
        ).values
    if "tmin" in data.columns:
        result["temp_min_f"] = data["tmin"].apply(
            lambda x: round(celsius_to_fahrenheit(x), 1) if pd.notna(x) else None
        ).values
    if "prcp" in data.columns:
        result["precip_in"] = data["prcp"].apply(
            lambda x: round(mm_to_inches(x), 2) if pd.notna(x) else None
        ).values
    if "snow" in data.columns:
        result["snow_in"] = data["snow"].apply(
            lambda x: round(cm_to_inches(x), 1) if pd.notna(x) else None
        ).values

    return result
