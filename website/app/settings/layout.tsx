'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ArrowLeft, Link2, Wallet } from 'lucide-react'

const navItems = [
  { href: '/settings/connections', label: 'Connections', icon: Link2 },
  { href: '/settings/wallet', label: 'Wallet', icon: Wallet },
]

export default function SettingsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()

  return (
    <div className="min-h-screen bg-ivory-100">
      <header className="border-b border-silver-700/10 bg-ivory-50/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            href="/chat"
            className="flex items-center gap-2 text-silver-600 hover:text-silver-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="font-sans text-sm">Back to Chat</span>
          </Link>
          <h1 className="font-display text-xl text-silver-800">Settings</h1>
          <div className="w-24" />
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          <aside className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href
                const Icon = item.icon
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                      isActive
                        ? 'bg-silver-700 text-ivory-100'
                        : 'text-silver-600 hover:bg-silver-100 hover:text-silver-800'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-sans font-medium">{item.label}</span>
                  </Link>
                )
              })}
            </nav>

            <div className="mt-8 p-4 bg-ivory-50 border border-silver-200 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
                  <span className="text-ivory-100 font-display font-bold">F</span>
                </div>
                <div>
                  <p className="font-display text-silver-800">Franklin</p>
                  <p className="text-xs text-silver-500 font-sans">AI Private Banker</p>
                </div>
              </div>
              <p className="text-xs text-silver-600 font-body leading-relaxed">
                Connect your accounts so Franklin can help manage your calendar,
                emails, and make purchases on your behalf.
              </p>
            </div>
          </aside>

          <main className="flex-1 min-w-0">{children}</main>
        </div>
      </div>
    </div>
  )
}
