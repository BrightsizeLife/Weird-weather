# Evals

Eval cases for the data-storytelling site skill. Each case names
what the brief is, what the LLM produces, and what to check.

The scripts under [`scripts/`](./scripts/) are the cheap automated
core. Everything else is a manual or screenshot-driven check.

## Scripts (run from any cwd)

```sh
node skills/design-data-storytelling-site/scripts/check_css_units.js \
     skills/design-data-storytelling-site

node skills/design-data-storytelling-site/scripts/validate_single_file_html.js \
     path/to/index.html
```

`check_css_units.js` scans the skill's own markdown fenced code
blocks for invalid CSS unit spacing (e.g., `1 px`, `220 px`, `1 fr`,
`90 deg`). Exits non-zero on any finding. Catches drift in the
docs the LLM is supposed to imitate.

`validate_single_file_html.js` checks a generated `index.html`. It
verifies:

- exactly one `<html>` / `<head>` / `<body>`;
- `<meta charset>` and `<meta name="viewport">` present;
- no external CSS / JS unless `--allow-cdn` is passed;
- every `<button role="tab">` has an `aria-controls` that resolves;
- every `[role="tabpanel"]` has a matching `aria-labelledby`;
- buttons either have visible text or an `aria-label`;
- focus rings are not unconditionally disabled (`outline:none` only
  appears together with `:focus-visible` rules);
- the file contains a `prefers-reduced-motion` rule;
- the file contains no invalid CSS unit spacing.

## Eval ledger

| id | brief | static check | manual / runtime check | success criteria |
|---|---|---|---|---|
| S01 | minimal brief, `allow_cdn: false`, no JSON | run `validate_single_file_html.js` | open in a browser at 360 / 720 / 1200 px | renders; no console errors; tab keyboard navigation works |
| S02 | full brief with `input_results_json_path` set to the example fixture | check that the file `fetch()`es the JSON path; on failure sets `data-status="degraded"` | drop in the example fixture and reload | chapters populate from JSON; missing JSON → graceful degradation |
| S03 | brief asks for a chapter the skill doesn't know | the file includes a `<!-- TODO: tab "X" was requested but no template exists -->` comment | n/a | document still emits and renders other chapters |
| S04 | `allow_cdn: false`, `use_d3: true` (contradictory) | the file ignores D3 and falls back to inline SVG | no `<script src="cdn">` in output | `validate_single_file_html.js` passes without `--allow-cdn` |
| S05 | `diagnostics.overall_status == "warning"` in the JSON | top-of-tab callout in model / expected_values / anomalies / methodology | manual: open and read | callout text present, posterior numbers still rendered with caveat |
| S06 | `diagnostics.overall_status == "failed"` in the JSON | summary headline numbers suppressed, anomaly heatmap replaced with a "suppressed" notice | manual: open and read | no posterior headline; diagnostics chapter prominent |
| S07 | reduced motion test | `@media (prefers-reduced-motion: reduce)` rule present | DevTools: emulate reduce-motion | non-essential transitions are flattened |
| S08 | mobile responsiveness | n/a | DevTools at 360 px width | no horizontal scroll; tab bar scrolls horizontally if needed |
| S09 | poster export, `allow_cdn: false` | export button falls back to canvas or a textual hint, no `html-to-image` import | click export button | does not throw; emits a fallback path |
| S10 | poster export, `allow_cdn: true` | export uses html-to-image at `pixelRatio: 4` | click export | downloads a PNG; failure path shows a textual error inline |
| S11 | invalid CSS unit drift | `check_css_units.js` against the skill markdown | n/a | exits 0 |
| S12 | accessibility — keyboard tabs | n/a | keyboard test | `ArrowLeft` / `ArrowRight` / `Home` / `End` move active tab; `Enter` / `Space` activate |
| S13 | accessibility — screen reader | n/a | VoiceOver / NVDA | each tab announces as `tabpanel`; charts have textual fallback |
| S14 | "best/worst" language audit | grep the generated file for `best`, `worst`, `winner`, `loser`, `amazing`, `incredible`, `shocking` | n/a | zero matches outside of code/data |
| S15 | data shape mismatch (JSON has unexpected `flag` value) | the file warns in the diagnostics chapter, falls back to `normal` | runtime test | non-fatal; site still loads |

## Static eval rubric

Mark FAIL if the produced file:

- Loads any external CSS or JS when `allow_cdn: false`.
- Has any `<button>` without text or `aria-label`.
- Uses `outline: none` without a `:focus-visible` replacement.
- Uses any CSS unit literal with internal whitespace.
- Includes "best", "worst", "winners", "losers", "amazing",
  "incredible", or "shocking" outside quoted user content.
- Editorializes a result (e.g., "the worst winter in history").
- Adds a cookie banner.
- Embeds analytics when `analytics_id` is null.

## Reporting

A skill change should:

1. Run `check_css_units.js` against the skill markdown.
2. Generate a sample `index.html` from the `fixtures/minimal_brief.yaml`
   and run `validate_single_file_html.js` against it.
3. Sweep S14 (language audit) on the generated file.
4. Document which evals were skipped (e.g., screen reader test) and
   why.
