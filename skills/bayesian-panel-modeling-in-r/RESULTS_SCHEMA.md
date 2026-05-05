# Results JSON schema

The generated `analysis.R` writes `output/results.json`. The
[`design-data-storytelling-site`](../design-data-storytelling-site/)
skill consumes it. This document is the contract.

All keys are present even when their value is empty (`null`, `{}`,
or `[]`). Consumers should not depend on key absence to mean
"missing"; they should check the value.

```json
{
  "metadata": {
    "generated_at": "2026-01-15T10:30:00Z",
    "data_path": "data/panel.csv",
    "n_rows": 1500,
    "n_units": 50,
    "unit_col": "station",
    "time_col": "year",
    "outcome_col": "temperature_anomaly",
    "factor_cols": ["region", "climate_zone"],
    "time_min": 1991,
    "time_max": 2020,
    "packages": {
      "brms": "2.21.0",
      "rstan": "2.32.6",
      "cmdstanr": "0.7.1",
      "loo": "2.7.0",
      "tidybayes": "3.0.6",
      "bayesplot": "1.11.1"
    },
    "modeling_engine": "brms",
    "backend": "cmdstanr",
    "warnings": [
      "Dropped 2 units below min_obs_per_unit=3.",
      "M3 fell back to uncorrelated ranef structure after divergence retry."
    ]
  },

  "summary_statistics": {
    "overall": {
      "n": 1500, "mean": 0.21, "sd": 1.42,
      "median": 0.18, "min": -4.10, "max": 4.95
    },
    "by_unit": [
      { "unit": "KORD", "n": 30, "mean": -0.10, "sd": 1.01, "n_missing": 0 }
    ],
    "by_time": [
      { "time": 1991, "n": 50, "mean": -0.30, "sd": 1.12 }
    ],
    "by_factor": [
      { "factor": "region", "level": "midwest", "n": 600, "mean": -0.05, "sd": 1.20 }
    ]
  },

  "candidate_models": [
    {
      "model_id": "M1",
      "formula": "outcome ~ 1 + s(time_numeric) + (1 | unit)",
      "fit_status": "success",
      "skip_reason": null,
      "priors": [
        { "class": "Intercept", "prior": "normal(0.21, 2.84)" },
        { "class": "b",         "prior": "normal(0, 1)" },
        { "class": "sd",        "prior": "student_t(3, 0, 2.5)" },
        { "class": "sigma",     "prior": "student_t(3, 0, 2.5)" }
      ],
      "sampling": {
        "chains": 4, "iter": 4000, "warmup": 1000,
        "adapt_delta": 0.95, "max_treedepth": 12,
        "elapsed_seconds": 142.3
      },
      "diagnostics": {
        "max_rhat": 1.003,
        "min_bulk_ess": 1820,
        "min_tail_ess": 1450,
        "n_divergent": 0,
        "max_treedepth_hits": 0,
        "ebfmi_min": 0.95,
        "status": "ok"
      },
      "loo": {
        "elpd_loo": -2453.21,
        "se_elpd_loo": 24.18,
        "p_loo": 38.4,
        "looic": 4906.42,
        "pareto_k_bad_count": 0
      }
    }
  ],

  "selected_model": {
    "model_id": "M3",
    "selection_reason": "Highest elpd_loo with elpd_diff > 2*se_diff vs next-best (M2).",
    "caveats": [
      "Posterior predictive checks show mild misfit at the lower tail."
    ]
  },

  "posterior_summaries": {
    "population_effects": [
      { "term": "Intercept",        "mean": 0.21, "sd": 0.18, "q05": -0.10, "q50": 0.21, "q95": 0.51, "rhat": 1.001, "bulk_ess": 4200 },
      { "term": "regionwest",       "mean": 0.42, "sd": 0.11, "q05":  0.24, "q50": 0.42, "q95": 0.61, "rhat": 1.000, "bulk_ess": 4800 }
    ],
    "group_effects": [
      { "unit": "KORD", "term": "Intercept",   "mean": -0.10, "sd": 0.21, "q05": -0.45, "q50": -0.10, "q95": 0.25 },
      { "unit": "KORD", "term": "time_scaled", "mean":  0.04, "sd": 0.07, "q05": -0.08, "q50":  0.04, "q95": 0.16 }
    ],
    "factor_effects": [
      { "factor": "region", "level": "west", "contrast_to": "midwest",
        "mean": 0.42, "q05": 0.24, "q50": 0.42, "q95": 0.61 }
    ],
    "variance_components": [
      { "term": "sd_unit__Intercept",   "mean": 0.55, "q05": 0.41, "q95": 0.74 },
      { "term": "sd_unit__time_scaled", "mean": 0.12, "q05": 0.07, "q95": 0.20 },
      { "term": "sigma",                "mean": 0.91, "q05": 0.86, "q95": 0.96 }
    ]
  },

  "expected_values": [
    {
      "unit": "KORD", "time": 2020,
      "expected_mean": 0.34, "expected_q05": 0.05, "expected_q50": 0.34, "expected_q95": 0.62,
      "prediction_q05": -1.32, "prediction_q50": 0.34, "prediction_q95": 2.01
    }
  ],

  "observations_with_scores": [
    {
      "unit": "KORD", "time": 2020,
      "observed": 1.85,
      "expected_q50": 0.34,
      "prediction_q05": -1.32,
      "prediction_q95": 2.01,
      "tail_probability": 0.062,
      "posterior_predictive_percentile": 0.938,
      "standardized_residual_like_score": 1.51,
      "flag": "watch"
    }
  ],

  "figures": [
    {
      "id": "observed_vs_expected_by_time",
      "path": "output/figures/observed_vs_expected_by_time.png",
      "title": "Observed vs expected by time",
      "description": "Posterior expected mean (line) with 90% credible ribbon vs observed points."
    }
  ],

  "diagnostics": {
    "overall_status": "ok",
    "warnings": [],
    "recommended_next_steps": [
      "Consider M4 with factor-by-unit varying effects if more data per cell becomes available."
    ]
  }
}
```

## Required keys

- `metadata` (object) — every nested field is required; arrays may be
  empty.
- `summary_statistics` — `overall`, `by_unit`, `by_time`, `by_factor`.
- `candidate_models` — array, one entry per attempted model. Failed
  / skipped models still appear with `fit_status` set accordingly.
- `selected_model` — `model_id` may be `null` if no model has
  acceptable diagnostics; `caveats` then explains.
- `posterior_summaries` — populated only for the selected model;
  empty arrays when `selected_model.model_id` is `null`.
- `expected_values` — array of unit/time cells with both
  `expected_*` (epred) and `prediction_*` (predicted observation)
  intervals.
- `observations_with_scores` — array of observations with anomaly
  scores and a flag.
- `figures` — array of `{id, path, title, description}`.
- `diagnostics` — `overall_status` is one of
  `"ok" | "warning" | "failed"`.

## Status semantics

- `"ok"`: every selected-model diagnostic passes the gate.
- `"warning"`: one or more diagnostics in the warning band; report
  tells the reader to interpret with caution.
- `"failed"`: the selected model is not interpretable. Site skill
  shows the diagnostics chapter and suppresses headline numbers.

## Compatibility

The site skill's [`RESULTS_INPUT_SCHEMA.md`](../design-data-storytelling-site/RESULTS_INPUT_SCHEMA.md)
maps this contract onto the rendered chapters. If you extend this
schema, update both documents.
