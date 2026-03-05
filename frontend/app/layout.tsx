import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AuditSentinel",
  description: "AI agent risk-aware audit and approval system"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full bg-background text-foreground">
        <div className="min-h-screen flex">
          <aside className="w-64 border-r border-border bg-card/60 backdrop-blur">
            <div className="px-6 py-5 border-b border-border">
              <div className="font-semibold text-lg tracking-tight">
                Audit<span className="text-primary">Sentinel</span>
              </div>
              <p className="text-xs text-gray-400 mt-1">
                Agentic risk-aware operations
              </p>
            </div>
            <nav className="px-4 py-4 space-y-1 text-sm">
              <a href="/" className="block px-3 py-2 rounded-md hover:bg-gray-800">
                Task submission
              </a>
              <a
                href="/decision"
                className="block px-3 py-2 rounded-md hover:bg-gray-800"
              >
                AI decision viewer
              </a>
              <a
                href="/approve"
                className="block px-3 py-2 rounded-md hover:bg-gray-800"
              >
                Human approval panel
              </a>
              <a
                href="/audit-logs"
                className="block px-3 py-2 rounded-md hover:bg-gray-800"
              >
                Blockchain audit logs
              </a>
            </nav>
          </aside>
          <main className="flex-1 min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <div className="max-w-5xl mx-auto py-8 px-6">{children}</div>
          </main>
        </div>
      </body>
    </html>
  );
}

