# Brent Oil Change Point Analysis

Change point analysis and statistical modeling of Brent crude oil prices to detect
structural breaks and associate them with major political and economic events —
built for **Birhan Energies**, a data-driven energy market consultancy.

This project analyzes over three decades of daily Brent oil prices (May 1987 –
September 2022) to help investors, policymakers, and energy companies understand
how geopolitical conflicts, OPEC decisions, sanctions, and economic shocks have
historically shifted oil prices.

---

## Getting Started

Clone this repository first:

```bash
git clone https://github.com/Redeat-Birhane/brent-oil-changepoint-analysis.git

cd brent-oil-changepoint-analysis
```

Then set up the environment:

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Place the raw dataset (`BrentOilPrices.csv`) inside `data/` before running any
notebooks.

---

## Project Structure
├── .vscode/                  # Editor settings
├── .github/workflows/        # CI (unit tests on push/PR)
├── data/                     # Raw data + compiled events dataset
├── docs/                     # Workflow, references, assumptions, model docs
├── notebooks/                # EDA and modeling notebooks
├── scripts/                  # Standalone scripts (backend, data prep)
├── src/                      # Reusable analysis modules
├── tests/                    # Unit tests
├── requirements.txt
└── README.md

---

## Objectives

1. Identify key events that significantly impacted Brent oil prices over the
   past decade(s).
2. Quantify how much these events affected price changes using Bayesian
   statistical methods.
3. Deliver clear, data-driven insights — via notebook, report, and dashboard —
   to guide investment strategy, policy development, and operational planning.

---

## Task 1 — Laying the Foundation for Analysis

Defines the analysis approach before any modeling begins.

- **`docs/analysis_workflow.md`** — end-to-end workflow from data loading to
  insight generation.
- **`data/events.csv`** — structured dataset of 15 major geopolitical/economic
  events (OPEC decisions, wars, sanctions, crises) with dates and descriptions.
- **`docs/assumptions_and_limitations.md`** — documented assumptions, plus a
  dedicated discussion on **correlation vs. causal impact** in time series.
- **`docs/references.md`** — key concepts reviewed (Bayesian change point
  detection, stationarity, volatility clustering, OPEC market structure).
- **`notebooks/1.0-eda-time-series-properties.ipynb`** — trend analysis,
  stationarity testing (ADF/KPSS), and volatility pattern analysis on raw
  price vs. log returns.
- **`docs/change_point_model_explanation.md`** — purpose of change point
  models, expected outputs (posterior over `tau`, quantified parameter
  shifts), and their limitations.

## Task 2 — Change Point Modeling and Insight Generation

Applies Bayesian change point detection to the price series.

- Data preparation: datetime conversion, log return calculation.
- Bayesian change point model built in **PyMC**:
  - Discrete uniform prior over switch point `tau`
  - Separate "before"/"after" parameters (μ1, μ2)
  - `pm.math.switch` to route the likelihood by time index
  - `pm.Normal` likelihood, sampled via MCMC (`pm.sample`)
- Convergence diagnostics (`pm.summary`, `pm.plot_trace`, r_hat).
- Posterior analysis of `tau` and before/after parameters, with quantified,
  probabilistic impact statements (e.g., "price shifted from $X to $Y, a Z%
  change").
- Detected change points cross-referenced against `data/events.csv` to
  formulate hypotheses about likely triggers.
- *(Optional extensions)*: incorporating macro variables (GDP, inflation,
  FX), VAR models, and Markov-switching regime models — noted as future work.

**Deliverable:** `notebooks/2.0-bayesian-change-point-model.ipynb`

## Task 3 — Interactive Dashboard

A full-stack dashboard so non-technical stakeholders can explore results
themselves.

**Backend (Flask)** — `scripts/backend/`
- REST APIs serving historical price data, change point results, and
  event-correlation data.
- Endpoints separated by concern: prices, change points, events.

**Frontend (React)** — `scripts/frontend/`
- Interactive charts (Recharts / Chart.js / D3.js) of price history with
  detected change points and event overlays.
- Date range filters, event highlight functionality, drill-down views.
- Responsive layout for desktop, tablet, and mobile.

**Deliverables:** working Flask API + React app, setup instructions, and
dashboard screenshots (see `scripts/README.md`).

---

## Tech Stack
- **Analysis:** Python, Pandas, NumPy, Statsmodels, PyMC, ArviZ, Matplotlib/Seaborn
- **Backend:** Flask
- **Frontend:** React, Recharts/Chart.js/D3.js
- **CI:** GitHub Actions (`.github/workflows/unittests.yml`)

## Testing

```bash
pytest tests/
```
