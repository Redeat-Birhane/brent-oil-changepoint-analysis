import numpy as np
import pandas as pd
import pytest

from src.change_point_model import (
    build_mean_shift_model, ModelError, get_change_point_date, summarize_impact
)
from src.change_point_model import build_volatility_shift_model

def make_synthetic_series(n=200, switch_at=100, mu1=0.0, mu2=2.0, sigma=0.5, seed=42):
    """Series with a known, deliberate mean shift at `switch_at`."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2020-01-01", periods=n, freq="D")
    values = np.concatenate([
        rng.normal(mu1, sigma, switch_at),
        rng.normal(mu2, sigma, n - switch_at),
    ])
    return pd.Series(values, index=dates)


# ---------- build_mean_shift_model ----------

def test_build_model_empty_series():
    with pytest.raises(ModelError, match="empty"):
        build_mean_shift_model(pd.Series([], dtype=float))


def test_build_model_with_nans():
    s = pd.Series([1.0, 2.0, np.nan, 3.0] * 10)
    with pytest.raises(ModelError, match="NaN"):
        build_mean_shift_model(s)


def test_build_model_too_short():
    s = pd.Series(np.random.randn(10))
    with pytest.raises(ModelError, match="only 10"):
        build_mean_shift_model(s)


def test_build_model_success():
    s = make_synthetic_series()
    model = build_mean_shift_model(s)
    assert "tau" in [v.name for v in model.free_RVs]
    assert "mu_1" in [v.name for v in model.free_RVs]
    assert "mu_2" in [v.name for v in model.free_RVs]


# ---------- get_change_point_date / summarize_impact (require sampling, kept minimal) ----------

def test_get_change_point_date_missing_tau():
    class FakeTrace:
        posterior = {}
    s = make_synthetic_series()
    with pytest.raises(ModelError, match="does not contain"):
        get_change_point_date(FakeTrace(), s)

def test_build_volatility_model_empty_series():
    with pytest.raises(ModelError, match="empty"):
        build_volatility_shift_model(pd.Series([], dtype=float))


def test_build_volatility_model_with_nans():
    s = pd.Series([1.0, 2.0, np.nan, 3.0] * 10)
    with pytest.raises(ModelError, match="NaN"):
        build_volatility_shift_model(s)


def test_build_volatility_model_too_short():
    s = pd.Series(np.random.randn(10))
    with pytest.raises(ModelError, match="only 10"):
        build_volatility_shift_model(s)


def test_build_volatility_model_success():
    s = make_synthetic_series()
    model = build_volatility_shift_model(s)
    var_names = [v.name for v in model.free_RVs]
    assert "tau" in var_names
    assert "mu" in var_names
    assert "sigma_1" in var_names
    assert "sigma_2" in var_names