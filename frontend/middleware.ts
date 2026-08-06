// middleware.ts
import { NextRequest, NextResponse } from "next/server"
import { PROTECTED_ROUTE_PREFIXES, AUTH_ONLY_ROUTES, REFRESH_COOKIE_NAME } from "@/lib/constants"

/**
 * Edge middleware — FAST, CHEAP first filter only.
 * Cannot verify JWT signature (no access to jose/secret key here
 * without duplicating backend logic). Just checks cookie PRESENCE.
 *
 * Real verification happens client-side via fetchCurrentUser()
 * on app load (see components/auth/AuthBootstrap.tsx below).
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const hasRefreshCookie = request.cookies.has(REFRESH_COOKIE_NAME)

  const isProtectedRoute = PROTECTED_ROUTE_PREFIXES.some((prefix) =>
    pathname.startsWith(prefix)
  )
  const isAuthOnlyRoute = AUTH_ONLY_ROUTES.some((route) =>
    pathname.startsWith(route)
  )

  if (isProtectedRoute && !hasRefreshCookie) {
    const loginUrl = new URL("/login", request.url)
    loginUrl.searchParams.set("redirect", pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isAuthOnlyRoute && hasRefreshCookie) {
    return NextResponse.redirect(new URL("/", request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Run on all paths except static files, images, and API routes
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
}