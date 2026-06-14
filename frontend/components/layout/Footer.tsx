// components/layout/Footer.tsx
"use client"

import Link from "next/link"
import {
  Zap, Mail, Shield, Truck, CreditCard, Award, ArrowRight
} from "lucide-react"
import {
  FaFacebookF, FaTwitter, FaInstagram, FaYoutube
} from "react-icons/fa"
import { motion } from "framer-motion"

const footerLinks = {
  shop: [
    { label: "All Products", href: "/products" },
    { label: "Categories", href: "/categories" },
    { label: "Deals & Offers", href: "/deals" },
    { label: "New Arrivals", href: "/products?sort=newest" },
  ],
  account: [
    { label: "My Profile", href: "/profile" },
    { label: "Order History", href: "/orders" },
    { label: "Wishlist", href: "/wishlist" },
    { label: "Wallet & Rewards", href: "/wallet" },
  ],
  support: [
    { label: "Help Center", href: "/help" },
    { label: "Track Order", href: "/orders" },
    { label: "Returns & Refunds", href: "/help/returns" },
    { label: "Contact Us", href: "/contact" },
  ],
  company: [
    { label: "About SnappCart", href: "/about" },
    { label: "Become a Seller", href: "/seller/register" },
    { label: "Privacy Policy", href: "/legal/privacy" },
    { label: "Terms of Service", href: "/legal/terms" },
  ],
}

const trustBadges = [
  { icon: Shield, label: "Secure Payments" },
  { icon: Truck, label: "Fast Delivery" },
  { icon: CreditCard, label: "Easy Returns" },
  { icon: Award, label: "Verified Sellers" },
]

const socialLinks = [
    { icon: FaFacebookF, href: "#", label: "Facebook" },
    { icon: FaTwitter, href: "#", label: "Twitter" },
    { icon: FaInstagram, href: "#", label: "Instagram" },
    { icon: FaYoutube, href: "#", label: "YouTube" },
  ]

export default function Footer() {
  return (
    <footer className="border-t border-border/50 bg-muted/20 mt-auto">

      {/* Trust badges strip */}
      <div className="border-b border-border/50">
        <div className="container mx-auto px-4 py-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {trustBadges.map((badge, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="flex items-center gap-3 justify-center md:justify-start"
              >
                <div className="p-2 rounded-lg bg-primary/10 text-primary">
                  <badge.icon className="h-4 w-4" />
                </div>
                <span className="text-sm font-medium">{badge.label}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Main footer content */}
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-2 md:grid-cols-6 gap-8">

          {/* Brand + Newsletter */}
          <div className="col-span-2 md:col-span-2 space-y-4">
            <Link href="/" className="flex items-center gap-2 group">
              <motion.div
                className="p-1.5 rounded-xl bg-primary"
                whileHover={{ rotate: 12, scale: 1.05 }}
                transition={{ type: "spring", stiffness: 400 }}
              >
                <Zap className="h-5 w-5 text-primary-foreground" />
              </motion.div>
              <span className="font-bold text-lg">SnappCart</span>
            </Link>

            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">
              Your one-stop shop for everything. Discover millions of
              products from verified sellers with AI-powered recommendations.
            </p>

            {/* Newsletter */}
            <div className="space-y-2 pt-2">
              <p className="text-sm font-medium">Get price drop alerts</p>
              <form className="flex gap-2 max-w-sm">
                <div className="relative flex-1">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="email"
                    placeholder="Enter your email"
                    className="w-full h-10 rounded-full border border-border bg-background pl-10 pr-4 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20 transition-all"
                  />
                </div>
                <motion.button
                  type="submit"
                  whileHover={{ scale: 1.08 }}
                  whileTap={{ scale: 0.92 }}
                  className="h-10 w-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 transition-colors shrink-0"
                >
                  <ArrowRight className="h-4 w-4" />
                </motion.button>
              </form>
            </div>
          </div>

          {/* Link Columns */}
          <FooterColumn title="Shop" links={footerLinks.shop} />
          <FooterColumn title="Account" links={footerLinks.account} />
          <FooterColumn title="Support" links={footerLinks.support} />
          <FooterColumn title="Company" links={footerLinks.company} />
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-border/50">
        <div className="container mx-auto px-4 py-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} SnappCart. All rights reserved.
          </p>

          {/* Social links */}
          <div className="flex items-center gap-2">
          {socialLinks.map((social, i) => (
            <motion.a
                key={i}
                href={social.href}
                aria-label={social.label}
                whileHover={{ scale: 1.15, rotate: 5 }}
                whileTap={{ scale: 0.9 }}
                className="p-2 rounded-full hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
            >
                <social.icon className="h-3.5 w-3.5" />
            </motion.a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}

function FooterColumn({
  title, links
}: {
  title: string
  links: { label: string; href: string }[]
}) {
  return (
    <div>
      <h3 className="font-semibold text-sm mb-4">{title}</h3>
      <ul className="space-y-2.5">
        {links.map((link, i) => (
          <li key={i}>
            <Link href={link.href}>
              <motion.span
                whileHover={{ x: 3 }}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors inline-block"
              >
                {link.label}
              </motion.span>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}