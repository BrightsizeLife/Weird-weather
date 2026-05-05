#!/usr/bin/env Rscript
# check_required_outputs.R
#
# Confirm that the output directory produced by the bayesian-panel-modeling
# skill contains every required file and that any figures listed inside
# results.json actually exist on disk.
#
# Usage:
#   Rscript check_required_outputs.R path/to/output
#
# Exit codes:
#   0  every required output present
#   1  one or more outputs missing
#   2  could not access the output directory

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  message("Usage: Rscript check_required_outputs.R path/to/output")
  quit(status = 2)
}

dir <- args[[1]]
if (!dir.exists(dir)) {
  message(sprintf("FAIL: output directory not found: %s", dir))
  quit(status = 2)
}

required <- c(
  "results.json",
  "model_report.md",
  "model_comparison.csv",
  "expected_values.csv",
  "observations_with_scores.csv",
  "summary_statistics.csv",
  "session_info.txt"
)

errors <- character(0)
for (f in required) {
  p <- file.path(dir, f)
  if (!file.exists(p)) {
    errors <- c(errors, sprintf("missing required output: %s", p))
    next
  }
  if (file.size(p) == 0) {
    errors <- c(errors, sprintf("required output is empty: %s", p))
  }
}

# Cross-check figures listed in results.json
results_path <- file.path(dir, "results.json")
if (file.exists(results_path) && requireNamespace("jsonlite", quietly = TRUE)) {
  j <- tryCatch(
    jsonlite::fromJSON(results_path, simplifyVector = FALSE),
    error = function(e) NULL
  )
  if (!is.null(j$figures)) {
    for (i in seq_along(j$figures)) {
      f <- j$figures[[i]]
      if (!is.null(f$path) && !file.exists(f$path)) {
        errors <- c(errors, sprintf("figure declared in results.json missing on disk: %s", f$path))
      }
    }
  }
}

if (length(errors) == 0) {
  message("OK: every required output is present and non-empty.")
  quit(status = 0)
} else {
  message("FAIL: missing or empty outputs:")
  for (e in errors) message("  - ", e)
  quit(status = 1)
}
