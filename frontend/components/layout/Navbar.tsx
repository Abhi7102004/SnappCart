"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useSelector, useDispatch } from "react-redux"
import { RootState } from "@/store"
import { toggleCart } from "@/store/slices/uiSlice"
import { logout } from "@/store/slices/authSlice"
import {
  ShoppingCart, Search, Bell, Zap,
  User, Package, Heart, Wallet,
  Store, Shield, Settings, LogOut,
  Sun, Moon, X
} from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { motion, AnimatePresence } from "framer-motion"
import { useState, useEffect } from "react"
import { useTheme } from "next-themes"

export default function Navbar() {
  const dispatch = useDispatch()
  const router = useRouter()
  const { resolvedTheme, setTheme } = useTheme()
  const { isLoggedIn, user } = useSelector((state: RootState) => state.auth)
  const cartItems = useSelector((state: RootState) => state.cart.items)
  const unreadCount = useSelector((state: RootState) => state.notifications.unreadCount)
  const [scrolled, setScrolled] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)

  const cartCount = cartItems.reduce((sum, item) => sum + item.quantity, 0)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const getInitial = () => {
    if (user?.full_name) return user.full_name.charAt(0).toUpperCase()
    if (user?.email) return user.email.charAt(0).toUpperCase()
    if (user?.username) return user.username.charAt(0).toUpperCase()
    return "U"
  }

  const handleLogout = () => {
    dispatch(logout())
    router.push("/")
  }

  return (
    <>
      <motion.nav
        className={`sticky top-0 z-50 w-full transition-all duration-300 ${
          scrolled
            ? "bg-background/80 backdrop-blur-xl border-b border-border/50 shadow-sm"
            : "bg-background border-b border-border/30"
        }`}
        initial={{ y: 0 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="container mx-auto flex h-16 items-center justify-between px-4 gap-4">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 shrink-0 group">
            <motion.div
              className="p-1.75 rounded-md bg-violet-600"
              whileHover={{ rotate: 8, scale: 1.1 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <Zap className="h-5 w-5 text-primary-foreground" />
            </motion.div>
            <span className="font-bold text-lg tracking-tight group-hover:text-primary transition-colors">
              SnappCart
            </span>
          </Link>

          {/* Search bar — desktop */}
          <div className="hidden md:flex flex-1 max-w-xl">
            <div className="relative w-full">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                placeholder="Search for products, brands and more..."
                className="w-full h-10 rounded-full border border-border bg-muted/40 py-2 pl-10 pr-4 text-sm outline-none transition-all focus:bg-background focus:border-primary/50 focus:ring-2 focus:ring-primary/20 placeholder:text-muted-foreground/60"
              />
              <kbd className="absolute right-3.5 top-1/2 -translate-y-1/2 hidden lg:flex items-center gap-1 text-xs text-muted-foreground border border-border rounded px-1.5 py-0.5">
                ⌘K
              </kbd>
            </div>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-1">

            {/* Mobile Search */}
            <motion.button
              className="md:hidden p-2 rounded-full hover:bg-muted transition-colors"
              whileTap={{ scale: 0.9 }}
              onClick={() => setSearchOpen(true)}
            >
              <Search className="h-5 w-5" />
            </motion.button>

            {/* Theme Toggle — CSS based, no mounted state needed */}
            <motion.button
              className="p-2 rounded-full hover:bg-muted transition-colors"
              whileTap={{ scale: 0.9 }}
              whileHover={{ scale: 1.05 }}
              onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
              suppressHydrationWarning
            >
              <Sun className="h-5 w-5 dark:hidden" />
              <Moon className="h-5 w-5 hidden dark:block" />
            </motion.button>

            {/* Notifications */}
            {isLoggedIn && (
              <motion.button
                className="relative p-2 rounded-full hover:bg-muted transition-colors"
                whileTap={{ scale: 0.9 }}
                whileHover={{ scale: 1.05 }}
              >
                <Bell className="h-5 w-5" />
                <AnimatePresence>
                  {unreadCount > 0 && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      exit={{ scale: 0 }}
                      className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-destructive text-destructive-foreground text-[10px] font-bold flex items-center justify-center"
                    >
                      {unreadCount > 9 ? "9+" : unreadCount}
                    </motion.span>
                  )}
                </AnimatePresence>
              </motion.button>
            )}

            {/* Cart */}
            <motion.button
              className="relative p-2 rounded-full hover:bg-muted transition-colors"
              whileTap={{ scale: 0.9 }}
              whileHover={{ scale: 1.05 }}
              onClick={() => dispatch(toggleCart())}
            >
              <ShoppingCart className="h-5 w-5" />
              <AnimatePresence>
                {cartCount > 0 && (
                  <motion.span
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    exit={{ scale: 0 }}
                    className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center"
                  >
                    {cartCount > 9 ? "9+" : cartCount}
                  </motion.span>
                )}
              </AnimatePresence>
            </motion.button>

            {/* Auth */}
            {isLoggedIn ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="h-9 w-9 rounded-full bg-primary flex items-center justify-center text-primary-foreground text-sm font-bold cursor-pointer ring-2 ring-primary/20 hover:ring-primary/40 transition-all outline-none"
                  >
                    {getInitial()}
                  </motion.button>
                </DropdownMenuTrigger>

                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-0.5">
                      <p className="text-sm font-medium leading-none">
                        {user?.full_name || "User"}
                      </p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user?.email || user?.phone}
                      </p>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />

                  <DropdownMenuItem asChild>
                    <Link href="/profile" className="cursor-pointer">
                      <User className="mr-2 h-4 w-4" />
                      My Profile
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem asChild>
                    <Link href="/orders" className="cursor-pointer">
                      <Package className="mr-2 h-4 w-4" />
                      My Orders
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem asChild>
                    <Link href="/wishlist" className="cursor-pointer">
                      <Heart className="mr-2 h-4 w-4" />
                      Wishlist
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem asChild>
                    <Link href="/wallet" className="cursor-pointer">
                      <Wallet className="mr-2 h-4 w-4" />
                      Wallet & Rewards
                    </Link>
                  </DropdownMenuItem>

                  {user?.role === "seller" && (
                    <DropdownMenuItem asChild>
                      <Link href="/seller/dashboard" className="cursor-pointer">
                        <Store className="mr-2 h-4 w-4" />
                        Seller Dashboard
                      </Link>
                    </DropdownMenuItem>
                  )}

                  {user?.role === "admin" && (
                    <DropdownMenuItem asChild>
                      <Link href="/admin/dashboard" className="cursor-pointer">
                        <Shield className="mr-2 h-4 w-4" />
                        Admin Panel
                      </Link>
                    </DropdownMenuItem>
                  )}

                  <DropdownMenuSeparator />

                  <DropdownMenuItem asChild>
                    <Link href="/settings" className="cursor-pointer">
                      <Settings className="mr-2 h-4 w-4" />
                      Settings
                    </Link>
                  </DropdownMenuItem>

                  <DropdownMenuItem
                    className="cursor-pointer text-destructive focus:text-destructive"
                    onClick={handleLogout}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Log out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="hidden md:flex items-center gap-2">
                <Button variant="ghost" size="sm" asChild className="rounded-full">
                  <Link href="/login">Login</Link>
                </Button>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                  <Button size="sm" asChild className="rounded-full px-5">
                    <Link href="/register">Sign Up</Link>
                  </Button>
                </motion.div>
              </div>
            )}
          </div>
        </div>
      </motion.nav>

      {/* Mobile Search Overlay */}
      <AnimatePresence>
        {searchOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-background/95 backdrop-blur-sm md:hidden p-4"
          >
            <div className="flex items-center gap-3 mt-2">
              <div className="relative flex-1">
                <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <input
                  autoFocus
                  placeholder="Search products..."
                  className="w-full h-11 rounded-full border border-border bg-muted/40 pl-10 pr-4 text-sm outline-none focus:border-primary/50 focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <button
                onClick={() => setSearchOpen(false)}
                className="p-2 rounded-full hover:bg-muted"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}