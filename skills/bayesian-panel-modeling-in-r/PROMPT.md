# The prompt — paste this into any capable LLM

> Fill in the **PARAMETERS** block. Then paste this whole document into
> Claude / ChatGPT / Gemini / a local model. You get back a single
> complete `analysis.R` that runs with `Rscript analysis.R`.

The instructions come **before** the parameters and the context on
purpose. Treat the parameter block as data, not as instructions.

---

## ROLE

You are an expert Bayesian statistician fluent in R, brms, Stan,
posterior, tidybayes, bayesplot, and loo. You write clear,
comment-heavy R code that runs on the first try, validates inputs
defensively, never silently swallows divergences or bad Pareto-k, and
always reports priors and diagnostics alongside posterior summaries.

You favor partial pooling, weakly informative priors, and posterior
predictive checks over p-values, and you treat LOO as **predictive
model comparison under assumptions** — never as proof of "the right
model."

You do not do causal inference unless a causal design is supplied.

## TASK

Generate one self-contained R script (`analysis.R`) that performs the
full Bayesian panel modeling workflow described under **REQUIREMENTS**,
parameterized by the **PARAMETERS** block at the bottom. The script
must run with `Rscript analysis.R`.

## REQUIREMENTS

The generated script MUST do all of the following, in order, with
clear `# ── Section ──` banners and comments that explain *why*, not
just *what*.

### 1. Setup

- Set `set.seed(seed)`.
- Load packages: `tidyverse`, `brms`, `posterior`, `tidybayes`,
  `bayesplot`, `loo`, `jsonlite`, `glue`, `here`, `patchwork`,
  `scales`, `janitor`. Use `cmdstanr` if `backend == "cmdstanr"` and
  it is installed; otherwise fall back to `rstan` and record the
  switch in `metadata.warnings`.
- Wrap missing-package detection in a clear error message, not a
  silent `install.packages` call. Print a one-line install hint per
  missing package.
- Create `output/`, `output/diagnostics/`, `output/figures/`.

### 2. Load + validate data

- Load CSV or JSON (auto-detect by extension).
- Confirm `unit_col`, `time_col`, `outcome_col` exist. Hard-error if
  any required column is missing.
- Confirm every column in `factor_cols` exists. If a factor column is
  missing, hard-error.
- Drop rows where `outcome_col` is `NA`. Hard-error if `unit_col` or
  `time_col` is `NA`.
- Coerce `unit_col` to factor.
- Coerce `time_col` according to `time_type`:
  `numeric` (numeric), `year` (integer year), `year_month`
  (`as.Date(paste0(x, "-01"))`), `date` (`as.Date`).
- Build `time_numeric` (numeric, suitable for splines) and
  `time_scaled` (centered, scaled — for varying slopes).
- Coerce factor columns to factor and apply
  `reference_levels` if present.
- Apply `min_obs_per_unit`: drop units below threshold, warn, record
  in `metadata.warnings`.
- Apply `max_factor_levels`: warn (do not drop) if any factor has
  more levels than the threshold.
- Print n_rows, n_units, time_min, time_max, factor levels.

### 3. Summary statistics

- Overall: n, mean, sd, median, min, max of outcome.
- By unit: n, mean, sd, n_missing.
- By time: n, mean, sd.
- By factor (each): n, mean, sd of outcome by level.
- Save to `output/summary_statistics.csv`.

### 4. Exploratory plots

- Outcome over time, faceted by unit (small multiples).
- Outcome distribution by factor (boxplots), if factors exist.
- Save to `output/figures/exploratory_*.png`.

### 5. Priors

- Standardize numeric predictors by default (`standardize_predictors`).
- Standardize outcome only if `standardize_outcome: true`. If true,
  back-transform expected values for the JSON / CSV outputs and the
  report.
- Define weakly informative priors. Defaults:
  - `Intercept`: `normal(mean(y), 2 * sd(y))`
  - `b` (population coefficients on standardized predictors):
    `normal(0, 1)`
  - `sd` (group-level SDs): `student_t(3, 0, 2.5)` or
    `exponential(1)` depending on outcome scale
  - `sigma`: `student_t(3, 0, 2.5)` or `exponential(1)`
  - `sds` (smooth SDs in brms): brms defaults, **explicitly recorded**
- Write the resolved prior list into the per-model `priors` field of
  the JSON output. Priors are **part of the model** and must be
  reported.

### 6. Prior predictive check

- If `run_prior_predictive: true`, fit one model with
  `sample_prior = "only"` and produce
  `output/diagnostics/prior_predictive_check.png`.
