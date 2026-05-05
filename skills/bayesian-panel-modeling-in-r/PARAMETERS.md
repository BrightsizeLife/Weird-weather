# Parameter reference

The YAML block at the bottom of [`PROMPT.md`](./PROMPT.md) is the
single source of truth that the generated script consumes. Every
parameter is documented here.

## Required

| name | type | example | notes |
|---|---|---|---|
| `data_path` | string | `"data/panel.csv"` | CSV (`.csv`) or JSON (`.json`). Path is relative to `Rscript`'s working directory. |
| `unit_col` | string | `"station"` | The panel unit. Coerced to factor. |
| `time_col` | string | `"year"` | Time index. Coerced according to `time_type`. |
| `outcome_col` | string | `"temperature_anomaly"` | Numeric response. Rows where this is `NA` are dropped. |

## Optional

| name | type | default | notes |
|---|---|---|---|
| `factor_cols` | list[string] | `[]` | Categorical context columns. Each becomes a fixed effect in `M2` and above. |
| `reference_levels` | object | first level | e.g. `{region: "west"}`. Sets the factor reference category. |
| `time_type` | enum | `"numeric"` | `numeric | date | year | year_month`. Drives coercion and the `s(time_numeric)` smooth. |
| `family` | enum | `"gaussian"` | brms response family. `gaussian | student | poisson | nb | bernoulli | beta | lognormal`. The script must error if family is incompatible with the outcome range (e.g. negative values with `lognormal`). |
| `candidate_models` | list[string] | `["M0","M1","M2","M3"]` | Which rungs of the model ladder to fit. See [`BAYESIAN_WORKFLOW.md`](./BAYESIAN_WORKFLOW.md). |
| `standardize_predictors` | bool | `true` | Standardize numeric predictors. Almost always on. |
| `standardize_outcome` | bool | `false` | If true, fit on the standardized scale. Back-transform expected values for outputs. |
| `backend` | enum | `"cmdstanr"` | `cmdstanr | rstan`. Falls back to `rstan` with a recorded warning if cmdstanr is unavailable. |
| `chains` | int | `4` | Number of MCMC chains. |
| `iter` | int | `4000` | Total iterations per chain (warmup + sampling). |
| `warmup` | int | `1000` | Warmup iterations per chain. |
| `adapt_delta` | float | `0.95` | Stan target acceptance. Raise (e.g. `0.99`) when divergences appear. |
| `max_treedepth` | int | `12` | Stan NUTS max tree depth. Raise to `15` for hard posteriors. |
| `loo_strategy` | enum | `"psis_loo"` | `psis_loo`. Currently the only supported primary strategy. |
| `fallback_cv` | enum | `"kfold"` | `kfold | reloo | none`. Triggered when many Pareto-k values exceed 0.7. |
| `kfold_K` | int | `10` | Number of folds when fallback is `kfold`. |
| `run_prior_predictive` | bool | `true` | Fit one model with `sample_prior = "only"` and plot draws. |
| `save_model_objects` | bool | `false` | If true, save `*.rds` brmsfit objects into `output/`. They are big. |
| `dark_theme_plots` | bool | `true` | Use a dark ggplot theme matching the Weird Weather palette. |
| `min_obs_per_unit` | int | `3` | Drop units below this. Recorded in `metadata.warnings`. |
| `max_factor_levels` | int | `20` | Warn if any factor exceeds this. Suggest binning. |
| `max_minutes_per_model` | int | `30` | Per-model runtime cap. Exceed → mark `failed`, `skip_reason: "timeout"`. |
| `output_dir` | string | `"output"` | Output root. |
| `seed` | int | `42` | `set.seed`, sampler seed, plot reproducibility. |

## Data shape contract

Long format: one row per (unit, time) observation.

```
station,year,temperature_anomaly,region,climate_zone
KORD,1991,-0.42,midwest,humid_continental
KORD,1992, 0.11,midwest,humid_continental
KDEN,1991,+0.83,west,semi_arid
...
```

If your data is wide, reshape with `tidyr::pivot_longer` first.

## When to override defaults

| situation | parameter | change |
|---|---|---|
| divergences in posterior | `adapt_delta` | raise to `0.99` |
| treedepth saturated | `max_treedepth` | raise to `15` |
| posterior is bimodal/funnel | `chains`, `iter` | more chains, more samples |
| outcome is bounded ≥ 0 | `family` | `lognormal` or `gamma` |
| outcome is a count | `family` | `poisson` or `nb` |
| outcome is a proportion | `family` | `beta` |
| many Pareto-k > 0.7 | `fallback_cv` | `kfold` |
| sparse small data | `candidate_models` | drop `M3`, `M4`, `M5` |
| seasonal time | `candidate_models` | include `M5` |
