# `replicate-mixed-effects-in-R/` — deprecated

> **Use [`../bayesian-panel-modeling-in-r/`](../bayesian-panel-modeling-in-r/) instead.**

This folder contains the original frequentist (mgcv + REML) version
of the modeling skill. It is kept here for historical reference and
to avoid breaking any existing prompt-pasters that still target
this path. It is **deprecated**.

## Why deprecated

The reference Weird Weather analysis has been re-grounded in
Bayesian multilevel modeling. The new skill,
[`bayesian-panel-modeling-in-r`](../bayesian-panel-modeling-in-r/), is
the supported path forward. It uses brms / Stan and emits a JSON
contract that the [`design-data-storytelling-site`](../design-data-storytelling-site/)
skill consumes directly.

Specifically, the new skill:

- Provides explicit weakly informative priors and a prior predictive
  check.
- Uses PSIS-LOO for predictive model comparison instead of block
  leave-one-time-out CV.
- Produces uncertainty-aware anomaly scores from the posterior
  predictive distribution rather than per-unit residual z-scores.
- Documents the difference between expected-value (epred) and
  predicted-observation (predict) intervals.
- Carries explicit YAML frontmatter, an output JSON schema, an eval
  ledger, fixtures, and validation scripts.

## Migration

| in this skill | new equivalent |
|---|---|
| `data_path` (csv/json) | `data_path` (csv/json) |
| `unit_var` | `unit_col` |
| `time_var` | `time_col` |
| `outcome_var` | `outcome_col` |
| `factors` | `factor_cols` |
| `spline_k`, `spline_basis` | brms `s()` defaults; tune via `candidate_models` and sampler params |
| block LOOCV across `[baseline, with_factors, with_interactions]` | `candidate_models` + `loo_compare()` |
| `gam.check`, `concurvity`, `gam.vcomp` | `pp_check`, `loo`, `posterior` summaries |
| per-unit σ + per-unit z-score | posterior predictive `tail_probability`, `posterior_predictive_percentile`, flag vocabulary |
| `output/results.json` (this skill's shape) | new schema in [`../bayesian-panel-modeling-in-r/RESULTS_SCHEMA.md`](../bayesian-panel-modeling-in-r/RESULTS_SCHEMA.md) |

## Why we did not delete it

- Keeping the directory preserves any existing links to its
  `SKILL.md` / `PROMPT.md`.
- It documents the prior approach for readers who want to compare
  the frequentist and Bayesian framings.

If you still need a non-Bayesian fallback in the new skill, see the
note in
[`../bayesian-panel-modeling-in-r/BAYESIAN_WORKFLOW.md`](../bayesian-panel-modeling-in-r/BAYESIAN_WORKFLOW.md)
under "Packages" — `mgcv` is acceptable as a non-Bayesian
sanity-check fallback only.
