'use client'

import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import { useEffect, useState, useRef, useMemo } from 'react'
import Link from 'next/link'
import { useChat } from '@ai-sdk/react'
import { TextStreamChatTransport } from 'ai'
import { Send, Settings, Wallet, Calendar, ArrowRight } from 'lucide-react'

const getMessageContent = (message: { parts?: Array<{ type: string; text?: string }> }) =>
  (message.parts || []).filter((p): p is { type: 'text'; text: string } => p.type === 'text').map(p => p.text).join('')

const parseMessage = (text: string) => {
  const thinkingRegex = /⟨thinking⟩([\s\S]*?)⟨\/thinking⟩/g
  let thinking = ''
  let response = text

  for (const match of text.matchAll(thinkingRegex)) {
    thinking += match[1]
    response = response.replace(match[0], '')
  }

  return { thinking: thinking.trim(), response: response.trim() }
}

const SUGGESTIONS = ['How should I start investing?', 'Help me create a budget', 'What are ETFs?']

const QUICK_ACTIONS = [
  { href: '/settings/wallet', icon: Wallet, title: 'Wallet', desc: 'Manage credits', bg: 'bg-green-100', color: 'text-green-600' },
  { href: '/settings/connections', icon: Calendar, title: 'Connections', desc: 'Google Calendar & Gmail', bg: 'bg-blue-100', color: 'text-blue-600' },
  { href: '/settings', icon: Settings, title: 'Settings', desc: 'Account preferences', bg: 'bg-silver-100', color: 'text-silver-600' },
]

export default function DashboardPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const transport = useMemo(() => new TextStreamChatTransport({ api: '/api/chat' }), [])
  const { messages, sendMessage, status } = useChat({ transport })
  const isChatLoading = status === 'streaming' || status === 'submitted'

  useEffect(() => {
    if (!loading && !user) router.push('/login')
  }, [user, loading, router])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isChatLoading) return
    const text = input.trim()
    setInput('')
    await sendMessage({ text })
  }

  const handleSuggestion = (text: string) => !isChatLoading && sendMessage({ text })

  if (loading) {
    return (
      <div className="min-h-screen bg-ivory-100 flex items-center justify-center">
        <div className="animate-pulse text-silver-600 font-serif text-xl">Loading...</div>
      </div>
    )
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-ivory-100">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Quick Actions */}
          <div className="space-y-4">
            <div className="mb-4">
              <h1 className="font-display text-2xl text-silver-800">Welcome, {user.email.split('@')[0]}</h1>
              <p className="text-silver-500 text-sm font-sans">Your wealth dashboard</p>
            </div>

            {QUICK_ACTIONS.map(({ href, icon: Icon, title, desc, bg, color }) => (
              <Link
                key={href}
                href={href}
                className="flex items-center gap-4 bg-ivory-50 border border-silver-200 rounded-xl p-4 hover:border-gold-400 transition-all group"
              >
                <div className={`w-10 h-10 rounded-lg ${bg} flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-sans font-medium text-silver-800">{title}</h3>
                  <p className="text-silver-500 text-xs">{desc}</p>
                </div>
                <ArrowRight className="w-4 h-4 text-silver-400 group-hover:text-gold-600" />
              </Link>
            ))}
          </div>

          {/* Main Chat Area */}
          <div className="lg:col-span-2 flex flex-col bg-ivory-50 border border-silver-200 rounded-2xl overflow-hidden" style={{ height: 'calc(100vh - 140px)' }}>
            {/* Chat Header */}
            <div className="flex items-center gap-3 px-6 py-4 border-b border-silver-200 bg-ivory-100/50">
              <img src="/franklin.jpg" alt="Franklin" className="w-10 h-10 rounded-full object-cover shadow-lg" />
              <div>
                <h2 className="font-display text-lg text-silver-800">Franklin</h2>
                <p className="text-xs text-silver-500 font-sans">Your AI Private Banker</p>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-8 space-y-4">
                  <p className="text-silver-600 font-body">
                    Ask me about investments, budgeting, market trends, or your financial goals.
                  </p>
                  <div className="flex flex-wrap justify-center gap-2">
                    {SUGGESTIONS.map((s) => (
                      <button
                        key={s}
                        onClick={() => handleSuggestion(s)}
                        disabled={isChatLoading}
                        className="px-3 py-1.5 rounded-full border border-silver-300 text-silver-600 text-sm font-sans hover:border-gold-400 hover:text-gold-600 transition-all disabled:opacity-50"
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {messages.map((m) => {
                const content = getMessageContent(m)
                const { thinking, response } = m.role === 'assistant' ? parseMessage(content) : { thinking: '', response: content }

                return (
                  <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      m.role === 'user' ? 'bg-silver-700 text-ivory-100' : 'bg-white border border-silver-200 text-silver-800'
                    }`}>
                      {m.role === 'assistant' && (
                        <div className="flex items-center gap-2 mb-2 pb-2 border-b border-silver-100">
                          <img src="/franklin.jpg" alt="Franklin" className="w-5 h-5 rounded-full" />
                          <span className="text-xs text-silver-500 font-sans">Franklin</span>
                        </div>
                      )}
                      {thinking && (
                        <p className="text-xs text-silver-400 italic mb-2 font-sans leading-relaxed">{thinking}</p>
                      )}
                      <p className="font-body text-sm leading-relaxed whitespace-pre-wrap">{response}</p>
                    </div>
                  </div>
                )
              })}

              {isChatLoading && messages[messages.length - 1]?.role === 'user' && (
                <div className="flex justify-start">
                  <div className="bg-white border border-silver-200 rounded-2xl px-4 py-3">
                    <div className="flex items-center gap-2">
                      <img src="/franklin.jpg" alt="Franklin" className="w-5 h-5 rounded-full" />
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse" />
                        <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse" style={{ animationDelay: '0.2s' }} />
                        <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse" style={{ animationDelay: '0.4s' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="px-4 py-3 border-t border-silver-200 bg-ivory-100/50">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask Franklin anything..."
                  disabled={isChatLoading}
                  className="flex-1 px-4 py-2.5 rounded-full border border-silver-300 bg-white text-silver-800 font-body text-sm placeholder:text-silver-400 focus:outline-none focus:border-gold-400 focus:ring-2 focus:ring-gold-400/20 disabled:opacity-50 transition-all"
                />
                <button
                  type="submit"
                  disabled={isChatLoading || !input.trim()}
                  className="w-10 h-10 rounded-full bg-silver-700 text-ivory-100 flex items-center justify-center hover:bg-silver-800 disabled:opacity-50 transition-all"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
