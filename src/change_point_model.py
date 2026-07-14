"""
Bayesian change point model for Brent oil log returns.

Keeps model definition, sampling, and result-summarization logic out of the
notebook so it can be tested and reused (e.g. by the dashboard backend).
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


def sample_model(model: pm.Model, draws: int = 2000, tune: int = 1000,
                  chains: int = 4, target_accept: float = 0.9,
                  random_seed: int = 42) -> az.InferenceData:
    """
    Run MCMC sampling on a PyMC model.

    Raises:
        ModelError: if sampling fails outright (e.g. bad model spec).
    """
    try:
        with model:
            trace = pm.sample(
                draws=draws, tune=tune, chains=chains,
                target_accept=target_accept, random_seed=random_seed,
                return_inferencedata=True, progressbar=True,
            )
    except Exception as e:
        raise ModelError(f"MCMC sampling failed: {e}")

    return trace


def check_convergence(trace: az.InferenceData, r_hat_threshold: float = 1.05) -> dict:
    """
    Check r_hat for all parameters. Returns a dict of {param: r_hat} and
    flags any parameter exceeding the threshold.

    Raises:
        ModelError: if r_hat cannot be computed (e.g. single chain).
    """
    try:
        summary = az.summary(trace)
    except Exception as e:
        raise ModelError(f"Failed to compute convergence summary: {e}")

    r_hat_numeric = pd.to_numeric(summary["r_hat"], errors="coerce")
    r_hats = r_hat_numeric.to_dict()

    n_missing = r_hat_numeric.isna().sum()
    if n_missing > 0:
        print(f"NOTE: r_hat could not be computed for {n_missing} parameter(s) "
              f"(shown as NaN) — likely a single-chain or degenerate parameter.")

    failed = {k: v for k, v in r_hats.items() if pd.notna(v) and v > r_hat_threshold}
    if failed:
        print(f"WARNING: {len(failed)} parameter(s) exceed r_hat threshold "
              f"of {r_hat_threshold}: {failed}")
    else:
        print(f"All parameters converged (r_hat <= {r_hat_threshold}).")

    return r_hats


def get_change_point_date(trace: az.InferenceData, series: pd.Series) -> pd.Timestamp:
    """
    Map the posterior mode of tau (an integer index) back to an actual date
    using the series' index.

    Raises:
        ModelError: if tau is not in the trace or maps out of range.
    """
    if "tau" not in trace.posterior:
        raise ModelError("Trace does not contain a 'tau' variable.")

    tau_samples = trace.posterior["tau"].values.flatten()
    tau_mode = int(pd.Series(tau_samples).mode().iloc[0])

    if tau_mode < 0 or tau_mode >= len(series):
        raise ModelError(f"Posterior tau index {tau_mode} is out of range for series of length {len(series)}.")

    return series.index[tau_mode]


def summarize_impact(trace: az.InferenceData) -> dict:
    """
    Return posterior means and 95% credible intervals for mu_1, mu_2, and
    the implied percent change, for reporting.
    """
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