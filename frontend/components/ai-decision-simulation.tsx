"use client";

import { useEffect, useState, useRef } from "react";
import { Card, CardHeader, CardTitle, CardContent, RiskPill, Badge } from "@/components/ui";

type Props = {
  isRunning: boolean;
  risk: string | null;
  riskScore: number | null;
  decision: string | null;
};

const STEPS = [
  { label: "Parsing task description", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { label: "Extracting risk keywords", icon: "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" },
  { label: "Matching governance policies", icon: "M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" },
  { label: "Calculating risk score", icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" },
  { label: "Determining execution path", icon: "M13 10V3L4 14h7v7l9-11h-7z" },
];

export function AIDecisionSimulation({ isRunning, risk, riskScore, decision }: Props) {
  const [completedSteps, setCompletedSteps] = useState<number[]>([]);
  const [activeStep, setActiveStep] = useState<number>(-1);
  const [showResult, setShowResult] = useState(false);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!isRunning) return;

    setCompletedSteps([]);
    setActiveStep(0);
    setShowResult(false);

    let step = 0;
    const advance = () => {
      if (step < STEPS.length) {
        setActiveStep(step);
        timerRef.current = setTimeout(() => {
          setCompletedSteps((prev) => [...prev, step]);
          step++;
          advance();
        }, 600);
      }
    };
    advance();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isRunning]);

  useEffect(() => {
    if (!isRunning && risk) {
      setCompletedSteps([0, 1, 2, 3, 4]);
      setActiveStep(-1);
      setShowResult(true);
    }
  }, [isRunning, risk]);

  if (completedSteps.length === 0 && !isRunning) return null;

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <svg className="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <CardTitle>AI Decision Simulation</CardTitle>
        </div>
        {isRunning && (
          <span className="flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-wider text-primary">
            <span className="h-1.5 w-1.5 rounded-full bg-primary animate-pulse" />
            Processing
          </span>
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {STEPS.map((step, i) => {
            const isCompleted = completedSteps.includes(i);
            const isActive = activeStep === i && isRunning;

            return (
              <div
                key={i}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all duration-300 ${
                  isActive
                    ? "bg-primary/[0.06] border border-primary/20"
                    : isCompleted
                    ? "bg-emerald-500/[0.04] border border-emerald-500/10"
                    : "border border-transparent opacity-40"
                }`}
              >
                <div className="flex-shrink-0">
                  {isCompleted ? (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500/20 animate-check-pop">
                      <svg className="h-3.5 w-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                  ) : isActive ? (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20">
                      <svg className="h-3.5 w-3.5 text-primary animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                    </div>
                  ) : (
                    <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/[0.04]">
                      <svg className="h-3.5 w-3.5 text-[#6B7280]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d={step.icon} />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-xs font-medium ${
                    isCompleted ? "text-emerald-300" : isActive ? "text-primary" : "text-[#6B7280]"
                  }`}>
                    Step {i + 1}
                  </p>
                  <p className={`text-[11px] ${
                    isCompleted ? "text-[#9CA3AF]" : isActive ? "text-[#E5E7EB]" : "text-[#6B7280]"
                  }`}>
                    {step.label}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {showResult && risk && (
          <div className="mt-4 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 space-y-3 animate-fade-in">
            <div className="flex items-center justify-between">
              <RiskPill risk={risk} />
              {riskScore != null && (
                <Badge>Confidence: {riskScore}%</Badge>
              )}
            </div>
            {decision && (
              <p className="text-xs text-[#9CA3AF]">
                Decision: <span className="text-[#E5E7EB] font-medium">{decision.replace(/_/g, " ")}</span>
              </p>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
