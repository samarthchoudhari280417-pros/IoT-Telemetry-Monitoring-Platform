import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "Smart Energy Monitor",
  description: "Real-time ESP32 energy monitoring dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-bg text-slate-100">
        <div className="mx-auto max-w-6xl px-4 py-6">
          <header className="mb-6 flex items-center justify-between">
            <h1 className="text-xl font-semibold tracking-tight">
              ⚡ Smart Energy Monitor
            </h1>
            <Nav />
          </header>
          {children}
        </div>
      </body>
    </html>
  );
}
