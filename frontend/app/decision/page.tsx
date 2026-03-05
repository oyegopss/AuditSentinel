"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Badge, RiskMeter, RiskPill } from "@/components/ui";

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
        const res = await fetch("http://localhost:8000/decision-trace");
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
        <h1 className="text-2xl font-semibold tracking-tight">
          AI decision explainability
        </h1>
        <p className="text-sm text-gray-400 max-w-xl">
          Inspect the latest agent decision with reasoning steps, confidence,
          risk band, and recommended governance action.
        </p>
      </header>

      <Card>
        <CardHeader>
          <div className="space-y-1">
            <CardTitle>Decision summary</CardTitle>
            {trace && (
              <div className="flex flex-wrap items-center gap-2 text-[11px] text-gray-400">
                <span>
                  Task ID:{" "}
                  <span className="font-mono text-gray-300">
                    {trace.task_id ?? "–"}
                  </span>
                </span>
                <span className="h-4 w-px bg-gray-700" />
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
          {loading && (
            <p className="text-sm text-gray-400">Loading latest decision trace…</p>
          )}
          {!loading && trace && (
            <>
              <p className="text-sm text-gray-100">{trace.output}</p>
              <RiskMeter score={trace.confidence ?? 0} />
              <div className="mt-4 space-y-2">
                <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide">
                  Reasoning steps
                </div>
                <ol className="space-y-1 text-sm text-gray-200 list-decimal list-inside">
                  {trace.reasoning_steps.map((step, idx) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              </div>
            </>
          )}
          {!loading && !trace && (
            <p className="text-sm text-gray-400">
              No decision trace available yet. Submit a task first.
            </p>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

