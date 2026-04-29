# Worked example — store-level retail sales by promo flag

This is the full path from "I have a panel dataset" to "the script ran
and these are the diagnostics."

## The data

`data/sales.csv`, 12 stores × 104 weeks of weekly revenue, with a
`promo` column flagging weeks where a corporate promotion was running.

```
store,week,sales,promo
A,1,12340,no
A,2,14020,yes
A,3,11020,no
...
L,104,9870,yes
```

## The filled-in parameters

```yaml
data_path:        "data/sales.csv"
data_format:      "csv"
unit_var:         "store"
time_var:         "week"
outcome_var:      "sales"
factors:          ["promo"]
reference_levels: { promo: "no" }
evaluation_time:  104
spline_k:         12
spline_basis:     "cr"
output_dir:       "output"
seed:             42
```

## The question

> Did promo weeks actually move sales above each store's own trend, or
> would a baseline trend-only model do just as well?

## Running it

1. Copy `PROMPT.md`. Paste the parameters above into the YAML block.
2. Paste into your LLM. Save the response as `analysis.R`.
3. `Rscript analysis.R`.

## What you'd see in the console

```
══ Loaded ══
n_obs:    1248
n_units:  12 (A, B, C, …, L)
time:     1 → 104
factors:  promo (no, yes)

══ Model summary ══
Family: gaussian; Link: identity
Formula: sales ~ s(week, k = 12, bs = "cr") + promo
                + s(store, bs = "re") + s(week, store, bs = "re")

Parametric coefficients:
              Estimate  Std. Error  t value  Pr(>|t|)
(Intercept)   11084.21      612.45    18.10    <2e-16 ***
promoyes        842.11       58.29    14.45    <2e-16 ***

══ Block CV (leave-one-week-out) — RMSE in $ ══
baseline           1124.82
with_factors        982.41
with_interactions   967.33

══ AIC / BIC ══
              AIC       BIC      edf
baseline    21834.2   21912.8   18.4
with_facs   21642.1   21726.0   19.4
with_inter  21618.7   21806.4   38.1

══ σ per store — top 5 / bottom 5 ══
store  sigma  n
F     1483.2  104   ← noisiest
J     1342.7  104
…
B      612.8  104
A      594.1  104   ← most predictable

══ Z-scores at week 104 — top / bottom 5 ══
store  sales   fitted   resid    sigma   z   promo
F     14820   11402   3418   1483.2  +2.30  yes
…
```

## What you'd see in the PDFs

`output/diagnostics.pdf` — four panels:
- QQ plot (residuals vs. theoretical normal — should hug the line)
- residuals vs. linear predictor (should be a featureless cloud)
- histogram of residuals (should be bell-shaped)
- response vs. fitted (should be diagonal)

`output/dharma.pdf` — DHARMa quantile residual diagnostics:
- KS test on uniformity (p > .05 = good)
- Dispersion test (p > .05 = good)
- Outlier test (boundary count)

## The interpretive story

Reading the CV table: `with_factors` cuts RMSE by ~13% over baseline
($142/wk). `with_interactions` adds another 1.5% ($15/wk) but at the
cost of 19 extra effective df. The economical choice: include promo as
a fixed effect, skip the interaction.

The z-score table tells you which store-week combinations were
genuinely surprising — F at week 104 was 2.3σ above its own promo-aware
trend. Worth a phone call to F's manager.

## Adapting

Want to add a `holiday` flag? Add it to `factors`. Want to test whether
promo's effect varies by store? Already there as the third nested
model. Want bootstrap CIs on the per-unit σ? Ask the LLM to add a
`boot::boot` call after step 8.
