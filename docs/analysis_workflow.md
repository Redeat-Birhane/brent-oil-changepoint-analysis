# Brent Oil Price Analysis — Workflow

## 1. Objective
Identify structural breaks (change points) in Brent crude oil prices (1987–2022)
and associate them with major geopolitical and economic events, to support
investment, policy, and operational decisions.

## 2. Data Loading and Preparation
- Load `BrentOilPrices.csv` (Date, Price).
- Parse `Date` (format `%d-%b-%y`) into datetime, sort chronologically, set as index.
- Check for missing values, duplicate dates, and outliers.
- Compute log returns: `log(P_t) - log(P_{t-1})` for stationarity and volatility analysis.

## 3. Exploratory Data Analysis
- Plot raw price series to identify visible trends, shocks, and volatility clusters.
- Plot log returns to inspect stationarity and volatility clustering.
- Run stationarity tests (ADF, KPSS) on price level vs. log returns.
- Rolling statistics (mean, std) to visualize volatility regimes over time.

## 4. Event Data Compilation
- Research 10–15 major events (OPEC decisions, wars, sanctions, financial crises)
  known to have influenced Brent prices.
- Store as structured CSV: `event_date, event_name, category, description`.

## 5. Bayesian Change Point Modeling
- Build a PyMC model with a discrete uniform prior over `tau` (switch point).
- Define pre/post-tau parameters (e.g., means μ1, μ2, and/or volatility σ1, σ2).
- Use `pm.math.switch` to route the likelihood mean/variance by time index.
- Sample posterior via MCMC (`pm.sample`).
- Diagnose convergence: r_hat ≈ 1.0, trace plots, effective sample size.

## 6. Interpretation and Association with Events
- Extract posterior distribution of tau → most probable change point date(s).
- Quantify shift in mean/volatility before vs. after tau (with credible intervals).
- Cross-reference change point dates (± reasonable window) against the event dataset.
- Formulate hypotheses connecting each detected change to a plausible cause.
- Explicitly flag hypotheses as correlational, not causal (see limitations).

## 7. Communication
- Technical results: Jupyter notebook with full code, plots, diagnostics.
- Stakeholder-facing: interactive dashboard (Flask + React) and a short written
  report/slide deck summarizing key findings in non-technical language.
- Primary channels: internal report (PDF/slides) for policymakers/investors,
  and the live dashboard for ongoing self-service exploration.

## 8. Assumptions and Limitations
See `docs/assumptions_and_limitations.md`.