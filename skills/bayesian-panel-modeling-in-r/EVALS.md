# Evals

Eval cases for the Bayesian R skill. Each case names what is fed in
and what to check in the produced `analysis.R` and (when run) its
outputs.

The Stan compilation + sampling cost makes "run every case in CI"
infeasible. The eval suite is therefore split:

- **Static evals** — the LLM produces `analysis.R`; we inspect the
  script for the required structures and forbidden patterns.
  Cheap. Run on every change.
- **Smoke evals** — run `analysis.R` against fixtures with very
  small data; check produced outputs.
  Run locally when R + brms + a Stan backend are available.
- **Schema evals** — run `validate_results_json.R` on a produced
  `output/results.json`. Cheap if you have R; not Stan-dependent.

## Eval ledger

| id | input | static check | smoke check | success criteria |
|---|---|---|---|---|
| E01 | minimal balanced panel (`fixtures/minimal_panel.csv`) | script contains `brms`, `loo`, `tidybayes`, posterior predictive checks, `add_epred_draws`, `add_predicted_draws` | `Rscript analysis.R` produces all required outputs; `results.json` validates | `diagnostics.overall_status == "ok"`; flags array is non-empty |
| E02 | no factor columns | script handles `factor_cols == []` without an `interactions` rung; M2 is skipped or reduced to M1 | runs to completion; `selected_model.model_id ∈ {M0, M1, M3}` | `diagnostics.overall_status == "ok"` |
| E03 | sparse units (`fixtures/sparse_units_panel.csv`, several units < `min_obs_per_unit`) | script applies `min_obs_per_unit` filter | runs; warnings include "dropped N units" | `metadata.warnings` non-empty; comparison table still produced |
| E04 | missing required column (drop `outcome_col` before run) | n/a (data-side test) | `Rscript analysis.R` exits non-zero with a clear error mentioning the missing column | clear, single-line error before any model fit |
| E05 | nonnumeric / unparseable time (`fixtures/bad_time_panel.csv`) | script declares `time_type` and converts; on parse failure exits with a clear error | `Rscript analysis.R` exits with a coercion error citing the failing rows | error message names `time_col` and `time_type` |
| E06 | too many factor levels (factor with > `max_factor_levels`) | script issues a warning, suggests binning | runs; `metadata.warnings` includes "factor X has Y levels" | `diagnostics.overall_status` is `"ok"` or `"warning"`; never silent |
| E07 | high Pareto-k scenario (small N, complex model) | script runs `reloo` or `kfold` per `fallback_cv` and records what it did | `metadata.warnings` includes the fallback note | `loo_compare` output uses the fallback CV when applicable |
| E08 | schema compliance | script writes `results.json` with all required keys | `Rscript scripts/validate_results_json.R output/results.json` returns 0 | every required key present; types match the schema |
| E09 | figure existence | script declares every figure path in `figures` | `Rscript scripts/check_required_outputs.R output` returns 0 | every figure listed in `figures` exists on disk |
| E10 | diagnostics failure behavior | inject a tiny dataset where MCMC will be unstable (e.g., 2 units × 3 obs) | script does not crash; report leads with "do not trust" warning | `diagnostics.overall_status ∈ {"warning", "failed"}`; `selected_model.caveats` non-empty |

## Static eval rubric

For E01–E10, when checking the produced `analysis.R`, mark FAIL if
the script:

- Calls `install.packages()` unconditionally.
- References `mgcv::gam` as the primary engine. (Optional sanity-check
  fallback only.)
- Says LOO "finds" or "selects the true model" anywhere.
- Claims a causal interpretation.
- Standardizes outcome without a corresponding back-transform.
- Drops `metadata.warnings`.
- Hardcodes paths outside `output_dir`.

Mark PASS otherwise.

## Smoke eval prerequisites

To run smoke evals locally:

1. R (≥ 4.2) installed.
2. `install.packages(c("brms", "tidyverse", "tidybayes", "posterior",
   "bayesplot", "loo", "jsonlite", "glue", "here", "patchwork",
   "scales", "janitor"))`.
3. Stan backend — `cmdstanr` (preferred) with `cmdstanr::install_cmdstan()`,
   or `rstan` with the matching toolchain.

Fixtures are tiny (≤ 50 rows) so the runtime is dominated by Stan
compilation, not sampling. Expect 1–3 minutes per smoke eval the
first time, ~30s after compilation cache is warm.

## Reporting

A skill change should:

1. Run all static evals.
2. Run schema evals if R is available.
3. Skip smoke evals if Stan is unavailable, but document that they
   were skipped.

The PR description should list which evals ran, which passed, and
which were skipped (and why).
