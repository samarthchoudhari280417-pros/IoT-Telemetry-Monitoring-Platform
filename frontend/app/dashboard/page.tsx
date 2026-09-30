"use client";
import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { api, Analytics, DailyPoint, Device, LatestReading, pollInterval } from "@/lib/api";
import StatCard from "@/components/StatCard";
import StatusBadge from "@/components/StatusBadge";

const DEFAULT_DEVICE = "esp32-energy-01";

export default function DashboardPage() {
  const [device, setDevice] = useState<Device | null>(null);
  const [latest, setLatest] = useState<LatestReading | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [daily, setDaily] = useState<DailyPoint[]>([]);
  const [powerHistory, setPowerHistory] = useState<{ time: string; power: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function tick() {
      try {
        const [devices, latestReading, analyticsData, dailyData] = await Promise.all([
          api.devices(),
          api.latestReading(DEFAULT_DEVICE).catch(() => null),
          api.analytics(DEFAULT_DEVICE).catch(() => null),
          api.dailyEnergy(DEFAULT_DEVICE, 14).catch(() => []),
        ]);
        if (cancelled) return;

        setDevice(devices.find((d) => d.device_id === DEFAULT_DEVICE) ?? devices[0] ?? null);
        setLatest(latestReading);
        setAnalytics(analyticsData);
        setDaily(dailyData);
        setError(null);

        if (latestReading) {
          setPowerHistory((prev) => {
            const next = [
              ...prev,
              {
                time: new Date(latestReading.timestamp).toLocaleTimeString(),
                power: latestReading.power,
              },
            ];
            return next.slice(-30); // keep last 30 points
          });
        }
      } catch (e) {
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
    <div className="space-y-6">
      {error && (
        <div className="rounded-lg border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error} Make sure the backend is running and NEXT_PUBLIC_API_URL is correct.
        </div>
      )}

      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-medium">{device?.name ?? device?.device_id ?? "No device yet"}</div>
          <div className="text-sm text-muted">
            {device?.last_seen ? `Last seen ${new Date(device.last_seen).toLocaleTimeString()}` : "Waiting for readings..."}
          </div>
        </div>
        {device && <StatusBadge status={device.status} />}
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard label="Current Power" value={analytics?.current_power_w ?? "--"} unit="W" accent />
        <StatCard label="Today" value={analytics ? (analytics.today_energy_wh / 1000).toFixed(2) : "--"} unit="kWh" />
        <StatCard label="This Month" value={analytics ? (analytics.month_energy_wh / 1000).toFixed(2) : "--"} unit="kWh" />
        <StatCard label="Average Power" value={analytics?.average_power_w ?? "--"} unit="W" />
        <StatCard label="Peak Power" value={analytics?.peak_power_w ?? "--"} unit="W" />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-border bg-panel p-4">
          <div className="mb-3 text-sm font-medium text-muted">Power usage over time</div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={powerHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232b36" />
              <XAxis dataKey="time" stroke="#8a97a6" fontSize={11} />
              <YAxis stroke="#8a97a6" fontSize={11} unit="W" />
              <Tooltip contentStyle={{ background: "#121820", border: "1px solid #232b36" }} />
              <Line type="monotone" dataKey="power" stroke="#3ddc97" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-xl border border-border bg-panel p-4">
          <div className="mb-3 text-sm font-medium text-muted">Daily energy consumption</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={daily}>
              <CartesianGrid strokeDasharray="3 3" stroke="#232b36" />
              <XAxis dataKey="date" stroke="#8a97a6" fontSize={11} />
              <YAxis stroke="#8a97a6" fontSize={11} unit="Wh" />
              <Tooltip contentStyle={{ background: "#121820", border: "1px solid #232b36" }} />
              <Bar dataKey="energy_wh" fill="#3ddc97" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl border border-border bg-panel p-4">
        <div className="mb-3 text-sm font-medium text-muted">Latest Reading</div>
        {latest ? (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-muted">
                <th className="pb-2 font-normal">Time</th>
                <th className="pb-2 font-normal">Voltage</th>
                <th className="pb-2 font-normal">Current</th>
                <th className="pb-2 font-normal">Power</th>
                <th className="pb-2 font-normal">Session Energy</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-t border-border">
                <td className="py-2">{new Date(latest.timestamp).toLocaleTimeString()}</td>
                <td className="py-2">{latest.voltage.toFixed(1)} V</td>
                <td className="py-2">{latest.current.toFixed(2)} A</td>
                <td className="py-2">{latest.power.toFixed(1)} W</td>
                <td className="py-2">{latest.energy_wh.toFixed(2)} Wh</td>
              </tr>
            </tbody>
          </table>
        ) : (
          <div className="text-sm text-muted">No readings yet.</div>
        )}
      </div>
    </div>
  );
}
