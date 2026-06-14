// app/loading.tsx
"use client"

import { motion } from "framer-motion"
import { Zap } from "lucide-react"

export default function Loading() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <motion.div
        className="h-14 w-14 rounded-2xl bg-primary flex items-center justify-center"
        animate={{
          scale: [1, 1.1, 1],
          rotate: [0, 10, -10, 0],
        }}
        transition={{
          duration: 1.5,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      >
        <Zap className="h-7 w-7 text-primary-foreground" />
      </motion.div>

      <motion.p
        className="text-sm text-muted-foreground"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        Loading SnappCart...
      </motion.p>
    </div>
  )
}