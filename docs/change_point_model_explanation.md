# Change Point Models: Purpose, Outputs, and Limitations

## Purpose
A change point model is designed to detect **structural breaks** — points in
time where the underlying statistical properties of a time series (mean,
variance, trend, or other parameters) shift from one regime to another.
Unlike a rolling window or a manually chosen threshold, a Bayesian change
point model treats the *location* of the break itself as unknown and infers
it probabilistically from the data.

In the context of Brent oil prices, this matters because:
- Oil prices don't move smoothly — they exhibit sudden regime shifts driven
  by supply shocks, geopolitical events, and policy decisions.
- A single global mean/variance across 35 years of data is meaningless; the
  market has behaved very differently across sub-periods (e.g., pre-2008 vs.
  the 2014–16 glut vs. post-COVID).
- By explicitly modeling *where* these shifts occur, we convert a vague
  "the market changed at some point" intuition into a quantified,
  probabilistic date estimate that can be cross-referenced against known
  events.

## Expected Outputs
A completed change point analysis produces:
1. **Posterior distribution over the change point date (`tau`)** — not a
   single date, but a distribution reflecting how confident the model is.
   A narrow, sharply peaked posterior means high certainty about *when* the
   shift happened; a wide, flat posterior means the data doesn't clearly
   support one specific date.
2. **Posterior distributions for the "before" and "after" parameters**
   (e.g., μ1 vs. μ2, and/or σ1 vs. σ2) — allowing probabilistic statements
   like "there is a 95% probability the mean shifted by at least $X."
3. **Quantified impact estimates**, e.g. "the average price moved from
   $71 to $94, a 32% increase, with 95% credible interval [$85, $103]."
4. **Convergence diagnostics** (r_hat, trace plots, effective sample size)
   confirming the MCMC sampler actually explored the posterior reliably —
   without this, the outputs above can't be trusted.

## Limitations
- **Detects association, not mechanism**: the model identifies *when*
  parameters changed, not *why*. Linking a change point to a specific event
  is a hypothesis based on temporal proximity, not a tested causal claim
  (see `assumptions_and_limitations.md` for the full discussion).
- **Single change point models are a simplification**: the basic model
  (as specified in Task 2) assumes exactly one switch point. Real price
  history likely contains many. This can be partially addressed by running
  the model on sub-segments, or extending to a multiple-change-point
  specification.
- **Sensitivity to model specification**: results depend on choices like
  the prior over `tau` (uniform here), the likelihood family (Normal), and
  whether both mean and variance are allowed to shift. Misspecification can
  bias which date the posterior favors.
- **Coincidental clustering of events**: because major events (crises,
  OPEC decisions, conflicts) sometimes cluster closely in time, a detected
  change point may sit near multiple plausible candidate events, making
  the "which event caused this" attribution genuinely ambiguous.
- **No forecasting guarantee**: identifying past change points doesn't by
  itself predict *future* ones; it characterizes historical regimes only.