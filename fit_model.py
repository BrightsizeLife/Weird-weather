#!/usr/bin/env python3
"""Fit statistical model and compute distance matrices for the dashboard.

Reads data/cities_weather.json (produced by fetch_data.py) and outputs
data/dashboard_data.json — a single pre-computed bundle for the dashboard.

Model: weather ~ spline(year) + (year | city); sigma ~ city
  - B-spline smooth trend over year (fixed effect)
  - Per-city random intercept + random slope on year
  - Per-city residual standard deviation (heteroscedastic)

Distance matrices:
  - 5 metric combos × 2 distance methods = 10 matrices (50×50 each)
  - Pre-computed climate matches per metric

Usage:
    python fit_model.py
"""

import json
import math
import os
import sys

import numpy as np

try:
    from scipy.interpolate import BSpline
    from scipy.linalg import lstsq
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("Warning: scipy not found, using numpy-only fallback for splines")


# ── ENSO Classifications ─────────────────────────────────────────────────────
# DJF ONI-based classification (source: NOAA CPC)
# El Niño: ONI >= 0.5, La Niña: ONI <= -0.5, Neutral: between

ENSO_PHASES = {
    1991: "el_nino",    # 1991-92 winter
    1992: "neutral",
    1993: "neutral",
    1994: "el_nino",    # 1994-95
    1995: "la_nina",    # 1995-96
    1996: "neutral",
    1997: "el_nino",    # 1997-98 (very strong)
    1998: "la_nina",    # 1998-99
    1999: "la_nina",    # 1999-00 (strong)
    2000: "la_nina",    # 2000-01
    2001: "neutral",
    2002: "el_nino",    # 2002-03
    2003: "neutral",
    2004: "el_nino",    # 2004-05 (weak)
    2005: "la_nina",    # 2005-06 (weak)
    2006: "el_nino",    # 2006-07 (weak)
    2007: "la_nina",    # 2007-08 (strong)
    2008: "la_nina",    # 2008-09 (weak)
    2009: "el_nino",    # 2009-10 (moderate)
    2010: "la_nina",    # 2010-11 (moderate)
    2011: "la_nina",    # 2011-12 (moderate)
    2012: "neutral",
    2013: "neutral",
    2014: "el_nino",    # 2014-15 (weak)
    2015: "el_nino",    # 2015-16 (very strong)
    2016: "neutral",
    2017: "la_nina",    # 2017-18 (weak)
    2018: "el_nino",    # 2018-19 (weak)
    2019: "neutral",
    2020: "la_nina",    # 2020-21 (moderate)
    2021: "la_nina",    # 2021-22 (weak)
    2022: "la_nina",    # 2022-23 (weak)
    2023: "el_nino",    # 2023-24 (strong)
    2024: "neutral",
    2025: "la_nina",    # 2025-26 (weak-moderate)
}


# ── Data Loading ──────────────────────────────────────────────────────────────

def load_data(path="data/cities_weather.json"):
    """Load the fetched weather data."""
    if not os.path.exists(path):
        print(f"Error: {path} not found. Run fetch_data.py first.")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


# ── B-Spline Basis ────────────────────────────────────────────────────────────

def make_bspline_knots(x, df=6, degree=3):
    """Compute B-spline knot vector from training data.

    Args:
        x: array of training values (years)
        df: degrees of freedom (number of basis functions)
        degree: spline degree (3 = cubic)

    Returns:
        knots: knot vector
    """
    x = np.asarray(x, dtype=float)
    n_internal = df - degree - 1
    if n_internal < 0:
        n_internal = 0

    if n_internal > 0:
        quantiles = np.linspace(0, 100, n_internal + 2)[1:-1]
        internal_knots = np.percentile(x, quantiles)
    else:
        internal_knots = np.array([])

    lo, hi = x.min(), x.max()
    knots = np.concatenate([
        np.repeat(lo, degree + 1),
        internal_knots,
        np.repeat(hi, degree + 1),
    ])
    return knots


