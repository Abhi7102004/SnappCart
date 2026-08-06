"use client"

import { useSelector } from "react-redux"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import type { RootState } from "@/store"

/**
 * Guards ALL routes inside (user)/ — profile, orders, wishlist, wallet, settings.
 * middleware.ts already did a cheap cookie-presence check before this
 * even rendered. This is the CLIENT-SIDE confirmation using real Redux state,
 * which by now has been verified/refreshed by AuthBootstrap.
 */
export default function UserLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { isLoggedIn, isFetchMeLoading } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    if (!isFetchMeLoading && !isLoggedIn) {
      router.replace("/login")
    }
  }, [isLoggedIn, isFetchMeLoading, router])

  if (isFetchMeLoading || !isLoggedIn) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="h-6 w-6 rounded-full border-2 border-primary border-t-transparent animate-spin" />
      </div>
    )
  }

  return <>{children}</>
}