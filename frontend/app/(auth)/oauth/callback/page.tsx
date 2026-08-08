"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useDispatch } from "react-redux"
import { motion } from "framer-motion"
import { Loader2, XCircle } from "lucide-react"

import type { AppDispatch } from "@/store"
import { updateAccessToken, fetchCurrentUser } from "@/store/slices/authSlice"

const ERROR_MESSAGES: Record<string, string> = {
  access_denied: "You cancelled the sign-in. No worries — try again anytime.",
  missing_params: "Something went wrong starting sign-in. Please try again.",
  oauth_failed: "Something went wrong signing you in. Please try again.",
}

export default function OAuthCallbackPage() {
  const dispatch = useDispatch<AppDispatch>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const errorCode = searchParams.get("error")
    if (errorCode) {
      setError(ERROR_MESSAGES[errorCode] || ERROR_MESSAGES.oauth_failed)
      return
    }

    const hash = window.location.hash
    const params = new URLSearchParams(hash.replace("#", ""))
    const token = params.get("access_token")

    if (!token) {
      setError("No access token received. Please try again.")
      return
    }

    dispatch(updateAccessToken(token))

    dispatch(fetchCurrentUser()).then((result) => {
      window.history.replaceState(null, "", "/oauth/callback")

      if (fetchCurrentUser.fulfilled.match(result)) {
        router.replace("/")
      } else {
        setError("Signed in, but couldn't load your profile. Please try logging in again.")
      }
    })
  }, [dispatch, router, searchParams])

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center shadow-sm"
    >
      {!error ? (
        <>
          <div className="mb-4 inline-flex rounded-full bg-primary/10 p-3 text-primary">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
          <h1 className="text-lg font-bold tracking-tight">Signing you in…</h1>
          <p className="mt-1 text-sm text-muted-foreground">This only takes a moment.</p>
        </>
      ) : (
        <>
          <div className="mb-4 inline-flex rounded-full bg-destructive/10 p-3 text-destructive">
            <XCircle className="h-8 w-8" />
          </div>
          <h1 className="mb-2 text-lg font-bold tracking-tight">Sign-in failed</h1>
          <p className="mb-6 text-sm text-muted-foreground">{error}</p>
          <Link
            href="/login"
            className="inline-flex h-11 items-center justify-center rounded-xl bg-primary px-6 text-sm font-semibold text-primary-foreground transition-colors hover:bg-primary/90"
          >
            Back to Login
          </Link>
        </>
      )}
    </motion.div>
  )
}