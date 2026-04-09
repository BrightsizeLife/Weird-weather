#!/usr/bin/env python3
"""Fetch weather data for all 50 cities from Open-Meteo API.

Run this locally (not in sandbox) to pull real data:
    pip install -r requirements.txt
    python fetch_data.py

Outputs:
    data/cities_weather.json  — Full dataset with normals + actuals
    data/cities_weather.csv   — Same data as CSV for easy viewing

The script fetches:
    1. Winter 2025-2026 actuals (Dec 1 2025 – Feb 28 2026)
    2. Historical normals computed from 30 winters (1991-2020)

Both come from Open-Meteo's archive API — free, no API key needed.
"""

import json
import os
import sys
import time

import pandas as pd

from weather.cities import CITIES
from weather.openmeteo import get_daily_weather
from weather.utils import winter_date_range


def fetch_winter_summary(lat, lon, start_date, end_date):
    """Fetch daily data and compute winter summary stats."""
    df = get_daily_weather(lat, lon, start_date, end_date)
    if df.empty:
        return None
    return {
        "avg_high": round(df["temp_max_f"].mean(), 1),
        "avg_low": round(df["temp_min_f"].mean(), 1),
        "total_snow": round(df["snowfall_in"].sum(), 1),
        "total_precip": round(df["precip_in"].sum(), 1),
        "days": len(df),
    }


def fetch_actuals(cities, year=2025):
    """Fetch winter actuals for all cities."""
    start, end = winter_date_range(year)
    print(f"\n{'='*60}")
    print(f"Fetching winter {year}-{year+1} actuals ({start} to {end})")
    print(f"{'='*60}")

    results = {}
    for i, city in enumerate(cities):
        label = f"{city['name']}, {city['state']}"
        print(f"  [{i+1:2d}/{len(cities)}] {label}...", end=" ", flush=True)
        try:
            summary = fetch_winter_summary(city["lat"], city["lon"], start, end)
            if summary:
                results[label] = summary
                print(f"avg_high={summary['avg_high']}°F  "
                      f"snow={summary['total_snow']}\"  "
                      f"precip={summary['total_precip']}\"")
            else:
                print("NO DATA")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.3)  # be polite to the API

    return results


def fetch_normals_and_timeseries(cities, start_year=1991, end_year=2020):
    """Fetch 30-year winter normals AND per-year time series for all cities.

    This fetches each winter season individually, stores per-year values
    for time series analysis, and averages them for normals.
    Makes ~30 API calls per city = ~1500 calls total for 50 cities.
    Takes a few minutes but only needs to run once.

    Returns:
        (normals_dict, timeseries_dict) where:
        - normals_dict maps city_label -> aggregated normal stats
        - timeseries_dict maps city_label -> list of per-year dicts
    """
    print(f"\n{'='*60}")
    print(f"Computing {start_year}-{end_year} winter normals + time series")
    print(f"{'='*60}")

    normals = {}
    timeseries = {}
    for i, city in enumerate(cities):
        label = f"{city['name']}, {city['state']}"
        print(f"  [{i+1:2d}/{len(cities)}] {label}...", end=" ", flush=True)

        yearly_highs = []
        yearly_lows = []
        yearly_snow = []
        yearly_precip = []
        city_ts = []

        for year in range(start_year, end_year):
            start, end = winter_date_range(year)
            try:
                df = get_daily_weather(city["lat"], city["lon"], start, end)
                if not df.empty:
                    high = df["temp_max_f"].mean()
                    low = df["temp_min_f"].mean()
                    snow = df["snowfall_in"].sum()
                    precip = df["precip_in"].sum()
                    yearly_highs.append(high)
                    yearly_lows.append(low)
                    yearly_snow.append(snow)
                    yearly_precip.append(precip)
                    city_ts.append({
                        "year": year,
                        "high": round(high, 1),
                        "low": round(low, 1),
                        "snow": round(snow, 1),
                        "precip": round(precip, 1),
                    })
            except Exception:
                pass  # skip failed years
            time.sleep(0.05)  # light throttle

        timeseries[label] = city_ts

        if yearly_highs:
            normals[label] = {
                "avg_high": round(sum(yearly_highs) / len(yearly_highs), 1),
                "avg_low": round(sum(yearly_lows) / len(yearly_lows), 1),
                "avg_snow": round(sum(yearly_snow) / len(yearly_snow), 1),
                "avg_precip": round(sum(yearly_precip) / len(yearly_precip), 1),
                "years_sampled": len(yearly_highs),
            }
            print(f"avg_high={normals[label]['avg_high']}°F  "
                  f"snow={normals[label]['avg_snow']}\"  "
                  f"precip={normals[label]['avg_precip']}\"  "
                  f"({len(yearly_highs)} yrs)")
        else:
            print("NO DATA")

    return normals, timeseries


