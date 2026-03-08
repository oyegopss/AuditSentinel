"use client";

import { RiskAnalyticsDashboard } from "@/components/risk-analytics-dashboard";

export default function RiskAnalyticsPage() {
  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
          Risk analytics
        </h1>
        <p className="text-sm text-[#9CA3AF] max-w-xl">
          Distribution of risk levels, trend analysis, recent high-risk tasks, and
          top detected keywords across tasks and audit actions.
        </p>
      </header>

      <RiskAnalyticsDashboard />
    </section>
  );
}
