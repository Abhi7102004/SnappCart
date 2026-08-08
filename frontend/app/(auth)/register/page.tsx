"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useDispatch, useSelector } from "react-redux"
import { motion, AnimatePresence } from "framer-motion"
import { Eye, EyeOff, Zap, Mail, CheckCircle2, User, Lock, Check, ArrowRight } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import { registerUser, clearAuthError } from "@/store/slices/authSlice"
import { OAuthButtons } from "@/components/auth/OAuthButtons"

/** Presentational only — read-only score from the current password value. */
function passwordStrength(pw: string) {
  if (!pw) return { score: 0, label: "", color: "", bar: "" }
  let score = 0
  if (pw.length >= 8) score++
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++
  if (/\d/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++

  return {
    score,
    ...[
      { label: "Too weak", color: "text-red-500", bar: "bg-red-500" },
      { label: "Weak", color: "text-red-500", bar: "bg-red-500" },
      { label: "Fair", color: "text-amber-500", bar: "bg-amber-500" },
      { label: "Good", color: "text-emerald-500", bar: "bg-emerald-500" },
      { label: "Strong", color: "text-emerald-600", bar: "bg-emerald-600" },
    ][score],
  }
}

export default function RegisterPage() {
  const dispatch = useDispatch<AppDispatch>()
  const { isRegisterLoading, error } = useSelector((state: RootState) => state.auth)

  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [registered, setRegistered] = useState(false)

  useEffect(() => {
    dispatch(clearAuthError())
  }, [dispatch])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    dispatch(clearAuthError())

    if (password !== confirmPassword) {
      toast.error("Passwords don't match")
      return
    }

    const result = await dispatch(
      registerUser({ email, password, full_name: fullName || undefined })
    )

    if (registerUser.fulfilled.match(result)) {
      setRegistered(true)
    } else {
      toast.error((result.payload as string) || "Registration failed")
    }
  }

  const strength = passwordStrength(password)
  const confirmMatches = confirmPassword.length > 0 && confirmPassword === password
  const confirmMismatch = confirmPassword.length > 0 && confirmPassword !== password

  const inputBase =
    "h-11 w-full rounded-xl border bg-background pl-10 text-sm outline-none transition-all"
  const inputOk =
    "border-border focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`w-full rounded-2xl border border-border bg-card p-8 shadow-xl shadow-black/5 ${
        registered ? "max-w-md" : "max-w-2xl"
      }`}
    >
      <AnimatePresence mode="wait">
        {registered ? (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center py-6 text-center"
          >
            <div className="mb-4 rounded-full bg-emerald-500/10 p-3 text-emerald-500">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h1 className="mb-2 text-xl font-bold tracking-tight">Check your email</h1>
            <p className="mb-6 text-sm leading-relaxed text-muted-foreground">
              We&apos;ve sent a verification link to{" "}
              <b className="text-foreground">{email}</b>. Click it to activate your account.
            </p>
            <Link
              href="/login"
              className="flex items-center gap-1.5 text-sm font-semibold text-violet-600 hover:underline dark:text-violet-400"
            >
              <Mail className="h-3.5 w-3.5" />
              Back to login
            </Link>
          </motion.div>
        ) : (
          <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="mb-7">
              <div className="mb-5 inline-flex h-11 w-11 items-center justify-center rounded-xl bg-violet-600 text-white">
                <Zap className="h-5 w-5" />
              </div>
              <h1 className="text-2xl font-bold tracking-tight">Create your account</h1>
              <p className="mt-1.5 text-sm text-muted-foreground">
                Join SnappCart and start shopping in minutes.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div className="grid grid-cols-1 items-start gap-x-5 gap-y-5 sm:grid-cols-2">
                {/* Full name */}
                <div className="space-y-1.5">
                  <label htmlFor="fullName" className="text-sm font-medium">Full name</label>
                  <div className="relative">
                    <User className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="fullName"
                      type="text"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="Abhishek Kumar"
                      className={`${inputBase} ${inputOk} pr-3`}
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="space-y-1.5">
                  <label htmlFor="email" className="text-sm font-medium">Email</label>
                  <div className="relative">
                    <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="email"
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      className={`${inputBase} ${inputOk} pr-3`}
                    />
                  </div>
                </div>

                {/* Password */}
                <div className="space-y-1.5">
                  <label htmlFor="password" className="text-sm font-medium">Password</label>
                  <div className="relative">
                    <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      required
                      minLength={8}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="At least 8 characters"
                      className={`${inputBase} ${inputOk} pr-10`}
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

                  {password ? (
                    <div className="pt-1">
                      <div className="flex gap-1">
                        {[0, 1, 2, 3].map((i) => (
                          <div
                            key={i}
                            className={`h-1 flex-1 rounded-full transition-colors ${
                              i < strength.score ? strength.bar : "bg-border"
                            }`}
                          />
                        ))}
                      </div>
                      <p className={`mt-1 text-xs font-medium ${strength.color}`}>{strength.label}</p>
                    </div>
                  ) : (
                    <p className="text-xs text-muted-foreground">
                      8+ chars, upper, lower &amp; number
                    </p>
                  )}
                </div>

                {/* Confirm password */}
                <div className="space-y-1.5">
                  <label htmlFor="confirmPassword" className="text-sm font-medium">Confirm password</label>
                  <div className="relative">
                    <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <input
                      id="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="Re-enter password"
                      className={`${inputBase} pr-10 ${
                        confirmMismatch
                          ? "border-destructive/60 focus:border-destructive/60 focus:ring-2 focus:ring-destructive/20"
                          : inputOk
                      }`}
                    />
                    {confirmMatches && (
                      <Check className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-emerald-500" />
                    )}
                  </div>
                  {confirmMismatch && (
                    <p className="text-xs font-medium text-destructive">Passwords don&apos;t match yet</p>
                  )}
                </div>
              </div>

              {error && (
                <p className="rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
              )}

              <button
                type="submit"
                disabled={isRegisterLoading}
                className="group flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-violet-600 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-violet-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {isRegisterLoading ? (
                  "Creating account..."
                ) : (
                  <>
                    Create account
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
              Already have an account?{" "}
              <Link href="/login" className="font-semibold text-violet-600 hover:underline dark:text-violet-400">
                Log in
              </Link>
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}