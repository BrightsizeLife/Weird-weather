# Worked example — Promo Lift, by store

A retail analyst has 12 stores × 104 weeks of sales, a `promo` flag,
and a Bayesian fit from the
[`bayesian-panel-modeling-in-r`](../bayesian-panel-modeling-in-r/) skill.
They want to publish a single-page narrative.

## The pipeline

1. Run the Bayesian R skill on the panel:

   ```yaml
   data_path:      "data/sales.csv"
   unit_col:       "store"
   time_col:       "week"
   outcome_col:    "sales"
   factor_cols:    ["promo"]
   candidate_models: ["M0", "M1", "M2", "M3"]
   family:         "gaussian"
   ```

   That writes `output/results.json`, `output/figures/*.png`, etc.

2. Run the site skill with the brief below; point
   `input_results_json_path` at the JSON.

## The brief

```yaml
project_title:    "Promo Lift"
subtitle:         "104 weeks · 12 stores · what the promo actually did"
author:           "Sam Patel"
homepage_url:     "https://acme-analytics.example"
audience:         "RGM team and finance — numerate, not statisticians"
thesis:           "Across 12 stores and 104 weeks, promo weeks shifted the posterior expected mean upward; per-store deviations vary."

data_shape:       "12 stores × 104 weeks of revenue with a corporate promo flag for ~30% of weeks."
source_notes:     "Internal sales DB; promo flag from corporate calendar."
unit_label:       "store"
time_label:       "week"
outcome_label:    "weekly sales ($)"

tabs:             ["essay", "summary", "model", "loo", "expected_values",
                   "anomalies", "diagnostics", "methodology", "artifacts"]
default_tab:      "essay"
visual_style:     "weird_weather_dark"
include_methodology:        true
include_code_blocks:        true
include_exportable_posters: true

input_results_json_path:    "output/results.json"
embed_figures_paths:        ["output/figures/posterior_expected_ribbons.png",
                             "output/figures/anomaly_score_heatmap.png",
                             "output/figures/factor_effect_posteriors.png"]

output_file:      "index.html"
allow_cdn:        false
use_d3:           false
respect_light_scheme: false
include_kofi:     false
kofi_username:    null
analytics_id:     null
```

## What the LLM should return (sketch)

A complete `index.html` with:

### Header

- Title "Promo Lift" with the gradient text treatment.
- Subtitle "104 weeks · 12 stores · what the promo actually did."
- Byline.
- Home link.

### Tabs

essay → summary → model → loo → expected_values → anomalies →
diagnostics → methodology → artifacts.

### Essay tab

~700–1200 words of serif prose. Three sections:

1. *What the promo did, in one ribbon.* Posterior expected weekly
   sales by store, with and without promo, 50% / 90% credible bands.
2. *Where the lift concentrates.* Posterior contrast distributions
   for `promo` per store from `posterior_summaries.factor_effects`.
3. *Why the uncertainty matters.* The cautious sentence about LOO
   and the descriptive-not-causal disclaimer.

Stat-tip annotations on every numeric claim.

### Summary tab

Six stat cards, populated from the JSON:

- Posterior population mean lift in $/week (with 90% credible
  interval).
- Number of stores flagged `unusual` or `extreme` in the latest
  observed week.
- Posterior `sd_unit__factor_promo` if M3 was selected (cross-store
  variability).
- LOO `elpd_diff` between the selected model and `M1`.
- `diagnostics.overall_status` badge.
- Total observations and store/week coverage.

### Model tab

The model ladder cards from `candidate_models[]`. Each card shows
formula, fit status, diagnostics badge, and elpd_loo with SE.

### LOO tab

The `loo_compare`-style table with elpd_diff ± SE bars. The
verbatim cautious sentence about LOO appears as a `.callout-box`.

### Expected values tab

Posterior expected ribbons (50% and 90%) for the population, plus
a small-multiples grid per store. Anomaly heatmap legend appears
in this tab as well, since flags are derived from
`observations_with_scores`.

### Anomalies tab

Unit × time heatmap colored by `tail_probability`, with the four
flag bands (`normal | watch | unusual | extreme`). A sortable table
below.

### Diagnostics tab

`diagnostics.overall_status` badge. Per-model diagnostics cards.
`metadata.warnings` rendered as bullets. If `overall_status` is
`"warning"` or `"failed"`, a callout at the top of every other
chapter says "interpret with caution" or "do not trust the
posterior summaries."

### Methodology tab

Editable code blocks for the resolved priors, the model formula,
the call to `brm()`, and the LOO comparison code. Each has Copy +
Reset buttons. The chapter ends with a "this is descriptive, not
causal" line.

### Artifacts tab

Three posters at 1200×1500, scaled to fit:

1. **Posterior expected ribbons by store.** Selected model's
   per-store epred ribbons, sorted by posterior median deviation.
2. **The flag heatmap.** Unit × time tiles with the four flag bands.
3. **The model card.** Formula, priors, and the LOO comparison
   table on a single shareable poster.

Each poster has an Export button. Because `allow_cdn: false`, the
export button uses a canvas fallback rather than `html-to-image`.

### Footer

"Data: internal sales DB · Model: M3 (varying intercept and slope per
store, gaussian, weakly informative priors) · Sam Patel, 2026 ·
Descriptive, not causal."

## Iterating

- Want a serif body in the essay only? Already there.
- Want to swap out the JSON without regenerating the page? Edit
  `output/results.json` and reload.
- Want a CDN-powered version with html-to-image and D3? Set
  `allow_cdn: true` and `use_d3: true` in the brief and re-prompt.
- Want a light theme? Set `respect_light_scheme: true`.

The skill is the prompt. The output is one file. Iterating means
changing the brief or the JSON and re-running.
