# Parameter reference

## Required parameters

| name | type | example | notes |
|---|---|---|---|
| `data_path` | string | `"data/panel.csv"` | CSV or JSON file. Relative to where you run `Rscript`. |
| `data_format` | enum | `"csv"` | One of `csv`, `json`. JSON expects an array of `{unit, time, outcome, …}` objects. |
| `unit_var` | string | `"store"` | The column that identifies the panel unit. |
| `time_var` | string | `"week"` | The column that varies within unit. Must be numeric or coercible. |
| `outcome_var` | string | `"sales"` | The numeric response. |

## Optional

| name | type | default | notes |
|---|---|---|---|
| `factors` | list of strings | `[]` | Categorical predictors. Each becomes a fixed effect, then a `:unit` interaction in the third nested model. Strings, not factors — the script coerces. |
| `reference_levels` | object | first level of each factor | The reference category for each factor. e.g., `{ "season": "winter" }`. |
| `evaluation_time` | numeric / string | `max(time)` | The time period to compute z-scores for. |
| `spline_k` | integer | `10` | Upper bound for `s(time, k=...)`. Generous is fine — REML picks the effective df below this. |
| `spline_basis` | enum | `"cr"` | One of `cr` (cubic regression), `tp` (thin plate), `bs` (B-spline). `cr` is fastest and usually plenty. |
| `output_dir` | string | `"output"` | Where the script writes `results.json` + diagnostic PDFs. |
| `seed` | integer | `42` | For reproducibility. |

## Data shape contract

The script expects **long** data — one row per unit-time observation:

```
| store | week | sales  | promo |
|-------|------|--------|-------|
| A     | 1    | 1234   | no    |
| A     | 2    | 1402   | yes   |
| A     | 3    | 1102   | no    |
| B     | 1    | 980    | no    |
...
```

If your data is wide (one column per time period), reshape first with
`tidyr::pivot_longer` *before* running this skill.

## Things to think about before you fill it out

- **Time spacing.** The model assumes time is roughly evenly spaced.
  Daily data + missing weekends is fine. Quarterly data with one big
  gap is fine. Daily data with a 3-year gap probably needs a
  break-point in the spline.

- **Factors with too many levels.** A factor with 100 levels means 100
  fixed-effect coefficients, and the `factor:unit` interaction explodes
  combinatorially. Bin first if you can. Or model that factor as a
  random effect by adding `s(big_factor, bs="re")` manually.

- **Factor that's a function of time.** ENSO phase, season, day-of-week
  — these are valid fixed effects. The model handles their joint
  estimation with the time smooth fine.

- **Outcome that's not gaussian.** This skill assumes gaussian errors.
  For counts, ask the LLM to switch to `family = poisson` or
  `family = nb`. For proportions, `family = betar`. The rest of the
  pipeline still works.

- **Missing data.** Rows with `NA` in `outcome_var` are dropped. Rows
  with `NA` in `unit_var` or `time_var` cause an error.
