"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { clsx } from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Task submission", icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" },
  { href: "/decision", label: "AI decision viewer", icon: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" },
  { href: "/approve", label: "Human approval panel", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
  { href: "/audit-logs", label: "Blockchain audit logs", icon: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" },
  { href: "/governance", label: "Governance score", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { href: "/monitoring", label: "Agent monitoring", icon: "M5.636 18.364a9 9 0 010-12.728m12.728 0a9 9 0 010 12.728m-9.9-2.829a5 5 0 010-7.07m7.072 0a5 5 0 010 7.07M13 12a1 1 0 11-2 0 1 1 0 012 0z" },
  { href: "/analytics", label: "Risk analytics", icon: "M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" },
];

export function Sidebar() {
  const pathname = usePathname();
  const path = (pathname ?? "").replace(/\/$/, "") || "/";

  return (
    <aside className="w-72 shrink-0 border-r border-white/[0.06] bg-[#0D1117]">
      <div className="border-b border-white/[0.06] px-7 py-7">
        <div className="font-semibold tracking-[0.18em] text-[11px] uppercase text-primary/70">
          Enterprise AI Governance
        </div>
        <div className="mt-2 text-2xl font-semibold tracking-tight text-[#E5E7EB]">
          Audit<span className="text-primary">Sentinel</span>
        </div>
        <p className="mt-2 max-w-[180px] text-xs leading-5 text-[#9CA3AF]">
          Risk-aware operations, approvals, and blockchain-backed auditability.
        </p>
      </div>

      <nav className="px-4 py-5">
        <div className="mb-3 px-3 text-[10px] font-medium uppercase tracking-[0.24em] text-[#6B7280]">
          Navigation
        </div>
        <div className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const active =
              path === item.href ||
              (item.href === "/dashboard" && (path === "/" || path === "/dashboard" || path.startsWith("/dashboard/"))) ||
              (item.href !== "/dashboard" && (path.startsWith(item.href) || path === item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "group relative flex items-center gap-3 rounded-xl border px-3.5 py-2.5 text-sm transition-all duration-200",
                  active
                    ? "border-primary/20 bg-primary/[0.06] text-primary shadow-[0_0_20px_rgba(245,197,66,0.06)]"
                    : "border-transparent text-[#9CA3AF] hover:border-white/[0.06] hover:bg-white/[0.03] hover:text-[#E5E7EB]"
                )}
              >
                <svg
                  className={clsx(
                    "h-4 w-4 flex-shrink-0 transition-colors",
                    active ? "text-primary" : "text-[#6B7280] group-hover:text-[#9CA3AF]"
                  )}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={1.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d={item.icon} />
                </svg>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </aside>
  );
}
