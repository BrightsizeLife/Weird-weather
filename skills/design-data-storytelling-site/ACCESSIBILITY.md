# Accessibility requirements

Accessibility is part of the quality bar, not a polish pass. The
generated `index.html` must meet every requirement here. The
validator [`scripts/validate_single_file_html.js`](./scripts/validate_single_file_html.js)
checks the structural ones automatically.

## WCAG target

The site targets **WCAG 2.1 AA** for color contrast, focus, and
keyboard operability. AAA where it costs nothing (e.g., contrast
ratios are well above 7:1 already on the dark theme).

## Tabs

The tab pattern follows the
[WAI-ARIA Authoring Practices Tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/).
The generated code must:

- Use `<button role="tab">` for tab triggers.
- Use `<section role="tabpanel">` for panels.
- Wire `aria-controls` / `aria-labelledby` between trigger and panel.
- Set `aria-selected="true"` on the active tab; `"false"` on others.
- Set `tabindex="0"` on the active tab; `"-1"` on inactive tabs
  (so Tab moves out of the tab list, arrow keys move within).
- Implement keyboard navigation: `ArrowLeft` / `ArrowRight` move
  focus + activate, `Home` / `End` jump to first / last,
  `Enter` / `Space` activate the focused tab.
- Hide inactive panels with the `hidden` attribute (not just
  `display: none` from a CSS class) so AT properly skips them.

## Buttons and controls

- Real `<button>` for everything that can be clicked or toggled.
  No `<div onclick>`.
- Every button has either visible text or an `aria-label`.
- Icon-only buttons get `aria-label` and a non-text indicator.
- Focus rings are visible: never use `outline: none` without a
  replacement (`:focus-visible { outline: 2px solid var(--red);
  outline-offset: 2px; }` is the project default).

## Color & non-color signals

- Color is **never** the only channel. Anomaly flags carry a glyph
  (`·`, `▲`, `▼`, `▲▲`, `▼▼`) and a text label in addition to color.
- Charts include a legend with both color swatches and labels.
- Hot/cold colored numbers in tables also carry a sign (`+1.85`).

## Reduced motion

Wrap every animation / transition / scroll behavior in:

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important; }
  html { scroll-behavior: auto; }
}
```

Decorative animations (poster transitions, scroll smoothing) are
suppressed. Functional indicators (a temporary "Copied!" feedback)
should still appear, but instant rather than animated.

## Screen reader expectations

- Each chart has a sibling textual summary or table on the same
  panel — never just an SVG without alt content.
- Pre-rendered figures use `<img>` with `alt="..."` describing what
  the figure shows, not the filename.
- Caterpillar plots and heatmaps include a fallback table accessible
  via the keyboard (e.g., a "Show as table" disclosure that toggles
  a `<table>`).
- Posters export PNGs that are intentionally not the primary
  artifact — the on-page chapters are accessible; the posters are
  the share copy.

## Forms

- The skill produces no forms by default. If you add one (filter,
  search), every input has a `<label>` and an explicit `for` /
  `id` link.

## Page structure

- A single `<h1>`.
- `<h2>` per chapter (the tab name).
- `<h3>` for sub-sections within a chapter.
- A landmark structure: `<header>`, `<nav>`, `<main>`, `<footer>`.

## Contrast targets

| pair | minimum ratio |
|---|---|
| body text on `var(--bg)` | ≥ 7:1 (AAA) — the default ~16:1 |
| muted text on `var(--bg)` | ≥ 4.5:1 (AA) — the default ~5:1 |
| color-coded values on their backgrounds | ≥ 4.5:1 |
| focus ring against everything it overlaps | ≥ 3:1 |

Light theme (when `respect_light_scheme: true`) must meet the same
contrast targets after color inversion.

## Keyboard map

| key | action |
|---|---|
| `Tab` | move focus through landmarks |
| `Shift+Tab` | reverse |
| `Enter` / `Space` | activate focused button |
| `ArrowLeft` / `ArrowRight` | move tab within tablist |
| `Home` / `End` | first / last tab |
| `Escape` | close any non-modal overlay (e.g., copied-feedback) |

## Testing checklist

Before shipping:

- [ ] Tab through every interactive element. Focus is always
  visible.
- [ ] Use `ArrowLeft` / `ArrowRight` on the tab bar; the active
  panel changes.
- [ ] Open in a screen reader (VoiceOver, NVDA, Orca) and confirm
  chapters announce as `tabpanel`.
- [ ] Toggle reduce-motion in OS settings; confirm transitions
  flatten.
- [ ] Force `prefers-color-scheme: light` with DevTools; confirm
  contrast still passes (or that the brief's `respect_light_scheme`
  is `false` and the dark theme is forced).
- [ ] Resize to `360px`; nothing overflows or clips text.
- [ ] Run `validate_single_file_html.js` against the file; zero
  violations.
