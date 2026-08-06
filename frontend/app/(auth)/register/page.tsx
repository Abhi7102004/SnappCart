"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useDispatch, useSelector } from "react-redux"
import { motion, AnimatePresence } from "framer-motion"
import { Eye, EyeOff, Zap, Mail, CheckCircle2 } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import { registerUser, clearAuthError } from "@/store/slices/authSlice"
import { OAuthButtons } from "@/components/auth/OAuthButtons"

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

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-sm rounded-2xl border border-border bg-card p-8"
    >
      <AnimatePresence mode="wait">
        {registered ? (
          <motion.div
            key="success"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center text-center py-4"
          >
            <div className="p-3 rounded-full bg-green-500/10 text-green-500 mb-4">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h1 className="text-lg font-bold mb-2">Check your email</h1>
            <p className="text-sm text-muted-foreground leading-relaxed mb-6">
              We&apos;ve sent a verification link to <b>{email}</b>. Click it to activate your account.
            </p>
            <Link
              href="/login"
              className="text-sm text-primary font-medium hover:underline flex items-center gap-1.5"
            >
              <Mail className="h-3.5 w-3.5" />
              Back to login
            </Link>
          </motion.div>
        ) : (
          <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex flex-col items-center mb-6">
              <div className="p-2 rounded-xl bg-primary mb-3">
                <Zap className="h-5 w-5 text-primary-foreground" />
              </div>
              <h1 className="text-xl font-bold">Create your account</h1>
              <p className="text-sm text-muted-foreground mt-1">Join SnappCart and start shopping</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Full name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Abhishek Kumar"
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Email</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Password</label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 8 characters"
                    className="w-full h-10 rounded-lg border border-border bg-background px-3 pr-10 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <p className="text-xs text-muted-foreground">
                  One uppercase, one lowercase, one number
                </p>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">Confirm password</label>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Re-enter password"
                  className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                />
              </div>

              {error && (
                <p className="text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2">
                  {error}
                </p>
              )}

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isRegisterLoading}
                className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {isRegisterLoading ? "Creating account..." : "Create Account"}
              </motion.button>
            </form>

            <div className="flex items-center gap-3 my-6">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs text-muted-foreground">or continue with</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            <OAuthButtons />

            <p className="text-center text-sm text-muted-foreground mt-6">
              Already have an account?{" "}
              <Link href="/login" className="text-primary font-medium hover:underline">
                Log in
              </Link>
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}