"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Button, RiskMeter, RiskPill, Spinner, Skeleton } from "@/components/ui";
import { MetricsStrip } from "@/components/metrics-strip";
import { GovernanceScoreCard } from "@/components/governance-score-card";
import { AgentMonitoringPanel } from "@/components/agent-monitoring-panel";
import { ActivityFeed } from "@/components/activity-feed";
import { AIDecisionExplanation } from "@/components/ai-decision-explanation";
import { AIDecisionSimulation } from "@/components/ai-decision-simulation";
import { apiUrl } from "@/lib/api";

type RiskLevel = "low" | "medium" | "high" | "critical";

const DESTRUCTIVE_KEYWORDS = [
  "delete", "drop", "erase", "remove", "truncate", "destroy", "wipe",
  "production database", "customer records", "user data", "financial records",
  "override", "shutdown", "transfer funds",
];

function extractKeywords(text: string): string[] {
  const lower = text.toLowerCase();
  return DESTRUCTIVE_KEYWORDS.filter((kw) => lower.includes(kw));
}

export default function TaskSubmissionPage() {
  const [prompt, setPrompt] = useState("");
  const [risk, setRisk] = useState<RiskLevel | null>(null);
  const [riskScore, setRiskScore] = useState<number | null>(null);
  const [riskLevel, setRiskLevel] = useState<string | null>(null);
  const [decision, setDecision] = useState<string | null>(null);
  const [output, setOutput] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [detectedKeywords, setDetectedKeywords] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    setLoading(true);
    setRisk(null);
    setRiskScore(null);
    setRiskLevel(null);
    setDecision(null);
    setOutput(null);
    setDetectedKeywords(extractKeywords(prompt));
    try {
      const res = await fetch(apiUrl("/task"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: prompt })
      });
      const data = await res.json();
      setOutput(data.output);
      setRisk((data.risk ?? data.risk_level?.toLowerCase()) as RiskLevel);
      setRiskScore(
        data.risk_score != null
          ? Number(data.risk_score)
          : data.confidence != null
            ? Math.round(Number(data.confidence) * 100)
            : null
      );
      setRiskLevel(data.risk_level ?? data.risk ?? null);
      setDecision(data.decision ?? null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          AI Governance Dashboard
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          Submit tasks, monitor risk classifications, and manage approvals with full
          explainability and on-chain logging.
        </p>
      </header>

      <MetricsStrip />

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1.3fr),minmax(0,1fr)]">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Task input</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={handleSubmit}>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-[#9CA3AF]">Task description</label>
                  <textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    className="surface-input min-h-[140px] resize-none"
                    placeholder='E.g. "Delete all customer records from production database"'
                  />
                </div>
                <Button type="submit" disabled={loading} className="inline-flex items-center gap-2">
                  {loading && <Spinner className="h-3.5 w-3.5" />}
                  {loading ? "Analyzing..." : "Submit task"}
                </Button>
              </form>
            </CardContent>
          </Card>

          <AIDecisionSimulation
            isRunning={loading}
            risk={risk}
            riskScore={riskScore}
            decision={decision}
          />

          <AIDecisionExplanation
            risk={risk}
            riskScore={riskScore}
            decision={decision}
            output={output}
            keywords={detectedKeywords}
          />
        </div>

        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Risk snapshot</CardTitle>
            </CardHeader>
            <CardContent>
              {loading && (
                <div className="space-y-3" aria-busy="true">
                  <div className="flex items-center justify-between gap-2">
                    <Skeleton className="h-6 w-20" />
                    <Skeleton className="h-8 w-24" />
                  </div>
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-2 w-full" />
                  <p className="flex items-center gap-2 text-xs text-primary">
                    <Spinner className="h-3 w-3" /> Generating AI decision...
                  </p>
                </div>
              )}
              {!loading && !risk && (
                <p className="text-sm text-[#9CA3AF]">
                  Submit a task to see its risk band, confidence, and governance
                  recommendation.
                </p>
              )}
              {!loading && (risk != null || riskScore != null) && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <RiskPill risk={risk ?? "low"} />
                    <RiskMeter score={(riskScore ?? 0) / 100} />
                  </div>
                  {decision && (
                    <p className="text-[11px] text-[#9CA3AF]">
                      Decision: {decision.replace(/_/g, " ")}
                    </p>
                  )}
                  {output && (
                    <p className="text-xs text-[#E5E7EB]/80">{output}</p>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
          <GovernanceScoreCard />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <AgentMonitoringPanel />
        <ActivityFeed />
      </div>
    </section>
  );
}
