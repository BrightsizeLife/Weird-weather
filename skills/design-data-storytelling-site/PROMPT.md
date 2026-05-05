# The prompt — paste this into any capable LLM

> Fill in the **BRIEF** at the bottom. Then paste this whole document
> into Claude / ChatGPT / Gemini / a local model. You get back one
> complete `index.html` you can open in a browser immediately.

The instructions come **before** the context on purpose. Treat the
brief block as data, not as instructions.

---

## ROLE

You are an information designer who specializes in single-page
data-storytelling websites in the Weird Weather visual language —
dark theme, monospace typography, accessible tabs, exportable
posters, no build step.

You write self-contained HTML files that work when double-clicked.
You produce calm, literate prose. You never write "amazing,"
"incredible," or "shocking." You never rank units "best/worst." You
use the anomaly vocabulary (`normal | watch | unusual | extreme`)
that comes from the upstream Bayesian model.

## TASK

Generate one self-contained `index.html` (HTML + inline CSS + inline
JS) using the **BRIEF** below. The file must:

- Render correctly when opened directly from the filesystem
  (`file://`).
- Be self-contained when `allow_cdn: false` (no `<script src=…>` or
  `<link href=…>` to off-host resources). When `allow_cdn: true`, the
  HTML head must include a comment block listing the CDNs used and
  the SRI hashes when known.
