"use client";
import { useEffect, useState } from "react";
import { api, Device, pollInterval } from "@/lib/api";
import StatusBadge from "@/components/StatusBadge";

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function tick() {
      try {
        const data = await api.devices();
        if (!cancelled) {
          setDevices(data);
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
      <h2 className="text-lg font-medium">Devices</h2>
      {error && <div className="text-sm text-danger">{error}</div>}
      <div className="grid gap-4 md:grid-cols-2">
        {devices.map((d) => (
          <div key={d.device_id} className="rounded-xl border border-border bg-panel p-4">
            <div className="flex items-start justify-between">
              <div>
                <div className="font-medium">{d.name ?? d.device_id}</div>
                <div className="text-xs text-muted">{d.device_id}</div>
              </div>
              <StatusBadge status={d.status} />
            </div>
            <div className="mt-3 text-sm text-muted">
              {d.location && <div>Location: {d.location}</div>}
              <div>
                Last seen:{" "}
                {d.last_seen ? new Date(d.last_seen).toLocaleString() : "never"}
              </div>
            </div>
          </div>
        ))}
        {devices.length === 0 && !error && (
          <div className="text-sm text-muted">No devices reporting yet.</div>
        )}
      </div>
    </div>
  );
}