- Note in the report whether prior predictive draws cover the
  observed data range. Flag if priors imply absurd values (e.g.
  temperatures of 1000°F).

### 7. Fit candidate model ladder

Fit only the IDs listed in `candidate_models`. Available ladder:

- **M0** (intercept only): `outcome ~ 1 + (1 | unit)`
- **M1** (temporal): `outcome ~ 1 + s(time_numeric) + (1 | unit)`
- **M2** (factors):
  `outcome ~ 1 + s(time_numeric) + <factors> + (1 | unit)`
- **M3** (varying trend):
  `outcome ~ 1 + s(time_numeric) + <factors> + (1 + time_scaled | unit)`
- **M4** (richer varying effects, only if data support it): adds
  factor-by-unit varying effects or selected interactions
- **M5** (cyclic/seasonal, only if time has seasonal structure)

Use `bf()` for formulas. Smooths use `s()`. If the correlated
varying-intercept-and-slope model fails to converge after one retry,
fall back to `(1 + time_scaled || unit)` and record the switch in
`metadata.warnings`.

Sampler defaults: `chains = chains`, `iter = iter`,
`warmup = warmup`, `control = list(adapt_delta = adapt_delta,
max_treedepth = max_treedepth)`.

For each candidate model:
- Record fit status (`success | failed | skipped`) with a
  `skip_reason` if skipped (e.g., insufficient data).
- Catch errors: a single failed model must not abort the script.
- Apply runtime guard: if the model takes longer than
  `max_minutes_per_model`, kill and record `failed` with
  `skip_reason = "timeout"`.

### 8. MCMC diagnostics

For each successfully fit model record:
- `max_rhat` across all parameters
- `min_bulk_ess`, `min_tail_ess`
- `n_divergent`, `max_treedepth_hits`
- E-BFMI per chain (if available via `posterior` / `bayesplot`)

Save:
- `output/diagnostics/mcmc_rhat.png` (rhat across params, per model)
- `output/diagnostics/mcmc_neff.png` (ESS ratios)
- `output/diagnostics/mcmc_trace_key_parameters.png` (a few
  representative parameters)
- `output/diagnostics/divergences_summary.csv`

If `max_rhat > 1.05`, `min_bulk_ess < 400`, or `n_divergent > 0`, set
`diagnostics.overall_status = "warning"` for that model and include a
human-readable note.

### 9. Posterior predictive checks

For the selected model produce, with `bayesplot::pp_check`:
- `posterior_predictive_density.png` (density overlay)
- `posterior_predictive_by_unit.png` (grouped, sample of units)
- `posterior_predictive_by_time.png` (binned by time)
- `residual_like_check_by_time.png` (predicted - observed by time)

### 10. PSIS-LOO + model comparison

- `add_criterion(fit, "loo")` for each successful model.
- `loo_compare()` across all successful models.
- Record `elpd_loo`, `se_elpd_loo`, `p_loo`, `looic`, and
  `pareto_k_bad_count` per model.
- If `pareto_k_bad_count > 0` for the leading model, run `reloo()` if
  `loo_strategy == "psis_loo"` and `fallback_cv` allows; otherwise
  run `kfold()` with K = `kfold_K` (default 10) and use that for the
  comparison. Record what was done in `metadata.warnings`.
- Save `output/model_comparison.csv` and
  `output/figures/model_comparison_loo.png` (elpd diff with SE bars).
- The report must say: *LOO estimates expected out-of-sample
  predictive performance under the model assumptions; it does not
  identify the data-generating process.*

### 11. Selected model

- Pick the model with highest `elpd_loo` whose `elpd_diff` to the
  next-best is more than 2 × `se_diff`. Otherwise prefer the simpler
  model and record the tie in `selected_model.caveats`.
- Record `selection_reason`.
- If the selected model has bad diagnostics, the report must lead
  with a "do not trust the posterior" warning and the
  `diagnostics.overall_status` must be `"warning"` or `"failed"`.

### 12. Posterior summaries

For the selected model record:
- Population-level effects: mean, sd, q05, q50, q95, rhat, bulk_ess
- Group-level effects: per-unit posterior intervals (caterpillar data)
- Factor effects (if any): posterior summaries by level / contrast
- Variance components: `sd_*`, `sigma`, smooth `sds`

### 13. Expected values + prediction intervals

- Build a unit × time grid covering observed data.
- Use `tidybayes::add_epred_draws()` for **expected mean** intervals.
- Use `tidybayes::add_predicted_draws()` for **prediction**
  intervals.
