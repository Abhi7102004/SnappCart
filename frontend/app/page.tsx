import Link from "next/link"
import { HealthCheck } from "@/types/api"
import {
  CheckCircle2,
  XCircle,
  Zap,
  ShoppingBag,
  Truck,
  Shield,
  Sparkles,
} from "lucide-react"

async function getHealthStatus(): Promise<HealthCheck | null> {
  try {
    const apiUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL
    const res = await fetch(`${apiUrl}/api/v1/health`, { cache: "no-store" })
    return res.json()
  } catch {
    return null
  }
}

export default async function HomePage() {
  const health = await getHealthStatus()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-linear-to-b from-primary/5 via-background to-background py-20 px-4">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-primary/5 blur-3xl" />
          <div className="absolute -bottom-20 -left-20 w-72 h-72 rounded-full bg-primary/5 blur-3xl" />
        </div>

        <div className="container mx-auto max-w-4xl text-center relative">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            Trusted shopping with fast delivery and great deals.
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 bg-linear-to-b from-foreground to-foreground/60 bg-clip-text text-transparent">
            Shop Smarter with{" "}
            <span className="text-primary">SnappCart</span>
          </h1>

          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed">
            Discover millions of products from verified sellers. Fast
            delivery, secure payments, and AI-powered recommendations.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link
              href="/products"
              className="inline-flex items-center justify-center gap-2 px-8 py-3 rounded-full bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-all hover:scale-105 active:scale-95"
            >
              <ShoppingBag className="h-4 w-4" />
              Start Shopping
            </Link>

            <Link
              href="/register"
              className="inline-flex items-center justify-center gap-2 px-8 py-3 rounded-full border border-border bg-background hover:bg-muted transition-all hover:scale-105 active:scale-95 font-medium"
            >
              <Zap className="h-4 w-4" />
              Become a Seller
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4 border-y border-border/50 bg-muted/20">
        <div className="container mx-auto max-w-5xl">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: <Truck className="h-6 w-6" />,
                title: "Fast Delivery",
                desc: "Same day delivery available in 100+ cities across India",
              },
              {
                icon: <Shield className="h-6 w-6" />,
                title: "Secure Payments",
                desc: "Razorpay, Stripe, UPI, COD — pay your way, always safe",
              },
              {
                icon: <Sparkles className="h-6 w-6" />,
                title: "AI Powered",
                desc: "Smart recommendations and search powered by Gemini AI",
              },
            ].map((feature, index) => (
              <div
                key={index}
                className="flex flex-col items-center text-center gap-3 p-6 rounded-2xl hover:bg-background transition-colors group"
              >
                <div className="p-3 rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all">
                  {feature.icon}
                </div>

                <h3 className="font-semibold text-base">
                  {feature.title}
                </h3>

                <p className="text-sm text-muted-foreground leading-relaxed">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Backend Status */}
      {health && (
        <section className="py-12 px-4">
          <div className="container mx-auto max-w-md">
            <div className="rounded-2xl border border-border bg-card p-6 space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="font-semibold text-sm">
                  System Status
                </h2>

                <span
                  className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                    health?.status === "healthy"
                      ? "bg-green-500/10 text-green-600 dark:text-green-400"
                      : "bg-yellow-500/10 text-yellow-600"
                  }`}
                >
                  {health?.status === "healthy"
                    ? "All Systems Operational"
                    : "Degraded"}
                </span>
              </div>

              <div className="space-y-2">
                {Object.entries(health.services).map(
                  ([service, status]) => (
                    <div
                      key={service}
                      className="flex items-center justify-between py-2 border-b border-border/50 last:border-0"
                    >
                      <span className="text-sm capitalize text-muted-foreground">
                        {service}
                      </span>

                      <div className="flex items-center gap-1.5">
                        {status ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-destructive" />
                        )}

                        <span
                          className={`text-xs font-medium ${
                            status
                              ? "text-green-500"
                              : "text-destructive"
                          }`}
                        >
                          {status ? "Online" : "Offline"}
                        </span>
                      </div>
                    </div>
                  )
                )}
              </div>

              <p className="text-xs text-muted-foreground">
                v{health.version} · {health.environment}
              </p>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}