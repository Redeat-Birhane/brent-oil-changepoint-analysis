# Assumptions and Limitations

## Assumptions
- Daily closing Brent price is representative of that trading day's market conditions.
- Missing/non-trading days (weekends, holidays) are excluded and treated as gaps,
  not interpolated, unless resampling is explicitly performed.
- The event dataset, though researched carefully, is not exhaustive; it focuses on
  major, well-documented events likely to have market-wide effects.
- A single/few change point(s) in a segment is a simplification — real markets may
  have many overlapping regime shifts; the model captures the most statistically
  dominant ones.
- Event "start dates" are approximations (e.g., announcement date vs. effective
  date); markets often react in anticipation of, or with a lag to, an event.

## Limitations
- **Correlation vs. causation**: A change point detected close in time to an event
  indicates statistical association, not proof that the event caused the shift.
  Multiple events can cluster in time, confounding attribution. The model does not
  test causal mechanisms — it only identifies when the statistical properties
  (mean/variance) of the price series changed.
- **Confounding factors**: Broader macroeconomic conditions (interest rates,
  USD strength, global GDP growth) are not modeled and could be the true driver
  behind a detected change.
- **Model simplicity**: A single-change-point mean-shift model may not capture
  gradual regime changes, seasonality, or multiple simultaneous change points
  (mitigated partially by extending to multiple change points if needed).
- **Lag and anticipation effects**: Markets may price in expected events before
  they occur, or react with a delay, making exact date-matching to the change
  point imprecise.
- **Data granularity**: Daily data cannot capture intraday volatility or
  news-driven price spikes and reversals within a single day.

## Correlation vs. Causal Impact (Discussion)
Detecting that a change point in the Bayesian model coincides with a known event
tells us *when* the statistical behavior of the price series changed — not *why*.
To claim causality would require, at minimum: a plausible economic mechanism
linking the event to oil supply/demand, evidence ruling out simultaneous
confounding events, and ideally a counterfactual or control comparison (e.g.,
similar commodities unaffected by the event). This analysis is explicitly
correlational — it surfaces hypotheses about drivers of price shifts, which
should be validated with domain expertise and, where possible, more rigorous
causal inference methods (e.g., difference-in-differences, event studies with
controls).