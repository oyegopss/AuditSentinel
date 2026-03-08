import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Sidebar } from "@/components/sidebar";
import { TopNavbar } from "@/components/TopNavbar";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

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
      <body className={`${inter.variable} h-full bg-[#0B0F19] font-sans text-[#E5E7EB] antialiased`}>
        <div className="min-h-screen bg-[#0B0F19]">
          <div className="flex min-h-screen flex-col">
            <TopNavbar />
            <div className="flex flex-1 min-h-0">
              <Sidebar />
              <main className="relative flex-1 min-h-full overflow-auto bg-[#0B0F19]">
                <div className="relative mx-auto max-w-6xl px-8 py-10">
                  {children}
                </div>
              </main>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
