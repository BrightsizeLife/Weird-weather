# ═══════════════════════════════════════════════════════════════════════════
#  Weird Weather — if we did this by the books, in R
# ═══════════════════════════════════════════════════════════════════════════
#
#  This is what the model would look like in R, done properly:
#
#    • ENSO phase as a model term (fixed effect), not post-hoc residual mean
#    • Smoothing parameter chosen by REML (data-driven, not hard-coded df)
#    • Block (leave-one-year-out) CV to compare nested models honestly
#    • Real diagnostics: QQ, residuals vs fitted, leverage, concurvity,
#      DHARMa simulation-based residuals, variance components
#
#  fit_model.py emits the dashboard JSON. This file is intentionally
#  separate — it's the "what the by-the-books version looks like" exhibit.
#  Run it standalone; it writes data/dashboard_data_R.json + two PDFs.
#
#  Dependencies (all on CRAN):
#    install.packages(c("mgcv", "dplyr", "tidyr", "jsonlite",
#                       "ggplot2", "broom", "DHARMa"))
#
#  Run:
#    Rscript if_we_did_this_in_R.R
#
# ═══════════════════════════════════════════════════════════════════════════

suppressPackageStartupMessages({
  library(mgcv)       # gam(): smooth + random effects + fixed effects in one
  library(dplyr)
  library(tidyr)
  library(jsonlite)
  library(broom)
  library(DHARMa)     # simulation-based residual diagnostics
})

set.seed(42)


# ── 1. Data ────────────────────────────────────────────────────────────────

cities_path <- "data/cities_weather.json"
stopifnot(file.exists(cities_path))

raw <- fromJSON(cities_path, simplifyDataFrame = FALSE)

# Flatten to one row per city-year (long format).
df_long <- bind_rows(lapply(raw, function(c) {
  if (is.null(c$timeseries) || length(c$timeseries) == 0) return(NULL)
  ts <- bind_rows(c$timeseries)
  ts$city <- paste0(c$name, ", ", c$state)
  ts
}))

# DJF ONI-based ENSO classification (must match fit_model.py ENSO_PHASES)
enso_phases <- c(
  `1991`="el_nino", `1992`="neutral", `1993`="neutral", `1994`="el_nino",
  `1995`="la_nina", `1996`="neutral", `1997`="el_nino", `1998`="la_nina",
  `1999`="la_nina", `2000`="la_nina", `2001`="neutral", `2002`="el_nino",
  `2003`="neutral", `2004`="el_nino", `2005`="la_nina", `2006`="el_nino",
  `2007`="la_nina", `2008`="la_nina", `2009`="el_nino", `2010`="la_nina",
  `2011`="la_nina", `2012`="neutral", `2013`="neutral", `2014`="el_nino",
  `2015`="el_nino", `2016`="neutral", `2017`="la_nina", `2018`="el_nino",
  `2019`="neutral", `2020`="la_nina", `2021`="la_nina", `2022`="la_nina",
  `2023`="el_nino", `2024`="neutral", `2025`="la_nina"
)

df_long$phase <- factor(
  enso_phases[as.character(df_long$year)],
  levels = c("neutral", "el_nino", "la_nina")   # neutral = reference
)
df_long$city <- factor(df_long$city)

df_temp <- df_long %>% filter(!is.na(high))


# ── 2. The model ───────────────────────────────────────────────────────────
#
#   high ~ s(year)           # smooth national trend, df chosen by REML
#        + phase             # ENSO fixed effect (vs neutral reference)
#        + s(city, bs="re")  # random intercept per city
#        + s(year, city, bs="re")   # random slope per city
#
# REML chooses the spline's effective df from the data — no hard-coded k.

m_full <- gam(
  high ~ s(year, k = 8, bs = "cr") +
         phase +
         s(city, bs = "re") +
         s(year, city, bs = "re"),
  data   = df_temp,
  method = "REML"
)


# ── 3. Diagnostics ─────────────────────────────────────────────────────────

cat("\n══ Model summary ══\n")
print(summary(m_full))

cat("\n══ Variance components ══\n")
print(gam.vcomp(m_full, rescale = FALSE))

cat("\n══ Concurvity (smooth-term collinearity) ══\n")
print(concurvity(m_full, full = FALSE))

# Standard 4-up diagnostic plot: QQ, residuals vs fitted, hist, response
pdf("diagnostics_temperature.pdf", width = 9, height = 9)
par(mfrow = c(2, 2))
gam.check(m_full)
dev.off()
cat("Saved: diagnostics_temperature.pdf\n")

