# Skills

Two reusable, agent-agnostic skills extracted from the Weird Weather
project. Each one is a prompt kit + supporting docs you can paste
into any capable LLM (Claude, GPT, Gemini, Llama, …) to apply the
same pattern to your own data.

They are also **skill-aware** for agents that consume Anthropic-style
agent skills: each `SKILL.md` carries YAML frontmatter, supporting
documents practice progressive disclosure, and explicit input /
output schemas, evals, and validation scripts make the skill
testable rather than aspirational.

## What "agent-agnostic" means

These skills do not depend on Claude Code, OpenAI Functions, MCP, or
any specific runtime. They are plain markdown that:

1. Tells the LLM what to do (ROLE, TASK, REQUIREMENTS, DO NOT,
   QUALITY BAR).
2. Gives the LLM a parameter / brief block to consume.
3. Specifies the output format and validation entry points.

You bring the LLM. The skill brings the structure.

---

## The two skills

### [`bayesian-panel-modeling-in-r/`](./bayesian-panel-modeling-in-r/)

> Generate a reproducible Bayesian R analysis script for a
> longitudinal / panel dataset. brms + Stan, weakly informative
> priors, prior + posterior predictive checks, MCMC diagnostics,
> PSIS-LOO model comparison, posterior expected values,
> uncertainty-aware anomaly scores, and a JSON output the site
> skill consumes.

**What you put in.** A panel dataset (long format) and a YAML
parameter block (unit, time, outcome, factors, sampler knobs).

**What you get out.** A single self-contained `analysis.R` that
produces:

- `output/results.json` (consumed by the site skill)
- `output/model_report.md` (human-readable interpretation)
- `output/figures/*.png` and `output/diagnostics/*.png`
- `output/{model_comparison, expected_values, observations_with_scores,
  summary_statistics}.csv`

**Read first.** [`SKILL.md`](./bayesian-panel-modeling-in-r/SKILL.md) ·
[`PROMPT.md`](./bayesian-panel-modeling-in-r/PROMPT.md) ·
[`PARAMETERS.md`](./bayesian-panel-modeling-in-r/PARAMETERS.md) ·
[`BAYESIAN_WORKFLOW.md`](./bayesian-panel-modeling-in-r/BAYESIAN_WORKFLOW.md) ·
[`RESULTS_SCHEMA.md`](./bayesian-panel-modeling-in-r/RESULTS_SCHEMA.md) ·
[`VISUALIZATION_SPEC.md`](./bayesian-panel-modeling-in-r/VISUALIZATION_SPEC.md) ·
[`EVALS.md`](./bayesian-panel-modeling-in-r/EVALS.md) ·
[`EXAMPLE.md`](./bayesian-panel-modeling-in-r/EXAMPLE.md)

### [`design-data-storytelling-site/`](./design-data-storytelling-site/)

> Generate a self-contained single-page HTML/CSS/JS data-storytelling
> site in the Weird Weather visual language. Dark, monospace,
> tabbed chapters, accessible by construction, responsive to 360px.
> Reads the Bayesian skill's results JSON to populate model,
> diagnostics, expected-values, and anomaly chapters.

**What you put in.** A brief (project, audience, thesis, tabs) and
optionally a `results.json` from the Bayesian skill.

**What you get out.** One `index.html`. Self-contained by default.
Open it in a browser and it works.

**Read first.** [`SKILL.md`](./design-data-storytelling-site/SKILL.md) ·
[`PROMPT.md`](./design-data-storytelling-site/PROMPT.md) ·
[`BRIEF_SCHEMA.md`](./design-data-storytelling-site/BRIEF_SCHEMA.md) ·
[`RESULTS_INPUT_SCHEMA.md`](./design-data-storytelling-site/RESULTS_INPUT_SCHEMA.md) ·
[`DESIGN-SYSTEM.md`](./design-data-storytelling-site/DESIGN-SYSTEM.md) ·
[`COMPONENTS.md`](./design-data-storytelling-site/COMPONENTS.md) ·
[`ACCESSIBILITY.md`](./design-data-storytelling-site/ACCESSIBILITY.md) ·
[`EVALS.md`](./design-data-storytelling-site/EVALS.md) ·
[`EXAMPLE.md`](./design-data-storytelling-site/EXAMPLE.md)

### [`replicate-mixed-effects-in-R/`](./replicate-mixed-effects-in-R/) (deprecated)

The original frequentist (mgcv + REML) version of the modeling
skill. Kept for historical reference. New work should use
[`bayesian-panel-modeling-in-r/`](./bayesian-panel-modeling-in-r/).
See its [`README.md`](./replicate-mixed-effects-in-R/README.md) for
the deprecation note.

---

## Which skill should I use?

| your situation | use |
|---|---|
| You have a panel dataset and want a defensible posterior | `bayesian-panel-modeling-in-r` |
| You have a finished analysis and want to publish it | `design-data-storytelling-site` |
| You have both | run them in order — Bayesian → site, with the JSON in between |
| You need causal inference | neither: bring a causal design |
| You need a real-time dashboard | neither: this is publish-once narrative work |
| You need a marketing page | neither: the visual language and voice are wrong |

---

## The pipeline

```
panel data ─▶ bayesian-panel-modeling-in-r ─▶ output/results.json ─┐
                                              + figures/ + report  │
                                                                   ▼
                                          design-data-storytelling-site
                                                                   │
                                                                   ▼
                                                            index.html
```

End-to-end: "I have a panel dataset" → "I have a published data
story" in two prompts and one Stan run.

---

## Quality bar

These skills converge on a small set of operative rules:

- **Bayesian uncertainty over point estimates.** Every effect,
  expected value, and "anomaly" carries a credible or posterior
  predictive interval.
- **Model comparison is predictive, not metaphysical truth.**
  PSIS-LOO estimates expected out-of-sample predictive performance
  under the model assumptions. It does not "find the right model."
- **Diagnostics gate interpretation.** If MCMC diagnostics fail,
  the report and the site say "do not trust" rather than burying
  the failure.
- **Accessibility is structural, not decorative.** The site
  validator checks tab patterns, focus rings, reduced-motion
  rules, and color-as-only-channel violations.
- **Validation scripts before trust.** Every change runs the schema
  and HTML validators. Smoke runs are documented when full runtime
  isn't feasible.
- **Calm voice.** Never `best | worst`. Use the flag vocabulary
  `normal | watch | unusual | extreme`.
- **Descriptive, not causal.** Unless a causal design is supplied,
  the report and the site say so plainly.

---

## Skill structure

Both skills follow the same shape:

```
skill-name/
├── SKILL.md            # YAML frontmatter + short overview (progressive disclosure root)
├── PROMPT.md           # the LLM-facing prompt with parameters/brief at the bottom
├── …schema docs…       # input + output contracts
├── …workflow docs…     # the operative procedure
├── EXAMPLE.md          # worked end-to-end example
├── EVALS.md            # eval ledger + rubric
├── fixtures/           # tiny inputs for smoke + schema evals
└── scripts/            # validators (Node for the site, R for the model)
```

This shape is deliberate. `SKILL.md` is short — agents that read
frontmatter route off the description, and humans can scan for
"when not to use." Detail lives in the supporting documents
(progressive disclosure).

---

## License

Part of the
[Weird Weather repo](https://github.com/BrightsizeLife/Weird-weather).
Use, fork, change. Attribution welcome but not required.
