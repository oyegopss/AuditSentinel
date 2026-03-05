"use client";

import { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, RiskPill, Button } from "@/components/ui";

type AuditLogItem = {
  action_description: string;
  action_hash: string;
  tx_hash: string | null;
  timestamp: string | null;
  risk: string;
  status: string;
};

export default function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const res = await fetch("http://localhost:8000/audit-log");
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

  const explorerUrl = (tx: string) =>
    `https://amoy.polygonscan.com/tx/${tx}`;

  return (
    <section className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Blockchain audit log
        </h1>
        <p className="text-sm text-gray-400 max-w-xl">
          Every approved high‑risk action is immutably logged on Polygon
          testnet. Inspect on‑chain records and drill into the original action
          metadata.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>On‑chain actions</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && (
            <p className="text-sm text-gray-400">Loading audit entries…</p>
          )}
          {!loading && logs.length === 0 && (
            <p className="text-sm text-gray-400">
              No audit entries yet. Approve a high‑risk simulation to log an
              action.
            </p>
          )}
          {!loading && logs.length > 0 && (
            <div className="overflow-x-auto text-xs">
              <table className="min-w-full border-collapse">
                <thead>
                  <tr className="border-b border-border/70 text-gray-400">
                    <th className="py-2 pr-3 text-left">Action</th>
                    <th className="py-2 px-3 text-left">Risk Level</th>
                    <th className="py-2 px-3 text-left">Approval Status</th>
                    <th className="py-2 px-3 text-left">Transaction Hash</th>
                    <th className="py-2 px-3 text-left">Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr
                      key={log.action_hash}
                      className="border-b border-border/40 last:border-b-0"
                    >
                      <td className="py-2 pr-3 align-top max-w-xs">
                        <div className="text-gray-100 line-clamp-2">
                          {log.action_description}
                        </div>
                        <div className="mt-1 font-mono text-[10px] text-gray-500">
                          {log.action_hash.slice(0, 10)}…
                        </div>
                      </td>
                      <td className="py-2 px-3 align-top">
                        <RiskPill risk={log.risk} />
                      </td>
                      <td className="py-2 px-3 align-top capitalize text-gray-200">
                        {log.status}
                      </td>
                      <td className="py-2 px-3 align-top font-mono text-[10px] text-emerald-300">
                        {log.tx_hash ? (
                          <a
                            href={explorerUrl(log.tx_hash)}
                            target="_blank"
                            rel="noreferrer"
                            className="hover:underline"
                          >
                            {log.tx_hash.slice(0, 12)}…
                          </a>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="py-2 px-3 align-top text-gray-400">
                        {log.timestamp
                          ? new Date(log.timestamp).toLocaleString()
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  );
}

