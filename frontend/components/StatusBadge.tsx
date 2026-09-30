export default function StatusBadge({ status }: { status: string }) {
  const online = status === "online";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
        online ? "bg-accent/15 text-accent" : "bg-danger/15 text-danger"
      }`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-accent" : "bg-danger"}`} />
      {online ? "Online" : "Offline"}
    </span>
  );
}
