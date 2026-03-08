"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, RiskPill } from "@/components/ui";

type Props = {
  risk: string | null;
  riskScore: number | null;
  decision: string | null;
  output: string | null;
  keywords?: string[];
};

export function AIDecisionExplanation({ risk, riskScore, decision, output, keywords }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!risk && !output) return null;

  const isCritical = risk === "critical" || risk === "high";
  const policyName = isCritical ? "Destructive Action Policy" : risk === "medium" ? "Moderate Risk Policy" : "Standard Execution Policy";

  const reasonText = isCritical
    ? "This task may permanently modify or delete sensitive production data and therefore requires mandatory human approval before execution."
    : risk === "medium"
    ? "This task involves financial or data operations that carry moderate risk. Human review is recommended."
    : "No destructive or high-risk patterns detected. Task is eligible for autonomous execution with standard audit logging.";

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <svg className="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <CardTitle>AI Decision Explanation</CardTitle>
        </div>
        {risk && <RiskPill risk={risk} />}
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <p className="text-xs font-medium text-[#9CA3AF] uppercase tracking-wide mb-1.5">
              Why was this classified as {(risk ?? "low").toUpperCase()}?
            </p>
            <p className="text-sm text-[#E5E7EB] leading-relaxed">{reasonText}</p>
          </div>

          {keywords && keywords.length > 0 && (
            <div>
              <p className="text-xs font-medium text-[#9CA3AF] uppercase tracking-wide mb-2">
                Detected keywords
              </p>
              <div className="flex flex-wrap gap-1.5">
                {keywords.map((kw) => (
                  <span
                    key={kw}
                    className="rounded-md border border-red-500/20 bg-red-500/8 px-2 py-0.5 text-[11px] font-medium text-red-300"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <p className="text-xs font-medium text-[#9CA3AF] uppercase tracking-wide mb-1">
              Policy triggered
            </p>
            <span className="inline-flex items-center rounded-md border border-primary/20 bg-primary/8 px-2.5 py-1 text-xs font-medium text-primary">
              {policyName}
            </span>
          </div>

          {decision && (
            <div>
              <p className="text-xs font-medium text-[#9CA3AF] uppercase tracking-wide mb-1">
                Decision outcome
              </p>
              <p className="text-sm text-[#E5E7EB]">{decision.replace(/_/g, " ")}</p>
            </div>
          )}

          {output && (
            <div>
              <button
                onClick={() => setExpanded(!expanded)}
                className="flex items-center gap-1.5 text-[11px] font-medium text-primary hover:text-hover transition-colors"
              >
                <svg
                  className={`h-3 w-3 transition-transform ${expanded ? "rotate-90" : ""}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
                {expanded ? "Hide reasoning" : "Show full reasoning"}
              </button>
              {expanded && (
                <div className="mt-2 rounded-xl border border-white/[0.06] bg-white/[0.02] p-3 text-xs text-[#9CA3AF] leading-relaxed animate-fade-in">
                  {output}
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
