import {
  ResponsiveContainer, AreaChart, Area, XAxis, YAxis,
  CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import { CATEGORY_COLORS } from "./Filters";

function CustomTooltip({ active, payload, label, eventsByDate }) {
  if (!active || !payload || !payload.length) return null;
  const price = payload[0].value;
  const event = eventsByDate[label];

  return (
    <div className="tooltip-box">
      <div className="tooltip-date">{label}</div>
      <div className="tooltip-price">${price.toFixed(2)}/bbl</div>
      {event && <div className="tooltip-event">⚠ {event.name}</div>}
    </div>
  );
}

export default function PriceChart({ prices, events, onEventClick }) {
  const eventsByDate = {};
  events.forEach((e) => { eventsByDate[e.date] = e; });

  // Downsample for render performance on the full ~9,000-point history
  const step = Math.max(1, Math.floor(prices.length / 1500));
  const sampled = prices.filter((_, i) => i % step === 0);

  return (
    <div className="panel chart-panel">
      <h3 className="panel-title">
        Brent Crude Price {events.length > 0 && `— ${events.length} event(s) highlighted`}
      </h3>
      <ResponsiveContainer width="100%" height={380}>
        <AreaChart data={sampled} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#E8974A" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#E8974A" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#2A3341" strokeDasharray="3 3" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "#5A6272", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            tickFormatter={(d) => d.slice(0, 4)}
            minTickGap={60}
            axisLine={{ stroke: "#2A3341" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#5A6272", fontSize: 11, fontFamily: "IBM Plex Mono" }}
            tickFormatter={(v) => `$${v}`}
            axisLine={false}
            tickLine={false}
            width={50}
          />
          <Tooltip content={<CustomTooltip eventsByDate={eventsByDate} />} />
          <Area
            type="monotone"
            dataKey="price"
            stroke="#E8974A"
            strokeWidth={1.5}
            fill="url(#priceFill)"
          />
          {events.map((e) => (
            <ReferenceLine
              key={e.date}
              x={e.date}
              stroke={CATEGORY_COLORS[e.category] || "#8B93A1"}
              strokeDasharray="2 3"
              strokeOpacity={0.7}
              onClick={() => onEventClick(e)}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}