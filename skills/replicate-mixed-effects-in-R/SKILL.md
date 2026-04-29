# Skill · Replicate the Weird Weather analysis in R, on your own data

> Drop this in front of any LLM (Claude, ChatGPT, Gemini, Llama, …) along
> with your parameters. You get back a single runnable R script that does:
> mixed-effects GAM with REML, nested-model comparison via block LOOCV,
> proper diagnostics, per-group σ, per-group z-scores, and saved PDFs.

The original analysis (50 US cities × 30 winters) lives at
[weather.cheapsensationalism.com](https://weather.cheapsensationalism.com).
The reference implementation is
[`if_we_did_this_in_R.R`](https://github.com/BrightsizeLife/Weird-weather/blob/main/if_we_did_this_in_R.R).
This skill abstracts that pattern so you can apply it to any panel
dataset: stores × weeks of sales, sensors × hours of readings, schools ×
years of test scores, hospitals × months of admissions.

---

## When to use this skill

Reach for this when **all** of these are true:

- You have a **panel** (a.k.a. longitudinal) dataset — repeated
  measurements of the same units over time.
- You want to know whether a unit's recent value is **unusual relative to
  its own history**, accounting for a global trend and unit-level
  baselines.
- You suspect a **categorical context** (regime, season, treatment, ENSO
  phase, promo flag) might be moving the dial, and want to test whether
  including it actually helps prediction.
- You want **honest** diagnostics — not just R² — and a defensible answer
  to "did you cross-validate the model choice?"

Don't use this skill if your data isn't longitudinal, if you have fewer
than ~5 observations per unit, or if you need a causal answer (this is
descriptive, not causal).

---

## What you get back

One file, `analysis.R`, that you run with `Rscript analysis.R`. It:

1. Loads your data (CSV or JSON, auto-detected).
2. Fits a mixed-effects GAM:
   `outcome ~ s(time) + factors + s(unit, bs="re") + s(time, unit, bs="re")`
   with REML so the smoothing parameter is data-driven.
3. Runs **block leave-one-time-out CV** comparing three nested models:
   baseline → +factors → +factor×unit interaction. Reports RMSE per
   model.
4. Reports AIC, BIC, effective df.
5. Runs full diagnostics — `gam.check`, DHARMa simulation-based
   residuals, `gam.vcomp` for variance components, `concurvity` for
   smooth-term collinearity.
6. Computes per-unit σ and per-unit z-scores for the most recent time
   period.
7. Writes `output/results.json` plus `output/diagnostics.pdf` and
   `output/dharma.pdf`.

The script is self-contained. No package outside CRAN. Comment-heavy so
you can read what each step does.

---

## How to use it

1. Open [`PROMPT.md`](./PROMPT.md). Copy the entire prompt.
2. Fill in the parameters block at the top (see
   [`PARAMETERS.md`](./PARAMETERS.md) for the full schema with defaults).
3. Paste the filled-in prompt into your LLM of choice.
4. The LLM returns a complete `analysis.R` you can run immediately.
5. (Optional) iterate: ask it to add bootstrap CIs, switch to `gamlss`
   for genuinely heteroscedastic errors, or wire the output into a
   Quarto report.

A worked example with sample data is in [`EXAMPLE.md`](./EXAMPLE.md).

---

## What "robust" means here

This skill is opinionated about a few things on purpose:

- **REML over GCV.** For mixed-effects models with random effects, REML
  has better small-sample properties.
- **Block CV (leave-one-time-out) over random k-fold.** For time-indexed
  data, random folds leak information across the time boundary. Blocked
  folds are the honest test.
- **Three nested models, always.** The CV table tells you whether your
  factor of interest pulls its weight. If `with_factor` doesn't beat
  `baseline` in held-out RMSE, the factor isn't earning its degrees of
  freedom.
- **Per-unit σ.** One global σ is a lie when units have different
  intrinsic noise levels. The skill reports both.
- **Diagnostics, not just summaries.** A model that summary-prints
  beautifully can have catastrophic residual structure. Always look at
  `gam.check` and DHARMa.

---

## Statistical notes (read once, save your future self)

- **k in `s(time, k = …)`**. mgcv's `k` is the *upper bound* on basis
  dimension; REML chooses the effective df below that. Set `k` generous
  (e.g., 10–15 for 30 time points) and let REML decide.
- **Random slopes are correlated with random intercepts by default.**
  mgcv estimates the variance components separately. If you want the
  correlation, fit the same model with `lme4::lmer` for comparison.
- **Heteroscedasticity.** mgcv assumes constant variance. If `gam.check`
  shows fan-shaped residuals, refit with `family = gaulss(...)` or
  switch to `gamlss::gamlss` with `sigma.formula = ~ unit`.
- **Concurvity ≠ multicollinearity.** It measures whether your smooth
  terms can stand in for one another. > 0.8 is concerning; > 0.95 is a
  warning.
- **DHARMa.** Simulation-based residuals — the "correct" way to assess
  GAM/GLMM residuals. KS test on the histogram should be non-significant.

---

## Adapting this beyond weather

The original was 50 cities × 30 winters of temperature. The skill works
for any panel. Some examples worth trying:

| Domain | unit | time | outcome | factor |
|---|---|---|---|---|
| Retail | store | week | sales | promo (T/F) |
| Public health | hospital | month | admissions | season |
| Education | school | year | test score | curriculum cohort |
| Energy | meter | hour | demand | day-of-week |
| Sports | team | season | wins | rule change era |

The skill prompt is parameterized exactly so this kind of swap is a
two-minute exercise.

---

## License

The skill is part of the [Weird Weather repo](https://github.com/BrightsizeLife/Weird-weather)
and inherits its license. Use it, fork it, change it, attribute if you'd like.
