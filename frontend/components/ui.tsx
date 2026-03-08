"use client";

import { clsx } from "clsx";
import { ReactNode, HTMLAttributes, ButtonHTMLAttributes } from "react";

export function Card(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div
      className={clsx(
        "panel-hover rounded-2xl border border-white/[0.08] bg-[#111827]",
        "shadow-card animate-fade-in",
        className
      )}
      {...rest}
    />
  );
}

export function CardHeader(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div
      className={clsx(
        "flex items-center justify-between gap-3 border-b border-white/[0.06] px-6 py-4",
        className
      )}
      {...rest}
    />
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-sm font-semibold tracking-tight text-[#E5E7EB]">
      {children}
    </h2>
  );
}

export function CardContent(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div className={clsx("space-y-4 px-6 py-5 text-sm", className)} {...rest} />
  );
}

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { className, ...rest } = props;
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-xs font-semibold",
        "bg-primary text-primary-foreground border border-[#F5D76E]",
        "shadow-[0_0_0_1px_rgba(245,197,66,0.18)] hover:scale-[1.015] hover:bg-hover hover:shadow-glow",
        "disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200",
        className
      )}
      {...rest}
    />
  );
}

export function Badge({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <span className={clsx(
      "inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wide text-primary",
      className
    )}>
      {children}
    </span>
  );
}

export function RiskPill({ risk }: { risk: string }) {
  const color =
    risk === "critical"
      ? "border-red-500/40 bg-red-500/12 text-red-300"
      : risk === "high"
      ? "border-orange-500/40 bg-orange-500/12 text-orange-300"
      : risk === "medium"
      ? "border-amber-500/40 bg-amber-500/12 text-amber-300"
      : "border-emerald-500/40 bg-emerald-500/12 text-emerald-300";

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em]",
        color
      )}
    >
      {risk}
    </span>
  );
}

export function Spinner({ className }: { className?: string }) {
  return (
    <svg
      className={clsx("animate-spin h-4 w-4", className)}
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return (
    <div
      className={clsx("animate-pulse rounded-xl bg-white/[0.04]", className)}
      aria-hidden
    />
  );
}

export function RiskMeter({ score }: { score: number }) {
  const pct = Math.round(score * 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px] text-[#9CA3AF]">
        <span>Risk score</span>
        <span className="font-medium text-primary">{pct}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-white/[0.06]">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-500 via-amber-400 to-red-500 transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] uppercase text-[#6B7280]">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
        <span>Critical</span>
      </div>
    </div>
  );
}
