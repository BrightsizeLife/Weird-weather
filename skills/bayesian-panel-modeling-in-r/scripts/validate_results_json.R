#!/usr/bin/env Rscript
# validate_results_json.R
#
# Validate the structural shape of a results.json produced by the
# bayesian-panel-modeling-in-r skill. Checks required keys, required
# nested fields, basic types, and emits clear messages naming the
# offending path.
#
# Usage:
#   Rscript validate_results_json.R path/to/results.json
#
# Exit codes:
#   0  every required key present and well-typed
#   1  missing or malformed required key
#   2  could not read the file at all

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  message("Usage: Rscript validate_results_json.R path/to/results.json")
  quit(status = 2)
}

path <- args[[1]]
if (!file.exists(path)) {
  message(sprintf("FAIL: results.json not found at %s", path))
  quit(status = 2)
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  message("FAIL: package 'jsonlite' is required.")
  quit(status = 2)
}

j <- tryCatch(
  jsonlite::fromJSON(path, simplifyVector = FALSE),
  error = function(e) {
    message(sprintf("FAIL: could not parse JSON at %s: %s", path, conditionMessage(e)))
    quit(status = 2)
  }
)

errors <- character(0)
report <- function(msg) errors[[length(errors) + 1]] <<- msg

req_top <- c("metadata", "summary_statistics", "candidate_models",
             "selected_model", "posterior_summaries", "expected_values",
             "observations_with_scores", "figures", "diagnostics")
for (k in req_top) {
  if (is.null(j[[k]])) report(sprintf("missing top-level key: %s", k))
}

# metadata
md <- j$metadata
md_req <- c("generated_at", "data_path", "n_rows", "n_units", "unit_col",
            "time_col", "outcome_col", "factor_cols", "modeling_engine",
            "backend", "warnings")
for (k in md_req) {
  if (is.null(md[[k]])) report(sprintf("metadata.%s missing", k))
}
if (!is.null(md$warnings) && !is.list(md$warnings) && !is.character(md$warnings)) {
  report("metadata.warnings must be an array of strings")
}

# candidate_models
cm <- j$candidate_models
if (!is.null(cm)) {
  if (!is.list(cm) || (length(cm) > 0 && is.null(cm[[1]]$model_id))) {
    report("candidate_models must be an array of objects with at least model_id")
  }
  for (i in seq_along(cm)) {
    m <- cm[[i]]
    for (k in c("model_id", "formula", "fit_status", "priors",
                "sampling", "diagnostics", "loo")) {
      if (is.null(m[[k]])) {
        report(sprintf("candidate_models[%d].%s missing", i, k))
      }
    }
  }
}

# selected_model
sm <- j$selected_model
if (!is.null(sm)) {
  for (k in c("model_id", "selection_reason", "caveats")) {
    if (is.null(sm[[k]])) report(sprintf("selected_model.%s missing", k))
  }
}

# posterior_summaries
ps <- j$posterior_summaries
if (!is.null(ps)) {
  for (k in c("population_effects", "group_effects",
              "factor_effects", "variance_components")) {
    if (is.null(ps[[k]])) report(sprintf("posterior_summaries.%s missing", k))
  }
}

# expected_values + observations_with_scores
if (!is.null(j$expected_values) && length(j$expected_values) > 0) {
  ev <- j$expected_values[[1]]
  for (k in c("unit", "time", "expected_q05", "expected_q50", "expected_q95",
              "prediction_q05", "prediction_q50", "prediction_q95")) {
    if (is.null(ev[[k]])) report(sprintf("expected_values[].%s missing", k))
  }
}
if (!is.null(j$observations_with_scores) && length(j$observations_with_scores) > 0) {
  o <- j$observations_with_scores[[1]]
  for (k in c("unit", "time", "observed", "expected_q50",
              "prediction_q05", "prediction_q95",
              "tail_probability", "posterior_predictive_percentile",
              "standardized_residual_like_score", "flag")) {
    if (is.null(o[[k]])) report(sprintf("observations_with_scores[].%s missing", k))
  }
  flags <- vapply(j$observations_with_scores, function(x) x$flag %||% "", character(1))
  bad <- setdiff(unique(flags), c("normal", "watch", "unusual", "extreme"))
  if (length(bad) > 0) {
    report(sprintf("invalid flag values: %s", paste(bad, collapse = ", ")))
  }
}

# diagnostics
dg <- j$diagnostics
if (!is.null(dg)) {
  if (is.null(dg$overall_status) ||
      !dg$overall_status %in% c("ok", "warning", "failed")) {
    report("diagnostics.overall_status must be one of ok|warning|failed")
  }
  for (k in c("warnings", "recommended_next_steps")) {
    if (is.null(dg[[k]])) report(sprintf("diagnostics.%s missing", k))
  }
}

# figures
fg <- j$figures
if (!is.null(fg) && length(fg) > 0) {
  f <- fg[[1]]
  for (k in c("id", "path", "title", "description")) {
    if (is.null(f[[k]])) report(sprintf("figures[].%s missing", k))
  }
}

`%||%` <- function(a, b) if (is.null(a)) b else a

if (length(errors) == 0) {
  message("OK: results.json validates against the schema contract.")
  quit(status = 0)
} else {
  message("FAIL: results.json validation errors:")
  for (e in errors) message("  - ", e)
  quit(status = 1)
}
