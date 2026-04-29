# Worked example — Promo Lift, by store

A retail analyst has 12 stores × 104 weeks of sales, a `promo` flag,
and wants to publish "did promo work?" The brief and what the LLM
returns.

## The brief

```yaml
project_title:        "Promo Lift"
project_kicker:       "104 weeks · 12 stores · what the promo actually did"
homepage_url:         "https://acme-analytics.example"
author_name:          "Sam Patel"
author_url:           "https://www.linkedin.com/in/sampatel"

data_description:     "12 stores, 104 weeks of revenue, with a corporate
                       promo flag for ~30% of weeks."
unit_var:             "store"
time_var:             "week"
outcome_vars:         ["sales"]
factors:              ["promo"]

thesis:               "Promo weeks added an average $842/store/week, but
                       the lift varies 3× across stores."
audience:             "RGM team + finance · numerate but not statisticians"
tone:                 "punchy"

tabs:
  essay:        true
  analysis:     true
  code:         true
  map:          false
  summary:      true
  matrix:       false
  table:        true
  ts_overview:  true
  ts_city:      true
  artifacts:    true

include_kofi:         false
ga_or_plausible_id:   ""
```

## What the LLM should return (sketch)

A complete `index.html` with:

### Header
- Title "Promo Lift" with the gradient text treatment.
- Kicker "104 weeks · 12 stores · what the promo actually did."
- Home link to `acme-analytics.example`.

### Tabs
Essay → Analysis → Code → Summary → Data Table → Time Series:
Overview → Time Series: Store → Artifacts.

(The Map and Matrix tabs are skipped per the brief.)

### Essay tab
~700–1200 words. Three sections: "the promo, in one chart," "what the
data says about which stores benefit," "why the variation matters."
Stat-tip annotations on every numeric claim.

### Analysis tab
The recipe: data shape, normalization (none here — single outcome,
single scale), the model (`sales ~ s(week) + promo + s(store, bs="re")
+ s(week, store, bs="re")`), CV procedure, what the diagnostics show.

### Code tab
Five editable code blocks:
1. Loading the data
2. The mgcv formula
3. The block-CV loop
4. Per-store σ computation
5. Per-store z-scores at the latest week

Each with Copy + Reset buttons. Followed by a "If we did this by the
books — in R" link section pointing back to this skill repo.

### Summary tab
Six stat cards:
- Average promo lift (red, $842)
- Best-performing store (red, "Store F, +$1,810/wk")
- Worst-performing store (blue, "Store J, +$210/wk")
- Block CV RMSE improvement (yellow, "12.6%")
- Stores with >2σ promo lift (green, "3 of 12")
- Average baseline weekly sales (text)

### Data Table tab
12 rows × 7 columns: store, baseline mean, promo mean, lift $, lift %,
promo σ, latest-week z-score. Sortable, with hot/cold coloring on lift.

### Time Series: Overview
12 small-multiple charts, one per store. Each shows: actual sales
line, model fit (smooth), promo weeks marked.

### Time Series: Store
Single store deep-dive with metric toggles, ENSO-style overlay (here:
promo overlay), comparison-to-other-stores spaghetti option.

### Artifacts tab
Seven posters:
1. **The Promo Lift Map** — but since `map: false` in the brief, this
   becomes "The Promo Lift Bar Chart": one bar per store, sorted by
   lift, colored by significance.
2. **Lift × significance scatter** — x = lift $, y = z-score, dot size
   = baseline sales.
3. **Per-store time series, faceted** — small multiples poster.
4. **The Model** — formula card + 3-pane CV/AIC/BIC.
5. **Scoreboard** — compact 12-row table of every store.
6. **The Variance Story** — promo σ per store, ranked.
7. **Strange but True** — 9 callouts, the headline numbers.

Every poster: 1200×1500, exportable to 4800×6000 PNG.

### Footer
"Data: internal sales DB · Model: sales ~ s(week) + promo + (week |
store) · Sam Patel, 2026"

## Re-running with a different brief

Change `tabs: { map: true }` to `false`, the LLM will skip map code.
Change `factors` to add another column, the LLM threads it through the
model formula and the time-series tab.

The skill is the prompt. The output is one file. Iterating means
changing the brief and asking again.
