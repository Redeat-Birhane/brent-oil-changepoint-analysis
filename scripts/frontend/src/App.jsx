import { useState, useEffect, useMemo } from "react";
import { getSummary, getPrices, getEvents } from "./api";
import Filters from "./components/Filters";
import PriceChart from "./components/PriceChart";
import EventTable from "./components/EventTable";
import "./index.css";

const ALL_CATEGORIES = [
  "Geopolitical Conflict", "Economic Shock", "OPEC Policy",
  "Sanctions", "Geopolitical Shock", "Market Extreme",
];

export default function App() {
  const [summary, setSummary] = useState(null);
  const [prices, setPrices] = useState([]);
  const [events, setEvents] = useState([]);
  const [startDate, setStartDate] = useState("1987-05-20");
  const [endDate, setEndDate] = useState("2022-09-30");
  const [activeCategories, setActiveCategories] = useState(ALL_CATEGORIES);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSummary().then(setSummary).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      getPrices(startDate, endDate),
      getEvents(null, startDate, endDate),
    ])
      .then(([priceRes, eventRes]) => {
        setPrices(priceRes.data);
        setEvents(eventRes.data);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [startDate, endDate]);

  const filteredEvents = useMemo(
    () => events.filter((e) => activeCategories.includes(e.category)),
    [events, activeCategories]
  );

  function handleDateChange(newStart, newEnd) {
    setStartDate(newStart);
    setEndDate(newEnd);
  }

  function toggleCategory(cat) {
    setActiveCategories((prev) =>
      prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1 className="header-title">
            Brent Crude <span className="accent">Change Point</span> Explorer
          </h1>
          <div className="header-subtitle">
            Birhan Energies — historical price analysis, 1987–2022
          </div>
        </div>
        {summary && (
          <div className="stat-row">
            <div className="stat">
              <span className="stat-label">Range</span>
              <span className="stat-value">
                ${summary.price_range.min} – ${summary.price_range.max}
              </span>
            </div>
            <div className="stat">
              <span className="stat-label">Data points</span>
              <span className="stat-value">{summary.total_price_points.toLocaleString()}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Events tracked</span>
              <span className="stat-value">{summary.total_events}</span>
            </div>
          </div>
        )}
      </header>

      {error && <div className="status-msg error">Error: {error}. Is the Flask backend running on port 5000?</div>}

      <div className="grid">
        <Filters
          startDate={startDate}
          endDate={endDate}
          onDateChange={handleDateChange}
          categories={ALL_CATEGORIES}
          activeCategories={activeCategories}
          onToggleCategory={toggleCategory}
        />

        <div>
          {loading ? (
            <div className="panel status-msg">Loading price data…</div>
          ) : (
            <PriceChart
              prices={prices}
              events={filteredEvents}
              onEventClick={setSelectedEvent}
            />
          )}

          <div style={{ marginTop: 20 }}>
            <EventTable events={filteredEvents} selectedEvent={selectedEvent} />
          </div>
        </div>
      </div>
    </div>
  );
}