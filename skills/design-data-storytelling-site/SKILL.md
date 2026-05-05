---
name: design-data-storytelling-site
description: Generates a self-contained single-page HTML/CSS/JS data-storytelling site in the Weird Weather visual language, with narrative chapters, accessible tabs, methodology/code sections, responsive layout, exportable share graphics, and support for Bayesian model output JSON. Use when the user wants a publishable narrative data story, not a generic dashboard, authenticated app, or marketing page.
---

# Skill · Design a data-storytelling site, Weird Weather visual language

A reusable, agent-agnostic prompt kit for turning a finished analysis
(ideally the JSON output of the
[`bayesian-panel-modeling-in-r`](../bayesian-panel-modeling-in-r/) skill)
into a single, self-contained `index.html` you can host on any static
host.

The aesthetic is the Weird Weather one: dark, monospace, literate,
serious about uncertainty. The skill is opinionated on purpose. If
you fight the opinions, you should pick a different skill.

---

## When to use

All of these should be true:

- You have **finished an analysis** with a clear thesis and ready
  data (ideally results JSON from the Bayesian R skill).
- You want a **publishable narrative**, not a dashboard, marketing
  page, or auth-gated app.
- The audience is technical-curious — analysts, journalists,
  decision-makers who can read a chart but might not run R.
- You will host **static HTML** somewhere (Vercel / Netlify / GitHub
  Pages / Cloudflare Pages).

## When **not** to use

- You need authentication, multi-user state, or write-back. This is
  a static document.
- You need real-time interactivity beyond reading-and-filtering.
- You want a generic admin dashboard.
- You want a marketing page with conversion CTAs. The voice and
  visual language are wrong for that.

---

## Required inputs

Filled into the YAML block at the top of [`PROMPT.md`](./PROMPT.md):

- A **brief** (project title, audience, thesis, tabs, etc.) — full
  schema in [`BRIEF_SCHEMA.md`](./BRIEF_SCHEMA.md).
- Optionally, a path to a **results JSON** produced by the Bayesian
  R skill — schema in [`RESULTS_INPUT_SCHEMA.md`](./RESULTS_INPUT_SCHEMA.md).
- Optional pre-rendered figure paths to embed.

## Generated outputs

- **One file** (`index.html` by default) — fully self-contained when
  `allow_cdn: false`.
- Inline CSS, inline JS, no build step.
- A consistent set of chapters (essay, summary cards, model section,
  posterior expected values, anomalies, methodology, artifacts).

---

## Workflow

1. Fill the brief.
2. Optionally point `input_results_json_path` at the Bayesian skill's
   `output/results.json`.
3. Paste [`PROMPT.md`](./PROMPT.md) (with brief filled in) into your
   LLM.
4. Save the response as `index.html`.
5. Run validators in [`scripts/`](./scripts/) (`check_css_units.js`,
   `validate_single_file_html.js`).
6. Open in a browser. Test responsive width down to 360px.

Detailed docs:

- [`BRIEF_SCHEMA.md`](./BRIEF_SCHEMA.md) — input brief contract.
- [`RESULTS_INPUT_SCHEMA.md`](./RESULTS_INPUT_SCHEMA.md) — how the
  results JSON maps onto chapters.
- [`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md) — colors, type, spacing.
- [`COMPONENTS.md`](./COMPONENTS.md) — copy-pasteable HTML/CSS.
- [`ACCESSIBILITY.md`](./ACCESSIBILITY.md) — accessibility
  requirements that gate "done."
- [`EXAMPLE.md`](./EXAMPLE.md) — worked brief.
- [`EVALS.md`](./EVALS.md) — eval plan and validation entry points.

---

## Failure modes (the generated file must handle them)

| failure | response |
|---|---|
| brief asks for tabs unsupported by data | emit the file with a clearly-marked `TODO` comment naming what was skipped and why; never silently drop |
| `input_results_json_path` is provided but missing required keys | emit the file with placeholder content for affected chapters and a console.warn at runtime; `data-status="degraded"` on `<body>` |
| `allow_cdn: false` but a chapter requires D3 | downgrade to inline SVG / Canvas; do not emit `<script src="cdn">` |
| browser does not support clipboard API | Copy buttons fall back to manual selection, no error |
| `prefers-reduced-motion: reduce` | suppress non-essential transitions |
| user opens the file from `file://` | works without a server (no fetch from the network unless `allow_cdn`) |
| poster export fails (e.g., html-to-image not loaded) | show a textual fallback, do not crash the page |

---

## Validation entry points

```sh
node skills/design-data-storytelling-site/scripts/check_css_units.js skills/design-data-storytelling-site
node skills/design-data-storytelling-site/scripts/validate_single_file_html.js path/to/index.html
```

`check_css_units.js` scans the skill's own markdown for invalid CSS
unit spacing (e.g., `1 px`, `220 px`, `1 fr`, `90 deg`).

`validate_single_file_html.js` checks a generated `index.html` for
the structural and accessibility properties listed in
[`EVALS.md`](./EVALS.md).

---

## Quality bar (operative)

- One file deploys everywhere. No build step, no bundler.
- Self-contained by default. CDNs only when explicitly enabled.
- Mobile-responsive down to 360px width.
- Accessible tabs (real `<button>`, `aria-selected`, keyboard
  navigation, visible focus).
- Color is never the only channel. `prefers-reduced-motion`
  respected. All charts have a textual fallback.
- Every CSS unit is **valid** — `1px` not `1 px`, `1fr` not `1 fr`,
  `90deg` not `90 deg`.
- Voice is calm and specific. Never "amazing/incredible/shocking."
  Never "best/worst." Use the anomaly flag vocabulary (`watch`,
  `unusual`, `extreme`).

---

## Pairing with the Bayesian R skill

Both skills together are designed as a pipeline:

1. `bayesian-panel-modeling-in-r` → `output/results.json`
2. `design-data-storytelling-site` reads that JSON and renders the
   chapters described in
   [`RESULTS_INPUT_SCHEMA.md`](./RESULTS_INPUT_SCHEMA.md).

The site skill works without the JSON — the brief alone is enough —
but it produces stronger output when it has structured posterior
information to render.

---

## License

Part of [Weird Weather](https://github.com/BrightsizeLife/Weird-weather).
Use, fork, change. Attribution welcome but not required.