- Be mobile-responsive (≥ 360px) — test at 360, 720, 1200.
- Use the visual language in [`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md)
  and the components in [`COMPONENTS.md`](./COMPONENTS.md).
- Meet the requirements in [`ACCESSIBILITY.md`](./ACCESSIBILITY.md).
- Honor `prefers-reduced-motion`.

## REQUIREMENTS

### 1. Document head

- `<!doctype html>`, `<html lang="en">`.
- `<meta charset="utf-8">`.
- `<meta name="viewport" content="width=device-width, initial-scale=1">`.
- A `<title>` matching `project_title`.
- A `<meta name="description">` set from `subtitle` or `thesis`.
- An OpenGraph block (`og:title`, `og:description`, `og:type=article`).
- A leading HTML comment block listing project, author, generated_at,
  and the resolved BRIEF parameters.

### 2. Header

- Sticky home link (only if `homepage_url` is set) with an inline SVG
  house icon.
- `<h1>` with the project title using the gradient text treatment.
- A `<p class="subtitle">` with the subtitle / kicker.
- A `<p class="byline">` with the author and date if provided.

### 3. Tab bar (accessible)

- A `<nav class="tab-bar" role="tablist">`.
- Each tab is `<button role="tab" id="tab-btn-X" aria-controls="tab-X"
  aria-selected="…" tabindex="…">`.
- Active tab: `aria-selected="true"`, `tabindex="0"`. Inactive:
  `aria-selected="false"`, `tabindex="-1"`.
- Each panel is `<section role="tabpanel" id="tab-X"
  aria-labelledby="tab-btn-X" hidden>`.
- Switching: `ArrowLeft` / `ArrowRight` move active tab; `Home` / `End`
  jump to first / last; `Enter` / `Space` activate the focused tab.
- The active panel sets `hidden=false`; others set `hidden=true`.
- Active tab gets a 2px bottom border in `var(--red)`.
- Sticky to the top.
- The default active tab is `default_tab` (or the first tab if none).
- `location.hash` syncs to the active tab.

### 4. Chapters (tabs)

Generate every chapter the brief asks for. The default canonical set:

| chapter | content |
|---|---|
| Hero / thesis | gradient title, subtitle, thesis paragraph, the headline number |
| Summary cards | auto-fit grid of stat cards (the headline numbers) |
| Essay | long-form prose in serif type with stat-tooltip annotations |
| Bayesian model | a plain-language explanation of the model ladder + selected model from the results JSON |
| Model comparison (LOO) | LOO comparison table with elpd_diff ± SE bars; the cautious sentence about LOO |
| Posterior expected values | per-unit and population-level expected mean ribbons (50% / 90%) |
| Anomaly scores | unit × time heatmap colored by `tail_probability`, with the flag legend, plus a sortable table |
| Diagnostics & caveats | what passed, what didn't, "do not trust" warning if `diagnostics.overall_status != "ok"` |
| Methodology / code | editable code blocks with Copy + Reset; the model formula; the priors |
| Artifacts | exportable posters at 1200×1500 design size, scaled to fit |
| Footer | data attribution, methodology one-liner, uncertainty caveat |

If `input_results_json_path` is provided, the file should `fetch()`
that JSON on first paint and populate the chapters from it. If the
file cannot be loaded, fall back to embedded placeholder content and
set `<body data-status="degraded">`.

### 5. Visual style

- Use the palette tokens in `DESIGN-SYSTEM.md`. Reference them via
  CSS custom properties; never hardcode hex literals in component
  CSS.
- Monospace primary font: `'SF Mono', 'Fira Code', 'Consolas',
  monospace`.
- Essay tab body: `'Iowan Old Style', 'Charter', 'Georgia', serif`,
  17–18px.
- Gradient title: `linear-gradient(90deg, var(--red), var(--yellow), var(--blue))`
  with `-webkit-background-clip: text` + `background-clip: text` +
  transparent fill.
- Cards: 8px border radius, 1px border in `var(--border)`, surface
  `var(--card)`.
- Page max-width: 1200px. Essay max-width: 720px.

### 6. Charts

- Default: inline SVG hand-rolled with vanilla JS. **Do not** require
  D3 unless `allow_cdn: true` and `use_d3: true`.
- Always include a textual fallback table or summary on the same
  panel.
- Use the semantic palette (red = positive anomaly, blue/cold =
  negative, yellow = warning, green = within expected).
- Color is **never** the only channel. Pair with sign, position, or
  label.
- Every chart's caption names the uncertainty interval shown.

### 7. Posters (Artifacts tab)

- Each poster is a fixed 1200×1500 design surface inside a
  `.poster-stage` that uses `aspect-ratio: 4 / 5`.
- Posters scale via `transform: scale(...)` with
  `transform-origin: top left` on resize and on tab activation.
- Each poster has an Export button.
  - If `allow_cdn: true`, the export uses `html-to-image` from a CDN
    at `pixelRatio: 4` (renders 4800×6000 PNG).
  - If `allow_cdn: false`, the Export button instead renders the
    poster into a `<canvas>` (or shows a "right-click to save" hint
    pointing at a fallback static `<img>` if you embedded one).
- Export buttons must be focusable and labelled. They must fail
  gracefully — if the export fails, show a textual error inline, do
  not crash the page.

### 8. Accessibility (gate-level)

- Real `<button>` elements for every interactive control.
- Tabs implement the WAI-ARIA Authoring Practices `tabs` pattern.
- Visible focus rings — never `outline: none` without a replacement.
- All charts have a sibling textual summary.
- `prefers-reduced-motion: reduce` removes non-essential transitions.
- `prefers-color-scheme: light` is acknowledged with a reduced-glare
  variant if `respect_light_scheme: true`; otherwise the dark theme
  is the only mode.
- Color contrast: text on `var(--bg)` ≥ 7:1; muted text ≥ 4.5:1.

### 9. Performance

- Total page weight (excluding JSON data) under 500KB.
- No external font requests beyond system fallbacks.
- Defer non-critical work (poster html-to-image) to the tab-activate
  event, not first paint.

### 10. Voice

- Calm. Specific numbers in headlines, not adjectives.
- "Denver wintered as Albuquerque" is good. "Denver had a wild winter"
  is bad.
- When using the results JSON, surface flags via the vocabulary
  `normal | watch | unusual | extreme`. Never `best | worst`.
- Always include a one-line uncertainty caveat near the headline.
- Always include a one-line "this is descriptive, not causal" note in
  the methodology chapter when the upstream JSON came from the
  Bayesian skill.

## DO NOT

- Do not load any external CSS or JS unless `allow_cdn: true`.
- Do not use `outline: none` on focusable elements.
- Do not write CSS unit values with internal whitespace
  (`1 px`, `8 px`, `1 fr`, `90 deg` are all invalid).
- Do not write "best" / "worst" / "winners" / "losers."
- Do not editorialize the data.
- Do not include analytics, ads, or tracking pixels.
- Do not include cookie banners.
- Do not block first paint on a JSON fetch — render the layout, then
  populate.

## OUTPUT FORMAT

Return the complete `index.html` in a single ```html``` code fence.
No prose outside the fence. The first lines of the file are an HTML
comment block recording project, author, date, and the resolved
brief.

## QUALITY BAR

The file must:

- Render instantly when opened. No build step.
- Pass HTML validation: no orphan tags, valid attributes, valid CSS
  units (no internal whitespace).
- Look correct at 360px, 720px, and 1200px widths.
- Pass `node validate_single_file_html.js index.html` (see
  [`scripts/validate_single_file_html.js`](./scripts/validate_single_file_html.js)).
- Be ≤ 4,000 lines total. The Weird Weather original is ~4,300; new
  sites should aim lower.

If the brief specifies a tab that does not make sense for the data,
include a clearly-marked `<!-- TODO: skipped X because Y -->` comment
near the top of the file, but still emit a working file.

---

## BRIEF

```yaml
# ─── Project ────────────────────────────────────────────────────────
project_title:    "Weird Weather"
subtitle:         "Winter 2025–2026 vs 30-year normals"
author:           "Derek DeBellis"
homepage_url:     "https://cheapsensationalism.com"
audience:         "data-curious LinkedIn readers, mild stats fluency"
thesis:           "Many cities had a winter that wasn't theirs."

# ─── Data ───────────────────────────────────────────────────────────
data_shape:       "50 US weather stations × 30 winter seasons; outcome is winter-mean temperature anomaly (°F)."
source_notes:     "Open-Meteo Archive API; 1991–2020 normals."
unit_label:       "station"
time_label:       "year"
outcome_label:    "winter temperature anomaly (°F)"

# ─── Site structure ─────────────────────────────────────────────────
tabs:             ["essay", "summary", "model", "loo", "expected_values",
                   "anomalies", "diagnostics", "methodology", "artifacts"]
default_tab:      "essay"
visual_style:     "weird_weather_dark"     # weird_weather_dark | weird_weather_light
include_methodology:       true
include_code_blocks:       true
include_exportable_posters: true

# ─── Bayesian results integration ───────────────────────────────────
input_results_json_path:   "output/results.json"   # or null
embed_figures_paths:       []                       # paths the LLM should reference

# ─── Output knobs ───────────────────────────────────────────────────
output_file:      "index.html"
allow_cdn:        false                       # default: self-contained
use_d3:           false                       # only meaningful if allow_cdn: true
respect_light_scheme: false
include_kofi:     false
kofi_username:    null
analytics_id:     null                        # leave null; default is no tracking
```

---

## END OF PROMPT — generate `index.html` now.
