# ═══════════════════════════════════════════════════════════════════════════
#  REFERENCE TEMPLATE — what the LLM should generate
#
#  Read this if you want to know what "good output" looks like for the
#  PROMPT.md skill in this directory. The LLM will adapt this scaffold
#  to your specific {data_path, unit_var, time_var, outcome_var, factors}.
#
#  This file is illustrative — it expects placeholder values. Don't run
#  it directly; use the skill prompt instead.
# ═══════════════════════════════════════════════════════════════════════════

suppressPackageStartupMessages({
  required <- c("mgcv", "dplyr", "tidyr", "jsonlite", "DHARMa", "broom")
  missing  <- required[!sapply(required, requireNamespace, quietly = TRUE)]
  if (length(missing) > 0) {
    cat("Installing missing packages:", paste(missing, collapse = ", "), "\n")
    install.packages(missing, repos = "https://cloud.r-project.org")
  }
  library(mgcv); library(dplyr); library(tidyr)
  library(jsonlite); library(DHARMa); library(broom)
})

# ── Parameters (filled in by the LLM from PROMPT.md) ────────────────────────

P <- list(
  data_path        = "data/panel.csv",
  data_format      = "csv",
  unit_var         = "unit",
  time_var         = "time",
  outcome_var      = "outcome",
  factors          = c(),                  # e.g. c("phase", "promo")
  reference_levels = list(),               # e.g. list(phase = "neutral")
  evaluation_time  = NA,                   # NA = use max(time)
  spline_k         = 10,
  spline_basis     = "cr",
  output_dir       = "output",
  seed             = 42
)
set.seed(P$seed)
dir.create(P$output_dir, showWarnings = FALSE, recursive = TRUE)

# ── 1. Load + validate ──────────────────────────────────────────────────────

stopifnot(file.exists(P$data_path))
df <- if (P$data_format == "csv") {
  read.csv(P$data_path, stringsAsFactors = FALSE)
} else {
  raw <- fromJSON(P$data_path, simplifyDataFrame = TRUE)
  if (is.data.frame(raw)) raw else bind_rows(raw)
}

required_cols <- c(P$unit_var, P$time_var, P$outcome_var, P$factors)
missing <- setdiff(required_cols, names(df))
if (length(missing) > 0) stop("Missing columns: ", paste(missing, collapse = ", "))

df <- df %>%
  rename(unit = !!P$unit_var, time = !!P$time_var, outcome = !!P$outcome_var) %>%
  filter(!is.na(outcome), !is.na(unit), !is.na(time)) %>%
  mutate(unit = as.factor(unit), time = as.numeric(time))

for (f in P$factors) {
  ref <- P$reference_levels[[f]]
  df[[f]] <- if (!is.null(ref)) relevel(as.factor(df[[f]]), ref = ref) else as.factor(df[[f]])
}

cat("══ Loaded ══\n")
cat("n_obs:   ", nrow(df), "\n")
cat("n_units: ", nlevels(df$unit), "\n")
cat("time:    ", min(df$time), "→", max(df$time), "\n")
for (f in P$factors) cat(sprintf("  %s: %s\n", f, paste(levels(df[[f]]), collapse = ", ")))

# ── 2. Build formulas ───────────────────────────────────────────────────────

base_terms <- sprintf("s(time, k = %d, bs = %s)", P$spline_k, deparse(P$spline_basis))
re_terms   <- "s(unit, bs = \"re\") + s(time, unit, bs = \"re\")"
factor_terms <- if (length(P$factors) > 0) paste(P$factors, collapse = " + ") else NULL
inter_terms  <- if (length(P$factors) > 0)
  paste(sprintf("%s:unit", P$factors), collapse = " + ") else NULL

f_baseline <- as.formula(paste("outcome ~", base_terms, "+", re_terms))
f_with_facs <- if (!is.null(factor_terms))
  as.formula(paste("outcome ~", base_terms, "+", factor_terms, "+", re_terms)) else f_baseline
