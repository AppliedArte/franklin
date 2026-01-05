'use client'

import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'
import Link from 'next/link'
import { MessageCircle, Settings, TrendingUp, Wallet, Calendar, ArrowRight } from 'lucide-react'

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="min-h-screen bg-ivory-100 flex items-center justify-center">
        <div className="animate-pulse text-silver-600 font-serif text-xl">Loading...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-ivory-100">
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="font-display text-3xl text-silver-800 mb-2">
            Welcome back, {user.email.split('@')[0]}
          </h1>
          <p className="text-silver-600 font-body">
            Your personal wealth management dashboard
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Link
            href="/chat"
            className="bg-ivory-50 border border-silver-200 rounded-2xl p-6 hover:border-gold-400 hover:shadow-lg transition-all group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-gold-100 flex items-center justify-center">
                <MessageCircle className="w-6 h-6 text-gold-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-silver-400 group-hover:text-gold-600 transition-colors" />
            </div>
            <h3 className="font-display text-xl text-silver-800 mb-2">Chat with Franklin</h3>
            <p className="text-silver-600 text-sm font-body">
              Get personalized financial advice and investment insights
            </p>
          </Link>

          <Link
            href="/settings/wallet"
            className="bg-ivory-50 border border-silver-200 rounded-2xl p-6 hover:border-gold-400 hover:shadow-lg transition-all group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                <Wallet className="w-6 h-6 text-green-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-silver-400 group-hover:text-gold-600 transition-colors" />
            </div>
            <h3 className="font-display text-xl text-silver-800 mb-2">Wallet & Credits</h3>
            <p className="text-silver-600 text-sm font-body">
              Manage your credits and payment methods
            </p>
          </Link>

          <Link
            href="/settings/connections"
            className="bg-ivory-50 border border-silver-200 rounded-2xl p-6 hover:border-gold-400 hover:shadow-lg transition-all group"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
                <Settings className="w-6 h-6 text-blue-600" />
              </div>
              <ArrowRight className="w-5 h-5 text-silver-400 group-hover:text-gold-600 transition-colors" />
            </div>
            <h3 className="font-display text-xl text-silver-800 mb-2">Connections</h3>
            <p className="text-silver-600 text-sm font-body">
              Link your accounts and manage integrations
            </p>
          </Link>
        </div>

        {/* Stats Section */}
        <div className="bg-ivory-50 border border-silver-200 rounded-2xl p-6 mb-8">
          <h2 className="font-display text-xl text-silver-800 mb-6">Your Activity</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-display text-gold-600 mb-1">0</div>
              <div className="text-silver-600 text-sm font-sans">Conversations</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-display text-gold-600 mb-1">$0</div>
              <div className="text-silver-600 text-sm font-sans">Credits Balance</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-display text-gold-600 mb-1">0</div>
              <div className="text-silver-600 text-sm font-sans">Connected Accounts</div>
            </div>
          </div>
        </div>

        {/* Resources */}
        <div className="bg-gradient-to-br from-silver-700 to-silver-800 rounded-2xl p-8 text-ivory-100">
          <div className="flex items-start gap-6">
            <img src="/franklin.jpg" alt="Franklin" className="w-16 h-16 rounded-full object-cover shadow-xl" />
            <div className="flex-1">
              <h2 className="font-display text-2xl mb-2">Ready to grow your wealth?</h2>
              <p className="text-ivory-200 font-body mb-4">
                Start a conversation with Franklin to get personalized investment advice,
                market insights, and help building your financial future.
              </p>
              <Link
                href="/chat"
                className="inline-flex items-center gap-2 bg-gold-500 text-silver-900 px-6 py-3 rounded-xl font-sans font-medium hover:bg-gold-400 transition-colors"
              >
                Start Chatting
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
