"use client";

import { clsx } from "clsx";
import { ReactNode, HTMLAttributes, ButtonHTMLAttributes } from "react";

export function Card(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div
      className={clsx(
        "rounded-lg border border-border bg-card/70 backdrop-blur shadow-sm",
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
        "px-4 py-3 border-b border-border flex items-center justify-between gap-2",
        className
      )}
      {...rest}
    />
  );
}

export function CardTitle({ children }: { children: ReactNode }) {
  return (
    <h2 className="text-sm font-semibold tracking-tight text-gray-100">
      {children}
    </h2>
  );
}

export function CardContent(props: HTMLAttributes<HTMLDivElement>) {
  const { className, ...rest } = props;
  return (
    <div className={clsx("px-4 py-3 text-sm space-y-3", className)} {...rest} />
  );
}

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  const { className, ...rest } = props;
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center rounded-md px-3 py-2 text-xs font-medium",
        "bg-primary text-primary-foreground shadow-sm hover:bg-emerald-500/90",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        className
      )}
      {...rest}
    />
  );
}

export function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-border/70 bg-black/40 px-2 py-0.5 text-[10px] uppercase tracking-wide text-gray-300">
      {children}
    </span>
  );
}

export function RiskPill({ risk }: { risk: string }) {
  const color =
    risk === "critical"
      ? "bg-red-500/20 text-red-300 border-red-500/40"
      : risk === "high"
      ? "bg-orange-500/20 text-orange-200 border-orange-500/40"
      : risk === "medium"
      ? "bg-yellow-500/20 text-yellow-200 border-yellow-500/40"
      : "bg-emerald-500/20 text-emerald-200 border-emerald-500/40";

  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide",
        color
      )}
    >
      {risk}
    </span>
  );
}

export function RiskMeter({ score }: { score: number }) {
  const pct = Math.round(score * 100);

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-[11px] text-gray-400">
        <span>Risk score</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full rounded-full bg-gray-800 overflow-hidden">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-300 to-red-500 transition-all"
          style={{ width: `${pct}%` }}
        />
      </div>
      <div className="flex justify-between text-[10px] text-gray-500 uppercase">
        <span>Low</span>
        <span>Medium</span>
        <span>High</span>
        <span>Critical</span>
      </div>
    </div>
  );
}