f_with_inter <- if (!is.null(inter_terms))
  as.formula(paste("outcome ~", base_terms, "+", factor_terms, "+", inter_terms, "+", re_terms)) else f_with_facs

# ── 3. Fit full model, diagnostics ──────────────────────────────────────────

m_full <- gam(f_with_facs, data = df, method = "REML")

cat("\n══ Model summary ══\n"); print(summary(m_full))
cat("\n══ Variance components ══\n"); print(gam.vcomp(m_full, rescale = FALSE))
cat("\n══ Concurvity ══\n"); print(concurvity(m_full, full = FALSE))

pdf(file.path(P$output_dir, "diagnostics.pdf"), width = 9, height = 9)
par(mfrow = c(2, 2)); gam.check(m_full); dev.off()

sim_res <- simulateResiduals(m_full, n = 500)
pdf(file.path(P$output_dir, "dharma.pdf"), width = 10, height = 6)
plot(sim_res); dev.off()

# ── 4. Block leave-one-time-out CV ──────────────────────────────────────────

block_cv <- function(formula, df) {
  yrs <- sort(unique(df$time)); preds <- numeric(nrow(df))
  for (yr in yrs) {
    train <- df %>% filter(time != yr); test <- df %>% filter(time == yr)
    fit <- tryCatch(gam(formula, data = train, method = "REML"), error = function(e) NULL)
    if (is.null(fit)) { preds[df$time == yr] <- NA; next }
    preds[df$time == yr] <- predict(fit, newdata = test)
  }
  sqrt(mean((df$outcome - preds)^2, na.rm = TRUE))
}

formulas <- list(baseline = f_baseline, with_factors = f_with_facs, with_interactions = f_with_inter)
cv_rmse <- sapply(formulas, block_cv, df = df)
cat("\n══ Block CV — RMSE ══\n"); print(round(cv_rmse, 3))

fits <- lapply(formulas, function(f) gam(f, data = df, method = "REML"))
ic_table <- data.frame(
  model = names(fits),
  AIC   = round(sapply(fits, AIC), 2),
  BIC   = round(sapply(fits, BIC), 2),
  edf   = round(sapply(fits, function(f) sum(f$edf)), 2)
)
cat("\n══ AIC / BIC ══\n"); print(ic_table)

# ── 5. Per-unit σ + z-scores at evaluation_time ─────────────────────────────

eval_t <- if (is.na(P$evaluation_time)) max(df$time) else P$evaluation_time

sigmas <- df %>%
  mutate(resid = residuals(m_full)) %>%
  group_by(unit) %>% summarise(sigma = sd(resid), n = n()) %>%
  mutate(sigma = ifelse(n < 5, sd(residuals(m_full)), sigma))

df$fitted <- fitted(m_full); df$resid <- residuals(m_full)
df <- df %>% left_join(sigmas %>% select(unit, sigma_unit = sigma), by = "unit") %>%
  mutate(z = resid / sigma_unit)

z_eval <- df %>% filter(time == eval_t) %>% arrange(desc(z)) %>%
  select(unit, time, outcome, fitted, resid, sigma_unit, z, all_of(P$factors))

cat(sprintf("\n══ z-scores at time = %s — top 5 / bottom 5 ══\n", eval_t))
print(head(z_eval, 5)); print(tail(z_eval, 5))

# ── 6. Save results ─────────────────────────────────────────────────────────

write_json(
  list(
    formula     = deparse(f_with_facs),
    family      = "gaussian", method = "REML",
    cv_rmse     = as.list(round(cv_rmse, 3)),
    ic_table    = ic_table,
    factor_coefs = as.list(round(coef(m_full)[!grepl("^s\\(", names(coef(m_full)))], 3)),
    sigmas      = sigmas,
    z_eval      = z_eval,
    metadata    = list(n_obs = nrow(df), n_units = nlevels(df$unit),
                       time_range = range(df$time), parameters = P)
  ),
  file.path(P$output_dir, "results.json"),
  auto_unbox = TRUE, pretty = TRUE
)

cat(sprintf("\nDone. Results in %s/\n", P$output_dir))
