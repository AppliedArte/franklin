'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'
import { Settings, LogOut, User, Menu, X } from 'lucide-react'
import { useState } from 'react'

const NAV_LINKS = [
  { href: '/dashboard', label: 'Dashboard', icon: User },
  { href: '/settings/wallet', label: 'Settings', icon: Settings, matchPrefix: '/settings' },
]

export function Navbar() {
  const { user, loading, signOut } = useAuth()
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const isActive = (path: string, matchPrefix?: string) =>
    matchPrefix ? pathname.startsWith(matchPrefix) : pathname === path

  if (pathname === '/login') return null

  return (
    <header className="border-b border-silver-700/10 bg-ivory-50/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3">
            <img src="/franklin.jpg" alt="Franklin" className="w-10 h-10 rounded-full object-cover shadow-lg" />
            <span className="font-display text-xl text-silver-800 hidden sm:block">Franklin</span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6">
            {user && NAV_LINKS.map(({ href, label, icon: Icon, matchPrefix }) => (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 text-sm font-sans transition-colors ${
                  isActive(href, matchPrefix) ? 'text-gold-600' : 'text-silver-600 hover:text-silver-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            ))}
          </nav>

          {/* Auth Section */}
          <div className="flex items-center gap-4">
            {loading ? (
              <div className="w-20 h-8 bg-silver-200 rounded animate-pulse" />
            ) : user ? (
              <>
                <div className="hidden sm:flex items-center gap-2 text-silver-600 text-sm font-sans">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  {user.email.split('@')[0]}
                </div>
                <button onClick={signOut} className="text-silver-500 hover:text-silver-700 transition-colors p-2" title="Sign out">
                  <LogOut className="w-4 h-4" />
                </button>
              </>
            ) : (
              <>
                <Link href="/chat" className="text-sm font-sans text-silver-600 hover:text-silver-800 transition-colors hidden sm:block">
                  Try Demo
                </Link>
                <Link href="/login" className="btn-primary text-sm px-4 py-2">Sign In</Link>
              </>
            )}

            {/* Mobile Menu Button */}
            {user && (
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="md:hidden p-2 text-silver-600"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && user && (
          <nav className="md:hidden pt-4 pb-2 border-t border-silver-200 mt-3 space-y-2">
            {NAV_LINKS.map(({ href, label, icon: Icon, matchPrefix }) => (
              <Link
                key={href}
                href={href}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-sans transition-colors ${
                  isActive(href, matchPrefix) ? 'bg-gold-50 text-gold-600' : 'text-silver-600 hover:bg-silver-50'
                }`}
              >
                <Icon className="w-4 h-4" />
                {label === 'Chat' ? 'Chat with Franklin' : label}
              </Link>
            ))}
          </nav>
        )}
      </div>
    </header>
  )
}
