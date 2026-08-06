"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter, useSearchParams } from "next/navigation"
import { useDispatch, useSelector } from "react-redux"
import { motion } from "framer-motion"
import { Eye, EyeOff, Zap, XCircle } from "lucide-react"
import { toast } from "sonner"

import type { AppDispatch, RootState } from "@/store"
import { resetPassword } from "@/store/slices/authSlice"

export default function ResetPasswordPage() {
  const dispatch = useDispatch<AppDispatch>()
  const router = useRouter()
  const searchParams = useSearchParams()
  const token = searchParams.get("token")
  const { isResetPasswordLoading } = useSelector((state: RootState) => state.auth)

  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [localError, setLocalError] = useState("")

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError("")

    if (password !== confirmPassword) {
      setLocalError("Passwords don't match")
      return
    }
    if (!token) {
      setLocalError("Missing reset token")
      return
    }

    const result = await dispatch(resetPassword({ token, new_password: password }))

    if (resetPassword.fulfilled.match(result)) {
      toast.success("Password reset! Please log in.")
      router.push("/login")
    } else {
      setLocalError((result.payload as string) || "Reset failed")
    }
  }

  if (!token) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center"
      >
        <div className="p-3 rounded-full bg-destructive/10 text-destructive mb-4 inline-flex">
          <XCircle className="h-8 w-8" />
        </div>
        <h1 className="text-lg font-bold mb-2">Invalid link</h1>
        <p className="text-sm text-muted-foreground mb-6">
          This password reset link is missing its token.
        </p>
        <Link href="/forgot-password" className="text-sm text-primary font-medium hover:underline">
          Request a new link
        </Link>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-sm rounded-2xl border border-border bg-card p-8"
    >
      <div className="flex flex-col items-center mb-6">
        <div className="p-2 rounded-xl bg-primary mb-3">
          <Zap className="h-5 w-5 text-primary-foreground" />
        </div>
        <h1 className="text-xl font-bold">Set a new password</h1>
        <p className="text-sm text-muted-foreground mt-1">Choose a strong new password</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="text-sm font-medium">New password</label>
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
          <p className="text-xs text-muted-foreground">One uppercase, one lowercase, one number</p>
        </div>

        <div className="space-y-1.5">
          <label className="text-sm font-medium">Confirm new password</label>
          <input
            type={showPassword ? "text" : "password"}
            required
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            placeholder="Re-enter password"
            className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
          />
        </div>

        {localError && (
          <p className="text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2">
            {localError}
          </p>
        )}

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.98 }}
          type="submit"
          disabled={isResetPasswordLoading}
          className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
        >
          {isResetPasswordLoading ? "Resetting..." : "Reset Password"}
        </motion.button>
      </form>
    </motion.div>
  )
}