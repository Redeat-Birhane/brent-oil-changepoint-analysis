const API_BASE = "http://localhost:5000/api";

async function request(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }
  return res.json();
}

export function getSummary() {
  return request("/summary");
}

export function getPrices(start, end) {
  const params = new URLSearchParams();
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  const qs = params.toString();
  return request(`/prices${qs ? `?${qs}` : ""}`);
}

export function getEvents(category, start, end) {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  if (start) params.set("start", start);
  if (end) params.set("end", end);
  const qs = params.toString();
  return request(`/events${qs ? `?${qs}` : ""}`);
}

export function getChangePoints() {
  return request("/changepoints");
}