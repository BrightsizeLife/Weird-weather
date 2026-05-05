# Fixtures

Small synthetic CSV fixtures for static and smoke evaluation of the
Bayesian R skill. They are deliberately tiny — Stan sampling on these
fixtures should complete in a few seconds (after one-time
compilation).

| file | shape | purpose |
|---|---|---|
| `minimal_panel.csv` | 5 units × 6 times = 30 rows; 1 numeric outcome; 1 factor with 2 levels | E01 — happy path |
| `sparse_units_panel.csv` | mixed: 3 units have 6 obs, 2 units have 1–2 obs | E03 — `min_obs_per_unit` should drop the sparse ones |
| `no_factors_panel.csv` | 5 units × 6 times, no factor columns | E02 — `factor_cols == []` path |
| `bad_time_panel.csv` | `time_col` contains the literal string `"unknown"` in some rows | E05 — coercion error path |

## Generating

These fixtures are checked in. To regenerate (or to grow a larger
synthetic panel):

```r
set.seed(42)
n_units <- 5
n_times <- 6
units   <- sprintf("U%02d", 1:n_units)
times   <- 1:n_times
df <- expand.grid(unit = units, time = times)
df$factor <- ifelse(as.integer(df$unit) %% 2 == 0, "A", "B")
unit_intercept <- setNames(rnorm(n_units, 0, 0.4), units)
df$outcome <- 1.0 +
  0.05 * df$time +
  ifelse(df$factor == "A", 0.2, -0.2) +
  unit_intercept[as.character(df$unit)] +
  rnorm(nrow(df), 0, 0.3)
write.csv(df, "minimal_panel.csv", row.names = FALSE)
```

## Why fixtures and not real data

Real panel data (the Weird Weather winter dataset) is upstream of
the skill, not part of it. The skill must work for any panel. The
fixtures exercise the script's plumbing: validation, factor handling,
sparsity guards, and JSON schema compliance. Statistical
interpretation of the fixtures is intentionally meaningless.
