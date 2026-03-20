#!/usr/bin/env python3
"""Smoke test: verify the weather toolkit against known reference data.

Tests Open-Meteo API connectivity and validates that fetched data
is in the right ballpark compared to the curated values in index.html.
"""

import sys

from weather import find_city, get_coords, build_comparison_table
from weather.openmeteo import get_winter_actuals
from weather.meteostat_client import get_winter_normals


def check_tolerance(label, fetched, expected, abs_tol=None, pct_tol=None):
    """Check if fetched value is within tolerance of expected."""
    if fetched is None:
        return False, f"{label}: fetched=None, expected={expected}"

    if abs_tol is not None:
        ok = abs(fetched - expected) <= abs_tol
        diff = fetched - expected
        return ok, f"{label}: fetched={fetched}, expected={expected}, diff={diff:+.1f} (tol=±{abs_tol})"

    if pct_tol is not None and expected != 0:
        pct = abs(fetched - expected) / abs(expected) * 100
        ok = pct <= pct_tol
        return ok, f"{label}: fetched={fetched}, expected={expected}, diff={pct:.0f}% (tol=±{pct_tol}%)"

    return fetched == expected, f"{label}: fetched={fetched}, expected={expected}"


def main():
    print("=" * 60)
    print("Weather Toolkit Verification")
    print("=" * 60)

    test_cities = ["Boston", "Phoenix", "Denver"]
    all_pass = True

    # Test 1: City registry lookups
    print("\n--- Test 1: City Registry ---")
    for name in test_cities:
        city = find_city(name)
        if city:
            print(f"  PASS  {name} -> ({city['lat']}, {city['lon']})")
        else:
            print(f"  FAIL  {name} not found")
            all_pass = False

    # Test 2: Open-Meteo API - fetch winter 2025-2026 actuals
    print("\n--- Test 2: Open-Meteo Winter Actuals ---")
    expected = {
        "Boston":  {"avg_high": 34, "total_snow": 61.0, "total_precip": 5.7},
        "Phoenix": {"avg_high": 72, "total_snow":  0.0, "total_precip": 1.5},
        "Denver":  {"avg_high": 53, "total_snow":  8.0, "total_precip": 2.0},
    }

    for name in test_cities:
        lat, lon = get_coords(name)
        try:
            actuals = get_winter_actuals(lat, lon, year=2025)
            print(f"\n  {name} (Open-Meteo):")
            print(f"    avg_high={actuals['avg_high']}°F  snow={actuals['total_snow']}\"  precip={actuals['total_precip']}\"")

            exp = expected[name]
            # Temperature: ±5°F tolerance (gridded vs station data)
            ok, msg = check_tolerance("avg_high", actuals["avg_high"], exp["avg_high"], abs_tol=5)
            status = "PASS" if ok else "FAIL"
            print(f"    {status}  {msg}")
            if not ok:
                all_pass = False

            # Snow: ±50% tolerance (snow is highly variable between grid and station)
            ok, msg = check_tolerance("snow", actuals["total_snow"], exp["total_snow"], pct_tol=50)
            status = "PASS" if ok else "WARN"  # Snow is advisory, not a hard fail
            print(f"    {status}  {msg}")

            # Precip: ±40% tolerance
            ok, msg = check_tolerance("precip", actuals["total_precip"], exp["total_precip"], pct_tol=40)
            status = "PASS" if ok else "WARN"
            print(f"    {status}  {msg}")

        except Exception as e:
            print(f"  FAIL  {name}: {e}")
            all_pass = False

    # Test 3: Meteostat normals
    print("\n--- Test 3: Meteostat Winter Normals ---")
    for name in test_cities:
        lat, lon = get_coords(name)
        try:
            normals = get_winter_normals(lat, lon)
            print(f"  {name}: avg_high={normals.get('avg_high')}°F, monthly_precip={normals.get('avg_precip_monthly')}\"")
            if normals.get("avg_high") is not None:
                print(f"    PASS  Data retrieved")
            else:
                print(f"    WARN  No data available (Meteostat coverage may be limited)")
        except Exception as e:
            print(f"  WARN  {name}: {e}")

    # Test 4: Comparison table
    print("\n--- Test 4: Comparison Table ---")
    try:
        table = build_comparison_table(cities=test_cities)
        print(f"  PASS  Generated table with {len(table)} rows, {len(table.columns)} columns")
        print(f"  Columns: {list(table.columns)}")
        for _, row in table.iterrows():
            print(f"    {row['city']}: matched to {row['climate_match']} (dist={row['match_distance']:.4f})")
    except Exception as e:
        print(f"  FAIL  {e}")
        all_pass = False

    # Summary
    print("\n" + "=" * 60)
    if all_pass:
        print("ALL TESTS PASSED")
    else:
        print("SOME TESTS FAILED (see above)")
    print("=" * 60)

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
