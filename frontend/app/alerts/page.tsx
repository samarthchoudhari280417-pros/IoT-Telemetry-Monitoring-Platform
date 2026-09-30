"use client";
import { useEffect, useState } from "react";
import { api, Alert, pollInterval } from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const data = await api.alerts();
        if (!cancelled) {
          setAlerts(data);
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
      <h2 className="text-lg font-medium">Alerts</h2>
      {error && <div className="text-sm text-danger">{error}</div>}
      <div className="space-y-2">
        {alerts.map((a) => (
          <div
            key={a.id}
            className="flex items-center justify-between rounded-xl border border-danger/30 bg-danger/5 px-4 py-3"
          >
            <div>
              <div className="text-sm font-medium text-slate-100">{a.message}</div>
              <div className="text-xs text-muted">
                {a.device_id} · {new Date(a.timestamp).toLocaleString()}
              </div>
            </div>
            <div className="text-sm font-semibold text-danger">{a.power.toFixed(0)} W</div>
          </div>
        ))}
        {alerts.length === 0 && !error && (
          <div className="text-sm text-muted">No alerts triggered.</div>
        )}
      </div>
    </div>
  );
}
