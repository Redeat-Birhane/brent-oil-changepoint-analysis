# Key References Reviewed

## Bayesian Change Point Detection
- Core idea: model a time series as having one (or more) unknown points `tau`
  where the data-generating parameters shift. `tau` itself is treated as a
  random variable with a prior, and inferred via Bayesian updating rather than
  fixed by a heuristic threshold.
- PyMC documentation — "Coal Mining Disasters" case study: the canonical
  worked example of a discrete switch point model, which this project's
  Brent oil model is structurally based on (switch point + before/after
  parameters + `pm.math.switch`).

## Time Series Fundamentals
- **Stationarity**: a series whose statistical properties (mean, variance,
  autocorrelation) don't change over time. Most classical models (ARIMA, and
  simple constant-parameter change point segments) assume stationarity within
  each regime.
- **Unit root tests** (Augmented Dickey-Fuller, KPSS): standard tests used to
  determine whether a series is stationary or needs differencing/transforming
  (e.g. via log returns) before modeling.
- **Volatility clustering**: the well-documented tendency in financial time
  series (Brent oil included) for large price changes to be followed by large
  changes (of either sign), and small by small — motivating models that allow
  variance, not just mean, to shift at a change point.

## Oil Market Structure
- Background reading on OPEC/OPEC+ decision-making, historical oil shocks
  (1990 Gulf War, 2008 financial crisis, 2014–16 price collapse, 2020
  COVID/price war) to build the event dataset and sanity-check which dates
  are plausible drivers of detected change points.

## Key Concepts Carried Into Modeling
- Model changes in **distributional parameters** (mean and/or variance), not
  the raw price level directly, since raw prices are non-stationary.
- Treat the change point date as an object of **inference with uncertainty**,
  not a fixed known date — the output is a posterior distribution over `tau`,
  not a single point estimate.
- Keep the causal claim boundary explicit (see `assumptions_and_limitations.md`):
  references on change point methodology are consistently clear that these
  models detect *when* structure changed, not *why*.