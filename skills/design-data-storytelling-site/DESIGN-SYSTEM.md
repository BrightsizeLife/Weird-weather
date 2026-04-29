# Design system

The visual rules that hold a Weird-Weather-family site together. If
you change one, change it deliberately.

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
| **yellow** | warm / warning / function names / annotation highlight |
| **green** | normal / strings / "within expected" |
| **blue** | cool / variables / "below trend" |
| **cold** | extreme negative anomaly |

### When to invert

Some domains read red as bad, green as good (clinical, financial loss,
churn). Swap by making `--red` your "negative" semantic and using
`--yellow` for the brand accent. Don't change the *number* of colors —
five is the limit before charts get noisy.

## Typography

- **Body, default**: `'SF Mono', 'Fira Code', 'Consolas', monospace`,
  15 px, line-height 1.6, color `var(--text)`.
- **Essay tab body only**: `'Iowan Old Style', 'Charter', 'Georgia',
  serif`, 17–18 px, line-height 1.7. Used for long-form prose where
  readability beats stylistic consistency.
- **H1 (gradient brand)**: monospace, 700, 2.2rem, with the 3-stop
  text gradient.
- **H2 (`.essay-section-head`)**: monospace, uppercase, 0.78rem,
  letter-spacing 0.18em, in `var(--muted)`. Section headers lean small
  and quiet.
- **Stat values**: monospace, 700, 1.8–2.2 rem, semantic color.
- **Code**: monospace, 0.82 rem, color `#c8c8c8` on `var(--card-deep)`.

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
| xs | 0.25 rem | inline gap |
| sm | 0.5 rem | tight stacks |
| md | 1 rem | default rhythm |
| lg | 1.5 rem | between cards |
| xl | 2.5 rem | between sections |
| 2xl | 4 rem | between major chapters |

Page max-width: 1200 px. Essay max-width: 720 px (long-form readability).

## Borders & radii

- 1 px border in `var(--border)` is the default.
- 8 px radius for cards.
- 6 px radius for code blocks.
- Pills get `border-radius: 999px`.

## Elevation

There's no elevation system — no shadows, no blurs. Hierarchy is
expressed by border + slightly different surface color (`var(--card)`
for elevated, `var(--card-deep)` for deeper).

## Iconography

Single-stroke SVG icons, 14–18 px, `fill: currentColor` so they inherit
the text color. The home icon in the header is the project's only
non-text mark.

## Charts

- D3 + plain SVG. No charting library.
- Margin convention: `padL = 60, padR = 30, padT = 50, padB = 40`.
- Gridlines: `stroke: var(--border)`, 1 px.
- Axis ticks: `fill: var(--muted)`, 12 px, monospace.
- Lines: 1.5–2 px, semantic palette.
- Dots: 4–6 px radius, 1.2 px black stroke for legibility on overlap.
- Always label both axes. Always note the unit.
- Use `aspect-ratio` not fixed pixel heights.

## Mobile rules

- Test at 360 px first, scale up.
- Tab bar gets `overflow-x: auto` + `flex-wrap: nowrap` below 400 px.
- Font sizes drop one notch in the essay (17 px → 15 px).
- Cards stack to single column below 700 px.
- Posters scale via `transform: scale(...)` with `transform-origin:
  top left`; the `.poster-stage` uses `aspect-ratio: 4 / 5` so layout
  is correct before the JS rescales.

## Tone of voice

The voice is a quiet character of the design.

- Never editorialize the data.
- Don't say "amazing," "incredible," "shocking."
- Don't pun.
- Use specific numbers in headlines, not vague claims.
- "Denver wintered as Albuquerque" is good. "Denver had a wild winter"
  is bad.
- Footnotes welcome. Long quotations from other people welcome.

## What to avoid

- **Frameworks** for a single-page site. React / Vue / Svelte are
  overkill and slow the page on first paint.
- **Web fonts** beyond the built-ins. Adds a request, defers rendering.
- **Carousels / sliders** that auto-play. Replace with a tab.
- **Modal dialogs** for data. Tabs handle the same job better.
- **Tooltips that block clicks.** Inline annotation is almost always
  better than hover text.
- **Animation that isn't telling you something.** Loading spinners
  yes, decorative wiggling no.
- **Cookie banners.** If you don't track, you don't need one. (And you
  shouldn't track.)

## Accessibility

- Real `<button>` for every interactive thing, never `<div onclick>`.
- Color is never the only signal. A red value should also have a `+`
  sign and a unit.
- Focus rings are visible. Don't `outline: none` without replacement.
- All charts have a fallback table or text summary on the same tab.
- Contrast ratio: light text on `var(--bg)` is ~16:1. The `var(--muted)`
  on `var(--bg)` is ~5:1, OK for secondary text.

## Performance

- Single HTML file. No build step.
- CDN deps load only on the tabs that need them, deferred. d3 +
  topojson + html-to-image is the upper bound; most projects need
  fewer.
- Data file: one JSON, fetched once on first paint, cached.
- Total page weight target: under 500 KB on first load (excluding
  data).
