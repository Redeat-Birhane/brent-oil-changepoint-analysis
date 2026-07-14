import { CATEGORY_COLORS } from "./Filters";

export default function EventTable({ events, selectedEvent }) {
  return (
    <div className="panel">
      <h3 className="panel-title">Events in range ({events.length})</h3>
      {events.length === 0 ? (
        <div className="status-msg">No events match the current filters.</div>
      ) : (
        <table className="event-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Event</th>
              <th>Category</th>
              <th>Description</th>
            </tr>
          </thead>
          <tbody>
            {events.map((e) => (
              <tr
                key={e.date}
                style={selectedEvent?.date === e.date ? { background: "#212936" } : undefined}
              >
                <td className="event-date">{e.date}</td>
                <td>{e.name}</td>
                <td>
                  <span
                    className="category-tag"
                    style={{ color: CATEGORY_COLORS[e.category] || "#8B93A1" }}
                  >
                    {e.category}
                  </span>
                </td>
                <td style={{ color: "#8B93A1" }}>{e.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}