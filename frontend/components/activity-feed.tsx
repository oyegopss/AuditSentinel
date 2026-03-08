"use client";

import { useEffect, useState, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type ActivityEvent = {
  event: string;
  timestamp: string;
  task_id?: string | null;
};

const POLL_INTERVAL_MS = 3000;

const EVENT_CONFIG: Record<string, { icon: string; color: string; dotColor: string }> = {
  task_submitted: { icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2", color: "text-blue-400", dotColor: "bg-blue-400" },
  risk_detection: { icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z", color: "text-red-400", dotColor: "bg-red-400" },
  awaiting_approval: { icon: "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z", color: "text-amber-400", dotColor: "bg-amber-400" },
  approval: { icon: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z", color: "text-emerald-400", dotColor: "bg-emerald-400" },
  blockchain_transaction: { icon: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1", color: "text-primary", dotColor: "bg-primary" },
};

const DEFAULT_CONFIG = { icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z", color: "text-[#9CA3AF]", dotColor: "bg-[#6B7280]" };

function formatTime(iso: string): string {
  if (!iso) return "\u2014";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString(undefined, {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return iso;
  }
}

export function ActivityFeed() {
  const [events, setEvents] = useState<ActivityEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const prevCountRef = useRef(0);

  const fetchFeed = async () => {
    try {
      const res = await fetch(apiUrl("/activity-feed"));
      if (!res.ok) throw new Error(res.statusText);
      const data = await res.json();
      const items = Array.isArray(data) ? data : [];
      setEvents(items);
      prevCountRef.current = items.length;
      setFetchError(null);
    } catch {
      setFetchError("Unable to load activity. Ensure the API is running.");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
    const id = setInterval(fetchFeed, POLL_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <Card>
      <CardHeader>
        <div>
          <CardTitle>Live governance activity</CardTitle>
          <p className="text-[11px] text-[#6B7280] mt-0.5">
            Real-time events as tasks move through risk checks, approvals, and blockchain logging.
          </p>
        </div>
      </CardHeader>
      <CardContent>
        {loading && events.length === 0 && !fetchError && (
          <p className="text-sm text-[#9CA3AF] py-2">Loading activity...</p>
        )}
        {fetchError && (
          <p className="text-sm text-amber-400 py-2">{fetchError}</p>
        )}
        {!loading && !fetchError && events.length === 0 && (
          <p className="text-sm text-[#9CA3AF] py-2">
            No activity yet. Submit a task or approve an action to see events.
          </p>
        )}
        {events.length > 0 && (
          <div className="relative">
            <div
              className="absolute left-[11px] top-3 bottom-3 w-px bg-white/[0.06]"
              aria-hidden
            />
            <ul className="space-y-0">
              {events.map((evt, idx) => {
                const cfg = EVENT_CONFIG[evt.event] ?? DEFAULT_CONFIG;

                return (
                  <li
                    key={`${evt.timestamp}-${evt.event}-${idx}`}
                    className="relative flex gap-4 pb-4 last:pb-0 animate-slide-in"
                    style={{ animationDelay: `${idx * 50}ms` }}
                  >
                    <div className="relative z-10 mt-0.5 flex-shrink-0">
                      <div className={`flex h-6 w-6 items-center justify-center rounded-full bg-white/[0.04] border border-white/[0.06] ${cfg.color}`}>
                        <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d={cfg.icon} />
                        </svg>
                      </div>
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-baseline gap-2">
                        <span className={`h-1.5 w-1.5 rounded-full ${cfg.dotColor}`} />
                        <span className="text-sm font-medium text-[#E5E7EB]">
                          {evt.event.replace(/_/g, " ")}
                        </span>
                        <span className="text-[11px] text-[#6B7280]">
                          {formatTime(evt.timestamp)}
                        </span>
                      </div>
                      {evt.task_id && (
                        <span className="text-[10px] font-mono text-[#6B7280] truncate max-w-[120px] block mt-0.5">
                          {evt.task_id}
                        </span>
                      )}
                    </div>
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
