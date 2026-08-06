// app/(auth)/verify-email/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { motion } from "framer-motion";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { toast } from "sonner";

import type { AppDispatch, RootState } from "@/store";
import { verifyEmail, resendVerificationEmail } from "@/store/slices/authSlice";

type Status = "verifying" | "success" | "error";

export default function VerifyEmailPage() {
  const dispatch = useDispatch<AppDispatch>();
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const { isResendVerificationLoading } = useSelector(
    (state: RootState) => state.auth
  );

  const [status, setStatus] = useState<Status>("verifying");
  const [message, setMessage] = useState("");
  const [resendEmail, setResendEmail] = useState("");
  const [resendSent, setResendSent] = useState(false);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("No verification token provided.");
      return;
    }

    dispatch(verifyEmail(token)).then((result) => {
      if (verifyEmail.fulfilled.match(result)) {
        setStatus("success");
        setMessage(result.payload.message);
      } else {
        setStatus("error");
        setMessage((result.payload as string) || "Verification failed");
      }
    });
  }, [token, dispatch]);

  const handleResend = async (e: React.FormEvent) => {
    e.preventDefault();
    const result = await dispatch(resendVerificationEmail(resendEmail));
    if (resendVerificationEmail.rejected.match(result)) {
      toast.error((result.payload as string) || "Something went wrong");
      return;
    }
    setResendSent(true);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full max-w-sm rounded-2xl border border-border bg-card p-8 text-center"
    >
      {status === "verifying" && (
        <>
          <div className="p-3 rounded-full bg-primary/10 text-primary mb-4 inline-flex">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
          <h1 className="text-lg font-bold">Verifying your email...</h1>
        </>
      )}

      {status === "success" && (
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }}>
          <div className="p-3 rounded-full bg-green-500/10 text-green-500 mb-4 inline-flex">
            <CheckCircle2 className="h-8 w-8" />
          </div>
          <h1 className="text-lg font-bold mb-2">Email verified!</h1>
          <p className="text-sm text-muted-foreground mb-6">{message}</p>
          <Link
            href="/login"
            className="inline-flex items-center justify-center h-10 px-6 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            Log In
          </Link>
        </motion.div>
      )}

      {status === "error" && (
        <motion.div initial={{ scale: 0.9 }} animate={{ scale: 1 }}>
          <div className="p-3 rounded-full bg-destructive/10 text-destructive mb-4 inline-flex">
            <XCircle className="h-8 w-8" />
          </div>
          <h1 className="text-lg font-bold mb-2">Verification failed</h1>
          <p className="text-sm text-muted-foreground mb-6">{message}</p>

          {!resendSent ? (
            <form onSubmit={handleResend} className="space-y-3">
              <input
                type="email"
                required
                value={resendEmail}
                onChange={(e) => setResendEmail(e.target.value)}
                placeholder="Enter your email to resend"
                className="w-full h-10 rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
              />
              <button
                type="submit"
                disabled={isResendVerificationLoading}
                className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {isResendVerificationLoading
                  ? "Sending..."
                  : "Resend Verification Email"}
              </button>
            </form>
          ) : (
            <p className="text-sm text-muted-foreground">
              If that email exists, a new link has been sent. Check your inbox.
            </p>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
