"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, RiskPill, Button, Spinner, Skeleton, Badge } from "@/components/ui";
import { apiUrl } from "@/lib/api";

type AuditLogItem = {
  action_description: string;
  action_hash: string;
  tx_hash: string | null;
  timestamp: string | null;
  risk: string;
  status: string;
};

function isSimulatedTx(hash: string | null): boolean {
  if (!hash) return false;
  if (hash.length !== 66) return true;
  const body = hash.slice(2);
  return body.slice(0, 32) === body.slice(32);
}

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);
  const [modalLog, setModalLog] = useState<AuditLogItem | null>(null);

  const exportPdf = async () => {
    setExportingPdf(true);
    try {
      const res = await fetch(apiUrl("/export-audit-report"));
      if (!res.ok) throw new Error(res.statusText);
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      const match = disposition?.match(/filename="?([^";]+)"?/);
      const name = match?.[1] ?? "audit-report.pdf";
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
    } finally {
      setExportingPdf(false);
    }
  };

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const res = await fetch(apiUrl("/audit-log"));
        const data = await res.json();
        setLogs(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  return (
    <section className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-2xl font-bold tracking-tight text-[#E5E7EB]">
            Blockchain audit log
          </h1>
          <p className="text-sm text-[#9CA3AF] max-w-xl">
            Every approved high-risk action is immutably logged on Polygon
            testnet. Inspect on-chain records and drill into action metadata.
          </p>
        </div>
        <Button
          type="button"
          disabled={exportingPdf}
          onClick={exportPdf}
          className="flex-shrink-0 inline-flex items-center gap-2"
        >
          {exportingPdf && <Spinner className="h-3.5 w-3.5" />}
          {exportingPdf ? "Generating..." : "Export PDF report"}
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>On-chain actions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && (
            <div className="space-y-2" aria-busy="true">
              <div className="flex items-center gap-2 text-sm text-[#9CA3AF]">
                <Spinner className="h-4 w-4" /> Loading audit entries...
              </div>
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          )}
          {!loading && logs.length === 0 && (
            <p className="text-sm text-[#9CA3AF]">
              No audit entries yet. Approve a high-risk simulation to log an action.
            </p>
          )}
          {!loading && logs.length > 0 && (
            <div className="overflow-x-auto text-xs">
              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="border-b border-white/[0.06] text-[#6B7280]">
                    <th className="py-2 pr-3 text-left font-medium">Action</th>
                    <th className="py-2 px-3 text-left font-medium">Risk</th>
                    <th className="py-2 px-3 text-left font-medium">Status</th>
                    <th className="py-2 px-3 text-left font-medium">Tx Hash</th>
                    <th className="py-2 px-3 text-left font-medium">Timestamp</th>
                    <th className="py-2 px-3 text-left font-medium">Explorer</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log, i) => {
                    const simulated = isSimulatedTx(log.tx_hash);

                    return (
                      <tr
                        key={log.action_hash + i}
                        className="border-b border-white/[0.04] last:border-b-0 animate-fade-in"
                        style={{ animationDelay: `${i * 30}ms` }}
                      >
                        <td className="py-2.5 pr-3 align-top max-w-xs">
                          <div className="text-[#E5E7EB] line-clamp-2">{log.action_description}</div>
                          <div className="mt-1 font-mono text-[10px] text-[#6B7280]">{log.action_hash.slice(0, 10)}...</div>
                        </td>
                        <td className="py-2.5 px-3 align-top"><RiskPill risk={log.risk} /></td>
                        <td className="py-2.5 px-3 align-top capitalize text-[#9CA3AF]">{log.status}</td>
                        <td className="py-2.5 px-3 align-top">
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono text-[10px] text-emerald-300">
                              {log.tx_hash ? `${log.tx_hash.slice(0, 12)}...` : "\u2014"}
                            </span>
                            {log.tx_hash && simulated && (
                              <Badge className="text-[8px] border-amber-500/20 bg-amber-500/8 text-amber-300">
                                Simulated
                              </Badge>
                            )}
                          </div>
                        </td>
                        <td className="py-2.5 px-3 align-top text-[#6B7280]">
                          {log.timestamp ? new Date(log.timestamp).toLocaleString() : "\u2014"}
                        </td>
                        <td className="py-2.5 px-3 align-top">
                          {log.tx_hash ? (
                            simulated ? (
                              <button
                                type="button"
                                onClick={() => setModalLog(log)}
                                className="bg-white/[0.06] hover:bg-white/[0.1] text-[#9CA3AF] hover:text-[#E5E7EB] px-3 py-1 rounded-lg text-[11px] border border-white/[0.06] transition-all"
                              >
                                View details
                              </button>
                            ) : (
                              <button
                                type="button"
                                onClick={() => window.open(`https://amoy.polygonscan.com/tx/${log.tx_hash}`, "_blank")}
                                className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 px-3 py-1 rounded-lg text-[11px] border border-emerald-500/20 transition-all"
                              >
                                View on PolygonScan
                              </button>
                            )
                          ) : (
                            <span className="text-[11px] text-[#6B7280]">No tx</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Simulated Tx Modal */}
      {modalLog && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in"
          onClick={() => setModalLog(null)}
        >
          <div
            className="w-full max-w-lg rounded-2xl border border-white/[0.1] bg-[#111827] shadow-glow-lg p-6 space-y-4 animate-scale-in"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-[#E5E7EB]">Simulated Chain Record</h3>
              <Badge className="border-amber-500/20 bg-amber-500/10 text-amber-300">Simulated</Badge>
            </div>
            <div className="space-y-3 text-sm">
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wide text-[#6B7280] mb-1">Transaction Hash</p>
                <p className="font-mono text-xs text-emerald-300 break-all">{modalLog.tx_hash}</p>
              </div>
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wide text-[#6B7280] mb-1">Timestamp</p>
                <p className="text-[#E5E7EB]">{modalLog.timestamp ? new Date(modalLog.timestamp).toLocaleString() : "\u2014"}</p>
              </div>
              <div>
                <p className="text-[11px] font-medium uppercase tracking-wide text-[#6B7280] mb-1">Task Description</p>
                <p className="text-[#E5E7EB]">{modalLog.action_description}</p>
              </div>
              <div className="flex gap-4">
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wide text-[#6B7280] mb-1">Risk Classification</p>
                  <RiskPill risk={modalLog.risk} />
                </div>
                <div>
                  <p className="text-[11px] font-medium uppercase tracking-wide text-[#6B7280] mb-1">Approval Status</p>
                  <span className="capitalize text-[#E5E7EB]">{modalLog.status}</span>
                </div>
              </div>
              <p className="text-[11px] text-amber-400/80 italic">
                This transaction was generated for demo purposes and does not exist on-chain.
                Set POLYGON_PRIVATE_KEY for real blockchain logging.
              </p>
            </div>
            <div className="flex justify-end">
              <Button type="button" onClick={() => setModalLog(null)}>Close</Button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
