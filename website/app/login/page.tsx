'use client'

import { useState } from 'react'
import Link from 'next/link'
import { ArrowLeft, Mail, Loader2, CheckCircle } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSent, setIsSent] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const { error } = await createClient().auth.signInWithOtp({
        email,
        options: { emailRedirectTo: 'https://www.askfranklin.xyz/chat' },
      })
      if (error) setError(error.message)
      else setIsSent(true)
    } catch {
      setError('Something went wrong. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-ivory-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-silver-700/10 bg-ivory-50/80 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link
            href="/"
            className="flex items-center gap-2 text-silver-600 hover:text-silver-800 transition-colors w-fit"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="font-sans text-sm">Back</span>
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center px-4 py-16">
        <div className="w-full max-w-md">
          {/* Logo */}
          <div className="text-center mb-8">
            <img src="/franklin.jpg" alt="Franklin" className="w-20 h-20 mx-auto rounded-full object-cover shadow-xl mb-6" />
            <h1 className="font-display text-3xl text-silver-800 mb-2">Welcome to Franklin</h1>
            <p className="text-silver-600 font-body">
              Sign in to access unlimited conversations with your AI private banker.
            </p>
          </div>

          {/* Login Form */}
          <div className="bg-ivory-50 border border-silver-200 rounded-2xl p-8 shadow-lg">
            {isSent ? (
              <div className="text-center space-y-4">
                <div className="w-16 h-16 mx-auto rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <h2 className="font-display text-xl text-silver-800">Check your email</h2>
                <p className="text-silver-600 font-body text-sm">
                  We've sent a magic link to <strong>{email}</strong>.
                  Click the link in the email to sign in.
                </p>
                <button
                  onClick={() => {
                    setIsSent(false)
                    setEmail('')
                  }}
                  className="text-gold-600 font-sans text-sm hover:text-gold-700 underline"
                >
                  Use a different email
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <label htmlFor="email" className="block text-sm font-sans text-silver-700">
                    Email address
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-silver-400" />
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="you@example.com"
                      required
                      disabled={isLoading}
                      className="w-full pl-12 pr-4 py-3 rounded-xl border border-silver-300 bg-ivory-100
                                 text-silver-800 font-body placeholder:text-silver-400
                                 focus:outline-none focus:border-gold-400 focus:ring-2 focus:ring-gold-400/20
                                 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    />
                  </div>
                </div>

                {error && (
                  <div className="text-red-600 text-sm font-sans bg-red-50 px-4 py-2 rounded-lg">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading || !email}
                  className="w-full btn-primary flex items-center justify-center gap-2 rounded-xl"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    'Send magic link'
                  )}
                </button>

                <p className="text-center text-xs text-silver-500 font-sans">
                  By signing in, you agree to our{' '}
                  <Link href="/privacy-policy" className="underline hover:text-silver-700">
                    Privacy Policy
                  </Link>
                </p>
              </form>
            )}
          </div>

          {/* Benefits */}
          <div className="mt-8 grid grid-cols-2 gap-4">
            {[
              { label: 'Unlimited chats', icon: '✨' },
              { label: 'Save history', icon: '📝' },
              { label: 'Personal insights', icon: '🎯' },
              { label: 'Priority access', icon: '🚀' },
            ].map(({ label, icon }) => (
              <div key={label} className="flex items-center gap-2 text-silver-600 text-sm font-sans">
                <span>{icon}</span>
                {label}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
