// app/(auth)/forgot-password/page.tsx
"use client"

import { useState } from "react"
import Link from "next/link"
import { useDispatch, useSelector } from "react-redux"
import { motion, AnimatePresence } from "framer-motion"
import { Mail, Zap, ArrowLeft, CheckCircle2 } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import { forgotPassword } from "@/store/slices/authSlice"

export default function ForgotPasswordPage() {
  const dispatch = useDispatch<AppDispatch>()
  const { isForgotPasswordLoading } = useSelector((state: RootState) => state.auth)

  const [email, setEmail] = useState("")
  const [sent, setSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const result = await dispatch(forgotPassword(email))

    if (forgotPassword.rejected.match(result)) {
      toast.error((result.payload as string) || "Something went wrong")
      return
    }
    setSent(true)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-sm rounded-2xl border border-border bg-card p-8"
    >
      <AnimatePresence mode="wait">
        {sent ? (
          <motion.div
            key="sent"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center text-center py-4"
          >
            <div className="p-3 rounded-full bg-green-500/10 text-green-500 mb-4">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h1 className="text-lg font-bold mb-2">Check your email</h1>
            <p className="text-sm text-muted-foreground leading-relaxed mb-6">
              If an account exists for <b>{email}</b>, we&apos;ve sent a password reset link.
            </p>
            <Link href="/login" className="text-sm text-primary font-medium hover:underline">
              Back to login
            </Link>
          </motion.div>
        ) : (
          <motion.div key="form" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="flex flex-col items-center mb-6">
              <div className="p-2 rounded-xl bg-primary mb-3">
                <Zap className="h-5 w-5 text-primary-foreground" />
              </div>
              <h1 className="text-xl font-bold">Forgot password?</h1>
              <p className="text-sm text-muted-foreground mt-1 text-center">
                Enter your email and we&apos;ll send you a reset link
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full h-10 rounded-lg border border-border bg-background pl-10 pr-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.01 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isForgotPasswordLoading}
                className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {isForgotPasswordLoading ? "Sending..." : "Send Reset Link"}
              </motion.button>
            </form>

            <Link
              href="/login"
              className="flex items-center justify-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mt-6 transition-colors"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to login
            </Link>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}