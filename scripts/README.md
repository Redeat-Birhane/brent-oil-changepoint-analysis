# Task 3: Interactive Dashboard

Flask backend + React frontend for exploring Brent oil price history,
detected change points, and the compiled event dataset.

## Architecture

scripts/
├── export_results.py   # Freezes analysis results into data/processed/*.json
├── backend/
│   ├── app.py           # Flask API
│   └── requirements.txt
└── frontend/
├── src/
│   ├── App.jsx
│   ├── api.js
│   ├── index.css
│   └── components/
│       ├── Filters.jsx
│       ├── PriceChart.jsx
│       └── EventTable.jsx
└── package.json

Data flow: `data/BrentOilPrices.csv` + `data/events.csv` → `export_results.py`
→ `data/processed/*.json` → Flask API → React dashboard.

## Setup

### 1. Export the data (run once, or after any data/notebook update)

From the repo root:
```bash
python scripts/export_results.py
```
This writes `prices.json`, `events.json`, and `change_points.json` to
`data/processed/`. The dashboard reads only these files — it does not
re-run any analysis live.

### 2. Start the backend

```bash
cd scripts/backend
pip install -r requirements.txt
python app.py
```
Runs on `http://localhost:5000`. Verify with:
```bash
curl http://localhost:5000/api/summary
```

### 3. Start the frontend

In a second terminal:
```bash
cd scripts/frontend
npm install
npm run dev
```
Open the printed URL (typically `http://localhost:5173`).

## API Endpoints

| Endpoint | Description | Query params |
|---|---|---|
| `GET /api/health` | Health check | — |
| `GET /api/summary` | Price range, date range, event count | — |
| `GET /api/prices` | Historical price series | `start`, `end` (YYYY-MM-DD) |
| `GET /api/events` | Event dataset | `category`, `start`, `end` |
| `GET /api/changepoints` | Task 2 change point results | — |

## Dashboard Features

- **Price chart** with event dates overlaid as reference lines, colored by category
- **Date range filter** to zoom into any period
- **Category filter chips** to isolate event types (OPEC Policy, Sanctions, etc.)
- **Drill-down table** listing all events in the current filtered view
- Responsive layout — filters panel collapses above the chart on narrow screens

## Screenshots

See `docs/screenshots/` for dashboard views (full history, filtered range, event drill-down).