"use client";

import { useState } from "react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Button,
  RiskMeter,
  RiskPill
} from "@/components/ui";

type SimulationResponse = {
  scenario: string;
  risk: string;
  score: number;
  explanation: string;
  requires_human_approval: boolean;
};

type ApprovalResponse = {
  status: string;
  risk: string;
  action_hash?: string | null;
  tx_hash?: string | null;
  timestamp?: string | null;
};

const SCENARIOS = [
  { id: "financial_loan_approval", label: "Financial loan approval" },
  { id: "database_deletion", label: "Database deletion" },
  { id: "healthcare_diagnosis", label: "Healthcare diagnosis" },
  { id: "automated_trading", label: "Automated trading" }
];

export default function ApprovalPanelPage() {
  const [scenario, setScenario] = useState(SCENARIOS[0].id);
  const [description, setDescription] = useState(
    "Run the selected scenario with typical parameters."
  );
  const [userId, setUserId] = useState("demo-user");
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [loadingSim, setLoadingSim] = useState(false);
  const [loadingApproval, setLoadingApproval] = useState(false);

  const runSimulation = async () => {
    setLoadingSim(true);
    setApproval(null);
    try {
      const res = await fetch("http://localhost:8000/simulate-risk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, description })
      });
      const data = await res.json();
      setSimulation(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSim(false);
    }
  };

  const sendApproval = async (approved: boolean) => {
    setLoadingApproval(true);
    try {
      const res = await fetch("http://localhost:8000/approve-action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, description, approved, user: userId })
      });
      const data = await res.json();
      setApproval(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingApproval(false);
    }
  };

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Human approval panel
        </h1>
        <p className="text-sm text-gray-400 max-w-xl">
          Simulate risky AI scenarios, inspect risk scores, and gate execution
          behind human approval. Approved high‑risk actions are logged to the
          blockchain.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Risk simulation</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-300">
                  Scenario
                </label>
                <select
                  value={scenario}
                  onChange={(e) => setScenario(e.target.value)}
                  className="w-full rounded-md border border-border bg-black/40 px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/40"
                >
                  {SCENARIOS.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-300">
                  User
                </label>
                <input
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  className="w-full rounded-md border border-border bg-black/40 px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/40"
                  placeholder="e.g. analyst-123"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-gray-300">
                  Action description
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full min-h-[90px] rounded-md border border-border bg-black/40 px-3 py-2 text-xs outline-none focus:ring-2 focus:ring-primary/60 focus:border-primary/40"
                />
              </div>
              <Button
                type="button"
                disabled={loadingSim}
                onClick={runSimulation}
              >
                {loadingSim ? "Simulating…" : "Simulate risk"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Decision & approval</CardTitle>
          </CardHeader>
          <CardContent>
            {!simulation && (
              <p className="text-sm text-gray-400">
                Run a risk simulation to see approval controls.
              </p>
            )}
            {simulation && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <RiskPill risk={simulation.risk} />
                  <RiskMeter score={simulation.score} />
                </div>
                <p className="text-xs text-gray-300">
                  {simulation.explanation}
                </p>
                {simulation.requires_human_approval ? (
                  <p className="text-xs text-amber-300">
                    Human approval is required for this risk band.
                  </p>
                ) : (
                  <p className="text-xs text-emerald-300">
                    This scenario could be auto‑approved, but you can still gate
                    it manually.
                  </p>
                )}
                <div className="flex gap-2 pt-2">
                  <Button
                    type="button"
                    className="bg-red-600 hover:bg-red-500"
                    disabled={loadingApproval}
                    onClick={() => sendApproval(false)}
                  >
                    {loadingApproval ? "Submitting…" : "Reject action"}
                  </Button>
                  <Button
                    type="button"
                    disabled={loadingApproval}
                    onClick={() => sendApproval(true)}
                  >
                    {loadingApproval ? "Submitting…" : "Approve & log"}
                  </Button>
                </div>
                {approval && (
                  <div className="mt-3 rounded-md border border-border/80 bg-black/40 px-3 py-2 text-[11px] space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="uppercase tracking-wide text-gray-500">
                        Outcome
                      </span>
                      <span className="font-semibold text-gray-100">
                        {approval.status}
                      </span>
                    </div>
                    {approval.tx_hash && (
                      <div className="flex flex-col gap-0.5">
                        <span className="text-gray-400">
                          Tx:{" "}
                          <span className="font-mono text-gray-200">
                            {approval.tx_hash}
                          </span>
                        </span>
                        {approval.timestamp && (
                          <span className="text-gray-400">
                            At:{" "}
                            {new Date(approval.timestamp).toLocaleString()}
                          </span>
                        )}
                      </div>
                    )}
                    {approval.action_hash && !approval.tx_hash && (
                      <span className="text-gray-400">
                        Action hash:{" "}
                        <span className="font-mono text-gray-200">
                          {approval.action_hash}
                        </span>
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  );
}

