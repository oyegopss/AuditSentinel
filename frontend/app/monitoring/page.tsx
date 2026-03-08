"use client";

import { AgentMonitoringPanel } from "@/components/agent-monitoring-panel";

export default function MonitoringPage() {
  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          Agent monitoring
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          Live status of Planning Agent, Execution Agent, Risk Engine,
          Blockchain Logger, and Database with heartbeat and uptime tracking.
        </p>
      </header>

      <AgentMonitoringPanel />
    </section>
  );
}
