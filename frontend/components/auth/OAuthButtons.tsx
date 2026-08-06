"use client"

import { FaGoogle, FaGithub } from "react-icons/fa"
import { motion } from "framer-motion"

export function OAuthButtons() {
  return (
    <div className="grid grid-cols-2 gap-3">
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        type="button"
        className="flex items-center justify-center gap-2 h-10 rounded-full border border-border text-sm font-medium hover:bg-muted transition-colors"
      >
        <FaGoogle className="h-3.5 w-3.5" />
        Google
      </motion.button>
      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        type="button"
        className="flex items-center justify-center gap-2 h-10 rounded-full border border-border text-sm font-medium hover:bg-muted transition-colors"
      >
        <FaGithub className="h-3.5 w-3.5" />
        GitHub
      </motion.button>
    </div>
  )
}