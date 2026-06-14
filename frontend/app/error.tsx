// app/error.tsx
"use client"

import { useEffect } from "react"
import { AlertTriangle, RefreshCw, Home } from "lucide-react"
import Link from "next/link"
import { motion } from "framer-motion"

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error("Application error:", error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] px-4 text-center">
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 200 }}
        className="p-4 rounded-2xl bg-destructive/10 text-destructive mb-6"
      >
        <AlertTriangle className="h-10 w-10" />
      </motion.div>

      <h1 className="text-2xl font-bold mb-2">Something went wrong</h1>
      <p className="text-muted-foreground max-w-md mb-8 leading-relaxed">
        We hit an unexpected error while loading this page.
        Don&apos;t worry, your cart and account are safe.
      </p>

      <div className="flex flex-col sm:flex-row gap-3">
        <button
          onClick={reset}
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all hover:scale-105 active:scale-95"
        >
          <RefreshCw className="h-4 w-4" />
          Try Again
        </button>
        <Link
          href="/"
          className="inline-flex items-center justify-center gap-2 px-6 py-2.5 rounded-full border border-border hover:bg-muted font-medium transition-all hover:scale-105 active:scale-95"
        >
          <Home className="h-4 w-4" />
          Go Home
        </Link>
      </div>

      {process.env.NODE_ENV === "development" && (
        <details className="mt-8 max-w-lg text-left">
          <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
            Error details (dev only)
          </summary>
          <pre className="mt-2 p-3 rounded-lg bg-muted text-xs overflow-auto text-destructive">
            {error.message}
            {error.stack}
          </pre>
        </details>
      )}
    </div>
  )
}