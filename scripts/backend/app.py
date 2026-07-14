"""
Flask backend serving Brent oil price, event, and change point data to the
React dashboard.
"""
import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed")


def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/prices")
def get_prices():
    """
    Historical price data, optionally filtered by date range.
    Query params: start=YYYY-MM-DD, end=YYYY-MM-DD
    """
    prices = load_json("prices.json")
    if prices is None:
        return jsonify({"error": "Price data not found. Run scripts/export_results.py first."}), 404

    start = request.args.get("start")
    end = request.args.get("end")

    if start:
        prices = [p for p in prices if p["date"] >= start]
    if end:
        prices = [p for p in prices if p["date"] <= end]

    return jsonify({"count": len(prices), "data": prices})


@app.route("/api/events")
def get_events():
    """
    Event dataset, optionally filtered by category or date range.
    Query params: category=<name>, start=YYYY-MM-DD, end=YYYY-MM-DD
    """
    events = load_json("events.json")
    if events is None:
        return jsonify({"error": "Event data not found. Run scripts/export_results.py first."}), 404

    category = request.args.get("category")
    start = request.args.get("start")
    end = request.args.get("end")

    if category:
        events = [e for e in events if e["category"].lower() == category.lower()]
    if start:
        events = [e for e in events if e["date"] >= start]
    if end:
        events = [e for e in events if e["date"] <= end]

    return jsonify({"count": len(events), "data": events})


@app.route("/api/changepoints")
def get_change_points():
    """Detected change point(s) from the Task 2 analysis."""
    change_points = load_json("change_points.json")
    if change_points is None:
        return jsonify({"error": "Change point data not found. Run scripts/export_results.py first."}), 404

    return jsonify({"count": len(change_points), "data": change_points})


@app.route("/api/summary")
def get_summary():
    """Combined summary: latest price, price range, event count — for a dashboard header."""
    prices = load_json("prices.json")
    events = load_json("events.json")

    if prices is None or events is None:
        return jsonify({"error": "Data not found. Run scripts/export_results.py first."}), 404

    price_values = [p["price"] for p in prices]

    return jsonify({
        "date_range": {"start": prices[0]["date"], "end": prices[-1]["date"]},
        "price_range": {"min": min(price_values), "max": max(price_values)},
        "total_price_points": len(prices),
        "total_events": len(events),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)