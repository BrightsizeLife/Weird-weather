# Brief schema

The YAML brief at the bottom of [`PROMPT.md`](./PROMPT.md) is the
single source of truth the LLM consumes. Every field is documented
here.

## Required

| field | type | example | notes |
|---|---|---|---|
| `project_title` | string | `"Weird Weather"` | Page `<title>`, `<h1>`. |
| `subtitle` | string | `"Winter 2025–2026 vs 30-year normals"` | Header subtitle, OG description fallback. |
| `audience` | string | `"data-curious LinkedIn readers"` | Drives voice and depth. |
| `thesis` | string | `"Many cities had a winter that wasn't theirs."` | The single sentence the page argues. |
| `data_shape` | string | `"50 stations × 30 winter seasons; outcome is winter-mean temperature anomaly (°F)."` | What the data is. |
| `tabs` | list[string] | `["essay","summary","model","loo","expected_values","anomalies","diagnostics","methodology","artifacts"]` | Which chapters to render. |

## Optional

| field | type | default | notes |
|---|---|---|---|
| `author` | string | `null` | Byline. |
| `homepage_url` | URL | `null` | Header home link. |
| `unit_label` | string | `"unit"` | Displayed label. |
| `time_label` | string | `"time"` | Displayed label. |
| `outcome_label` | string | `"outcome"` | Displayed label, including units. |
| `source_notes` | string | `null` | Data attribution; rendered in the footer. |
| `default_tab` | string | first of `tabs` | Active tab on first paint. |
| `visual_style` | enum | `"weird_weather_dark"` | `weird_weather_dark | weird_weather_light` |
| `include_methodology` | bool | `true` | Methodology chapter on/off. |
| `include_code_blocks` | bool | `true` | Editable code blocks in methodology. |
| `include_exportable_posters` | bool | `true` | Artifacts tab on/off. |
| `input_results_json_path` | string | `null` | Path to the Bayesian skill's `output/results.json`. When provided, chapters populate from it. |
| `embed_figures_paths` | list[string] | `[]` | Pre-rendered figure paths to `<img>` into the page. |
| `output_file` | string | `"index.html"` | Output filename. |
| `allow_cdn` | bool | `false` | When `false`, the file is fully self-contained. |
| `use_d3` | bool | `false` | Only meaningful with `allow_cdn: true`. |
| `respect_light_scheme` | bool | `false` | If true, generate a reduced-glare light variant via `prefers-color-scheme: light`. |
| `include_kofi` | bool | `false` | Tip-jar card. |
| `kofi_username` | string | `null` | Required when `include_kofi: true`. |
| `analytics_id` | string | `null` | Default is no tracking; set this only if you must. |

## Tab semantics

The skill knows about a canonical set. Each entry below maps to a
chapter the prompt describes in detail.

| tab id | chapter | populated from |
|---|---|---|
| `essay` | long-form prose, serif | brief `thesis` + `audience` + your prose |
| `summary` | stat-card grid | `metadata`, `summary_statistics`, top anomaly counts |
| `model` | model ladder + selected model | `candidate_models`, `selected_model` |
| `loo` | LOO comparison + cautious LOO sentence | `candidate_models[].loo`, `loo_compare` rows |
| `expected_values` | population + per-unit posterior expected ribbons | `expected_values` |
| `anomalies` | unit × time heatmap + sortable table | `observations_with_scores` |
| `diagnostics` | what passed, what didn't, do-not-trust banner if applicable | `diagnostics`, `candidate_models[].diagnostics` |
| `methodology` | model formula, priors, code blocks | `selected_model`, `candidate_models[].priors`, your code |
| `artifacts` | exportable posters | derived from above |
| `essay_only_extras` (optional) | map / matrix / time series small multiples | brief-defined |

Unknown tabs in `tabs` cause the generated file to include a
`<!-- TODO: tab "X" was requested but no template exists -->` comment
and skip the panel.

## Validation

A brief is valid when:

- Every required field is non-empty.
- `tabs` contains at least one known tab id.
- `default_tab`, if set, appears in `tabs`.
- `kofi_username` is set whenever `include_kofi: true`.
- `input_results_json_path`, if set, points at a file the skill
  consumer can fetch (file path or relative URL).

The generated file should validate the brief in a `<script>` block at
load time when `input_results_json_path` is set, and fall back
gracefully if the JSON is missing or malformed.
