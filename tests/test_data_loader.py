import os
import tempfile
import pandas as pd
import pytest

from src.data_loader import load_price_data, load_events_data, get_events_in_range, DataLoadError


# ---------- Fixtures ----------

@pytest.fixture
def valid_price_csv(tmp_path):
    path = tmp_path / "prices.csv"
    df = pd.DataFrame({
        "Date": ["20-May-87", "21-May-87", "Apr 22, 2020"],
        "Price": [18.63, 18.45, 25.10],
    })
    df.to_csv(path, index=False)
    return str(path)


@pytest.fixture
def valid_events_csv(tmp_path):
    path = tmp_path / "events.csv"
    years = range(1990, 2002)  # 1990-2001, 12 rows, enough to pass the >=10 check
    rows = [
        {"event_date": f"{year}-01-01", "event_name": f"Event {year}",
         "category": "OPEC Policy", "description": "desc"}
        for year in years
    ]
    pd.DataFrame(rows).to_csv(path, index=False)
    return str(path)


# ---------- load_price_data ----------

def test_load_price_data_missing_file():
    with pytest.raises(DataLoadError, match="not found"):
        load_price_data("does/not/exist.csv")


def test_load_price_data_missing_column(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"Date": ["20-May-87"]}).to_csv(path, index=False)
    with pytest.raises(DataLoadError, match="missing required column"):
        load_price_data(str(path))


def test_load_price_data_bad_price_values(tmp_path):
    path = tmp_path / "bad_price.csv"
    pd.DataFrame({"Date": ["20-May-87", "21-May-87"], "Price": [18.63, "not_a_number"]}).to_csv(path, index=False)
    with pytest.raises(DataLoadError, match="non-numeric"):
        load_price_data(str(path))


def test_load_price_data_success(valid_price_csv):
    df = load_price_data(valid_price_csv)
    assert list(df.columns) >= ["Price", "log_price", "log_return"]
    assert df.index.is_monotonic_increasing
    assert pd.isna(df["log_return"].iloc[0])  # first row has no prior day


def test_load_price_data_duplicate_dates(tmp_path):
    path = tmp_path / "dupes.csv"
    pd.DataFrame({"Date": ["20-May-87", "20-May-87"], "Price": [18.63, 18.70]}).to_csv(path, index=False)
    with pytest.raises(DataLoadError, match="duplicate date"):
        load_price_data(str(path))


# ---------- load_events_data ----------

def test_load_events_data_missing_file():
    with pytest.raises(DataLoadError, match="not found"):
        load_events_data("does/not/exist.csv")


def test_load_events_data_too_few_rows(tmp_path):
    path = tmp_path / "few_events.csv"
    pd.DataFrame({
        "event_date": ["2020-01-01"], "event_name": ["X"],
        "category": ["Y"], "description": ["Z"],
    }).to_csv(path, index=False)
    with pytest.raises(DataLoadError, match="at least 10"):
        load_events_data(str(path))


def test_load_events_data_success(valid_events_csv):
    df = load_events_data(valid_events_csv)
    assert len(df) >= 10
    assert df["event_date"].is_monotonic_increasing


# ---------- get_events_in_range ----------

def test_get_events_in_range(valid_events_csv):
    df = load_events_data(valid_events_csv)
    subset = get_events_in_range(df, "1990-01-01", "1995-01-01")
    assert (subset["event_date"] <= pd.Timestamp("1995-01-01")).all()
    assert (subset["event_date"] >= pd.Timestamp("1990-01-01")).all()