def bspline_basis(x, df=6, degree=3, knots=None):
    """Evaluate B-spline basis matrix.

    Args:
        x: array of values to evaluate at
        df: degrees of freedom (used only if knots is None)
        degree: spline degree (3 = cubic)
        knots: pre-computed knot vector (from make_bspline_knots)

    Returns:
        (n_obs, n_basis) design matrix
    """
    x = np.asarray(x, dtype=float)

    if knots is None:
        knots = make_bspline_knots(x, df=df, degree=degree)

    n_basis = len(knots) - degree - 1
    basis = np.zeros((len(x), n_basis))

    for i in range(n_basis):
        c = np.zeros(n_basis)
        c[i] = 1.0
        spl = BSpline(knots, c, degree, extrapolate=True)
        basis[:, i] = spl(x)

    return basis


def bspline_basis_numpy(x, df=6, x_train=None):
    """Fallback: polynomial basis if scipy unavailable.
    Uses x_train stats for consistent centering/scaling across train and predict.
    """
    x = np.asarray(x, dtype=float)
    if x_train is not None:
        x_train = np.asarray(x_train, dtype=float)
        mean, std = x_train.mean(), x_train.std() + 1e-10
    else:
        mean, std = x.mean(), x.std() + 1e-10
    x_std = (x - mean) / std
    return np.column_stack([x_std ** p for p in range(df)])


# ── Model Fitting ─────────────────────────────────────────────────────────────

