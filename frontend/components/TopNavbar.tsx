"use client";

import { useState } from "react";
import { Button, Spinner } from "@/components/ui";
import { apiUrl } from "@/lib/api";

export function TopNavbar() {
  const [exportingReport, setExportingReport] = useState(false);

  const exportAuditReport = async () => {
    setExportingReport(true);
    try {
      const res = await fetch(apiUrl("/export-audit-report"));
      if (!res.ok) throw new Error(res.statusText);
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      const name = disposition?.match(/filename="?([^";]+)"?/)?.[1] ?? "audit-report.pdf";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
    } finally {
      setExportingReport(false);
    }
  };

  return (
    <header
      className="sticky top-0 z-10 flex h-16 shrink-0 items-center justify-between border-b border-white/[0.06] bg-[#0D1117]/95 backdrop-blur-md px-6"
      style={{ minHeight: "64px" }}
    >
      <div className="flex items-center gap-4">
        <span className="text-lg font-semibold tracking-tight text-[#E5E7EB]">
          AuditSentinel
        </span>
        <span className="rounded border border-primary/20 bg-primary/[0.06] px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-primary/80">
          Demo mode
        </span>
      </div>

      <div className="flex items-center gap-3">
        <Button
          type="button"
          onClick={exportAuditReport}
          disabled={exportingReport}
        >
          {exportingReport && <Spinner className="h-3.5 w-3.5" />}
          {exportingReport ? "Generating..." : "Export Audit Report"}
        </Button>
      </div>
    </header>
  );
}
