"use client";

import { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, Button, RiskMeter, RiskPill, Spinner, Skeleton, Badge } from "@/components/ui";
import { apiUrl } from "@/lib/api";

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
  const [description, setDescription] = useState("Run the selected scenario with typical parameters.");
  const [userId, setUserId] = useState("demo-user");
  const [simulation, setSimulation] = useState<SimulationResponse | null>(null);
  const [approval, setApproval] = useState<ApprovalResponse | null>(null);
  const [loadingSim, setLoadingSim] = useState(false);
  const [loadingApproval, setLoadingApproval] = useState(false);

  const runSimulation = async () => {
    setLoadingSim(true);
    setApproval(null);
    try {
      const res = await fetch(apiUrl("/simulate-risk"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, description })
      });
      setSimulation(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingSim(false);
    }
  };

  const sendApproval = async (approved: boolean) => {
    setLoadingApproval(true);
    try {
      const res = await fetch(apiUrl("/approve-action"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scenario, description, approved, user: userId })
      });
      setApproval(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingApproval(false);
    }
  };

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          Human approval panel
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          Simulate risky AI scenarios, inspect risk scores, and gate execution
          behind human approval. Approved high-risk actions are logged to the blockchain.
        </p>
      </header>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Risk simulation</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-[#9CA3AF]">Scenario</label>
                <select value={scenario} onChange={(e) => setScenario(e.target.value)} className="surface-input text-xs">
                  {SCENARIOS.map((s) => (<option key={s.id} value={s.id}>{s.label}</option>))}
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-[#9CA3AF]">User</label>
                <input value={userId} onChange={(e) => setUserId(e.target.value)} className="surface-input text-xs" placeholder="e.g. analyst-123" />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-[#9CA3AF]">Action description</label>
                <textarea value={description} onChange={(e) => setDescription(e.target.value)} className="surface-input min-h-[110px] text-xs" />
              </div>
              <Button type="button" disabled={loadingSim} onClick={runSimulation} className="inline-flex items-center gap-2">
                {loadingSim && <Spinner className="h-3.5 w-3.5" />}
                {loadingSim ? "Simulating..." : "Simulate risk"}
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>Decision & approval</CardTitle></CardHeader>
          <CardContent>
            {loadingSim && (
              <div className="space-y-3" aria-busy="true">
                <Skeleton className="h-6 w-20" />
                <Skeleton className="h-4 w-full" />
                <p className="text-xs text-[#9CA3AF] flex items-center gap-2"><Spinner className="h-3 w-3" /> Running risk simulation...</p>
              </div>
            )}
            {!loadingSim && !simulation && (
              <p className="text-sm text-[#9CA3AF]">Run a risk simulation to see approval controls.</p>
            )}
            {!loadingSim && simulation && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <RiskPill risk={simulation.risk} />
                  <RiskMeter score={simulation.score} />
                </div>
                <p className="text-xs text-[#E5E7EB]/80">{simulation.explanation}</p>
                {simulation.requires_human_approval ? (
                  <p className="text-xs text-amber-400">Human approval is required for this risk band.</p>
                ) : (
                  <p className="text-xs text-primary/70">This scenario could be auto-approved, but you can still gate it manually.</p>
                )}
                <div className="flex gap-2 pt-2">
                  <Button type="button" className="bg-red-600 hover:bg-red-500 border-red-500 inline-flex items-center gap-2" disabled={loadingApproval} onClick={() => sendApproval(false)}>
                    {loadingApproval && <Spinner className="h-3.5 w-3.5" />}
                    {loadingApproval ? "Submitting..." : "Reject action"}
                  </Button>
                  <Button type="button" className="inline-flex items-center gap-2" disabled={loadingApproval} onClick={() => sendApproval(true)}>
                    {loadingApproval && <Spinner className="h-3.5 w-3.5" />}
                    {loadingApproval ? "Submitting..." : "Approve & log"}
                  </Button>
                </div>
                {approval && (
                  <div className="mt-3 space-y-2 rounded-xl border border-white/[0.08] bg-white/[0.02] px-3.5 py-3 text-[11px] animate-fade-in">
                    <div className="flex items-center justify-between">
                      <span className="uppercase tracking-wide text-[#6B7280]">Outcome</span>
                      <Badge className={approval.status === "approved" ? "border-emerald-500/20 bg-emerald-500/10 text-emerald-300" : "border-red-500/20 bg-red-500/10 text-red-300"}>
                        {approval.status}
                      </Badge>
                    </div>
                    {approval.tx_hash && (
                      <div className="flex flex-col gap-0.5">
                        <span className="text-[#9CA3AF]">Tx: <span className="font-mono text-emerald-300">{approval.tx_hash}</span></span>
                        {approval.timestamp && <span className="text-[#6B7280]">At: {new Date(approval.timestamp).toLocaleString()}</span>}
                      </div>
                    )}
                    {approval.action_hash && !approval.tx_hash && (
                      <span className="text-[#9CA3AF]">Action hash: <span className="font-mono text-primary">{approval.action_hash}</span></span>
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
