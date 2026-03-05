"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Button, RiskMeter, RiskPill } from "@/components/ui";

type RiskLevel = "low" | "medium" | "high" | "critical";

export default function TaskSubmissionPage() {
  const [prompt, setPrompt] = useState("");
  const [risk, setRisk] = useState<RiskLevel | null>(null);
  const [confidence, setConfidence] = useState(0);
  const [output, setOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/task", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: prompt })
      });
      const data = await res.json();
      setOutput(data.output);
      setRisk(data.risk as RiskLevel);
      setConfidence(data.confidence ?? 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Submit AI task
        </h1>
        <p className="text-sm text-gray-400 max-w-xl">
          Describe what you want the agent to do. AuditSentinel will plan,
          simulate, and route decisions through risk-aware checks and optional
          human approval, with full explainability and on‑chain logging.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-[minmax(0,3fr),minmax(0,2fr)]">
        <Card>
          <CardHeader>
            <CardTitle>Task input</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <label className="text-sm font-medium">Task description</label>
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  className="w-full min-h-[140px] rounded-md border border-border bg-black/40 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/40"
                  placeholder="E.g. Perform due diligence on vendor X using open web data and internal risk rules..."
                />
              </div>
              <Button type="submit" disabled={loading}>
                {loading ? "Submitting…" : "Submit task"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Risk snapshot</CardTitle>
          </CardHeader>
          <CardContent>
            {!risk && (
              <p className="text-sm text-gray-400">
                Submit a task to see its risk band, confidence, and governance
                recommendation.
              </p>
            )}
            {risk && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <RiskPill risk={risk} />
                  <RiskMeter score={confidence} />
                </div>
                {output && (
                  <p className="text-xs text-gray-300">{output}</p>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}
