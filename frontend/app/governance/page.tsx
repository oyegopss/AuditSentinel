"use client";

import { GovernanceScoreCard } from "@/components/governance-score-card";

export default function GovernancePage() {
  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          Governance score dashboard
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          AI governance score (0-100) based on high-risk actions, rejected
          decisions, and blockchain-verified audit logs.
        </p>
      </header>

      <div className="max-w-md">
        <GovernanceScoreCard />
      </div>
    </section>
  );
}