def fit_metric_model(cities_data, metric, spline_df=6):
    """Fit: y ~ spline(year) + (year | city); sigma ~ city

    Args:
        cities_data: list of city dicts with timeseries
        metric: 'high', 'snow', or 'precip'

    Returns:
        dict with fitted values, predictions, z-scores, etc.
    """
    # Collect all observations
    city_labels = []
    city_indices = []
    years_all = []
    y_all = []
    city_map = {}  # label -> index

    for city in cities_data:
        label = f"{city['name']}, {city['state']}"
        ts = city.get("timeseries", [])
        if not ts:
            continue

        if label not in city_map:
            city_map[label] = len(city_map)

        ci = city_map[label]
        for pt in ts:
            val = pt.get(metric)
            if val is not None:
                city_labels.append(label)
                city_indices.append(ci)
                years_all.append(pt["year"])
                y_all.append(val)

    if len(y_all) < 10:
        return None

    y = np.array(y_all)
    years = np.array(years_all, dtype=float)
    ci_arr = np.array(city_indices)
    n_cities = len(city_map)
    n_obs = len(y)

    # Build design matrix: [spline_basis | city_dummies | city * year_centered]
    year_center = years.mean()
    year_scaled = (years - year_center) / 10.0  # scale years to decades

    # Compute knots once from training data, reuse for predictions
    if HAS_SCIPY:
        spline_knots = make_bspline_knots(years, df=spline_df)
        X_spline = bspline_basis(years, knots=spline_knots)
    else:
        X_spline = bspline_basis_numpy(years, df=spline_df, x_train=years)

    # City dummy variables (random intercepts)
    X_city = np.zeros((n_obs, n_cities))
    for i, ci in enumerate(ci_arr):
        X_city[i, ci] = 1.0

    # City × year interaction (random slopes)
    X_city_year = np.zeros((n_obs, n_cities))
    for i, ci in enumerate(ci_arr):
        X_city_year[i, ci] = year_scaled[i]

    # Full design matrix
    X = np.column_stack([X_spline, X_city, X_city_year])

    # Fit via least squares with ridge regularization on random effects
    # Regularize city effects and city×year effects to shrink toward zero
    n_spline = X_spline.shape[1]
    n_total = X.shape[1]

    # Add small ridge penalty to random effects
    lambda_re = 0.1
    penalty = np.zeros(n_total)
    penalty[n_spline:] = lambda_re
    P = np.diag(penalty)

    # Solve (X'X + P) β = X'y
    XtX = X.T @ X + P
    Xty = X.T @ y
    beta = np.linalg.solve(XtX, Xty)

    # Fitted values and residuals
    y_hat = X @ beta
    residuals = y - y_hat

    # Per-city sigma (heteroscedastic variance)
    city_sigmas = {}
    label_list = list(city_map.keys())
    for label, ci in city_map.items():
        mask = ci_arr == ci
        city_resid = residuals[mask]
        if len(city_resid) > 2:
            city_sigmas[label] = float(np.std(city_resid, ddof=1))
        else:
            city_sigmas[label] = float(np.std(residuals, ddof=1))

    # Extract coefficients
    beta_spline = beta[:n_spline]
    beta_city_intercept = beta[n_spline:n_spline + n_cities]
    beta_city_slope = beta[n_spline + n_cities:]

    # Generate smooth spline trend (population average, no city effects)
    year_grid = np.arange(1991, 2027, 0.5)
    if HAS_SCIPY:
        X_grid_spline = bspline_basis(year_grid, knots=spline_knots)
    else:
        X_grid_spline = bspline_basis_numpy(year_grid, df=spline_df, x_train=years)

    trend_values = X_grid_spline @ beta_spline
    global_sigma = float(np.std(residuals, ddof=1))

    spline_trend = []
    for i, yr in enumerate(year_grid):
        spline_trend.append({
            "year": float(yr),
            "fitted": round(float(trend_values[i]), 2),
            "ci_lo": round(float(trend_values[i] - 1.96 * global_sigma), 2),
            "ci_hi": round(float(trend_values[i] + 1.96 * global_sigma), 2),
        })

    # Per-city predictions and z-scores
    city_results = {}
    for city in cities_data:
        label = f"{city['name']}, {city['state']}"
        if label not in city_map:
            continue
        ci = city_map[label]
        ts = city.get("timeseries", [])
        sigma = city_sigmas.get(label, global_sigma)

        # City-specific fitted values for each year in its timeseries
        fitted_vals = []
        for pt in ts:
            yr = pt["year"]
            val = pt.get(metric)
            if val is None:
                continue
            yr_arr = np.array([yr], dtype=float)
            if HAS_SCIPY:
                xs = bspline_basis(yr_arr, knots=spline_knots)
            else:
                xs = bspline_basis_numpy(yr_arr, df=spline_df, x_train=years)
            # Population trend + city intercept + city slope
            yr_s = (yr - year_center) / 10.0
            pred = float((xs @ beta_spline).item()) + float(beta_city_intercept[ci]) + float(beta_city_slope[ci]) * yr_s
            fitted_vals.append({
                "year": yr,
                "actual": round(float(val), 2),
                "fitted": round(pred, 2),
                "ci_lo": round(pred - 1.96 * sigma, 2),
                "ci_hi": round(pred + 1.96 * sigma, 2),
            })

        # Z-score for 2025
        z_score = None
        anomaly_pct = None
        pt_2025 = [fv for fv in fitted_vals if fv["year"] == 2025]
        if pt_2025:
            resid_2025 = pt_2025[0]["actual"] - pt_2025[0]["fitted"]
            if sigma > 0:
                z_score = round(resid_2025 / sigma, 2)
                # Approximate percentile from z-score
                from math import erf
                anomaly_pct = round(50 * (1 + erf(abs(z_score) / 2**0.5)), 1)

        # Per-city ENSO analysis: how does this city respond to ENSO phases?
        city_enso = {"la_nina": [], "el_nino": [], "neutral": []}
        for fv in fitted_vals:
            yr = fv["year"]
            if yr == 2025:
                continue
            phase = ENSO_PHASES.get(int(yr), "neutral")
            resid = fv["actual"] - fv["fitted"]
            city_enso[phase].append(resid)

        enso_la_nina = round(float(np.mean(city_enso["la_nina"])), 3) if city_enso["la_nina"] else 0
        enso_el_nino = round(float(np.mean(city_enso["el_nino"])), 3) if city_enso["el_nino"] else 0
        enso_sensitivity = round(enso_el_nino - enso_la_nina, 3)

        # Volatility trend: is sigma increasing? Compare first half vs second half
        hist_fitted = [fv for fv in fitted_vals if fv["year"] < 2025]
        mid = len(hist_fitted) // 2
        if mid > 2:
            first_half_resids = [fv["actual"] - fv["fitted"] for fv in hist_fitted[:mid]]
            second_half_resids = [fv["actual"] - fv["fitted"] for fv in hist_fitted[mid:]]
            sigma_early = float(np.std(first_half_resids, ddof=1)) if len(first_half_resids) > 1 else sigma
            sigma_late = float(np.std(second_half_resids, ddof=1)) if len(second_half_resids) > 1 else sigma
            volatility_change = round(sigma_late - sigma_early, 3)
            volatility_ratio = round(sigma_late / sigma_early, 3) if sigma_early > 0 else 1.0
        else:
            volatility_change = 0
            volatility_ratio = 1.0

        city_results[label] = {
            "fitted_values": fitted_vals,
            "sigma": round(sigma, 3),
            "random_intercept": round(float(beta_city_intercept[ci]), 3),
            "random_slope": round(float(beta_city_slope[ci]), 4),
            "z_score_2025": z_score,
            "anomaly_pct": anomaly_pct,
            "enso_la_nina_effect": enso_la_nina,
            "enso_el_nino_effect": enso_el_nino,
            "enso_sensitivity": enso_sensitivity,
            "volatility_change": volatility_change,
            "volatility_ratio": volatility_ratio,
        }

    # ── Enhanced Analytics ──────────────────────────────────────────────────

    # 1. Trend significance: linear regression of metric on year
    unique_years = np.array(sorted(set(years_all)))
    year_means = []
    for yr in unique_years:
        mask = years == yr
        year_means.append(np.mean(y[mask]))
    year_means = np.array(year_means)

    # Simple OLS: y_mean = a + b * year
    yr_centered = unique_years - unique_years.mean()
    b_trend = np.sum(yr_centered * (year_means - year_means.mean())) / np.sum(yr_centered ** 2)
    a_trend = year_means.mean() - b_trend * 0
    trend_residuals = year_means - (a_trend + b_trend * yr_centered)
    se_b = np.sqrt(np.sum(trend_residuals ** 2) / (len(unique_years) - 2) / np.sum(yr_centered ** 2))
    t_stat = b_trend / se_b if se_b > 0 else 0
    # Approximate p-value from t-distribution (two-sided)
    df_resid = len(unique_years) - 2
    # Use normal approximation for p-value
    from math import erfc
    p_value = erfc(abs(t_stat) / 2**0.5)
    trend_per_decade = round(b_trend * 10, 3)
    trend_significant = p_value < 0.05
    trend_direction = "warming" if b_trend > 0 else "cooling"

    # 2. ENSO impact analysis
    enso_effects = {"el_nino": [], "la_nina": [], "neutral": []}
    for i, yr in enumerate(years_all):
        phase = ENSO_PHASES.get(int(yr), "neutral")
        resid_val = residuals[i]
        enso_effects[phase].append(float(resid_val))

    enso_means = {}
    for phase, vals in enso_effects.items():
        if vals:
            arr = np.array(vals)
            enso_means[phase] = {
                "mean": round(float(np.mean(arr)), 3),
                "std": round(float(np.std(arr, ddof=1)), 3) if len(arr) > 1 else 0,
                "n": len(arr),
            }
        else:
            enso_means[phase] = {"mean": 0, "std": 0, "n": 0}

    # ENSO significance: is La Niña different from El Niño?
    el_nino_resids = np.array(enso_effects["el_nino"]) if enso_effects["el_nino"] else np.array([0])
    la_nina_resids = np.array(enso_effects["la_nina"]) if enso_effects["la_nina"] else np.array([0])
    enso_diff = float(np.mean(el_nino_resids) - np.mean(la_nina_resids))

    # 3. Random effects correlation (intercept vs slope)
    intercepts = np.array([float(beta_city_intercept[i]) for i in range(n_cities)])
    slopes = np.array([float(beta_city_slope[i]) for i in range(n_cities)])

    if np.std(intercepts) > 0 and np.std(slopes) > 0:
        re_correlation = float(np.corrcoef(intercepts, slopes)[0, 1])
    else:
        re_correlation = 0.0

    # 4. Variance decomposition
    total_var = float(np.var(y))
    fitted_var = float(np.var(y_hat))
    residual_var = float(np.var(residuals))
    r_squared = fitted_var / total_var if total_var > 0 else 0

    # Spline-only variance (fixed effects without city effects)
    spline_only_fitted = X_spline @ beta_spline
    spline_var = float(np.var(spline_only_fitted))

    # City effects variance
    city_fitted = np.zeros(n_obs)
    for i in range(n_obs):
        ci = ci_arr[i]
        city_fitted[i] = float(beta_city_intercept[ci]) + float(beta_city_slope[ci]) * year_scaled[i]
    city_var = float(np.var(city_fitted))

    # 5. Random effects distribution for spaghetti plot
    random_effects_list = []
    for label, ci in city_map.items():
        random_effects_list.append({
            "city": label,
            "intercept": round(float(beta_city_intercept[ci]), 3),
            "slope_per_decade": round(float(beta_city_slope[ci]), 4),
            "sigma": round(city_sigmas.get(label, global_sigma), 3),
        })

    # Sort by slope for trajectory visualization
    random_effects_list.sort(key=lambda x: x["slope_per_decade"])

    # 6. ENSO year annotations for timeseries
    enso_years = []
    for yr in range(1991, 2026):
        phase = ENSO_PHASES.get(yr, "neutral")
        enso_years.append({"year": yr, "phase": phase})

    # 7. Sigma rankings (highest/lowest predictability)
    sigma_ranked = sorted(city_results.items(), key=lambda x: x[1]["sigma"], reverse=True)
    highest_sigma_city = sigma_ranked[0][0] if sigma_ranked else None
    lowest_sigma_city = sigma_ranked[-1][0] if sigma_ranked else None

    return {
        "spline_trend": spline_trend,
        "city_results": city_results,
        "global_sigma": round(global_sigma, 3),
        "trend": {
            "per_decade": trend_per_decade,
            "direction": trend_direction,
            "p_value": round(p_value, 4),
            "significant": trend_significant,
            "t_stat": round(t_stat, 3),
        },
        "enso": {
            "means": enso_means,
            "el_nino_vs_la_nina_diff": round(enso_diff, 3),
            "years": enso_years,
        },
        "random_effects": {
            "intercept_slope_correlation": round(re_correlation, 3),
            "intercept_sd": round(float(np.std(intercepts)), 3),
            "slope_sd": round(float(np.std(slopes)), 4),
            "effects": random_effects_list,
        },
        "variance_decomposition": {
            "total": round(total_var, 3),
            "r_squared": round(r_squared, 3),
            "spline_share": round(spline_var / total_var, 3) if total_var > 0 else 0,
            "city_share": round(city_var / total_var, 3) if total_var > 0 else 0,
            "residual_share": round(residual_var / total_var, 3) if total_var > 0 else 0,
        },
        "sigma_rankings": {
            "highest_sigma_city": highest_sigma_city,
            "lowest_sigma_city": lowest_sigma_city,
            "highest_sigma_val": round(sigma_ranked[0][1]["sigma"], 3) if sigma_ranked else 0,
            "lowest_sigma_val": round(sigma_ranked[-1][1]["sigma"], 3) if sigma_ranked else 0,
        },
    }


