// Thin client for the FastAPI backend. Reads polling every few seconds keep
// this simple (no WebSockets) per the project's "keep it simple" goal.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Device {
  device_id: string;
  name: string | null;
  location: string | null;
  last_seen: string | null;
  status: "online" | "offline";
}

export interface Reading {
  id: number;
  device_id: string;
  timestamp: string;
  voltage: number;
  current: number;
  power: number;
  energy_wh: number;
}

export interface LatestReading extends Reading {
  device_status: string;
}

export interface Analytics {
  device_id: string;
  current_power_w: number;
  today_energy_wh: number;
  month_energy_wh: number;
  average_power_w: number;
  peak_power_w: number;
}

export interface DailyPoint {
  date: string;
  energy_wh: number;
}

export interface Alert {
  id: number;
  device_id: string;
  timestamp: string;
  power: number;
  threshold: number;
  message: string;
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`API request failed: ${path} (${res.status})`);
  }
  return res.json();
}

export const api = {
  devices: () => fetchJson<Device[]>("/api/v1/devices"),
  device: (id: string) => fetchJson<Device>(`/api/v1/devices/${id}`),
  latestReading: (deviceId?: string) =>
    fetchJson<LatestReading>(`/api/v1/readings/latest${deviceId ? `?device_id=${deviceId}` : ""}`),
  readings: (deviceId?: string, limit = 50) =>
    fetchJson<Reading[]>(
      `/api/v1/readings?limit=${limit}${deviceId ? `&device_id=${deviceId}` : ""}`
    ),
  dailyEnergy: (deviceId: string, days = 30) =>
    fetchJson<DailyPoint[]>(`/api/v1/readings/daily?device_id=${deviceId}&days=${days}`),
  monthlyEnergy: (deviceId: string, months = 12) =>
    fetchJson<{ month: string; energy_wh: number }[]>(
      `/api/v1/readings/monthly?device_id=${deviceId}&months=${months}`
    ),
  analytics: (deviceId: string) => fetchJson<Analytics>(`/api/v1/analytics?device_id=${deviceId}`),
  alerts: (deviceId?: string, limit = 50) =>
    fetchJson<Alert[]>(`/api/v1/alerts?limit=${limit}${deviceId ? `&device_id=${deviceId}` : ""}`),
};

/** Poll a fetcher every `intervalMs` (default 5s), returning the latest value + error state. */
export function pollInterval() {
  return 5000;
}
