"use client";

import { useEffect, useState } from "react";
import { apiUrl } from "@/lib/api";

type Metrics = {
  total_tasks: number;
  high_risk_tasks: number;
  human_interventions: number;
  blockchain_verified: number;
};

const METRIC_CARDS: {
  key: keyof Metrics;
  label: string;
  desc: string;
  icon: string;
  color: string;
}[] = [
  {
    key: "total_tasks",
    label: "Total AI Tasks",
    desc: "Tasks processed by agents",
    icon: "M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4",
    color: "text-blue-400",
  },
  {
    key: "high_risk_tasks",
    label: "High Risk Tasks",
    desc: "Critical + high severity",
    icon: "M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z",
    color: "text-red-400",
  },
  {
    key: "human_interventions",
    label: "Human Interventions",
    desc: "Approved or rejected actions",
    icon: "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z",
    color: "text-amber-400",
  },
  {
    key: "blockchain_verified",
    label: "Blockchain Verified",
    desc: "On-chain audit records",
    icon: "M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1",
    color: "text-emerald-400",
  },
];

export function MetricsStrip() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(apiUrl("/dashboard-metrics"));
        if (!res.ok) return;
        const data = await res.json();
        setMetrics(data.metrics);
      } catch {
        /* ignore */
      }
    };
    load();
    const id = setInterval(load, 8000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {METRIC_CARDS.map((card, i) => (
        <div
          key={card.key}
          className={`group relative overflow-hidden rounded-2xl border border-white/[0.08] bg-[#111827] p-5 shadow-card transition-all duration-300 hover:shadow-glow hover:border-primary/20 opacity-0 animate-fade-in`}
          style={{ animationDelay: `${i * 80}ms`, animationFillMode: "forwards" }}
        >
          <div className="flex items-start justify-between">
            <div className="space-y-1">
              <p className="text-[11px] font-medium uppercase tracking-wider text-[#9CA3AF]">
                {card.label}
              </p>
              <p className="text-3xl font-bold tabular-nums text-[#E5E7EB]">
                {metrics ? metrics[card.key] : "—"}
              </p>
              <p className="text-[11px] text-[#6B7280]">{card.desc}</p>
            </div>
            <div className={`rounded-xl bg-white/[0.04] p-2.5 ${card.color}`}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={card.icon} />
              </svg>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