# ── Distance Matrices ────────────────────────────────────────────────────────

def compute_distance_matrices(cities_data):
    """Compute 50×50 distance matrices for multiple metrics and methods.

    Metrics: overall, temp, snow, rain, snow_rain
    Methods: euclidean, manhattan

    Returns:
        dict of metric -> method -> 2D list
        Also returns matches (per metric) and cluster order.
    """
    # Filter to cities with both hist and act
    complete = [c for c in cities_data if "hist" in c and "act" in c]
    labels = [f"{c['name']}, {c['state']}" for c in complete]
    n = len(complete)

    # Extract values
    hist_highs = np.array([c["hist"]["high"] for c in complete])
    hist_snows = np.array([c["hist"]["snow"] for c in complete])
    hist_precips = np.array([c["hist"]["precip"] for c in complete])

    act_highs = np.array([c["act"]["high"] for c in complete])
    act_snows = np.array([c["act"]["snow"] for c in complete])
    act_precips = np.array([c["act"]["precip"] for c in complete])

    # Normalization bounds (from historical normals)
    def norm_range(arr):
        lo, hi = arr.min(), arr.max()
        r = hi - lo
        if r == 0:
            r = 1
        return lo, r

    h_lo, h_r = norm_range(hist_highs)
    s_lo, s_r = norm_range(hist_snows)
    p_lo, p_r = norm_range(hist_precips)

    def normalize(val, lo, r):
        return (val - lo) / r

    # Normalized historical normals
    norm_h = normalize(hist_highs, h_lo, h_r)
    norm_s = normalize(hist_snows, s_lo, s_r)
    norm_p = normalize(hist_precips, p_lo, p_r)

    # Normalized actuals (using same bounds as normals for comparability)
    act_norm_h = normalize(act_highs, h_lo, h_r)
    act_norm_s = normalize(act_snows, s_lo, s_r)
    act_norm_p = normalize(act_precips, p_lo, p_r)

    # Define metric selections (which dimensions to use)
    metric_configs = {
        "overall": {"dims": ["high", "snow", "precip"]},
        "temp": {"dims": ["high"]},
        "snow": {"dims": ["snow"]},
        "rain": {"dims": ["precip"]},
        "snow_rain": {"dims": ["snow", "precip"]},
    }

    dim_map_hist = {"high": norm_h, "snow": norm_s, "precip": norm_p}
    dim_map_act = {"high": act_norm_h, "snow": act_norm_s, "precip": act_norm_p}

    distances = {}
    matches = {}

    for metric_name, config in metric_configs.items():
        dims = config["dims"]

        # Build vectors for this metric
        hist_vecs = np.column_stack([dim_map_hist[d] for d in dims])
        act_vecs = np.column_stack([dim_map_act[d] for d in dims])

        # Compute distance matrices (actual vs historical norms of all cities)
        # This shows: "how close is city i's actual winter to city j's normal winter?"
        euclidean_mat = np.zeros((n, n))
        manhattan_mat = np.zeros((n, n))

        for i in range(n):
            for j in range(n):
                diff = act_vecs[i] - hist_vecs[j]
                euclidean_mat[i, j] = float(np.sqrt(np.sum(diff ** 2)))
                manhattan_mat[i, j] = float(np.sum(np.abs(diff)))

        distances[metric_name] = {
            "euclidean": [[round(euclidean_mat[i, j], 4) for j in range(n)] for i in range(n)],
            "manhattan": [[round(manhattan_mat[i, j], 4) for j in range(n)] for i in range(n)],
        }

        # Find best match for each city (which historical normal matches its actual?)
        metric_matches = {}
        threshold_5pct = 0.05 * math.sqrt(len(dims))
        for i in range(n):
            best_j = int(np.argmin(euclidean_mat[i]))
            best_dist = euclidean_mat[i, best_j]
            self_dist = euclidean_mat[i, i]
            is_asterisk = bool(self_dist <= threshold_5pct)

            metric_matches[labels[i]] = {
                "match": labels[best_j],
                "distance": round(float(best_dist), 4),
                "self_distance": round(float(self_dist), 4),
                "is_asterisk": is_asterisk,
            }

        matches[metric_name] = metric_matches

    # Hierarchical clustering for heatmap ordering
    cluster_order = hierarchical_cluster_order(distances["overall"]["euclidean"], n)

    return distances, matches, labels, cluster_order


