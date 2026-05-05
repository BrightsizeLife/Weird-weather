#!/usr/bin/env Rscript
# smoke_test_generated_script.R
#
# Helper for running a generated `analysis.R` against a fixture in
# this skill's `fixtures/` directory and then validating the
# resulting `output/` tree.
#
# This is NOT a fully automated end-to-end test. brms + Stan
# compilation make that expensive on first run. The script:
#
#   1. Verifies that R + brms + a Stan backend are available.
#   2. Runs the user-provided `analysis.R` (path passed as arg 1).
#   3. Validates the produced output via the other two scripts.
#
# Usage:
#   Rscript smoke_test_generated_script.R path/to/analysis.R [output_dir]
#
# It is the *user's* job to ensure that `analysis.R` is parameterized
# to read one of the fixtures in `../fixtures/` and write to
# `output_dir`.
#
# Exit codes:
#   0  smoke test passed
#   1  output validation failed
#   2  prerequisite missing (R package, Stan backend, or analysis.R)
#   3  analysis.R itself errored

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 1) {
  message("Usage: Rscript smoke_test_generated_script.R path/to/analysis.R [output_dir]")
  quit(status = 2)
}

analysis_path <- args[[1]]
output_dir    <- if (length(args) >= 2) args[[2]] else "output"

if (!file.exists(analysis_path)) {
  message(sprintf("FAIL: analysis.R not found at %s", analysis_path))
  quit(status = 2)
}

# Prereqs
need <- c("brms", "loo", "tidybayes", "posterior", "bayesplot", "jsonlite")
missing <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) > 0) {
  message(sprintf("FAIL: missing R packages: %s", paste(missing, collapse = ", ")))
  message("Install with: install.packages(c(", paste(sprintf("'%s'", missing), collapse = ", "), "))")
  quit(status = 2)
}

backend_ok <- requireNamespace("cmdstanr", quietly = TRUE) ||
              requireNamespace("rstan",    quietly = TRUE)
if (!backend_ok) {
  message("FAIL: neither cmdstanr nor rstan is installed.")
  quit(status = 2)
}

# Run the analysis as a separate Rscript invocation so we can capture
# its exit status cleanly.
status <- system2("Rscript", shQuote(analysis_path))
if (status != 0) {
  message(sprintf("FAIL: analysis.R exited with status %d", status))
  quit(status = 3)
}

script_dir <- dirname(sys.frame(1)$ofile %||% normalizePath(commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))[1]]))
`%||%` <- function(a, b) if (is.null(a)) b else a

check_required <- file.path(script_dir, "check_required_outputs.R")
validate_json  <- file.path(script_dir, "validate_results_json.R")

ok <- TRUE
if (file.exists(check_required)) {
  if (system2("Rscript", c(shQuote(check_required), shQuote(output_dir))) != 0) ok <- FALSE
}
if (file.exists(validate_json)) {
  rj <- file.path(output_dir, "results.json")
  if (system2("Rscript", c(shQuote(validate_json), shQuote(rj))) != 0) ok <- FALSE
}

if (ok) {
  message("OK: smoke test passed.")
  quit(status = 0)
} else {
  message("FAIL: output validation failed.")
  quit(status = 1)
}
