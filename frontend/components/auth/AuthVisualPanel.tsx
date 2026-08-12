"use client"

import Link from "next/link"
import { motion } from "framer-motion"
import { Zap, Truck, Shield, Sparkles } from "lucide-react"

const features = [
  { icon: Truck, title: "Fast Delivery", desc: "Same-day delivery in 100+ cities" },
  { icon: Shield, title: "Secure Payments", desc: "Razorpay, UPI, cards — always protected" },
  { icon: Sparkles, title: "AI Powered", desc: "Smart search & recommendations built in" },
]

export function AuthVisualPanel() {
  return (
    <div className="relative hidden w-1/2 overflow-hidden bg-gradient-to-br from-violet-600 via-violet-700 to-indigo-950 lg:flex">
      {/* Decorative blobs — same motif as homepage hero (Day 14) */}
      <motion.div
        className="absolute -left-24 -top-24 h-96 w-96 rounded-full bg-white/10 blur-3xl"
        animate={{ y: [0, 24, 0] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute bottom-0 right-0 h-[28rem] w-[28rem] rounded-full bg-fuchsia-400/10 blur-3xl"
        animate={{ y: [0, -24, 0] }}
        transition={{ duration: 9, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Subtle dot grid texture */}
      <div
        className="absolute inset-0 opacity-[0.07]"
        style={{
          backgroundImage: "radial-gradient(circle, white 1px, transparent 1px)",
          backgroundSize: "28px 28px",
        }}
      />

      <div className="relative z-10 flex w-full flex-col justify-between p-12 text-white">
        <Link href="/" className="inline-flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15 backdrop-blur">
            <Zap className="h-5 w-5" />
          </div>
          <span className="text-lg font-bold tracking-tight">SnappCart</span>
        </Link>

        <div className="max-w-sm">
          <h2 className="text-3xl font-bold leading-tight tracking-tight">
            Shop smarter,
            <br />
            not harder.
          </h2>
          <p className="mt-3 text-sm leading-relaxed text-white/70">
            Millions of products, verified sellers, and AI that actually helps you find what you need.
          </p>

          <div className="mt-10 space-y-5">
            {features.map((f) => (
              <div key={f.title} className="flex items-start gap-3">
                <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/10">
                  <f.icon className="h-4 w-4" />
                </div>
                <div>
                  <p className="text-sm font-semibold">{f.title}</p>
                  <p className="text-xs text-white/60">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <p className="text-xs text-white/40">© {new Date().getFullYear()} SnappCart</p>
      </div>
    </div>
  )
}