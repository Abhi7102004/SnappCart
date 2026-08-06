// components/auth/AuthBootstrap.tsx
"use client"

import { useEffect, useRef } from "react"
import { useDispatch, useSelector } from "react-redux"
import type { AppDispatch, RootState } from "@/store"
import { fetchCurrentUser } from "@/store/slices/authSlice"

/**
 * Runs ONCE when the app loads (mounted in Providers, Day 32).
 *
 * Redux Persist rehydrates isLoggedIn/user from localStorage instantly,
 * but that data could be STALE (access token expired while tab was closed).
 * This component always re-verifies against the backend on load.
 *
 * If the access token is expired but the refresh token (httpOnly cookie)
 * is still valid, Day 30's axios interceptor transparently refreshes it —
 * the user never sees a flicker.
 *
 * If BOTH are invalid, the interceptor dispatches logout() automatically,
 * and this component's fetchCurrentUser().rejected case just no-ops.
 */
export function AuthBootstrap({ children }: { children: React.ReactNode }) {
  const dispatch = useDispatch<AppDispatch>()
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn)
  const hasChecked = useRef(false)

  useEffect(() => {
    // Only verify if Redux Persist rehydrated a "logged in" state.
    // A genuinely logged-out user has nothing to verify.
    if (isLoggedIn && !hasChecked.current) {
      hasChecked.current = true
      dispatch(fetchCurrentUser())
    }
  }, [isLoggedIn, dispatch])

  return <>{children}</>
}