"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Badge } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type GovernanceScore = {
  governance_score: number;
  total_tasks: number;
  high_risk_tasks: number;
  rejected_actions: number;
};

const SIZE = 96;
const STROKE = 8;
const RADIUS = (SIZE - STROKE) / 2;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

export function GovernanceScoreCard() {
  const [data, setData] = useState<GovernanceScore | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchScore = async () => {
      setLoading(true);
      try {
        const res = await fetch(apiUrl("/governance-score"));
        const json = await res.json();
        setData(json);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchScore();
  }, []);

  const score = data?.governance_score ?? 50;
  const pct = Math.max(0, Math.min(100, score));
  const strokeDashoffset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;

  const strokeColor =
    pct >= 85 ? "stroke-primary" : pct >= 65 ? "stroke-amber-400" : pct >= 40 ? "stroke-orange-400" : "stroke-red-400";

  return (
    <Card>
      <CardHeader>
        <div className="space-y-1">
          <CardTitle>AI governance score</CardTitle>
          <p className="text-[11px] text-[#6B7280] max-w-xs">
            Score (0-100) from high-risk actions, rejected decisions, and on-chain logs.
          </p>
        </div>
        <Badge>{loading ? "loading..." : "live"}</Badge>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-6">
          <div className="relative flex-shrink-0" style={{ width: SIZE, height: SIZE }}>
            <svg width={SIZE} height={SIZE} className="-rotate-90" aria-hidden>
              <circle cx={SIZE / 2} cy={SIZE / 2} r={RADIUS} fill="none" strokeWidth={STROKE} className="stroke-white/[0.06]" />
              <circle
                cx={SIZE / 2} cy={SIZE / 2} r={RADIUS} fill="none"
                strokeWidth={STROKE} strokeLinecap="round"
                strokeDasharray={CIRCUMFERENCE} strokeDashoffset={strokeDashoffset}
                className={`transition-[stroke-dashoffset] duration-700 ${strokeColor}`}
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-xl font-semibold tabular-nums text-primary">{pct}</span>
              <span className="text-[10px] text-[#6B7280] uppercase tracking-wide">/ 100</span>
            </div>
          </div>
          <div className="space-y-1.5 text-xs min-w-0">
            {[
              { label: "Total tasks", value: data?.total_tasks ?? 0 },
              { label: "High-risk tasks", value: data?.high_risk_tasks ?? 0 },
              { label: "Rejected actions", value: data?.rejected_actions ?? 0 },
            ].map((row) => (
              <div key={row.label} className="flex justify-between gap-3">
                <span className="text-[#9CA3AF]">{row.label}</span>
                <span className="tabular-nums font-medium text-[#E5E7EB]">{row.value}</span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
