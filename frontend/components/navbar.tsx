"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Menu, X } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { ModeToggle } from "./mode-toggle"
import NotificationDropdown from "./notification-dropdown"
import { useUser } from "@/hooks/useUser"
import { api } from "@/lib/api"
import { Skeleton } from "./ui/skeleton"

export default function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const pathname = usePathname()
  const { user, isAuthenticated, loading } = useUser()

  const handleLogout = async () => {
    await api.post("/auth/logout/", {})
    window.location.href = "/"
  }

  const navItems = [
    { name: "Home", href: "/" },
    { name: "About", href: "/about" },
  ]

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950 bg-opacity-90 dark:bg-opacity-90 backdrop-blur-sm">
      <div className="container mx-auto px-4 md:px-6">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-2xl font-bold text-purple-600 dark:text-purple-400">MentorMatch.ai</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "text-sm font-medium transition-colors hover:text-purple-600 dark:hover:text-purple-400",
                  pathname === item.href ? "text-purple-600 dark:text-purple-400" : "text-gray-600 dark:text-gray-300",
                )}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="hidden md:flex items-center space-x-4">
            {loading ? (
              <div className="flex items-center space-x-4">
                <Skeleton className="h-8 w-8 rounded-full" />
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-8 w-20" />
              </div>
            ) : isAuthenticated ? (
              <>
                <ModeToggle />
                <NotificationDropdown />
                <Button variant="outline" size="sm" onClick={handleLogout}>
                  Log out
                </Button>
                <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                  <Link href="/dashboard">Dashboard</Link>
                </Button>
              </>
            ) : (
              <>
                <ModeToggle />
                <Button variant="outline" size="sm">
                  <Link href="/login">Log in</Link>
                </Button>
                <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                  <Link href="/signup">Sign up</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile Navigation Toggle */}
          <div className="flex items-center md:hidden space-x-2">
            {isAuthenticated && <NotificationDropdown />}
            <ModeToggle />
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 focus:outline-none"
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800">
          <div className="container mx-auto px-4 py-4 space-y-3">
            {navItems.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  "block text-sm font-medium transition-colors hover:text-purple-600 dark:hover:text-purple-400",
                  pathname === item.href ? "text-purple-600 dark:text-purple-400" : "text-gray-600 dark:text-gray-300",
                )}
                onClick={() => setIsMenuOpen(false)}
              >
                {item.name}
              </Link>
            ))}
            <div className="pt-3 space-y-2">
             {loading ? (
                <Skeleton className="h-9 w-full" />
              ) : isAuthenticated ? (
                <Button variant="outline" className="w-full" onClick={handleLogout}>
                  Log out
                </Button>
              ) : (
                <>
                  <Button variant="outline" className="w-full">
                    <Link href="/login" className="w-full">
                      Log in
                    </Link>
                  </Button>
                  <Button className="w-full bg-purple-600 hover:bg-purple-700">
                    <Link href="/signup" className="w-full">
                      Sign up
                    </Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  )
}