# Skill · Design a data-storytelling website like Weird Weather

> Drop this in front of any LLM. Describe what your data is and who it's
> for. Get back a complete, opinionated single-file HTML/CSS/JS scaffold
> in the same visual language as
> [weather.cheapsensationalism.com](https://weather.cheapsensationalism.com)
> — dark theme, monospace typography, tabbed structure, editable code
> blocks, exportable infographic posters, mobile-friendly.

---

## What the design language is for

A *data-storytelling* site is one that:

- Tells a story end-to-end, not just shows charts.
- Lives at one URL, on one page, with **tabs** as chapters.
- Treats the **essay** as the primary artifact, with charts as supporting
  evidence that you can drill into.
- Ships **shareable artifacts** (high-res PNG posters) so readers can
  carry the story to LinkedIn / Twitter / a deck.
- Shows the **methodology and code** plainly. No black boxes. People
  trust what they can read.
- Loads fast. No frameworks. One HTML file, vanilla JS, D3 only when
  charts demand it.

If that pattern fits your project, this skill produces a scaffold that
already does it. If your need is different (a marketing site, a
dashboard with auth, a data app with real interactivity), this skill is
the wrong tool.

---

## When to use this skill

Reach for it when **all** of these apply:

- You have **finished an analysis** and want to publish it on the web.
- The audience is technical-curious — analysts, journalists, data
  hobbyists, decision-makers who can read a chart but might not run R.
- You want to **own the URL** and the design — not pour the work into a
  Substack or Notion template.
- You want it **shareable** in the LinkedIn / Twitter sense, not the
  pay-walled-newsletter sense.
- You can host static HTML somewhere (Vercel, Netlify, GitHub Pages,
  Cloudflare Pages — all free, all 5-minute setups).

---

## What you get back

One file: `index.html`. Self-contained. Open it in a browser and it
works. Inside:

- **Header** with project title, gradient brand text, kicker subtitle,
  link back to your homepage.
- **Sticky tab bar** with the chapters of your story.
- **Tab panels** — one per chapter. The skill generates a sensible
  default set: Essay, Analysis, Code, Map / Time Series / Matrix
  (whichever fit your data), Summary, Artifacts.
- **Editable code blocks** in the Code tab — readers can copy your
  source.
- **Exportable posters** in the Artifacts tab — 1200×1500 designed,
  4800×6000 PNG via `html-to-image`.
- **Mobile responsive** — tested down to ~360px.
- **Dark theme** matching the Weird Weather palette (or a swap, if
  you'd rather).
- **Tip jar / call-to-action** card at the bottom (optional).
- **Footer** with attribution and source link.
- **No frameworks**. d3, topojson, html-to-image are the only CDN deps,
  loaded only on tabs that use them.

---

## How to use it

1. Open [`PROMPT.md`](./PROMPT.md). Copy the full prompt.
2. Fill in the `BRIEF` block with what your project is.
3. Paste into Claude / ChatGPT / Gemini.
4. The LLM returns a complete `index.html`. Save it, open it.
5. Drop your data into a `data/` folder, swap in your assets, ship.

For visual reference and the underlying system, see:

- [`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md) — colors, typography, spacing,
  the rules
- [`COMPONENTS.md`](./COMPONENTS.md) — copy-pasteable HTML/CSS for every
  block (tabs, stat cards, chart frames, callouts, posters)
- [`EXAMPLE.md`](./EXAMPLE.md) — a worked brief and the resulting site

---

## What "robust" means here

This skill is opinionated about a handful of things on purpose. Honoring
them produces sites that look like they belong to the same family;
breaking them produces sites that don't.

- **One file deploys everywhere.** No build step, no bundler, no
  package.json. If your asset pipeline has more steps than `git push`,
  you've taken a wrong turn.
- **Dark theme, monospace primary type.** It signals "made for reading,
  not for converting." It also degrades better on cheap monitors than a
  bright theme.
- **Tabs are chapters, not navigation.** A visitor reads them in order.
  The default order is Essay → Analysis / Code → Map / Charts →
  Artifacts.
- **Every chart is also a poster.** If a chart is interesting enough to
  put on a tab, it's interesting enough to be exportable. The Artifacts
  pattern encodes this.
- **Code is editable, not read-only.** A `<textarea>` with a Copy button
  beats a syntax-highlighted `<pre>` for "I want to fork this."
- **Mobile is not an afterthought.** Test at 360px before you ship.
  Most LinkedIn clicks come from phones.
- **No tracking, no ads, no paywall.** This is the cultural glue. Tip
  jars are fine.

---

## Color palette (the Weird Weather defaults)

| token | hex | use |
|---|---|---|
| `--bg` | `#000` | page background |
| `--card` | `#111` | card / surface |
| `--card-deep` | `#0d0d0d` | code blocks, math cards |
| `--border` | `#222` | dividers |
| `--text` | `#E0E0E0` | body |
| `--muted` | `#888` | secondary, captions |
| `--red` | `#E8594F` | hot / brand accent |
| `--yellow` | `#F5A623` | warm / file names |
| `--blue` | `#4A90D9` | cool / variables |
| `--green` | `#69f0ae` | normal / success / strings |

The palette is climate-coded but transposes: red = positive/hot/important,
blue = negative/cool/calm, yellow = warning/highlight, green =
normal/healthy. If your domain inverts that (e.g., red = bad, green =
good), swap in `PROMPT.md`.

---

## Typography

- **Primary:** `'SF Mono', 'Fira Code', 'Consolas', monospace` — the
  whole site, including body copy. This is the visual signature.
- **Titles:** the same monospace, but rendered with a 3-stop linear
  gradient (`red → yellow → blue`) and `-webkit-background-clip: text`.
- **Essay body:** Iowan Old Style or Charter — in just the Essay tab,
  for readability of long-form. Everything else stays mono.

---

## Adapting beyond weather

The pattern works for any analysis with a longitudinal or panel
structure. Swap the words and the data:

| Project | Essay tab | Map tab | Time Series | Artifacts |
|---|---|---|---|---|
| 50 cities × 30 winters | "Where winter went" | nearest-match map | per-city trend | "Where winter went" poster |
| 12 stores × 104 weeks | "What promo did" | store map | per-store sales | "Promo-lift scoreboard" |
| 200 hospitals × 24 months | "The admit pattern" | hospital map | per-hospital trend | "Outliers we should call" |

The skill prompt asks for your data shape and the question you're
answering, then generates the right tabs.

---

## License

Part of the [Weird Weather repo](https://github.com/BrightsizeLife/Weird-weather).
Inherits its license. Use it, fork it, change it, attribution is
appreciated but not required.
