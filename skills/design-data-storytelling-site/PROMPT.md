# The prompt — paste this into any LLM

> Fill in the **BRIEF** section. Then paste the whole thing into Claude /
> ChatGPT / Gemini. You will get back one complete `index.html` you can
> open immediately.

---

## ROLE

You are an information designer who specializes in single-page
data-storytelling websites in the Weird Weather visual language —
dark theme, monospace typography, tabbed structure, editable code
blocks, exportable infographic posters, no build step. You write
self-contained HTML files that work when double-clicked.

## TASK

Generate a single complete `index.html` (HTML + inline CSS + inline JS)
based on the brief below. The file must:

- Be self-contained (no external CSS / JS files; CDN deps are OK).
- Render correctly when opened directly from the filesystem.
- Be mobile-responsive (≥ 360 px).
- Use the visual language described in **DESIGN SYSTEM** below.
- Provide every component listed in **REQUIRED COMPONENTS** below.

## BRIEF

```yaml
project_title:        # e.g. "Weird Weather"
project_kicker:       # one-line tagline for the header subtitle
                      # e.g. "Winter 2025–2026 vs 30-year normals"
homepage_url:         # what the home-link in the header points to
                      # e.g. "https://cheapsensationalism.com"
author_name:          # for byline + footer
author_url:           # author's homepage / LinkedIn / etc.

# What the data is
data_description:     # 1–2 sentences about the dataset
                      # e.g. "50 US cities × 30 winter seasons. Three metrics
                      #       per season: avg high temp, total snow, total precip."
unit_var:             # what each row represents (e.g. "city", "store", "school")
time_var:             # what advances (e.g. "year", "week")
outcome_vars:         # list of numeric metrics
                      # e.g. ["high_temp_F", "snowfall_in", "precip_in"]
factors:              # list of categorical context vars (optional)
                      # e.g. ["enso_phase"]

# What story you want to tell
thesis:               # one sentence — what you concluded
                      # e.g. "Many cities had a winter that wasn't theirs."
audience:             # who's reading this and what they care about
                      # e.g. "data-curious LinkedIn folks, mild stats fluency"
tone:                 # "formal" | "playful" | "essayistic" | "punchy"

# Tabs to include (skip any you don't need)
tabs:
  essay:        true    # long-form prose with stat-tooltip annotations
  analysis:     true    # methodology walkthrough with recipe-step cards
  code:         true    # editable code blocks with Copy/Reset buttons
  map:          false   # set true if data is geographic
  summary:      true    # callout-card grid of headline numbers
  matrix:       false   # set true if you want a unit-by-unit distance heatmap
  table:        true    # sortable data table
  ts_overview:  true    # small-multiples per-unit time series
  ts_city:      true    # single-unit deep-dive view
  artifacts:    true    # exportable infographic posters

# Optional extras
include_kofi:         false   # set true to include a tip-jar card at the bottom
kofi_username:                # required if include_kofi is true
ga_or_plausible_id:           # blank for no analytics; that's the recommended default

# Color palette overrides (defaults match Weird Weather)
palette:
  bg:        "#000"
  card:      "#111"
  card_deep: "#0d0d0d"
  border:    "#222"
  text:      "#E0E0E0"
  muted:     "#888"
  red:       "#E8594F"
  yellow:    "#F5A623"
  blue:      "#4A90D9"
  green:     "#69f0ae"
```

## DESIGN SYSTEM

### Colors

Use the `palette` from the brief as CSS variables on `:root`. Reference
them everywhere by `var(--red)` etc. Don't hardcode hex values in
component code.

The semantic mapping:
- red = positive / hot / brand accent / file names
- blue = negative / cool / variables
- yellow = warning / highlight / functions
- green = normal / strings / success

### Typography

- **Body, everywhere except the essay**: `'SF Mono', 'Fira Code',
  'Consolas', monospace`. This is non-negotiable — it's the visual
  signature.
- **Headers**: same monospace, but with a 3-stop linear gradient
  applied to the text:
  ```css
  background: linear-gradient(90deg, var(--red), var(--yellow), var(--blue));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  ```
- **Essay tab body only**: a serif (`'Iowan Old Style', 'Charter',
  'Georgia', serif`) at 17–18 px for readability.
- **Letter-spacing** on uppercase labels: 0.08–0.18em.

### Spacing & layout

- Page max-width: ~1200 px.
- Tab panels: 1.5 rem padding.
- Cards: 8 px border radius, 1 px border in `var(--border)`,
  background in `var(--card)`.

### Header

```html
<header>
  <a class="home-link" href="${homepage_url}" title="${homepage_url}">
    <svg viewBox="0 0 24 24" aria-hidden="true">…house icon…</svg>
    <span>${homepage_label}</span>
  </a>
  <h1>${project_title}</h1>
  <div class="subtitle">${project_kicker}</div>
</header>
```

The `h1` uses the gradient text treatment.

### Tab bar

Sticky at the top. Tabs are buttons with `data-tab` attributes.
Active tab gets a 2 px bottom border in `var(--red)`.

