"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Badge, RiskMeter, RiskPill } from "@/components/ui";
import { DecisionTimeline } from "@/components/decision-timeline";
import { apiUrl } from "@/lib/api";

type DecisionTrace = {
  task_id: string | null;
  output: string;
  reasoning_steps: string[];
  confidence: number;
  risk: string;
  recommended_action: string;
  created_at: string;
};

export default function DecisionPage() {
  const [trace, setTrace] = useState<DecisionTrace | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchTrace = async () => {
      setLoading(true);
      try {
        const res = await fetch(apiUrl("/decision-trace"));
        const data = await res.json();
        setTrace(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchTrace();
  }, []);

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          AI decision explainability
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          Inspect the latest agent decision with reasoning steps, confidence,
          risk band, and recommended governance action.
        </p>
      </header>

      <Card>
        <CardHeader>
          <div className="space-y-1">
            <CardTitle>Decision summary</CardTitle>
            {trace && (
              <div className="flex flex-wrap items-center gap-2 text-[11px] text-[#6B7280]">
                <span>Task ID: <span className="font-mono text-[#9CA3AF]">{trace.task_id ?? "\u2013"}</span></span>
                <span className="h-4 w-px bg-white/[0.06]" />
                <span>Created: {new Date(trace.created_at).toLocaleString()}</span>
              </div>
            )}
          </div>
          {trace && (
            <div className="flex items-center gap-2">
              <RiskPill risk={trace.risk} />
              <Badge>conf {Math.round((trace.confidence ?? 0) * 100)}%</Badge>
              <Badge>{trace.recommended_action}</Badge>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {loading && <p className="text-sm text-[#9CA3AF]">Loading latest decision trace...</p>}
          {!loading && trace && (
            <>
              <p className="text-sm text-[#E5E7EB]">{trace.output}</p>
              <RiskMeter score={trace.confidence ?? 0} />
              <div className="mt-4 space-y-2">
                <div className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide">Reasoning steps</div>
                <ol className="space-y-1 text-sm text-[#E5E7EB]/80 list-decimal list-inside">
                  {trace.reasoning_steps.map((step, idx) => (<li key={idx}>{step}</li>))}
                </ol>
              </div>
            </>
          )}
          {!loading && !trace && (
            <p className="text-sm text-[#9CA3AF]">No decision trace available yet. Submit a task first.</p>
          )}
        </CardContent>
      </Card>

      <DecisionTimeline />
    </section>
  );
}
