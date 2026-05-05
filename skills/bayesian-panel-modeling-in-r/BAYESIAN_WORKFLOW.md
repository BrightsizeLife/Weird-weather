# Bayesian workflow — the operative version

This is the workflow the generated `analysis.R` follows. It is not
"pick one model and pray." It is the standard
[Bayesian workflow](https://arxiv.org/abs/2011.01808) (Gelman et al.):
priors → prior predictive → fit → diagnostics → posterior predictive →
model comparison → interpretation, with every step capable of telling
you to stop.

## Packages

Core (required):

- `tidyverse` — data manipulation and plotting plumbing
- `brms` — Bayesian regression interface to Stan
- `posterior` — draws-as-data and convergence diagnostics
- `tidybayes` — tidy interface to draws, `add_epred_draws`,
  `add_predicted_draws`
- `bayesplot` — diagnostic + posterior predictive check plots
- `loo` — PSIS-LOO, model comparison, Pareto-k
- `jsonlite`, `here`, `glue`, `patchwork`, `scales`, `janitor`

Backend:

- `cmdstanr` (preferred) with a CmdStan installation
- `rstan` as fallback

Optional, if useful and only when justified:

- `projpred` — projection predictive variable selection / submodel
  evaluation
- `marginaleffects` or `emmeans` — average marginal effects, contrasts

Not central:

- `mgcv` — only as a non-Bayesian sanity-check fallback. Not the main
  engine.
- `DHARMa` — DHARMa is built around frequentist GLM/GLMM residuals;
  prefer brms / bayesplot posterior predictive checks here.

## The model ladder

Fit only the IDs in `candidate_models`. Higher rungs require more
data — let `min_obs_per_unit`, `max_factor_levels`, and
`max_minutes_per_model` gate complexity.

| id | formula | when |
|---|---|---|
| `M0` | `outcome ~ 1 + (1 | unit)` | Always-available baseline. Tells you how much variance is between vs. within units. |
| `M1` | `outcome ~ 1 + s(time_numeric) + (1 | unit)` | Adds a smooth trend across time. Default minimum useful model. |
| `M2` | `outcome ~ 1 + s(time_numeric) + <factors> + (1 | unit)` | Adds factor fixed effects. Skipped if `factor_cols` is empty. |
| `M3` | `outcome ~ 1 + s(time_numeric) + <factors> + (1 + time_scaled | unit)` | Varying intercept + slope per unit (correlated). |
| `M4` | M3 + factor-by-unit varying effects (e.g. `(1 | unit:factor)`) or selected interactions | Only if every unit-by-factor cell has enough obs. |
| `M5` | M3/M2 + cyclic seasonal term (e.g. `s(month_of_year, bs = "cc")`) | Only if `time_type` exposes a seasonal cycle. |

### Convergence-friendly fallbacks

- If the correlated `(1 + time_scaled | unit)` model fails to converge
  after one retry with `adapt_delta = 0.99`, fall back to the
  uncorrelated form `(1 + time_scaled || unit)` and record the
  switch in `metadata.warnings`. Document this choice in the report.
- If smooths take too long to compile/sample, fall back to a
  polynomial: replace `s(time_numeric)` with
  `time_numeric + I(time_numeric^2) + I(time_numeric^3)` and record.
- If `M4` cannot be fit because of sparse cells, skip with
  `skip_reason: "insufficient_data_for_interaction"`.

## Priors

Priors are **part of the model**. The script must record the resolved
priors in the per-model `priors` field of `results.json`.

Defaults (assume standardized predictors; if `standardize_outcome` is
true, replace `mean(y)` and `sd(y)` with 0 and 1):

| parameter | prior | rationale |
|---|---|---|
| `Intercept` | `normal(mean(y), 2 * sd(y))` | Centered on the data, wide enough to be regulated weakly |
| `b` (population coefs) | `normal(0, 1)` (standardized predictors) | Weakly informative; mass concentrated on plausible standardized effects |
| `sd` (group-level SDs) | `student_t(3, 0, 2.5)` | Heavy-tailed and weakly regularizing; or `exponential(1)` on standardized scale |
| `sigma` | `student_t(3, 0, 2.5)` | Same logic |
| `sds` (smooth wiggliness) | brms default, **explicitly recorded** | Avoid silent priors |

Do not invent priors that are sharper than the data warrants. If you
want a stronger prior, justify it in the report.

## Prior predictive check

Fit one model with `sample_prior = "only"` and plot draws against the
observed data range. The check passes if prior draws are wide enough
to cover the data without being absurd (e.g., temperatures of 1000°F
are absurd; the prior is too wide).

If absurd, tighten and retry. Record the iteration.

## Sampling

Default: `chains = 4, iter = 4000, warmup = 1000`. With cmdstanr,
parallelize via `cores = parallel::detectCores()` capped at `chains`.

Set `control = list(adapt_delta = adapt_delta, max_treedepth =
max_treedepth)`.

Per fit, capture:

- `max_rhat`
- `min_bulk_ess`, `min_tail_ess`
- `n_divergent`
- `max_treedepth_hits`
- E-BFMI per chain (via `posterior::ebfmi` if available)

## Diagnostics gate

A model is **acceptable** when:

- `max_rhat < 1.05`
- `min_bulk_ess >= 400` and `min_tail_ess >= 400`
- `n_divergent == 0`
- `max_treedepth_hits == 0`

Otherwise the model is **warning** or **failed**, and the report must
say so. The diagnostics gate is not optional.

If divergences happen, raise `adapt_delta` to 0.99 and retry once. If
still divergent, record the warning and proceed only for the purpose
of producing the report; do not present its posterior summaries as
trustworthy.

## Posterior predictive checks

Use `bayesplot::pp_check()`. At minimum:

- density overlay (`type = "dens_overlay"`)
- group-level overlay by a sample of units (`type = "dens_overlay_grouped"`)
- time-binned check
- residual-like check vs. time

A model that produces posterior predictive draws that systematically
miss the data on these views is not interpretable, regardless of LOO.

## LOO and model comparison

- `loo()` (or `add_criterion(fit, "loo")`) per model.
- `loo_compare()` for pairwise comparison.
- Report `elpd_diff` and `se_diff` per pair. The leading model is
  preferred when `elpd_diff > 2 * se_diff`. Otherwise prefer the
  simpler model and record the tie.
- Pareto-k diagnostic: count `pareto_k > 0.7`. If many, run `reloo()`
  or `kfold()` per `fallback_cv`.
- Optionally compute stacking weights when multiple models are
  plausible.

**The cautious sentence the report must contain:** *PSIS-LOO
estimates expected log predictive density on new data drawn from the
same DGP, under the model assumptions. It does not identify the
true data-generating process; it ranks candidate models on predictive
performance, with uncertainty.*

## Selected model

Rule:

1. Among models with acceptable diagnostics, pick the one with
   highest `elpd_loo` such that `elpd_diff > 2 * se_diff` to the
   next-best.
2. If no such gap exists, prefer the simpler model.
3. If no model has acceptable diagnostics, the report leads with a
   "do not trust the posterior" warning and `selected_model.caveats`
   includes a `"diagnostics_unacceptable"` entry.

## Posterior summaries

For the selected model:

- Population effects: posterior mean / sd / q05 / q50 / q95, plus
  rhat / bulk_ess for transparency.
- Group effects: per-unit posterior intervals (the data behind the
  caterpillar plot).
- Factor effects: posterior contrasts vs. the reference level.
- Variance components: `sd_*` per group term, `sigma`, smooth `sds`.

## Expected values + prediction intervals

- Build a (unit × time) prediction grid covering observed combinations.
- `add_epred_draws()` — posterior draws of the **expected mean**,
  integrated over the random effects of *that* unit. Summarize per
  cell as q05 / q50 / q95.
- `add_predicted_draws()` — posterior draws of the **predicted
  observation** (epred + residual noise). Summarize per cell as
  q05 / q50 / q95.

Distinguish the two intervals in every plot subtitle.

## Anomaly scores

Anomaly scoring is **uncertainty-aware** by construction. For each
observation `(unit, time, y_obs)`:

- `tail_probability`:
  - if `y_obs > expected_q50`: `mean(Y_rep >= y_obs)`
  - else: `mean(Y_rep <= y_obs)`
  - i.e., the smaller posterior predictive tail.
- `posterior_predictive_percentile`: the empirical CDF of `y_obs` in
  the posterior predictive draws.
- `standardized_residual_like_score`:
  `(y_obs - expected_q50) / sd(Y_rep)`. **Document explicitly** that
  this is a rough scale, not a t-statistic and not a frequentist
  z-score.

Flag thresholds:

| flag | tail_probability |
|---|---|
| `extreme` | `< 0.01` |
| `unusual` | `< 0.05` |
| `watch` | `< 0.10` |
| `normal` | otherwise |

These flags are the language to use in the storytelling site, not
"good/bad" or "best/worst."

## What this workflow does not do

- It does not prove a causal effect. The report must say so.
- It does not prove a "true" model. LOO is predictive comparison
  under the model assumptions.
- It does not replace domain knowledge in choosing priors and family.
- It does not handle measurement error, missingness mechanisms, or
  selection bias automatically — those require explicit modeling.
