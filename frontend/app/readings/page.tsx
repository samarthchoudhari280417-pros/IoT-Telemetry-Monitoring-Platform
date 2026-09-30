"use client";
import { useEffect, useState } from "react";
import { api, Reading, pollInterval } from "@/lib/api";

export default function ReadingsPage() {
  const [readings, setReadings] = useState<Reading[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const data = await api.readings(undefined, 50);
        if (!cancelled) {
          setReadings(data);
          setError(null);
        }
      } catch {
        if (!cancelled) setError("Could not reach the backend API.");
      }
    }
    tick();
    const id = setInterval(tick, pollInterval());
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-medium">Recent Readings</h2>
      {error && <div className="text-sm text-danger">{error}</div>}
      <div className="overflow-hidden rounded-xl border border-border bg-panel">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-muted">
              <th className="px-4 py-2 font-normal">Device</th>
              <th className="px-4 py-2 font-normal">Time</th>
              <th className="px-4 py-2 font-normal">Voltage</th>
              <th className="px-4 py-2 font-normal">Current</th>
              <th className="px-4 py-2 font-normal">Power</th>
              <th className="px-4 py-2 font-normal">Energy</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((r) => (
              <tr key={r.id} className="border-b border-border/50 last:border-0">
                <td className="px-4 py-2">{r.device_id}</td>
                <td className="px-4 py-2">{new Date(r.timestamp).toLocaleTimeString()}</td>
                <td className="px-4 py-2">{r.voltage.toFixed(1)} V</td>
                <td className="px-4 py-2">{r.current.toFixed(2)} A</td>
                <td className="px-4 py-2">{r.power.toFixed(1)} W</td>
                <td className="px-4 py-2">{r.energy_wh.toFixed(2)} Wh</td>
              </tr>
            ))}
          </tbody>
        </table>
        {readings.length === 0 && !error && (
          <div className="px-4 py-6 text-sm text-muted">No readings yet.</div>
        )}
      </div>
    </div>
  );
}