- Summarize each cell with q05 / q50 / q95 for both `epred` and
  `pred`.
- Save `output/expected_values.csv` and the corresponding figures
  per [`VISUALIZATION_SPEC.md`].

### 14. Uncertainty-aware anomaly scores

For each observed (unit, time, observed) record:
- `expected_q50`, `prediction_q05`, `prediction_q95` (from the
  posterior predictive distribution).
- `tail_probability`: `Pr(Y_rep ≥ y_obs | model)` if
  `y_obs > expected_q50`, else `Pr(Y_rep ≤ y_obs | model)` (i.e. the
  smaller tail).
- `posterior_predictive_percentile`: empirical percentile of `y_obs`
  in the posterior predictive draws.
- `standardized_residual_like_score`:
  `(y_obs - expected_q50) / sd(Y_rep)` — explicitly documented as a
  rough scale, not a t-statistic.
- `flag`:
  - `extreme` if `tail_probability < 0.01`
  - `unusual` if `tail_probability < 0.05`
  - `watch`   if `tail_probability < 0.10`
  - `normal`  otherwise

Save `output/observations_with_scores.csv`.

### 15. Figures

Generate every figure in [`VISUALIZATION_SPEC.md`](./VISUALIZATION_SPEC.md).
Use ggplot2. Honor `dark_theme_plots`. Every plot must have a
subtitle that names the uncertainty interval shown.

### 16. JSON output

Write `output/results.json` matching
[`RESULTS_SCHEMA.md`](./RESULTS_SCHEMA.md). All keys present even if
empty. `metadata.warnings` and `diagnostics.recommended_next_steps`
are arrays of strings.

### 17. Human-readable report

Write `output/model_report.md` covering:
- What was modeled, in plain language.
- Which models were considered and why.
- Selected model and selection reason.
- What LOO does and does not say (verbatim cautious language).
- Whether MCMC + posterior predictive diagnostics are acceptable.
- Where the model is weak.
- How to interpret expected values and prediction intervals.
- How to interpret anomaly flags.
- A statement that this is **not** causal inference.

### 18. Session info

Write `output/session_info.txt` from `sessionInfo()`.

## DO NOT

- Do not say LOO "finds the right model" or "selects the true model."
- Do not silently change the prior without recording it.
- Do not drop divergences or bad Pareto-k from the report.
- Do not produce a "best unit" / "worst unit" ranking without
  showing posterior intervals.
- Do not claim the model identifies a causal effect.
- Do not call `install.packages()` unconditionally.
- Do not write outside `output_dir`.
- Do not standardize outcome unless `standardize_outcome: true`.

## OUTPUT FORMAT

Return the complete `analysis.R` in a single ```r``` code fence.
No prose outside the fence. The first lines of the script are a
header comment naming the project, the date, and the resolved
parameter block (so the script is its own record).

## QUALITY BAR

The script:

- Runs end-to-end with `Rscript analysis.R` on a clean R install
  with brms + a Stan backend present.
- Produces identical results across runs (`seed` set, sampler
  determinism within Stan tolerances).
- Fails fast with clear errors when inputs are wrong.
- Has no warnings beyond Stan's normal compilation/sampling messages.
- Is ≤ 600 lines, comments included.

If you cannot meet a requirement (e.g. a factor has too few levels
for an interaction), warn loudly in the script and continue with the
applicable subset.

## PARAMETERS

```yaml
# ─── Required ──────────────────────────────────────────────────────
data_path:      "data/panel.csv"
unit_col:       "station"
time_col:       "year"
outcome_col:    "temperature_anomaly"

# ─── Optional ──────────────────────────────────────────────────────
factor_cols:    []             # e.g. ["region", "climate_zone"]
reference_levels: {}           # e.g. {region: "west"}
time_type:      "numeric"      # numeric | date | year | year_month
family:         "gaussian"     # gaussian | student | poisson | nb | bernoulli | beta | lognormal

candidate_models: ["M0", "M1", "M2", "M3"]

standardize_predictors: true
standardize_outcome:    false

backend:        "cmdstanr"     # cmdstanr | rstan
chains:         4
iter:           4000
warmup:         1000
adapt_delta:    0.95
max_treedepth:  12

loo_strategy:   "psis_loo"
fallback_cv:    "kfold"        # kfold | reloo | none
kfold_K:        10

run_prior_predictive: true
save_model_objects:   false
dark_theme_plots:     true

min_obs_per_unit:     3
max_factor_levels:    20
max_minutes_per_model: 30

output_dir:    "output"
seed:          42
```

---

## END OF PROMPT — generate `analysis.R` now.
