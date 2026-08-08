"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useDispatch, useSelector } from "react-redux"
import { motion } from "framer-motion"
import { Eye, EyeOff, Mail, Lock, Zap, ArrowRight } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import { loginUser, clearAuthError } from "@/store/slices/authSlice"
import { OAuthButtons } from "@/components/auth/OAuthButtons"

export default function LoginPage() {
  const dispatch = useDispatch<AppDispatch>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const { isLoginLoading, error } = useSelector((state: RootState) => state.auth)

  const [emailOrPhone, setEmailOrPhone] = useState("")
  const [password, setPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)

  useEffect(() => {
    dispatch(clearAuthError())
  }, [dispatch])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(clearAuthError())

    const result = await dispatch(loginUser({ email_or_phone: emailOrPhone, password }))

    if (loginUser.fulfilled.match(result)) {
      toast.success("Welcome back!")
      const redirectTo = searchParams.get("redirect") || "/"
      router.push(redirectTo)
    } else {
      toast.error((result.payload as string) || "Login failed")
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-lg rounded-2xl border border-border bg-card p-8 shadow-xl shadow-black/5"
    >
      <div className="mb-7">
        <div className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-violet-600 text-white">
          <Zap className="h-5 w-5" />
        </div>
        <h1 className="text-2xl font-bold tracking-tight">Welcome back</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">
          Log in to your SnappCart account to continue.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label htmlFor="emailOrPhone" className="text-sm font-medium">
            Email or phone
          </label>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              id="emailOrPhone"
              type="text"
              required
              value={emailOrPhone}
              onChange={(e) => setEmailOrPhone(e.target.value)}
              placeholder="you@example.com"
              className="h-11 w-full rounded-xl border border-border bg-background pl-10 pr-3 text-sm outline-none transition-all focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex items-center justify-between">
            <label htmlFor="password" className="text-sm font-medium">
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
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              className="h-11 w-full rounded-xl border border-border bg-background pl-10 pr-10 text-sm outline-none transition-all focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
            />
            <button
              type="button"
              aria-label={showPassword ? "Hide password" : "Show password"}
              onClick={() => setShowPassword((s) => !s)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
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
        <span className="text-xs text-muted-foreground">or continue with</span>
        <div className="h-px flex-1 bg-border" />
      </div>

      <OAuthButtons />

      <p className="mt-7 text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-semibold text-violet-600 hover:underline dark:text-violet-400">
          Sign up
        </Link>
      </p>
    </motion.div>
  )
}