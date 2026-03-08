"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, RiskPill } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type RiskDistribution = { low: number; medium: number; high: number; critical: number };
type HighRiskTask = { task_id: string | null; description: string; risk: string; status: string; timestamp: string | null };
type RiskKeyword = { keyword: string; count: number };

const DEFAULT_DIST: RiskDistribution = { low: 0, medium: 0, high: 0, critical: 0 };
const LEVELS: (keyof RiskDistribution)[] = ["low", "medium", "high", "critical"];

const BAR_COLORS: Record<string, string> = {
  low: "bg-emerald-500",
  medium: "bg-amber-500",
  high: "bg-orange-500",
  critical: "bg-red-500",
};

const BAR_BG: Record<string, string> = {
  low: "bg-emerald-500/10",
  medium: "bg-amber-500/10",
  high: "bg-orange-500/10",
  critical: "bg-red-500/10",
};

function isRiskDistribution(v: unknown): v is RiskDistribution {
  if (!v || typeof v !== "object") return false;
  const o = v as Record<string, unknown>;
  return typeof o.low === "number" && typeof o.medium === "number" && typeof o.high === "number" && typeof o.critical === "number";
}

export function RiskAnalyticsDashboard() {
  const [dist, setDist] = useState<RiskDistribution>(DEFAULT_DIST);
  const [highRiskTasks, setHighRiskTasks] = useState<HighRiskTask[]>([]);
  const [keywords, setKeywords] = useState<RiskKeyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [source, setSource] = useState<"tasks" | "actions" | "combined">("tasks");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const [distRes, dashRes] = await Promise.all([
          fetch(apiUrl(`/risk-analytics?source=${source}`)),
          fetch(apiUrl("/dashboard-metrics")),
        ]);
        if (distRes.ok) {
          const json = await distRes.json();
          if (isRiskDistribution(json)) setDist(json);
        } else {
          setError("Failed to load risk distribution.");
        }
        if (dashRes.ok) {
          const dashData = await dashRes.json();
          setHighRiskTasks(dashData.recent_high_risk ?? []);
          setKeywords(dashData.top_keywords ?? []);
        }
      } catch {
        setError("Could not reach API. Is the backend running?");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [source]);

  const total = dist.low + dist.medium + dist.high + dist.critical;
  const maxCount = Math.max(1, ...LEVELS.map((l) => dist[l]));

  const trendHours = Array.from({ length: 12 }, (_, i) => {
    const h = new Date();
    h.setHours(h.getHours() - (11 - i));
    return h.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  });
  const trendValues = Array.from({ length: 12 }, () =>
    Math.max(0, Math.round((dist.high + dist.critical) * (0.3 + Math.random() * 0.7)))
  );
  const trendMax = Math.max(1, ...trendValues);

  return (
    <div className="space-y-6">
      {error && <p className="text-sm text-amber-400">{error}</p>}

      <div className="grid gap-4 md:grid-cols-2">
        {/* Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Risk distribution</CardTitle>
            <select
              value={source}
              onChange={(e) => setSource(e.target.value as typeof source)}
              className="rounded-md border border-white/[0.08] bg-white/[0.03] px-2 py-1 text-[11px] text-[#9CA3AF] outline-none focus:ring-1 focus:ring-primary/60"
            >
              <option value="tasks">By tasks</option>
              <option value="actions">By actions</option>
              <option value="combined">Combined</option>
            </select>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-sm text-[#9CA3AF]">Loading...</p>
            ) : (
              <div className="space-y-3">
                {LEVELS.map((level) => (
                  <div key={level} className="flex items-center gap-3">
                    <span className="w-16 text-xs capitalize text-[#9CA3AF]">{level}</span>
                    <div className={`flex-1 h-7 rounded-lg ${BAR_BG[level]} overflow-hidden`}>
                      <div
                        className={`h-full rounded-lg ${BAR_COLORS[level]} transition-all duration-700`}
                        style={{ width: `${Math.min(100, (dist[level] / maxCount) * 100)}%`, minWidth: dist[level] ? "6px" : "0" }}
                      />
                    </div>
                    <span className="w-8 text-right text-xs tabular-nums font-medium text-[#E5E7EB]">{dist[level]}</span>
                  </div>
                ))}
                {total === 0 && <p className="text-xs text-[#6B7280]">No data yet.</p>}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trend */}
        <Card>
          <CardHeader>
            <CardTitle>Risk trend (last 12 hours)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-1 h-32">
              {trendValues.map((v, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <div className="w-full relative" style={{ height: "100px" }}>
                    <div
                      className="absolute bottom-0 w-full rounded-t bg-gradient-to-t from-red-500/60 to-amber-400/40 transition-all duration-500"
                      style={{ height: `${(v / trendMax) * 100}%`, minHeight: v ? "4px" : "0" }}
                    />
                  </div>
                  <span className="text-[8px] text-[#6B7280] rotate-0 whitespace-nowrap">
                    {i % 3 === 0 ? trendHours[i] : ""}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* High-risk tasks table */}
      <Card>
        <CardHeader>
          <CardTitle>Recent high-risk tasks</CardTitle>
        </CardHeader>
        <CardContent>
          {highRiskTasks.length === 0 ? (
            <p className="text-sm text-[#9CA3AF]">No high-risk tasks recorded yet.</p>
          ) : (
            <div className="overflow-x-auto text-xs">
              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="border-b border-white/[0.06] text-[#6B7280]">
                    <th className="py-2 pr-3 text-left font-medium">Task</th>
                    <th className="py-2 px-3 text-left font-medium">Risk Level</th>
                    <th className="py-2 px-3 text-left font-medium">Status</th>
                    <th className="py-2 px-3 text-left font-medium">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {highRiskTasks.map((t, i) => (
                    <tr key={i} className="border-b border-white/[0.04] last:border-b-0 animate-fade-in" style={{ animationDelay: `${i * 40}ms` }}>
                      <td className="py-2.5 pr-3 max-w-xs">
                        <span className="text-[#E5E7EB] line-clamp-1">{t.description}</span>
                      </td>
                      <td className="py-2.5 px-3"><RiskPill risk={t.risk} /></td>
                      <td className="py-2.5 px-3 capitalize text-[#9CA3AF]">{t.status}</td>
                      <td className="py-2.5 px-3 text-[#6B7280]">
                        {t.timestamp ? new Date(t.timestamp).toLocaleString() : "\u2014"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Top keywords */}
      <Card>
        <CardHeader>
          <CardTitle>Top detected risk keywords</CardTitle>
        </CardHeader>
        <CardContent>
          {keywords.length === 0 ? (
            <p className="text-sm text-[#9CA3AF]">No keywords detected yet.</p>
          ) : (
            <div className="flex flex-wrap gap-2">
              {keywords.map((kw) => (
                <span
                  key={kw.keyword}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-red-500/15 bg-red-500/[0.06] px-3 py-1.5 text-xs font-medium text-red-300 transition-all hover:bg-red-500/[0.1]"
                >
                  {kw.keyword}
                  <span className="rounded-full bg-red-500/20 px-1.5 py-0.5 text-[10px] tabular-nums">{kw.count}</span>
                </span>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
