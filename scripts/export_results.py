"""
Exports price data, event data, and the Task 2 model interpretation into
static JSON files under data/processed/, so the Flask backend can serve
them instantly without re-running MCMC sampling.

Run manually after any notebook update whose results should reach the
dashboard:
    python scripts/export_results.py
"""
import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_price_data, load_events_data, DataLoadError

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")


def export_prices(df):
    records = [
        {"date": idx.strftime("%Y-%m-%d"), "price": round(float(row["Price"]), 2)}
        for idx, row in df.iterrows()
    ]
    path = os.path.join(OUTPUT_DIR, "prices.json")
    with open(path, "w") as f:
        json.dump(records, f)
    print(f"Wrote {len(records)} price records to {path}")


def export_events(events_df):
    records = [
        {
            "date": row["event_date"].strftime("%Y-%m-%d"),
            "name": row["event_name"],
            "category": row["category"],
            "description": row["description"],
        }
        for _, row in events_df.iterrows()
    ]
    path = os.path.join(OUTPUT_DIR, "events.json")
    with open(path, "w") as f:
        json.dump(records, f, indent=2)
    print(f"Wrote {len(records)} event records to {path}")


def export_change_points():
    """
    Task 2 result, recorded manually from the notebook run rather than
    re-sampled here (MCMC is slow; this file is the single source of
    truth the dashboard reads from — update it if the notebook result
    changes).
    """
    change_points = [
        {
            "model": "mean_shift_full_series",
            "date": "1988-09-12",
            "mu_before": 0.0,
            "mu_before_hdi": [-0.010, 0.007],
            "mu_after": 0.003,
            "mu_after_hdi": [-0.018, 0.021],
            "statistically_significant": False,
            "note": (
                "Overlapping 95% HDIs; no nearby event; consistent with "
                "Task 1 finding that mean log return is stable across the "
                "full history. See docs/assumptions_and_limitations.md."
            ),
        }
    ]
    path = os.path.join(OUTPUT_DIR, "change_points.json")
    with open(path, "w") as f:
        json.dump(change_points, f, indent=2)
    print(f"Wrote {len(change_points)} change point record(s) to {path}")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        df = load_price_data(os.path.join(os.path.dirname(__file__), "..", "data", "BrentOilPrices.csv"))
        events_df = load_events_data(os.path.join(os.path.dirname(__file__), "..", "data", "events.csv"))
    except DataLoadError as e:
        print(f"Export failed: {e}")
        sys.exit(1)

    export_prices(df)
    export_events(events_df)
    export_change_points()


if __name__ == "__main__":
    main()