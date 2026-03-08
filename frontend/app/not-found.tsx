import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <p className="text-6xl font-bold tracking-tight text-[#E5E7EB]/20">404</p>
      <h1 className="mt-2 text-xl font-semibold text-[#E5E7EB]">
        This page could not be found.
      </h1>
      <p className="mt-2 max-w-sm text-sm text-[#9CA3AF]">
        The route you requested doesn&apos;t exist. Return to the dashboard to continue.
      </p>
      <Link
        href="/dashboard"
        className="mt-6 inline-flex items-center justify-center rounded-xl border border-primary/20 bg-primary/[0.06] px-4 py-2.5 text-sm font-semibold text-primary hover:bg-primary/[0.1] transition-colors"
      >
        Back to dashboard
      </Link>
    </div>
  );
}
