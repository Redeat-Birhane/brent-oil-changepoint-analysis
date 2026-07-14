"""
Bayesian change point model for Brent oil log returns.

Uses the `nutpie` NUTS sampler by default, which ships precompiled binaries
and does not require a C++ compiler (a common blocker on Windows).
"""
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az


class ModelError(Exception):
    """Raised when model input is invalid or fitting fails."""
    pass


def build_mean_shift_model(series: pd.Series) -> pm.Model:
    """
    Build a single change point model on a 1D series (e.g. log returns).

    Prior: tau ~ DiscreteUniform over all time indices.
    Likelihood: Normal, with mean switching from mu_1 to mu_2 at tau,
    and a single shared sigma.

    Raises:
        ModelError: if the series is empty, has NaNs, or is too short.
    """
    if series is None or len(series) == 0:
        raise ModelError("Input series is empty.")

    if series.isna().any():
        raise ModelError(
            f"Input series contains {series.isna().sum()} NaN value(s); "
            "drop or fill them before modeling."
        )

    if len(series) < 30:
        raise ModelError(
            f"Input series has only {len(series)} observations; "
            "need a reasonably long series for a meaningful change point."
        )

    y = series.values
    n = len(y)
    idx = np.arange(n)

    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

        mu_1 = pm.Normal("mu_1", mu=y.mean(), sigma=y.std() * 2)
        mu_2 = pm.Normal("mu_2", mu=y.mean(), sigma=y.std() * 2)
        sigma = pm.HalfNormal("sigma", sigma=y.std() * 2)

        mu = pm.math.switch(tau >= idx, mu_1, mu_2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=y)

    return model

def sample_model(model: pm.Model, draws: int = 1000, tune: int = 1000,
                  chains: int = 4, random_seed: int = 42) -> az.InferenceData:
    """
    Run MCMC sampling on a PyMC model. PyMC auto-assigns a compound step
    (NUTS for continuous parameters, Metropolis for the discrete tau).
    """
    try:
        with model:
            trace = pm.sample(
                draws=draws, tune=tune, chains=chains,
                random_seed=random_seed,
                progressbar=True,
            )
    except Exception as e:
        raise ModelError(f"MCMC sampling failed: {e}")

    return trace


def check_convergence(trace: az.InferenceData, r_hat_threshold: float = 1.05) -> dict:
    """
    Check r_hat for all parameters. Returns a dict of {param: r_hat} and
    flags any parameter exceeding the threshold.
    """
    try:
        summary = az.summary(trace)
    except Exception as e:
        raise ModelError(f"Failed to compute convergence summary: {e}")

    r_hat_numeric = pd.to_numeric(summary["r_hat"], errors="coerce")
    r_hats = r_hat_numeric.to_dict()

    n_missing = r_hat_numeric.isna().sum()
    if n_missing > 0:
        print(f"NOTE: r_hat could not be computed for {n_missing} parameter(s).")

    failed = {k: v for k, v in r_hats.items() if pd.notna(v) and v > r_hat_threshold}

    if failed:
        print(f"WARNING: {len(failed)} parameter(s) exceed r_hat threshold "
              f"of {r_hat_threshold}: {failed}")
    else:
        print(f"All parameters converged (r_hat <= {r_hat_threshold}).")

    return r_hats


def get_change_point_date(trace: az.InferenceData, series: pd.Series) -> pd.Timestamp:
    """Map the posterior mode of tau back to an actual date."""
    if "tau" not in trace.posterior:
        raise ModelError("Trace does not contain a 'tau' variable.")

    tau_samples = trace.posterior["tau"].values.flatten()
    tau_mode = int(pd.Series(tau_samples).mode().iloc[0])

    if tau_mode < 0 or tau_mode >= len(series):
        raise ModelError(f"Posterior tau index {tau_mode} is out of range.")

    return series.index[tau_mode]


def summarize_impact(trace: az.InferenceData) -> dict:
    """Posterior means and 95% credible intervals for mu_1, mu_2, and % change."""
    summary = az.summary(trace, var_names=["mu_1", "mu_2"], hdi_prob=0.95)

    mu_1_mean = summary.loc["mu_1", "mean"]
    mu_2_mean = summary.loc["mu_2", "mean"]

    pct_change = None
    if mu_1_mean != 0:
        pct_change = (mu_2_mean - mu_1_mean) / abs(mu_1_mean) * 100

    return {
        "mu_1_mean": mu_1_mean,
        "mu_1_hdi": (summary.loc["mu_1", "hdi_2.5%"], summary.loc["mu_1", "hdi_97.5%"]),
        "mu_2_mean": mu_2_mean,
        "mu_2_hdi": (summary.loc["mu_2", "hdi_2.5%"], summary.loc["mu_2", "hdi_97.5%"]),
        "pct_change": pct_change,
    }

def build_volatility_shift_model(series: pd.Series) -> pm.Model:
    """
    Build a single change point model where VOLATILITY (sigma) shifts at
    tau, rather than the mean. Motivated by Task 1 EDA: Brent log returns
    hover near a constant mean across the full history, but volatility
    clusters into distinct regimes (calm vs. turbulent periods).

    Prior: tau ~ DiscreteUniform over all time indices.
    Likelihood: Normal with a single shared mean (mu), but sigma switches
    from sigma_1 to sigma_2 at tau.

    Raises:
        ModelError: if the series is empty, has NaNs, or is too short.
    """
    if series is None or len(series) == 0:
        raise ModelError("Input series is empty.")

    if series.isna().any():
        raise ModelError(
            f"Input series contains {series.isna().sum()} NaN value(s); "
            "drop or fill them before modeling."
        )

    if len(series) < 30:
        raise ModelError(
            f"Input series has only {len(series)} observations; "
            "need a reasonably long series for a meaningful change point."
        )

    y = series.values
    n = len(y)
    idx = np.arange(n)

    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)

        mu = pm.Normal("mu", mu=y.mean(), sigma=y.std() * 2)
        sigma_1 = pm.HalfNormal("sigma_1", sigma=y.std() * 2)
        sigma_2 = pm.HalfNormal("sigma_2", sigma=y.std() * 2)

        sigma = pm.math.switch(tau >= idx, sigma_1, sigma_2)

        pm.Normal("obs", mu=mu, sigma=sigma, observed=y)

    return model


def summarize_volatility_impact(trace: az.InferenceData) -> dict:
    """
    Posterior means and 95% credible intervals for sigma_1, sigma_2, and
    the implied percent change in volatility.
    """
    summary = az.summary(trace, var_names=["sigma_1", "sigma_2"], hdi_prob=0.95)

    sigma_1_mean = summary.loc["sigma_1", "mean"]
    sigma_2_mean = summary.loc["sigma_2", "mean"]

    pct_change = None
    if sigma_1_mean != 0:
        pct_change = (sigma_2_mean - sigma_1_mean) / sigma_1_mean * 100

    return {
        "sigma_1_mean": sigma_1_mean,
        "sigma_1_hdi": (summary.loc["sigma_1", "hdi_2.5%"], summary.loc["sigma_1", "hdi_97.5%"]),
        "sigma_2_mean": sigma_2_mean,
        "sigma_2_hdi": (summary.loc["sigma_2", "hdi_2.5%"], summary.loc["sigma_2", "hdi_97.5%"]),
        "pct_change": pct_change,
    }