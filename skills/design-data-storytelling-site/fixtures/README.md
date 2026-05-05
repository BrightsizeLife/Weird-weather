# Fixtures

Smoke-test inputs for the data-storytelling site skill.

| file | purpose |
|---|---|
| `minimal_brief.yaml` | A minimum-viable brief that exercises every chapter the skill knows about. |
| `example_results.json` | A small but schema-valid `results.json` that matches the shape of the Bayesian R skill's output. Drop into `output/results.json` next to a generated `index.html` to test the JSON-hydrated path. |

## Generating

`example_results.json` is hand-written and small (one model, three
units, three time points, three observation rows). It is not a real
Bayesian fit; it exists to exercise the consumer side of the
schema. To regenerate from a real run, point the Bayesian R skill
at one of its own fixtures:

```sh
Rscript analysis.R   # with PARAMETERS pointing at fixtures/minimal_panel.csv
cp output/results.json \
   skills/design-data-storytelling-site/fixtures/example_results.json
```

Keep the fixture small. It exists to validate the contract, not to
look pretty.
