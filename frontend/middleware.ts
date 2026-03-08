import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const VALID_PATHS = new Set([
  "/dashboard",
  "/decision",
  "/approve",
  "/audit-logs",
  "/governance",
  "/monitoring",
  "/analytics",
]);

const REDIRECT_TO_DASHBOARD = new Set([
  "/",
  "",
  "/AuditSentinel",
  "/auditsentinel",
]);

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (REDIRECT_TO_DASHBOARD.has(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  if (
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  const base = "/" + pathname.split("/").filter(Boolean)[0];
  if (VALID_PATHS.has(base)) {
    return NextResponse.next();
  }

  return NextResponse.redirect(new URL("/dashboard", request.url));
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
