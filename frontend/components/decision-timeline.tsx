"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type TimelineEvent = {
  event_type: string;
  timestamp: string;
  status: string;
  task_id: string | null;
  summary: string;
  extra?: Record<string, unknown> | null;
};

const EVENT_LABELS: Record<string, string> = {
  task_submitted: "Task submitted",
  ai_decision: "AI decision generated",
  risk_detection: "Risk detection",
  human_approval_request: "Human approval request",
  approval_decision: "Approval decision",
  human_approval: "Approval decision",
  blockchain_logging: "Blockchain logging",
};

const EVENT_COLORS: Record<string, string> = {
  task_submitted: "bg-blue-500",
  ai_decision: "bg-primary",
  risk_detection: "bg-amber-500",
  human_approval_request: "bg-orange-500",
  approval_decision: "bg-emerald-500",
  human_approval: "bg-emerald-500",
  blockchain_logging: "bg-primary",
};

function formatTime(iso: string): string {
  if (!iso) return "\u2014";
  try {
    const d = new Date(iso);
    return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return iso;
  }
}

export function DecisionTimeline() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTimeline = async () => {
      setLoading(true);
      try {
        const res = await fetch(apiUrl("/decision-timeline"));
        const data = await res.json();
        setEvents(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchTimeline();
  }, []);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Decision timeline</CardTitle>
        <p className="text-[11px] text-[#6B7280]">Chronological events for each AI task</p>
      </CardHeader>
      <CardContent>
        {loading && <p className="text-sm text-[#9CA3AF] py-4">Loading timeline...</p>}
        {!loading && events.length === 0 && (
          <p className="text-sm text-[#9CA3AF] py-4">No events yet. Submit a task or approve an action to see the timeline.</p>
        )}
        {!loading && events.length > 0 && (
          <div className="relative">
            <div className="absolute left-[11px] top-2 bottom-2 w-px bg-white/[0.06]" aria-hidden />
            <ul className="space-y-0">
              {events.map((evt, i) => (
                <li key={`${evt.timestamp}-${evt.event_type}-${i}`} className="relative flex gap-4 pb-6 last:pb-0 animate-slide-in" style={{ animationDelay: `${i * 50}ms` }}>
                  <div className={`relative z-10 flex-shrink-0 w-6 h-6 rounded-full border-2 border-[#0B0F19] ${EVENT_COLORS[evt.event_type] ?? "bg-[#6B7280]"}`} />
                  <div className="min-w-0 flex-1 pt-0.5">
                    <div className="flex flex-wrap items-baseline gap-2">
                      <span className="text-sm font-medium text-[#E5E7EB]">{EVENT_LABELS[evt.event_type] ?? evt.event_type}</span>
                      <span className="text-[11px] text-[#6B7280]">{formatTime(evt.timestamp)}</span>
                      <span className="text-[11px] text-[#9CA3AF] capitalize">{evt.status}</span>
                    </div>
                    {evt.extra && Object.keys(evt.extra).length > 0 && (
                      <div className="mt-1 text-xs text-[#9CA3AF] space-y-0.5">
                        {"risk" in evt.extra && <span className="mr-2">Risk: {String(evt.extra.risk)}</span>}
                        {"output" in evt.extra && <p className="line-clamp-2 text-[#6B7280]">{String(evt.extra.output)}</p>}
                        {"tx_hash" in evt.extra && (
                          <a
                            href={`https://amoy.polygonscan.com/tx/${evt.extra.tx_hash}`}
                            target="_blank"
                            rel="noreferrer"
                            className="font-mono text-primary hover:text-hover hover:underline"
                          >
                            {String(evt.extra.tx_hash).slice(0, 18)}...
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
