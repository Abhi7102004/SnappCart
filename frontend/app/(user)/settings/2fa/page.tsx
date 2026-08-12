// app/(user)/settings/2fa/page.tsx
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { QRCodeSVG } from "qrcode.react";
import { Shield, Copy, Check, Eye, EyeOff } from "lucide-react";
import { toast } from "sonner";

import { api } from "@/lib/axios";
import { useAuth } from "@/hooks/useAuth";
import { getApiError } from "@/lib/api-error";
import {
  TwoFactorSetupResponse,
  TwoFactorConfirmResponse,
} from "@/types/two-factor";

type Step = "idle" | "setup" | "confirm" | "backup_codes";

export default function TwoFactorSettingsPage() {
  const { user } = useAuth();
  const twoFactorEnabled = (user as typeof user & { two_factor_enabled: boolean })?.two_factor_enabled ?? false;
  const [step, setStep] = useState<Step>("idle");
  const [setupData, setSetupData] = useState<TwoFactorSetupResponse | null>(
    null
  );
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [code, setCode] = useState("");
  const [disableCode, setDisableCode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showSecret, setShowSecret] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [savedConfirmed, setSavedConfirmed] = useState(false);

  // Only sellers and admins can use 2FA (Day 36 decision)
  if (!user || user.role === "customer") {
    return (
      <div className="max-w-md mx-auto py-12 text-center">
        <Shield className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
        <p className="text-muted-foreground text-sm">
          Two-factor authentication is available for seller and admin accounts.
        </p>
      </div>
    );
  }

  const handleSetup = async () => {
    setIsLoading(true);
    try {
      const { data } = await api.post<TwoFactorSetupResponse>(
        "/auth/2fa/setup"
      );
      setSetupData(data);
      setStep("setup");
    } catch (e) {
      toast.error(getApiError(e));
    } finally {
      setIsLoading(false);
    }
  };

  const handleConfirm = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const { data } = await api.post<TwoFactorConfirmResponse>(
        "/auth/2fa/confirm",
        { code }
      );
      setBackupCodes(data.backup_codes);
      setStep("backup_codes");
      toast.success("2FA enabled!");
    } catch (e) {
      toast.error(getApiError(e));
    } finally {
      setIsLoading(false);
      setCode("");
    }
  };

  const handleDisable = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await api.post("/auth/2fa/disable", { code: disableCode });
      toast.success("2FA disabled");
      setDisableCode("");
      // Force page refresh to update twoFactorEnabled state
      window.location.reload();
    } catch (e) {
      toast.error(getApiError(e));
    } finally {
      setIsLoading(false);
    }
  };

  const copyCode = (code: string, index: number) => {
    navigator.clipboard.writeText(code);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  const copyAllCodes = () => {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    toast.success("All backup codes copied!");
  };

  return (
    <div className="max-w-md mx-auto py-8 px-4">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-2 rounded-xl bg-primary/10 text-primary">
          <Shield className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-bold">Two-Factor Authentication</h1>
          <p className="text-sm text-muted-foreground">
            {twoFactorEnabled
              ? "Currently enabled"
              : "Currently disabled"}
          </p>
        </div>
        <div
          className={`ml-auto h-2 w-2 rounded-full ${
            twoFactorEnabled ? "bg-green-500" : "bg-muted"
          }`}
        />
      </div>

      <AnimatePresence mode="wait">
        {/* ── IDLE: not yet enabled ── */}
        {step === "idle" && !twoFactorEnabled && (
          <motion.div
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-2xl border border-border p-6 space-y-4"
          >
            <p className="text-sm text-muted-foreground leading-relaxed">
              Add an extra layer of security to your account. After setup,
              you&apos;ll need your authenticator app every time you log in.
            </p>
            <motion.button
              whileHover={{ scale: 1.01 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSetup}
              disabled={isLoading}
              className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
            >
              {isLoading ? "Setting up..." : "Enable 2FA"}
            </motion.button>
          </motion.div>
        )}

        {/* ── SETUP: show QR code ── */}
        {step === "setup" && setupData && (
          <motion.div
            key="setup"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <div className="rounded-2xl border border-border p-6 space-y-4">
              <p className="text-sm font-medium">
                Step 1 — Scan this QR code with your authenticator app
              </p>
              <div className="flex justify-center p-4 bg-white rounded-xl">
                <QRCodeSVG value={setupData.otpauth_uri} size={180} />
              </div>

              <div className="space-y-1.5">
                <p className="text-xs text-muted-foreground">
                  Can&apos;t scan? Enter this code manually:
                </p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 text-xs bg-muted rounded-lg px-3 py-2 font-mono tracking-wider">
                    {showSecret
                      ? setupData.secret
                      : "•".repeat(setupData.secret.length)}
                  </code>
                  <button
                    onClick={() => setShowSecret((s) => !s)}
                    className="p-2 text-muted-foreground hover:text-foreground"
                  >
                    {showSecret ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            <form
              onSubmit={handleConfirm}
              className="rounded-2xl border border-border p-6 space-y-4"
            >
              <p className="text-sm font-medium">
                Step 2 — Enter the 6-digit code to confirm it worked
              </p>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                required
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                placeholder="000000"
                className="w-full h-12 rounded-lg border border-border bg-background px-4 text-center text-xl tracking-[0.4em] font-mono outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                autoFocus
              />
              <motion.button
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isLoading || code.length !== 6}
                className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
              >
                {isLoading ? "Verifying..." : "Confirm & Enable"}
              </motion.button>
            </form>
          </motion.div>
        )}

        {/* ── BACKUP CODES: shown once ── */}
        {step === "backup_codes" && (
          <motion.div
            key="backup"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border border-border p-6 space-y-4"
          >
            <div className="p-3 rounded-xl bg-amber-500/10 text-amber-600 dark:text-amber-400 text-sm">
              <p className="font-medium mb-1">Save these backup codes now</p>
              <p className="text-xs leading-relaxed">
                Each code works once if you lose access to your authenticator
                app. These won&apos;t be shown again.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2">
              {backupCodes.map((c, i) => (
                <button
                  key={i}
                  onClick={() => copyCode(c, i)}
                  className="flex items-center justify-between px-3 py-2 rounded-lg bg-muted text-sm font-mono hover:bg-muted/80 transition-colors group"
                >
                  <span className="tracking-wider">{c}</span>
                  {copiedIndex === i ? (
                    <Check className="h-3.5 w-3.5 text-green-500" />
                  ) : (
                    <Copy className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  )}
                </button>
              ))}
            </div>

            <button
              onClick={copyAllCodes}
              className="w-full text-sm text-primary hover:underline"
            >
              Copy all codes
            </button>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={savedConfirmed}
                onChange={(e) => setSavedConfirmed(e.target.checked)}
                className="mt-0.5"
              />
              <span className="text-sm text-muted-foreground">
                I&apos;ve saved my backup codes in a safe place
              </span>
            </label>

            <motion.button
              whileTap={{ scale: 0.98 }}
              disabled={!savedConfirmed}
              onClick={() => window.location.reload()}
              className="w-full h-10 rounded-full bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors disabled:opacity-60"
            >
              Done
            </motion.button>
          </motion.div>
        )}

        {/* ── ENABLED: disable option ── */}
        {step === "idle" && twoFactorEnabled && (
          <motion.div
            key="enabled"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-2xl border border-border p-6 space-y-4"
          >
            <p className="text-sm text-muted-foreground leading-relaxed">
              Your account is protected with two-factor authentication. To
              disable it, enter a code from your authenticator app.
            </p>
            <form onSubmit={handleDisable} className="space-y-3">
              <input
                type="text"
                inputMode="numeric"
                maxLength={10}
                required
                value={disableCode}
                onChange={(e) => setDisableCode(e.target.value)}
                placeholder="000000"
                className="w-full h-12 rounded-lg border border-border bg-background px-4 text-center text-xl tracking-[0.4em] font-mono outline-none focus:border-destructive/50 focus:ring-2 focus:ring-destructive/20 transition-all"
              />
              <motion.button
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isLoading || disableCode.length < 6}
                className="w-full h-10 rounded-full border border-destructive text-destructive text-sm font-medium hover:bg-destructive/10 transition-colors disabled:opacity-60"
              >
                {isLoading ? "Disabling..." : "Disable 2FA"}
              </motion.button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
