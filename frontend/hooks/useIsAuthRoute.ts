import { usePathname } from "next/navigation"

export function useIsAuthRoute() {
    const pathname = usePathname()
    return ["/login", "/register", "/forgot-password",
            "/reset-password", "/verify-email", "/oauth"]
      .some((route) => pathname.startsWith(route))
  }