def main():
    print("Weird Weather — Data Fetcher")
    print(f"Cities: {len(CITIES)}")

    # Fetch actuals (fast — 1 API call per city)
    actuals = fetch_actuals(CITIES, year=2025)

    # Fetch normals + per-year time series (slower — 29 API calls per city)
    normals, timeseries = fetch_normals_and_timeseries(CITIES, start_year=1991, end_year=2020)

    # Combine into final dataset
    combined = []
    for city in CITIES:
        label = f"{city['name']}, {city['state']}"
        entry = {
            "name": city["name"],
            "state": city["state"],
            "lat": city["lat"],
            "lon": city["lon"],
        }

        act = actuals.get(label)
        if act:
            entry["act"] = {
                "high": act["avg_high"],
                "snow": act["total_snow"],
                "precip": act["total_precip"],
            }

        norm = normals.get(label)
        if norm:
            entry["hist"] = {
                "high": norm["avg_high"],
                "snow": norm["avg_snow"],
                "precip": norm["avg_precip"],
            }

        # Add time series (historical years + 2025 actual)
        ts = timeseries.get(label, [])
        if act:
            ts.append({
                "year": 2025,
                "high": act["avg_high"],
                "low": act.get("avg_low", None),
                "snow": act["total_snow"],
                "precip": act["total_precip"],
            })
        entry["timeseries"] = ts

        combined.append(entry)

    # Write output
    os.makedirs("data", exist_ok=True)

    with open("data/cities_weather.json", "w") as f:
        json.dump(combined, f, indent=2)
    print(f"\nWrote data/cities_weather.json ({len(combined)} cities)")

    # Also write a flat CSV
    rows = []
    for c in combined:
        row = {"name": c["name"], "state": c["state"], "lat": c["lat"], "lon": c["lon"]}
        if "hist" in c:
            row["hist_high"] = c["hist"]["high"]
            row["hist_snow"] = c["hist"]["snow"]
            row["hist_precip"] = c["hist"]["precip"]
        if "act" in c:
            row["act_high"] = c["act"]["high"]
            row["act_snow"] = c["act"]["snow"]
            row["act_precip"] = c["act"]["precip"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv("data/cities_weather.csv", index=False)
    print(f"Wrote data/cities_weather.csv")

    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Cities with actuals: {sum(1 for c in combined if 'act' in c)}/{len(combined)}")
    print(f"Cities with normals: {sum(1 for c in combined if 'hist' in c)}/{len(combined)}")

    # Quick sanity check
    print(f"\nSample data:")
    for name in ["Boston, MA", "Phoenix, AZ", "Denver, CO"]:
        for c in combined:
            if f"{c['name']}, {c['state']}" == name:
                print(f"  {name}:")
                if "hist" in c:
                    h = c["hist"]
                    print(f"    Normal:  {h['high']}°F high, {h['snow']}\" snow, {h['precip']}\" precip")
                if "act" in c:
                    a = c["act"]
                    print(f"    2025-26: {a['high']}°F high, {a['snow']}\" snow, {a['precip']}\" precip")


if __name__ == "__main__":
    main()