def hierarchical_cluster_order(dist_matrix, n):
    """Simple agglomerative clustering to order cities for heatmap.

    Uses average linkage on the symmetric part of the distance matrix.
    Returns a permutation of indices that groups similar cities together.
    """
    # Make symmetric: average of (actual_i vs normal_j) and (actual_j vs normal_i)
    mat = np.array(dist_matrix)
    sym = (mat + mat.T) / 2

    # Greedy nearest-neighbor chain ordering
    remaining = set(range(n))
    order = []
    current = 0  # start with first city
    remaining.remove(current)
    order.append(current)

    while remaining:
        dists = [(sym[current, j], j) for j in remaining]
        dists.sort()
        current = dists[0][1]
        remaining.remove(current)
        order.append(current)

    return order


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Weird Weather — Model Fitting & Distance Computation")

    # Load data
    data = load_data("data/cities_weather.json")
    print(f"Loaded {len(data)} cities")

    # Count cities with timeseries
    ts_count = sum(1 for c in data if c.get("timeseries"))
    print(f"Cities with time series: {ts_count}")

    # Fit models for each metric
    print("\n" + "=" * 60)
    print("Fitting statistical models...")
    print("=" * 60)

    model_results = {}
    for metric in ["high", "snow", "precip"]:
        print(f"  Fitting {metric}...", end=" ", flush=True)
        result = fit_metric_model(data, metric, spline_df=6)
        if result:
            n_cities = len(result["city_results"])
            z_scores = [v["z_score_2025"] for v in result["city_results"].values()
                        if v["z_score_2025"] is not None]
            if z_scores:
                max_z = max(z_scores, key=abs)
                max_city = [k for k, v in result["city_results"].items()
                            if v["z_score_2025"] == max_z][0]
                print(f"done ({n_cities} cities, max |z|={abs(max_z):.2f} at {max_city})")
            else:
                print(f"done ({n_cities} cities)")
            model_results[metric] = result
        else:
            print("FAILED (insufficient data)")

    # Compute distance matrices
    print("\n" + "=" * 60)
    print("Computing distance matrices...")
    print("=" * 60)

    distances, matches, city_labels, cluster_order = compute_distance_matrices(data)
    print(f"  {len(city_labels)} cities × 5 metrics × 2 methods = {len(city_labels)**2 * 10} distances")

    # Sample matches
    for sample_city in ["Boston, MA", "Phoenix, AZ", "Denver, CO"]:
        if sample_city in matches.get("overall", {}):
            m = matches["overall"][sample_city]
            ast = " ★" if m["is_asterisk"] else ""
            print(f"  {sample_city} → {m['match']}{ast} (d={m['distance']:.4f})")

    # Build dashboard bundle
    print("\n" + "=" * 60)
    print("Building dashboard data bundle...")
    print("=" * 60)

    bundle = {
        "generated": __import__("datetime").datetime.now().isoformat(),
        "cities": data,
        "model": model_results,
        "distances": distances,
        "matches": matches,
        "city_labels": city_labels,
        "cluster_order": cluster_order,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/dashboard_data.json", "w") as f:
        json.dump(bundle, f)

    # File size
    size_mb = os.path.getsize("data/dashboard_data.json") / (1024 * 1024)
    print(f"Wrote data/dashboard_data.json ({size_mb:.1f} MB)")

    # Summary statistics
    print(f"\n{'='*60}")
    print("MODEL SUMMARY")
    print(f"{'='*60}")
    for metric, result in model_results.items():
        z_scores = [v["z_score_2025"] for v in result["city_results"].values()
                    if v["z_score_2025"] is not None]
        if z_scores:
            z_arr = np.array(z_scores)
            print(f"  {metric:8s}: global_σ={result['global_sigma']:.2f}  "
                  f"mean_|z|={np.mean(np.abs(z_arr)):.2f}  "
                  f"max_|z|={np.max(np.abs(z_arr)):.2f}  "
                  f"anomalous(|z|>2): {np.sum(np.abs(z_arr) > 2)}/{len(z_arr)}")


if __name__ == "__main__":
    main()