```html
<nav class="tab-bar">
  <button class="tab-btn active" data-tab="essay">Essay</button>
  <!-- … -->
</nav>
```

### Tab switching

```js
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelector(`.tab-btn[data-tab="${name}"]`)?.classList.add('active');
  document.getElementById('tab-' + name)?.classList.add('active');
  history.replaceState(null, '', '#' + name);
}
document.querySelectorAll('.tab-btn').forEach(b =>
  b.addEventListener('click', () => switchTab(b.dataset.tab)));
if (location.hash) switchTab(location.hash.slice(1));
```

Tab switching also rescales any infographic posters in the Artifacts
tab (see REQUIRED COMPONENTS).

## REQUIRED COMPONENTS

Generate every one of these. Each gets its own clearly-commented section
in the file.

### 1. Stat card grid (Summary tab)

Auto-fit columns, min 220 px. Each card: small label (uppercase muted),
big value with semantic color, small detail line.

### 2. Editable code block (Code tab)

`<textarea class="code-editable">` inside a `.code-card` with a header
showing the file name and a Copy + Reset button row. Original code is
captured on load; Reset restores it.

```js
document.querySelectorAll('.code-card').forEach(card => {
  const ta = card.querySelector('textarea.code-editable');
  const original = ta.value;
  function autosize() {
    ta.style.height = 'auto';
    ta.style.height = (ta.scrollHeight + 4) + 'px';
  }
  ta.addEventListener('input', autosize);
  requestAnimationFrame(autosize);
  card.querySelector('[data-copy]')?.addEventListener('click', async () => {
    await navigator.clipboard.writeText(ta.value);
  });
  card.querySelector('[data-reset]')?.addEventListener('click', () => {
    ta.value = original; autosize();
  });
});
```

### 3. Math card (math formula displays)

Background `linear-gradient(135deg, var(--card-deep), var(--bg))`,
1 px border, label / formula / note layout. Formula font is a serif
math face (`'Cambria Math', 'STIX Two Math', Times, serif`) at 1.45 rem.

### 4. Recipe-step card (Analysis tab)

Numbered steps with a circular badge, an explanation, optional inline
data spans:

```html
<div class="recipe-step">
  <span class="step-num">1</span>
  <span class="step-text">…copy…</span>
</div>
```

### 5. Callout box

Left border in `var(--yellow)`, dark card background, used for sidebars
and "by the way" framing.

### 6. Sortable data table (Data Table tab)

Header click toggles sort. Tabular numerals. Hot/cold values colored
red/blue.

### 7. Time-series chart frame

Each chart is a D3 SVG inside a labeled card. Use a consistent
margin convention: `padL = 60, padR = 30, padT = 50, padB = 40`.
Grid lines in `var(--border)`. Lines / dots in semantic palette.

### 8. Infographic poster (Artifacts tab)

Each poster is a fixed 1200×1500 design surface inside a
`.poster-stage` that scales-to-fit using `transform: scale(...)`.
Each poster has an Export button that uses `html-to-image` (CDN) to
render the poster at `pixelRatio: 4` (= 4800×6000 PNG) and trigger a
download.

```js
import 'https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js';
btn.addEventListener('click', async () => {
  const poster = document.getElementById(btn.dataset.target);
  const prevTransform = poster.style.transform;
  poster.style.transform = 'scale(1)';
  try {
    const url = await htmlToImage.toPng(poster, {
      pixelRatio: 4, width: 1200, height: 1500,
      backgroundColor: '#000', cacheBust: true,
    });
    const a = document.createElement('a');
    a.href = url; a.download = btn.dataset.name + '.png';
    document.body.appendChild(a); a.click(); a.remove();
  } finally { poster.style.transform = prevTransform; }
});
```

### 9. Footer

Source attribution, methodology one-liner, optional model formula.

### 10. (Optional) Ko-fi card + floating mug button

If `include_kofi` is true, add a tip-jar card near the bottom and a
floating coffee-mug FAB.

## ACCESSIBILITY

- All interactive elements have `aria-*` attributes where helpful.
- Color is never the *only* signal — important values also have an
  arrow / sign / label.
- Tab buttons are real `<button>` elements (keyboard-reachable).
- Focus rings are visible.

## QUALITY BAR

The generated file should:
- Render instantly when opened. No build step.
- Pass HTML validation (no orphan tags, valid attributes).
- Look correct on a 360-px mobile viewport (test in DevTools).
- Survive a `view-source` review — clean indentation, semantic
  structure, comments at major section boundaries.
- Be ≤ 4,000 lines in total (the Weird Weather original is ~4,300, but
  much of that is data-specific content; new sites should target less).

## OUTPUT FORMAT

Return the complete file in a single ```html``` code fence. No commentary
outside the fence. The file's first lines should be a comment block
naming the project, the date, and the parameters used.

If you cannot meet a requirement (e.g., the brief specifies tabs that
don't make sense for the data), include a clearly-marked TODO comment
at the top with what you skipped and why, but still emit a working file.

---

## END OF PROMPT — generate the file now.