# Simulation-based residual diagnostics (works for GAMs, GLMMs, etc.)
sim_res <- simulateResiduals(m_full, n = 500)
pdf("dharma_temperature.pdf", width = 10, height = 6)
plot(sim_res)
dev.off()
cat("Saved: dharma_temperature.pdf\n")


# ── 4. Block CV: does ENSO actually pull its weight? ───────────────────────
#
# Three nested models compared by leave-one-year-out CV. Out-of-time folds
# are a stricter test than random k-fold for time-indexed data.

formulas <- list(
  baseline    = high ~ s(year, k = 8, bs = "cr") +
                       s(city, bs = "re") +
                       s(year, city, bs = "re"),
  with_enso   = high ~ s(year, k = 8, bs = "cr") +
                       phase +
                       s(city, bs = "re") +
                       s(year, city, bs = "re"),
  enso_x_city = high ~ s(year, k = 8, bs = "cr") +
                       phase +
                       s(city, bs = "re") +
                       s(year, city, bs = "re") +
                       phase:city
)

block_cv_rmse <- function(formula, df) {
  yrs <- sort(unique(df$year))
  preds <- numeric(nrow(df))
  for (yr in yrs) {
    train <- df %>% filter(year != yr)
    test  <- df %>% filter(year == yr)
    fit   <- gam(formula, data = train, method = "REML")
    preds[df$year == yr] <- predict(fit, newdata = test)
  }
  sqrt(mean((df$high - preds)^2))
}

cat("\n══ Block CV (leave-one-year-out) — RMSE in °F ══\n")
cv_rmse <- sapply(formulas, block_cv_rmse, df = df_temp)
print(round(cv_rmse, 3))

# In-sample AIC / BIC comparison
fits <- lapply(formulas, function(f) gam(f, data = df_temp, method = "REML"))
ic_table <- data.frame(
  model = names(fits),
  AIC   = round(sapply(fits, AIC), 2),
  BIC   = round(sapply(fits, BIC), 2),
  edf   = round(sapply(fits, function(f) sum(f$edf)), 2)
)
cat("\n══ AIC / BIC ══\n")
print(ic_table)


# ── 5. Per-city sigma (heteroscedastic errors) ─────────────────────────────
#
# mgcv assumes constant variance. For genuinely heteroscedastic errors,
# fit with mgcv::gam(family = gaulss(...)) or gamlss::gamlss(sigma.formula).
# Here we use the residual SD per city — same convention as fit_model.py.

city_sigmas <- df_temp %>%
  mutate(resid = residuals(m_full)) %>%
  group_by(city) %>%
  summarise(sigma = sd(resid), n = n()) %>%
  arrange(desc(sigma))

cat("\n══ σ per city — top 5 / bottom 5 ══\n")
print(rbind(head(city_sigmas, 5), tail(city_sigmas, 5)))


# ── 6. Per-city z-scores for 2025 ──────────────────────────────────────────

df_temp$fitted <- fitted(m_full)
df_temp$resid  <- residuals(m_full)
df_temp <- df_temp %>%
  left_join(city_sigmas %>% select(city, sigma_city = sigma), by = "city") %>%
  mutate(z = resid / sigma_city)

z_2025 <- df_temp %>%
  filter(year == 2025) %>%
  arrange(desc(z)) %>%
  select(city, high, fitted, resid, sigma_city, z, phase)

cat("\n══ 2025 z-scores — top 5 / bottom 5 ══\n")
print(head(z_2025, 5))
print(tail(z_2025, 5))


# ── 7. Save outputs ────────────────────────────────────────────────────────

dir.create("data", showWarnings = FALSE)

write_json(
  list(
    model       = paste("high ~ s(year, k=8) + phase +",
                        "s(city, bs=re) + s(year, city, bs=re)"),
    family      = "gaussian",
    method      = "REML",
    cv_rmse     = as.list(round(cv_rmse, 3)),
    ic_table    = ic_table,
    enso_coefs  = as.list(round(coef(m_full)[grep("phase", names(coef(m_full)))], 3)),
    n_obs       = nrow(df_temp),
    n_cities    = nlevels(df_temp$city),
    city_sigmas = city_sigmas,
    z_2025      = z_2025
  ),
  "data/dashboard_data_R.json",
  auto_unbox = TRUE,
  pretty     = TRUE
)

cat("\nDone. Wrote data/dashboard_data_R.json plus two PDFs.\n")
