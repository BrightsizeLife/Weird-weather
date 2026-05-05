---
name: bayesian-panel-modeling-in-r
description: Generates a reproducible Bayesian R workflow for longitudinal or panel datasets using brms/Stan, multilevel models, prior and posterior predictive checks, LOO model comparison, posterior summaries, expected values, uncertainty-aware anomaly scores, diagnostics, visualizations, and JSON outputs for data storytelling. Use when the user has repeated measurements by unit over time and wants descriptive or predictive modeling with uncertainty, not causal inference.
---

# Skill · Bayesian multilevel modeling for panel data, in R

A reusable, agent-agnostic prompt kit. Feed it a panel dataset
(repeated measurements of units over time) and it produces a single
self-contained R analysis script that fits Bayesian multilevel models
with [brms](https://paulbuerkner.com/brms/), runs the full diagnostic
ladder, compares models with PSIS-LOO, and emits JSON the
[design-data-storytelling-site](../design-data-storytelling-site/) skill
can consume.

It replaces the older `replicate-mixed-effects-in-R` skill, which was
frequentist (mgcv + REML). LOO and PSIS replace block-LOOCV; brms
replaces mgcv as the modeling engine. The Weird Weather analysis
remains the reference application.

---

## When to use

All of these should be true:

- You have a **panel** dataset — repeated measurements of the same
  units over time.
- You want a **descriptive or predictive** answer with calibrated
  uncertainty, not a causal one.
- You can tolerate model fitting that takes minutes (small data) to
  tens of minutes (richer models, many chains).
- You can install brms and a Stan backend (`cmdstanr` preferred,
  `rstan` fallback).

## When **not** to use

- Pure cross-section (no repeated measurements per unit). Use a flat
  regression skill instead.
- You need causal identification (instrumental variables, RDD,
  difference-in-differences, synthetic control). This skill is
  explicitly descriptive/predictive.
- You need real-time scoring with sub-second latency. Stan posterior
  draws are not the right shape for that.
- The dataset is too small for partial pooling to do useful work
  (fewer than ~3 units, or fewer than ~3 observations per unit).

---

## Required inputs

Filled into the YAML block in [`PROMPT.md`](./PROMPT.md):

- `data_path`: CSV or JSON file path
- `unit_col`: column identifying the panel unit
- `time_col`: column identifying time
- `outcome_col`: numeric response
- `factor_cols`: optional categorical context columns
- `family`: response family (default `gaussian`)
- `candidate_models`: which rungs of the model ladder to fit
- Sampler / standardization / backend knobs

Full schema with defaults: [`PARAMETERS.md`](./PARAMETERS.md).

## Generated outputs

The generated R script writes:

| path | meaning |
|---|---|
| `output/results.json` | structured JSON for downstream skills (see [`RESULTS_SCHEMA.md`](./RESULTS_SCHEMA.md)) |
| `output/model_report.md` | human-readable interpretation |
| `output/model_comparison.csv` | LOO comparison table |
| `output/expected_values.csv` | unit/time-level posterior expected values + intervals |
| `output/observations_with_scores.csv` | observed values with uncertainty-aware anomaly scores |
| `output/summary_statistics.csv` | descriptive stats by unit/time/factor |
| `output/diagnostics/*.png` | MCMC + posterior predictive diagnostics |
| `output/figures/*.png` | publication figures (see [`VISUALIZATION_SPEC.md`](./VISUALIZATION_SPEC.md)) |
| `output/session_info.txt` | `sessionInfo()` for reproducibility |

---

## Workflow

The generated script is structured as a numbered pipeline. Each step
maps to a heading in the output.

1. Load + validate data (required cols, types, missingness).
2. Coerce unit/time/factors; standardize numeric predictors; optionally
   standardize outcome.
3. Summary statistics (overall, by unit, by time, by factor).
4. Exploratory plots.
5. Define weakly informative priors.
6. Prior predictive check.
7. Fit model ladder (`M0`–`M5`, see [`BAYESIAN_WORKFLOW.md`](./BAYESIAN_WORKFLOW.md)).
8. MCMC diagnostics (Rhat, ESS, divergences, treedepth, E-BFMI).
9. Posterior predictive checks (density overlay, group, time, residual-like).
10. PSIS-LOO + Pareto-k diagnostic; reloo or k-fold fallback.
11. Posterior summaries (population, group, factor, variance components).
12. Expected values + posterior predictive intervals by unit/time.
13. Uncertainty-aware anomaly scores + flags.
14. Save figures, CSVs, JSON, report.

The detailed Bayesian workflow guide is
[`BAYESIAN_WORKFLOW.md`](./BAYESIAN_WORKFLOW.md). Visualization spec is
[`VISUALIZATION_SPEC.md`](./VISUALIZATION_SPEC.md). Output JSON contract
is [`RESULTS_SCHEMA.md`](./RESULTS_SCHEMA.md).

---

## How to use

1. Open [`PROMPT.md`](./PROMPT.md). Fill in the YAML parameters.
2. Paste into your LLM. You get back a single `analysis.R`.
3. Run `Rscript analysis.R`.
4. Optionally run validators in [`scripts/`](./scripts/) on the output.

Worked example: [`EXAMPLE.md`](./EXAMPLE.md). Eval plan and fixtures:
[`EVALS.md`](./EVALS.md), [`fixtures/`](./fixtures/).

---

## Failure modes (the script must handle these explicitly)

| failure | response |
|---|---|
| missing required column | hard error before fitting |
| `time_col` is not numeric/date/year | hard error with a coercion hint |
| unit has < `min_obs_per_unit` rows | drop unit, warn, record in `metadata.warnings` |
| factor has only one level | drop term, warn |
| factor has > `max_factor_levels` levels | warn, suggest binning, fit anyway with a complexity warning |
| MCMC diverges or `max_rhat > 1.05` | mark `diagnostics.overall_status = "warning"` and tell the report not to trust the posterior |
| Pareto-k > 0.7 in many obs | run `reloo` or `kfold` per `fallback_cv` |
| brms / Stan not installed | clear message pointing to install instructions; non-zero exit |
| outcome family inappropriate for data range (e.g. negative values with `lognormal`) | hard error before fitting |

The script is **defensive by design**: bad diagnostics never silently
become a "result." If the posterior cannot be trusted, the report and
JSON say so.

---

## Validation entry points

Run from the directory where the generated `analysis.R` produced
`output/`:

```sh
Rscript skills/bayesian-panel-modeling-in-r/scripts/check_required_outputs.R output
Rscript skills/bayesian-panel-modeling-in-r/scripts/validate_results_json.R output/results.json
```

A smoke-test plan for fixtures is in
[`scripts/smoke_test_generated_script.R`](./scripts/smoke_test_generated_script.R).

The eval plan in [`EVALS.md`](./EVALS.md) lists the canonical test
cases (minimal balanced, no factors, sparse units, missing column,
nonnumeric time, too many factor levels, high Pareto-k, schema
compliance, plot existence, diagnostics-failure behavior).

---

## Statistical philosophy (operative, not decorative)

- This is **descriptive/predictive** Bayesian modeling unless you
  bring a causal design.
- LOO estimates **expected out-of-sample predictive accuracy under
  assumptions**. It does not "find the right model" or prove the
  data-generating process.
- Posterior predictive checks diagnose whether the model can generate
  data that resemble the observed data. Passing them is necessary,
  not sufficient.
- **Priors are part of the model.** They are reported, not hidden.
- **Diagnostics gate interpretation.** If MCMC diagnostics are bad,
  the report tells the reader not to trust the posterior summaries.
- Uncertainty intervals appear throughout — every effect, every
  expected value, every "anomaly."
- Anomaly flags are based on posterior predictive tail probabilities,
  not moral language. Use `normal | watch | unusual | extreme`.
- Avoid ranking units "best/worst" without the uncertainty attached.

---

## License

Part of [Weird Weather](https://github.com/BrightsizeLife/Weird-weather).
Use, fork, change. Attribution welcome but not required.
