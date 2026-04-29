# Skills

Two reusable, agent-agnostic skills extracted from this project. Each
one is a prompt + supporting docs you can paste into any capable LLM
(Claude, ChatGPT, Gemini, Llama, etc.) to apply the same pattern to
your own data.

## What "agent-agnostic" means

These skills do **not** depend on Claude Code, OpenAI Functions, MCP,
or any specific runtime. They're plain markdown that:

1. Tells the LLM what to do (ROLE, TASK, REQUIREMENTS).
2. Gives the LLM a parameter block to consume.
3. Specifies the output format.

You bring the LLM. The skill brings the structure.

---

## [`replicate-mixed-effects-in-R/`](./replicate-mixed-effects-in-R/)

> Replicate the Weird Weather analysis on your own panel data, in R,
> by the books.

**What you put in:** the path to your data, the unit / time / outcome
columns, optional categorical factors.

**What you get out:** a single self-contained R script that fits a
mixed-effects GAM with REML, runs block leave-one-time-out CV across
three nested models (baseline → +factors → +factor×unit), produces
real diagnostics (gam.check, DHARMa, concurvity, variance components),
computes per-unit σ and per-unit z-scores, and writes JSON + diagnostic
PDFs.

**Read first:** [`SKILL.md`](./replicate-mixed-effects-in-R/SKILL.md) ·
[`PROMPT.md`](./replicate-mixed-effects-in-R/PROMPT.md) ·
[`PARAMETERS.md`](./replicate-mixed-effects-in-R/PARAMETERS.md) ·
[`EXAMPLE.md`](./replicate-mixed-effects-in-R/EXAMPLE.md)

---

## [`design-data-storytelling-site/`](./design-data-storytelling-site/)

> Generate a complete single-file HTML/CSS/JS data-storytelling website
> in the Weird Weather visual language.

**What you put in:** a brief (project title, data shape, thesis,
audience, tabs you want).

**What you get out:** one `index.html` file you can open in a browser.
Dark theme, monospace, sticky tab bar, editable code blocks, exportable
infographic posters, mobile-friendly. Self-contained.

**Read first:** [`SKILL.md`](./design-data-storytelling-site/SKILL.md) ·
[`PROMPT.md`](./design-data-storytelling-site/PROMPT.md) ·
[`DESIGN-SYSTEM.md`](./design-data-storytelling-site/DESIGN-SYSTEM.md) ·
[`COMPONENTS.md`](./design-data-storytelling-site/COMPONENTS.md) ·
[`EXAMPLE.md`](./design-data-storytelling-site/EXAMPLE.md)

---

## Pairing the two skills

These are designed to compose:

1. Use **`replicate-mixed-effects-in-R`** to fit the model and write
   `output/results.json`.
2. Use **`design-data-storytelling-site`** with that JSON shape in the
   brief; the LLM produces a site that reads it.

Result: end-to-end "I have a panel dataset" → "I have a published
data story" in two prompts and an evening.

---

## License

Part of the [Weird Weather repo](https://github.com/BrightsizeLife/Weird-weather).
Use, fork, change. Attribution welcome but not required.
