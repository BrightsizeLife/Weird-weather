# Visualization spec

The generated `analysis.R` produces every figure listed here. Each
figure is a ggplot2 plot saved as PNG at print quality
(`width = 8`, `height = 5`, `dpi = 200`) unless noted.

The aesthetic goal is **calm, literate, and honest** — Weird Weather
DNA, not dashboard glitter. Every plot's subtitle names the
uncertainty interval. Color carries meaning; it is never the only
channel.

## Theme

A reusable `theme_weird()` function:

- Dark background (`#000`) when `dark_theme_plots: true`, light
  fallback otherwise.
- Monospace primary font (`"SF Mono", "Fira Code", "Consolas"`).
- Muted text color `#888` for axis text, `#E0E0E0` for plot text.
- 1px panel border in `#222`. No major gridlines on the dark theme;
  `linetype = "dotted"` minor grid in `#222`.
- Legend at top, horizontal.

Color palette (semantic):

| token | hex | use |
|---|---|---|
| `red` | `#E8594F` | hot / positive anomaly / brand accent |
| `yellow` | `#F5A623` | warning / annotation |
| `blue` | `#4A90D9` | cool / variables |
| `green` | `#69f0ae` | normal / within expected |
| `cold` | `#1565c0` | extreme negative anomaly |

## Diagnostic figures

Saved under `output/diagnostics/`.

| file | content | subtitle |
|---|---|---|
| `prior_predictive_check.png` | density of prior predictive draws over observed range | "Prior predictive draws (gray) vs observed (line). Wide enough? Absurd?" |
| `mcmc_rhat.png` | Rhat across parameters per model | "Rhat by parameter. Acceptable < 1.05." |
| `mcmc_neff.png` | bulk + tail ESS ratios per model | "Effective sample size ratios. Acceptable ≥ 0.1." |
| `mcmc_trace_key_parameters.png` | trace plots for representative parameters | "Trace plots for key parameters; chains should overlap." |
| `pareto_k_plot.png` | Pareto-k for selected model's LOO | "Pareto-k diagnostic. Counts above 0.7 motivate reloo or kfold." |
| `posterior_predictive_density.png` | `pp_check(type="dens_overlay")` | "Posterior predictive density vs observed." |
| `posterior_predictive_by_unit.png` | grouped pp_check on a sample of units | "Posterior predictive density vs observed, by unit (sample)." |
| `posterior_predictive_by_time.png` | binned by time | "Posterior predictive distribution vs observed, by time bin." |
| `residual_like_check_by_time.png` | observed minus posterior mean vs time | "Predicted minus observed by time. Look for structure." |

## Story figures

Saved under `output/figures/`.

| file | content | required elements | subtitle |
|---|---|---|---|
| `observed_vs_expected_by_time.png` | observed points + posterior expected mean line + 90% credible ribbon, faceted or pooled by time | data points, posterior mean, ribbon | "Posterior expected mean with 90% credible interval; points are observations." |
| `observed_vs_expected_by_unit.png` | small-multiples per unit (sampled if >24 units) of the same overlay | per-unit panels with shared y-axis | "Per-unit posterior expected mean with 90% credible interval." |
| `posterior_expected_ribbons.png` | population-level expected value over time with ribbon | line + 50%/90% nested ribbons | "Population-level posterior expected mean. 50% and 90% credible intervals." |
| `unit_deviation_caterpillar.png` | per-unit posterior intervals for the random intercept (or trend), sorted | dot + segment per unit | "Per-unit deviation from population intercept (50% and 90% credible intervals)." |
| `anomaly_score_heatmap.png` | unit × time tile heatmap colored by `tail_probability`, with explicit flag bands | colorbar bands, flag legend | "Posterior predictive tail probability by unit and time. Flags: watch / unusual / extreme." |
| `factor_effect_posteriors.png` (if factors) | posterior contrast distributions per factor level | density or interval-eye | "Posterior contrast distributions vs reference level (50% and 90% credible intervals)." |
| `model_comparison_loo.png` | elpd diff with SE bars, sorted | dot + horizontal SE bars | "LOO elpd_diff with ±1 SE bars. LOO compares predictive performance, not truth." |
| `uncertainty_explainer.png` | a small reference plot showing what the ribbons mean (epred vs predict) | two ribbons over a single example unit | "Epred (mean uncertainty) vs predicted (mean + noise). The wider one includes residual noise." |

## Chart construction rules

- **Always** show uncertainty. A line without a ribbon is incomplete.
- **Two ribbons or one band with shading** distinguish 50% from 90%.
  Default to nested 50% / 90% ribbons.
- **Distinguish epred from predict** in subtitles. Readers will
  conflate them otherwise.
- **Avoid chartjunk.** No drop shadows, no gradient fills inside data
  marks, no 3D.
- **Use a fixed aspect ratio** within figure family; don't let
  ggplot's defaults vary panel size between plots.
- **Color carries meaning.** Red = positive anomaly, blue/cold =
  negative anomaly, yellow = warning state, green = within expected.
  Never use color for purely decorative grouping.
- **Color is not the only channel.** Anomaly flags also have a
  textual label and a sort order on the heatmap.
- **Axis labels include units.** "°F", "$/wk", "admissions / month."
- **Subtitle names the interval.** Not "uncertainty band" — say
  "90% credible interval" or "90% posterior predictive interval."

## Caterpillar plot specifics

- One row per unit, sorted by posterior median.
- Dot at posterior median, thick segment for 50% credible interval,
  thin segment for 90% credible interval.
- A reference line at 0 (the population mean / no-deviation).
- Color the dot by sign of the median (red positive, blue negative)
  for the dark theme; never rely on color alone — the position vs.
  zero is the primary cue.

## Anomaly heatmap specifics

- Tile per (unit, time) cell.
- Fill encodes `tail_probability`, with discrete flag breaks
  (`extreme < 0.01`, `unusual < 0.05`, `watch < 0.10`, `normal`
  otherwise).
- Y axis: units, ordered by posterior median deviation.
- X axis: time, in the original units.
- Legend: 4 discrete flag bands with their probability ranges.
- Provide a small inset table or caption listing the 5 most extreme
  flagged cells.

## Honesty rules

- Do not put a smooth trend line through observational data without
  a credible interval.
- Do not call a single posterior summary "the answer." Show the
  distribution.
- Do not annotate "winners" or "losers"; use the flag vocabulary.
- Do not cherry-pick units; if you facet a sample, say so in the
  subtitle and pick by `posterior_predictive_percentile` extremes
  symmetrically.
- Every figure must be reproducible from `seed` + the code.
