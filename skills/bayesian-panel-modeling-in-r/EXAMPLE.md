# Worked example — 50 stations × 30 winters of temperature anomaly

The reference application of this skill is the Weird Weather analysis:
50 US weather stations, 30 winter seasons (1991–2020), winter-mean
temperature anomaly per station-year, with `region` and `climate_zone`
as factors.

## Brief, in one paragraph

> Across 30 winters and 50 stations, did individual stations
> experience seasons that were unusual *for that station*, after
> partial-pooling toward a population trend and accounting for region
> and climate zone? Quantify the uncertainty.

This is a descriptive, predictive question, not a causal one. We are
not asking "did climate change cause Denver's mild 2024 winter."

## Filled parameters

```yaml
data_path:        "data/winter_anomalies.csv"
unit_col:         "station"
time_col:         "year"
outcome_col:      "temperature_anomaly_F"
factor_cols:      ["region", "climate_zone"]
reference_levels: { region: "midwest", climate_zone: "humid_continental" }
time_type:        "year"
family:           "gaussian"

candidate_models: ["M0", "M1", "M2", "M3"]

standardize_predictors: true
standardize_outcome:    false

backend:        "cmdstanr"
chains:         4
iter:           4000
warmup:         1000
adapt_delta:    0.95
max_treedepth:  12

loo_strategy:   "psis_loo"
fallback_cv:    "kfold"
kfold_K:        10

run_prior_predictive: true
save_model_objects:   false
dark_theme_plots:     true

min_obs_per_unit:     5
max_factor_levels:    20
max_minutes_per_model: 30

output_dir:    "output"
seed:          42
```

## Running it

1. Copy [`PROMPT.md`](./PROMPT.md), drop in the YAML above.
2. Paste into Claude / GPT / Gemini.
3. Save the response as `analysis.R`.
4. `Rscript analysis.R`.

## What you'd expect to see

### Console (excerpt)

```
══ Loaded ══
n_rows:   1500
n_units:  50
time:     1991 → 2020
factors:  region (4 levels), climate_zone (5 levels)

══ Priors (M3) ══
Intercept     normal(0.21, 2.84)
b             normal(0, 1)
sd            student_t(3, 0, 2.5)
sigma         student_t(3, 0, 2.5)
sds           brms default (recorded in results.json)

══ Sampling (M3) ══
4 chains × 4000 iter, warmup 1000, adapt_delta 0.95
Elapsed: 142.3s

══ MCMC diagnostics (M3) ══
max_rhat:          1.003
min_bulk_ess:      1820
min_tail_ess:      1450
n_divergent:       0
max_treedepth_hits: 0
status:            ok

══ LOO comparison ══
        elpd_diff  se_diff
M3       0.0       0.0
M2     -23.4       8.1
M1     -41.2      11.3
M0    -180.7      19.4

══ Selected model: M3 ══
Reason: Highest elpd_loo with elpd_diff > 2*se_diff vs next-best (M2).

══ Anomaly flags (winter 2020, all stations) ══
extreme:  3 (KDEN, KSLC, KBOI)
unusual: 11
watch:   18
normal:  18
```

### Files

```
output/
├── results.json
├── model_report.md
├── model_comparison.csv
├── expected_values.csv
├── observations_with_scores.csv
├── summary_statistics.csv
├── session_info.txt
├── diagnostics/
│   ├── prior_predictive_check.png
│   ├── mcmc_rhat.png
│   ├── mcmc_neff.png
│   ├── mcmc_trace_key_parameters.png
│   ├── pareto_k_plot.png
│   ├── posterior_predictive_density.png
│   ├── posterior_predictive_by_unit.png
│   ├── posterior_predictive_by_time.png
│   ├── residual_like_check_by_time.png
│   └── divergences_summary.csv
└── figures/
    ├── observed_vs_expected_by_time.png
    ├── observed_vs_expected_by_unit.png
    ├── posterior_expected_ribbons.png
    ├── unit_deviation_caterpillar.png
    ├── anomaly_score_heatmap.png
    ├── factor_effect_posteriors.png
    ├── model_comparison_loo.png
    └── uncertainty_explainer.png
```

## Interpretation, the careful version

- **M3 wins on PSIS-LOO**, with elpd_diff to M2 well outside 2 × SE.
  This means M3 is preferred for predicting unseen station-years
  *under M3's assumptions*. It does not mean M3 is "true."
- **Diagnostics pass**: Rhat < 1.05, ESS > 400, no divergences.
  Posterior summaries are interpretable.
- **Posterior predictive checks** show the model captures the bulk
  of the distribution. Mild misfit at the lower tail is recorded as
  a caveat.
- **Anomaly flags** for winter 2020: KDEN, KSLC, KBOI are flagged
  `extreme`. The flag is uncertainty-aware — `tail_probability < 0.01`
  in the posterior predictive distribution. They are not "broken
  records"; they are observations with strong tail evidence under
  the model.
- **Caveats**: this is descriptive. It does not isolate El Niño,
  climate change, or local urbanization. Causal claims require a
  causal design.

## Adapting the example

Swap the columns and the question:

| domain | unit | time | outcome | factors |
|---|---|---|---|---|
| Retail | store | week | sales | promo |
| Public health | hospital | month | admissions | season |
| Education | school | year | test_score | curriculum_cohort |
| Energy | meter | hour | demand | day_of_week |
| Sports | team | season | wins | rule_change_era |

The prompt is parameterized exactly so this swap is a five-minute
exercise. Keep `min_obs_per_unit` honest: hourly meter data with 8760
obs per unit is one regime; sports teams with 10 seasons is another.
