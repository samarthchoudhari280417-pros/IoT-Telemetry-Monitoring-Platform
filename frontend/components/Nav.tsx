"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/devices", label: "Devices" },
  { href: "/readings", label: "Readings" },
  { href: "/alerts", label: "Alerts" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="flex gap-1 rounded-lg border border-border bg-panel p-1">
      {links.map((l) => {
        const active = pathname === l.href;
        return (
          <Link
            key={l.href}
            href={l.href}
            className={`rounded-md px-3 py-1.5 text-sm transition-colors ${
              active ? "bg-accent/15 text-accent" : "text-muted hover:text-slate-200"
            }`}
          >
            {l.label}
          </Link>
        );
      })}
    </nav>
  );
}
