"""
Core data loading utilities for the Brent oil change point analysis.

Keeping this logic out of notebooks so it can be unit tested and reused
across notebooks, scripts, and the dashboard backend.
"""
import os
import pandas as pd


class DataLoadError(Exception):
    """Raised when input data fails to load or fails validation."""
    pass


def load_price_data(path: str) -> pd.DataFrame:
    """
    Load and validate the Brent oil price series.

    Expects columns: 'Date', 'Price'. Dates may be in mixed formats
    (e.g. '20-May-87' and 'Apr 22, 2020'), so parsing uses format='mixed'.

    Returns a DataFrame indexed by Date, sorted chronologically, with
    an added 'log_price' and 'log_return' column.

    Raises:
        DataLoadError: if the file is missing, unreadable, missing
            required columns, or dates/prices fail to parse.
    """
    if not os.path.exists(path):
        raise DataLoadError(f"Price data file not found at: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise DataLoadError(f"Failed to read CSV at {path}: {e}")

    required_cols = {"Date", "Price"}
    missing = required_cols - set(df.columns)
    if missing:
        raise DataLoadError(f"Price data is missing required column(s): {missing}")

    try:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", dayfirst=True)
    except Exception as e:
        raise DataLoadError(f"Failed to parse 'Date' column: {e}")

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    n_bad_prices = df["Price"].isna().sum()
    if n_bad_prices > 0:
        raise DataLoadError(
            f"{n_bad_prices} row(s) have non-numeric or missing 'Price' values."
        )

    df = df.sort_values("Date").reset_index(drop=True)
    df.set_index("Date", inplace=True)

    if df.index.duplicated().any():
        n_dupes = df.index.duplicated().sum()
        raise DataLoadError(f"Found {n_dupes} duplicate date(s) in price data.")

    df["log_price"] = df["Price"].apply(lambda x: pd.NA if x <= 0 else x).astype(float)
    import numpy as np
    df["log_price"] = np.log(df["Price"])
    df["log_return"] = df["log_price"].diff()

    return df


def load_events_data(path: str) -> pd.DataFrame:
    """
    Load and validate the compiled events dataset used to interpret
    detected change points.

    Expects columns: 'event_date', 'event_name', 'category', 'description'.

    Raises:
        DataLoadError: if the file is missing, unreadable, missing
            required columns, has too few events, or dates fail to parse.
    """
    if not os.path.exists(path):
        raise DataLoadError(f"Events data file not found at: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise DataLoadError(f"Failed to read CSV at {path}: {e}")

    required_cols = {"event_date", "event_name", "category", "description"}
    missing = required_cols - set(df.columns)
    if missing:
        raise DataLoadError(f"Events data is missing required column(s): {missing}")

    try:
        df["event_date"] = pd.to_datetime(df["event_date"], format="%Y-%m-%d")
    except Exception as e:
        raise DataLoadError(f"Failed to parse 'event_date' column: {e}")

    if len(df) < 10:
        raise DataLoadError(
            f"Events dataset has only {len(df)} rows; at least 10 are required."
        )

    df = df.sort_values("event_date").reset_index(drop=True)
    return df


def get_events_in_range(events_df: pd.DataFrame, start, end) -> pd.DataFrame:
    """Return events whose event_date falls within [start, end]."""
    start, end = pd.to_datetime(start), pd.to_datetime(end)
    return events_df[
        (events_df["event_date"] >= start) & (events_df["event_date"] <= end)
    ].reset_index(drop=True)