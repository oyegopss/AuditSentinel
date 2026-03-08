"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent, Button } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type ComponentStatus = "active" | "processing" | "completed" | "error";

type ComponentState = {
  id: string;
  name: string;
  status: ComponentStatus;
  message: string;
  last_check: string;
};

const POLL_INTERVAL_MS = 4000;

const AGENT_ICONS: Record<string, string> = {
  planning_agent: "M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z",
  execution_agent: "M13 10V3L4 14h7v7l9-11h-7z",
  risk_engine: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z",
  blockchain_logger: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1",
  database: "M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4",
};

function statusColor(status: ComponentStatus): string {
  switch (status) {
    case "active": return "bg-emerald-500";
    case "processing": return "bg-primary";
    case "completed": return "bg-emerald-400";
    case "error": return "bg-red-500";
    default: return "bg-[#6B7280]";
  }
}

function statusTextColor(status: ComponentStatus): string {
  switch (status) {
    case "active": return "text-emerald-400";
    case "processing": return "text-primary";
    case "completed": return "text-emerald-300";
    case "error": return "text-red-400";
    default: return "text-[#6B7280]";
  }
}

function formatUptime(startTime: Date): string {
  const now = new Date();
  const diff = Math.floor((now.getTime() - startTime.getTime()) / 1000);
  const h = Math.floor(diff / 3600);
  const m = Math.floor((diff % 3600) / 60);
  const s = diff % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

export function AgentMonitoringPanel() {
  const [components, setComponents] = useState<ComponentState[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uptimeStr, setUptimeStr] = useState("");
  const startTimeRef = useRef(new Date());

  const fetchStatus = useCallback(async () => {
    try {
      const res = await fetch(apiUrl("/agent-status"));
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      setComponents(Array.isArray(data) ? data : []);
      setError(null);
    } catch {
      setError("Backend unreachable. Ensure the API is running.");
      setComponents([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
    const pollId = setInterval(fetchStatus, POLL_INTERVAL_MS);
    const uptimeId = setInterval(() => {
      setUptimeStr(formatUptime(startTimeRef.current));
    }, 1000);
    return () => {
      clearInterval(pollId);
      clearInterval(uptimeId);
    };
  }, [fetchStatus]);

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Agent monitoring</CardTitle>
          <p className="text-[11px] text-[#6B7280] mt-0.5">
            System uptime: <span className="font-mono text-[#9CA3AF]">{uptimeStr || "..."}</span>
          </p>
        </div>
      </CardHeader>
      <CardContent>
        {loading && components.length === 0 && (
          <p className="text-sm text-[#9CA3AF] py-2">Loading...</p>
        )}
        {error && components.length === 0 && (
          <div className="space-y-2 py-2">
            <p className="text-sm text-amber-400">{error}</p>
            <Button
              type="button"
              className="border-primary/20 bg-transparent text-primary hover:bg-primary/[0.06]"
              onClick={() => fetchStatus()}
            >
              Retry
            </Button>
          </div>
        )}
        <div className="grid gap-3 sm:grid-cols-2">
          {components.map((c, i) => {
            const icon = AGENT_ICONS[c.id] || AGENT_ICONS.database;

            return (
              <div
                key={c.id}
                className="flex items-start gap-3 rounded-xl border border-white/[0.06] bg-white/[0.02] px-3.5 py-3 transition-all hover:border-white/[0.1] animate-fade-in"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="relative mt-0.5 flex-shrink-0">
                  <div className={`flex h-8 w-8 items-center justify-center rounded-lg bg-white/[0.04] ${statusTextColor(c.status)}`}>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d={icon} />
                    </svg>
                  </div>
                  <div className={`absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-[#111827] ${statusColor(c.status)} ${c.status === "active" ? "animate-heartbeat" : ""}`} />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-medium text-[#E5E7EB]">
                      {c.name}
                    </span>
                    <span className={`text-[10px] font-medium uppercase tracking-wide ${statusTextColor(c.status)}`}>
                      {c.status}
                    </span>
                  </div>
                  <p className="mt-0.5 text-[11px] text-[#6B7280]">{c.message}</p>
                  <p className="mt-0.5 text-[10px] text-[#6B7280]">
                    Last check: {new Date(c.last_check).toLocaleTimeString(undefined, {
                      hour: "2-digit", minute: "2-digit", second: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
