"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useDispatch, useSelector } from "react-redux"
import { motion } from "framer-motion"
import { Eye, EyeOff, Mail, Lock, Zap, ArrowRight } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import {
  loginUser,
  clearAuthError,
  clearTwoFactorState,
} from "@/store/slices/authSlice"
import { OAuthButtons } from "@/components/auth/OAuthButtons"
import { api } from "@/lib/axios"
import { isTwoFactorResponse } from "@/types/two-factor"
import type { TwoFactorVerifyRequest } from "@/types/two-factor"

export default function LoginPage() {
  const dispatch = useDispatch<AppDispatch>()
  const router = useRouter()
  const searchParams = useSearchParams()

  const {
    isLoginLoading,
    error,
    isTwoFactorRequired,
    pendingTwoFactorSession,
  } = useSelector((state: RootState) => state.auth)

  const [emailOrPhone, setEmailOrPhone] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  // ── 2FA state ─────────────────────────────────────────────
  const [twoFactorCode, setTwoFactorCode] = useState("")
  const [isTwoFactorLoading, setIsTwoFactorLoading] = useState(false)

  useEffect(() => {
    dispatch(clearAuthError())
  }, [dispatch])

  // ── Normal login ───────────────────────────────────────────
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(clearAuthError())

    const result = await dispatch(
      loginUser({
        email_or_phone: emailOrPhone,
        password,
      })
    )

    if (loginUser.fulfilled.match(result)) {
      // If 2FA is required, stay on this page.
      // The 2FA UI (isTwoFactorRequired) is driven by Redux state,
      // already set inside authSlice's fulfilled case.
      if (isTwoFactorResponse(result.payload)) {
        return
      }

      toast.success("Welcome back!")

      const redirectTo = searchParams.get("redirect") || "/"
      router.push(redirectTo)
    } else {
      toast.error((result.payload as string) || "Login failed")
    }
  }

  // ── 2FA verification ──────────────────────────────────────
  const handleTwoFactorSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!pendingTwoFactorSession) return

    setIsTwoFactorLoading(true)

    try {
      const { data } = await api.post(
        "/auth/2fa/verify",
        {
          session_token: pendingTwoFactorSession,
          code: twoFactorCode,
        } satisfies TwoFactorVerifyRequest
      )

      // Clear the temporary 2FA state
      dispatch(clearTwoFactorState())

      // Store the actual authenticated login response
      dispatch({
        type: "auth/login/fulfilled",
        payload: data,
      })

      toast.success("Welcome back!")

      const redirectTo = searchParams.get("redirect") || "/"
      router.push(redirectTo)
    } catch {
      toast.error("Invalid or expired code")
    } finally {
      setIsTwoFactorLoading(false)
    }
  }

  // ── 2FA SCREEN ─────────────────────────────────────────────
  if (isTwoFactorRequired) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 shadow-xl shadow-black/5"
      >
        <div className="flex flex-col items-center mb-6">
          <div className="p-2 rounded-xl bg-primary mb-3">
            <Zap className="h-5 w-5 text-primary-foreground" />
          </div>

          <h1 className="text-xl font-bold">
            Two-factor authentication
          </h1>

          <p className="text-sm text-muted-foreground mt-1 text-center">
            Enter the 6-digit code from your authenticator app
          </p>
        </div>

        <form
          onSubmit={handleTwoFactorSubmit}
          className="space-y-4"
        >
          <input
            type="text"
            inputMode="numeric"
            maxLength={10}
            required
            autoFocus
            value={twoFactorCode}
            onChange={(e) =>
              setTwoFactorCode(
                e.target.value.replace(/\s/g, "")
              )
            }
            placeholder="000000"
            className="w-full h-12 rounded-lg border border-border bg-background px-4 text-center text-xl tracking-[0.4em] font-mono outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
          />

          <p className="text-xs text-center text-muted-foreground">
            Or enter a 10-character backup code
          </p>

          <motion.button
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={
              isTwoFactorLoading ||
              twoFactorCode.length < 6
            }
            className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
          >
            {isTwoFactorLoading
              ? "Verifying..."
              : "Verify"}
          </motion.button>
        </form>

        <button
          type="button"
          onClick={() => {
            setTwoFactorCode("")
            dispatch(clearTwoFactorState())
          }}
          className="w-full text-center text-sm text-muted-foreground hover:text-foreground mt-4 transition-colors"
        >
          ← Back to login
        </button>
      </motion.div>
    )
  }

  // ── NORMAL LOGIN SCREEN ────────────────────────────────────
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 shadow-xl shadow-black/5"
    >
      <div className="flex flex-col items-center mb-6">
        <div className="p-2 rounded-xl bg-primary mb-3">
          <Zap className="h-5 w-5 text-primary-foreground" />
        </div>

        <h1 className="text-xl font-bold">
          Welcome back
        </h1>

        <p className="text-sm text-muted-foreground mt-1 text-center">
          Log in to your SnappCart account to continue.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label
            htmlFor="emailOrPhone"
            className="text-sm font-medium"
          >
            Email or phone
          </label>

          <div className="relative">
            <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            <input
              id="emailOrPhone"
              type="text"
              required
              value={emailOrPhone}
              onChange={(e) =>
                setEmailOrPhone(e.target.value)
              }
              placeholder="you@example.com"
              className="h-11 w-full rounded-xl border border-border bg-background pl-10 pr-3 text-sm outline-none transition-all focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label
              htmlFor="password"
              className="text-sm font-medium"
            >
              Password
            </label>

            <Link
              href="/forgot-password"
              className="text-xs font-medium text-violet-600 hover:underline dark:text-violet-400"
            >
              Forgot password?
            </Link>
          </div>

          <div className="relative">
            <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

            <input
              id="password"
              type={showPassword ? "text" : "password"}
              required
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              placeholder="Enter your password"
              className="h-11 w-full rounded-xl border border-border bg-background pl-10 pr-10 text-sm outline-none transition-all focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
            />

            <button
              type="button"
              aria-label={
                showPassword
                  ? "Hide password"
                  : "Show password"
              }
              onClick={() =>
                setShowPassword((s) => !s)
              }
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>

        {error && (
          <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={isLoginLoading}
          className="group flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-violet-600 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isLoginLoading ? (
            "Logging in..."
          ) : (
            <>
              Log in
              <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </>
          )}
        </button>
      </form>

      <div className="my-6 flex items-center gap-3">
        <div className="h-px flex-1 bg-border" />
        <span className="text-xs text-muted-foreground">
          or continue with
        </span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <OAuthButtons />

      <p className="mt-7 text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link
          href="/register"
          className="font-semibold text-violet-600 hover:underline dark:text-violet-400"
        >
          Sign up
        </Link>
      </p>
    </motion.div>
  )
}