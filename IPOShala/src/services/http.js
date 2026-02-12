import { API_BASE } from "../config/api";

export async function apiGet(path) {
  const res = await fetch(`${API_BASE}${path}`);

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `API Error: ${res.status}`);
  }

  return res.json();
}
