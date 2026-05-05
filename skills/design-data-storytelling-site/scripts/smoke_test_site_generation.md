# Smoke test for site generation

Generating an `index.html` requires a capable LLM. There is no
unattended end-to-end CI for this skill. The smoke test below is the
manual procedure you run after editing the skill prompt or schemas.

## Inputs

- The current [`PROMPT.md`](../PROMPT.md).
- A filled brief, e.g. [`fixtures/minimal_brief.yaml`](../fixtures/minimal_brief.yaml).
- Optionally, [`fixtures/example_results.json`](../fixtures/example_results.json)
  at `output/results.json`.

## Procedure

1. Open `PROMPT.md`. Replace the BRIEF block with the contents of
   `fixtures/minimal_brief.yaml`.
2. Paste the whole document into your LLM of choice.
3. Save the response as `index.html` in a fresh directory. If the
   brief sets `input_results_json_path: "output/results.json"`,
   create `output/` next to the file and copy
   `fixtures/example_results.json` to `output/results.json`.
4. Run the validator:

   ```sh
   node skills/design-data-storytelling-site/scripts/validate_single_file_html.js \
        path/to/index.html
   ```

5. Open the file in a browser. Confirm:
   - Layout renders at 360px, 720px, and 1200px widths.
   - Tab keyboard navigation works (`ArrowLeft` / `ArrowRight` /
     `Home` / `End`, `Enter` / `Space`).
   - The console has no errors.
   - When `input_results_json_path` is set: chapters populate from
     the JSON; if you remove `output/results.json`, the page still
     renders with `<body data-status="degraded">` and placeholder
     content.

## What success looks like

- `validate_single_file_html.js` exits 0.
- The page renders without script errors.
- The diagnostics tab shows the right status from the JSON.
- The anomaly heatmap legend uses
  `normal | watch | unusual | extreme`, never `best | worst`.
- No external network requests fire when `allow_cdn: false`.

## What to file when it fails

- The brief used.
- The model and version that generated the file.
- The validator output.
- A screenshot of the failing browser state (or DevTools error).

Open an issue against the skill prompt or the failing schema; the
fix usually belongs in `PROMPT.md`, `BRIEF_SCHEMA.md`, or
`RESULTS_INPUT_SCHEMA.md`, not in the generated file.
