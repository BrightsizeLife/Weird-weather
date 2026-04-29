# The prompt — paste this into any LLM

> Fill in the **PARAMETERS** block. Leave defaults where you don't have a
> preference. Then paste the whole thing into Claude / ChatGPT / Gemini /
> any capable model. You will get back a single complete `analysis.R`.

---

## ROLE

You are an expert applied statistician fluent in R, mgcv, and reproducible
analysis. You write clear, comment-heavy R code that runs on the first
try. You favor REML over GCV for mixed-effects, block CV over random
k-fold for time-indexed data, and you always include real diagnostics.

## TASK

Generate a single self-contained R script (`analysis.R`) that performs a
mixed-effects GAM analysis with cross-validated model comparison and full
diagnostics, using the parameters below. The script must run with
`Rscript analysis.R`.

## PARAMETERS

```yaml
# ─── Required ───────────────────────────────────────────────────────────

data_path:        # e.g. "data/sales.csv" or "data/panel.json"
data_format:      # "csv" or "json"; if "json", expects an array of {unit, time, outcome, ...} objects

unit_var:         # column name for the panel unit (e.g., "store", "city", "school")
time_var:         # column name for time (e.g., "year", "week_start", "month")
outcome_var:      # column name for the response (e.g., "sales", "high_temp", "admissions")

# ─── Optional but recommended ──────────────────────────────────────────

factors:          # list of categorical predictors to test in the model;
                  # each will be a fixed effect, plus a model variant with
                  # factor:unit interactions.
                  # e.g., ["enso_phase", "promo_flag"]

reference_levels: # mapping factor -> reference level (defaults to first)
                  # e.g., { enso_phase: "neutral", promo_flag: "no" }

evaluation_time:  # the time value for "this period's z-scores"
                  # (defaults to max(time) in the data)

# ─── Sensible defaults you usually don't change ────────────────────────

spline_k: 10            # upper bound on smooth basis dimension; REML picks below
spline_basis: "cr"      # cubic regression spline; "tp" thin-plate also fine
output_dir: "output"    # writes results.json + diagnostics PDFs here
seed: 42
```

## REQUIREMENTS

The generated script MUST:

1. **Load** the data from `data_path` (CSV or JSON). If JSON, flatten to
   a long data frame with one row per unit-time observation. Coerce
   `unit_var` to factor, ensure `time_var` is numeric, drop rows where
   `outcome_var` is `NA`.

2. **Validate** the inputs at the top: print sample size, number of units,
   time range, and the levels of each factor. Stop with an informative
   error if any required column is missing.

3. **Fit the full model** with mgcv:
   ```
   outcome ~ s(time, k = spline_k, bs = spline_basis)
           + (each factor as a fixed effect)
           + s(unit, bs = "re")
           + s(time, unit, bs = "re")
   ```
   using `method = "REML"`.

4. **Print a model summary**, variance components (`gam.vcomp`), and
   concurvity (`concurvity(m, full = FALSE)`).

5. **Save standard diagnostic plots** to `output/diagnostics.pdf` via
   `gam.check`, and **DHARMa simulation-based residuals** to
   `output/dharma.pdf`.

6. **Run block leave-one-time-out CV** comparing three nested models:
   - **baseline**: `s(time) + s(unit, bs="re") + s(time, unit, bs="re")`
   - **with_factors**: baseline + each factor as a fixed effect
   - **with_interactions**: with_factors + each `factor:unit` term
     (skip this if there are no factors specified)

   Report a CV-RMSE table (one row per model). For each held-out time
   period, refit the model on the remaining periods and predict the
   held-out points.

7. **Compute AIC and BIC** for the in-sample fits of all three models.
   Print a comparison table.

8. **Compute per-unit σ** as the standard deviation of residuals from
   the full model, restricted to units with ≥ 5 observations.

9. **Compute per-unit z-scores for `evaluation_time`** as
   `(actual − fitted) / sigma_unit`. Sort and print the top 5 most
   positive and top 5 most negative.

10. **Write `output/results.json`** with: model formula, family, method,
    cv_rmse table, AIC/BIC table, factor coefficient estimates with SEs,
    per-unit σ, evaluation-time z-scores, and a `metadata` block with
    sample size, number of units, time range, and the parameters used.

11. **Be defensive**: handle the case where a factor has only one level
    in some CV fold (skip the term, log a warning), where a unit has too
    few observations (use pooled σ), and where mgcv fails to converge
    (catch, print, and return non-zero exit code).

12. **Comment generously**. Each section starts with a `# ── Section ──`
    banner. Comments explain *why*, not just *what*.

## DEPENDENCIES

Use only CRAN packages: `mgcv`, `dplyr`, `tidyr`, `jsonlite`, `DHARMa`,
`broom`. The script should `install.packages` any missing dependency
before loading (with a check, not an unconditional install).

## OUTPUT FORMAT

Return the complete script in a single ```r``` code fence. No
explanation outside the code fence — comments inside the script are the
explanation. The first line of the script must be the file header,
including the parameters that were filled in (so the script is its own
record of what produced it).

## QUALITY BAR

The script should:
- Run end-to-end on a clean R install with `Rscript analysis.R`.
- Produce identical results across runs (the `seed` is set).
- Fail fast with clear errors when inputs are wrong.
- Have no warnings beyond mgcv's normal smoothing-parameter messages.
- Be ≤ 300 lines, including comments.

If you cannot meet a requirement (e.g., a factor has too few levels for
interaction testing), print a clear warning and continue with the
applicable subset, rather than crashing.

---

## END OF PROMPT — generate the script now.
