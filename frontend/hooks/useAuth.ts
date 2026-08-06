// hooks/useAuth.ts
import { useSelector } from "react-redux"
import type { RootState } from "@/store"

/**
 * Small convenience hook — avoids repeating
 * useSelector((state: RootState) => state.auth) across every
 * component that needs auth info (Navbar, ProductPage's "buy" button, etc.)
 */
export function useAuth() {
  const auth = useSelector((state: RootState) => state.auth)
  return {
    user: auth.user,
    isLoggedIn: auth.isLoggedIn,
    isLoading: auth.isFetchMeLoading || auth.isLoginLoading,
  }
}