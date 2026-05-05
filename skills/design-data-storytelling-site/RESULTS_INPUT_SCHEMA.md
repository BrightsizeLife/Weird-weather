# Results JSON input schema

When the brief sets `input_results_json_path`, the generated
`index.html` reads a `results.json` produced by the
[`bayesian-panel-modeling-in-r`](../bayesian-panel-modeling-in-r/) skill.
This document is the contract on the consuming side.

The producing side is documented at
[`bayesian-panel-modeling-in-r/RESULTS_SCHEMA.md`](../bayesian-panel-modeling-in-r/RESULTS_SCHEMA.md).
If you change one document, change the other.

## Mapping JSON fields to chapters

| JSON path | site chapter | rendered as |
|---|---|---|
| `metadata.{n_rows, n_units, time_min, time_max}` | hero / summary | inline kicker + stat cards |
| `metadata.warnings` | diagnostics | bulleted "what we adjusted along the way" list |
| `summary_statistics.overall` | summary | one big stat card: n, mean, sd |
| `summary_statistics.by_unit` | essay sidebars / table | optional sortable mini-table |
| `summary_statistics.by_time` | expected_values | secondary axis values for time labels |
| `summary_statistics.by_factor` | model | factor-level pre-fit context |
| `candidate_models[]` | model | "ladder" cards, one per attempted model |
| `candidate_models[].priors` | methodology | bulleted prior list, verbatim |
| `candidate_models[].diagnostics` | diagnostics | per-model status badge (`ok | warning | failed`) |
| `candidate_models[].loo` | loo | LOO comparison row |
| `selected_model` | model + methodology | "selected: M3 — reason" callout |
| `selected_model.caveats` | diagnostics | yellow callout list |
| `posterior_summaries.population_effects` | model | population-coefficient table with intervals |
| `posterior_summaries.group_effects` | expected_values | input for the per-unit caterpillar plot |
| `posterior_summaries.factor_effects` | model | per-factor contrast cards |
| `posterior_summaries.variance_components` | methodology | variance components table |
| `expected_values[]` | expected_values | per-(unit, time) posterior ribbon data |
| `observations_with_scores[]` | anomalies | heatmap + sortable table |
| `figures[]` | embedded `<img>` | pre-rendered figures from R |
| `diagnostics.overall_status` | diagnostics | top-of-tab status badge |
| `diagnostics.warnings` | diagnostics | bulleted list |
| `diagnostics.recommended_next_steps` | methodology | bulleted "next steps" |

## Trust gates

The generated file must lead with a "do not trust the posterior
summaries" warning when `diagnostics.overall_status != "ok"`. The
warning is rendered as a `.callout-box` at the top of every chapter
that surfaces posterior numbers (model, expected_values, anomalies,
methodology).

When `diagnostics.overall_status == "failed"`:

- Suppress all headline numbers in `summary`.
- Do not render the anomaly heatmap; replace with a
  "diagnostics did not pass; anomalies suppressed" panel.
- Keep the diagnostics chapter visible and detailed.

## Anomaly flag rendering

`observations_with_scores[].flag` ∈
`{normal, watch, unusual, extreme}`.

| flag | color token | non-color cue |
|---|---|---|
| `normal` | `--green` | (none) |
| `watch` | `--yellow` | `·` |
| `unusual` | `--red` (positive) / `--cold` (negative) | `▲` / `▼` |
| `extreme` | bright `--red` (positive) / `--cold` (negative) | `▲▲` / `▼▼` |

The legend names the underlying tail probability bands explicitly
(`< 0.10`, `< 0.05`, `< 0.01`).

## Defensive fetching

The generated file should:

1. Render the static layout first.
2. `fetch(input_results_json_path)` after `DOMContentLoaded`.
3. On success: hydrate chapters and remove placeholder content.
4. On failure: keep placeholder content, set
   `<body data-status="degraded">`, log a `console.warn` with the
   path that failed.
5. Never `alert()` the user; never block the page.

The fetch must be a same-origin or `file://` request. Do not embed
absolute URLs to a remote host inside the generated file.

## Versioning

If the producing skill bumps the schema, add a `metadata.schema_version`
key. The site skill should read it and warn (in the diagnostics
chapter) if the version is unrecognized, but still render what it
can.
