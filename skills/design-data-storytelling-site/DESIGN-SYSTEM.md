# Design system

The visual rules that hold a Weird-Weather-family site together. If
you change one, change it deliberately.

CSS unit values are written without internal whitespace everywhere
in this skill: `1px`, not `1 px`; `1fr`, not `1 fr`; `90deg`, not
`90 deg`. The validator in [`scripts/check_css_units.js`](./scripts/check_css_units.js)
enforces this for fenced code blocks.

## Color tokens

```css
:root {
  --bg:        #000;
  --card:      #111;
  --card-deep: #0d0d0d;
  --border:    #222;
  --text:      #E0E0E0;
  --muted:     #888;
  --red:       #E8594F;
  --yellow:    #F5A623;
  --blue:      #4A90D9;
  --green:     #69f0ae;
  --cold:      #1565c0;
}
```

### Semantic mapping

| color | meaning |
|---|---|
| **red** | hot / positive anomaly / brand accent / file names in code |
| **yellow** | warm / warning (`watch` flag) / function names / annotation highlight |
| **green** | normal / strings / "within expected" |
| **blue** | cool / variables / "below trend" |
| **cold** | extreme negative anomaly |

These map onto the Bayesian skill's flag vocabulary
(`normal | watch | unusual | extreme`):

| flag | color | optional non-color signal |
|---|---|---|
| `normal` | `--green` | no glyph |
| `watch` | `--yellow` | `·` |
| `unusual` | `--red` (or `--cold` if negative) | `▲` / `▼` |
| `extreme` | bright `--red` (or `--cold`) | `▲▲` / `▼▼` |

Color is never the only channel. Position vs. zero, sign glyphs,
and labels carry the same information for screen readers and
color-blind viewers.

### When to invert

Some domains read red as bad, green as good (clinical, financial loss,
churn). Swap by making `--red` your "negative" semantic and using
`--yellow` for the brand accent. Don't change the *number* of colors —
five is the limit before charts get noisy.

## Typography

- **Body, default**: `'SF Mono', 'Fira Code', 'Consolas', monospace`,
  `15px`, `line-height: 1.6`, color `var(--text)`.
- **Essay tab body only**: `'Iowan Old Style', 'Charter', 'Georgia',
  serif`, `17px`–`18px`, `line-height: 1.7`. Long-form prose where
  readability beats stylistic consistency.
- **H1 (gradient brand)**: monospace, `font-weight: 700`, `2.2rem`,
  with the 3-stop text gradient.
- **H2 (`.essay-section-head`)**: monospace, uppercase, `0.78rem`,
  `letter-spacing: 0.18em`, color `var(--muted)`. Section headers
  lean small and quiet.
- **Stat values**: monospace, `font-weight: 700`, `1.8rem`–`2.2rem`,
  semantic color.
- **Code**: monospace, `0.82rem`, color `#c8c8c8` on
  `var(--card-deep)`.

### The gradient

```css
background: linear-gradient(90deg, var(--red), var(--yellow), var(--blue));
-webkit-background-clip: text;
background-clip: text;
-webkit-text-fill-color: transparent;
```

Use sparingly: H1 in the header, poster titles, the occasional
emphasis. Overuse turns into a mood ring.

## Spacing

| token | size | use |
|---|---|---|
| xs | `0.25rem` | inline gap |
| sm | `0.5rem` | tight stacks |
| md | `1rem` | default rhythm |
| lg | `1.5rem` | between cards |
| xl | `2.5rem` | between sections |
| 2xl | `4rem` | between major chapters |

Page max-width: `1200px`. Essay max-width: `720px` (long-form
readability).

## Borders & radii

- `1px` border in `var(--border)` is the default.
- `8px` radius for cards.
- `6px` radius for code blocks.
- Pills get `border-radius: 999px`.

## Elevation

There is no elevation system — no shadows, no blurs. Hierarchy is
expressed by border + slightly different surface color (`var(--card)`
for elevated, `var(--card-deep)` for deeper).

## Iconography

Single-stroke SVG icons, `14px`–`18px`, `fill: currentColor` so they
inherit the text color. The home icon in the header is the project's
only non-text mark.

## Charts

- Plain SVG hand-rolled with vanilla JS by default. D3 is opt-in via
  `allow_cdn: true` and `use_d3: true`.
- Margin convention: `padL = 60, padR = 30, padT = 50, padB = 40`.
- Gridlines: `stroke: var(--border)`, `1px`.
- Axis ticks: `fill: var(--muted)`, `12px`, monospace.
- Lines: `1.5px`–`2px`, semantic palette.
- Dots: `4px`–`6px` radius, `1.2px` black stroke for legibility on
  overlap.
- Always label both axes. Always note the unit.
- Use `aspect-ratio` not fixed pixel heights.
- Every chart's caption names the uncertainty interval shown
  (50% credible, 90% credible, 90% posterior predictive, etc.).
- Every chart has a sibling textual summary or table for screen
  readers and copy-paste.

## Mobile rules

- Test at `360px` first, scale up.
- Tab bar gets `overflow-x: auto` + `flex-wrap: nowrap` below `400px`.
- Font sizes drop one notch in the essay (`17px` → `15px`).
- Cards stack to single column below `700px`.
- Posters scale via `transform: scale(...)` with
  `transform-origin: top left`. The `.poster-stage` uses
  `aspect-ratio: 4 / 5` so layout is correct before the JS rescales.

## Tone of voice

The voice is a quiet character of the design.

- Never editorialize the data.
- Don't say "amazing," "incredible," or "shocking."
- Don't pun.
- Use specific numbers in headlines, not vague claims.
- "Denver wintered as Albuquerque" is good. "Denver had a wild
  winter" is bad.
- "Three stations flagged `extreme` for winter 2020" is good.
  "The worst winter ever" is bad.
- Footnotes welcome. Long quotations from other people welcome.

## What to avoid

- **Frameworks** for a single-page site. React / Vue / Svelte are
  overkill and slow first paint.
- **Web fonts** beyond system fallbacks. Adds a request, defers
  rendering.
- **Carousels / sliders** that auto-play. Replace with a tab.
- **Modal dialogs** for data. Tabs handle the same job better.
- **Tooltips that block clicks.** Inline annotation is almost always
  better than hover text.
- **Animation that isn't telling you something.** Loading spinners
  yes, decorative wiggling no.
- **Cookie banners.** If you don't track, you don't need one.

## Accessibility

See [`ACCESSIBILITY.md`](./ACCESSIBILITY.md) for the full checklist.
Headlines:

- Real `<button>` for every interactive thing.
- Color is never the only signal.
- Focus rings are visible. Don't `outline: none` without a
  replacement.
- All charts have a fallback table or text summary on the same panel.
- Contrast: light text on `var(--bg)` is ~16:1; `var(--muted)` on
  `var(--bg)` is ~5:1, OK for secondary text.

## Performance

- Single HTML file. No build step.
- CDN deps load only when `allow_cdn: true`. The default is fully
  inline — d3 / topojson / html-to-image are not on the wire.
- Data file: one JSON, fetched once on first paint, cached.
- Total page weight target: under `500KB` on first load (excluding
  data).
