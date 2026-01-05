'use client'

import { useChat } from '@ai-sdk/react'
import { TextStreamChatTransport } from 'ai'
import { useState, useRef, useEffect, useMemo } from 'react'
import { Send, MessageCircle } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth-context'

const DEMO_MESSAGE_LIMIT = 5
const SUGGESTIONS = ['How should I start investing?', 'Help me create a budget', 'What are ETFs?', 'Portfolio advice']

const getMessageContent = (message: { parts?: Array<{ type: string; text?: string }> }) =>
  (message.parts || []).filter((p): p is { type: 'text'; text: string } => p.type === 'text').map(p => p.text).join('')

export default function ChatPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [showLoginPrompt, setShowLoginPrompt] = useState(false)
  const [messageCount, setMessageCount] = useState(0)
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const transport = useMemo(() => new TextStreamChatTransport({ api: '/api/chat' }), [])
  const { messages, sendMessage, status } = useChat({ transport })
  const isChatLoading = status === 'streaming' || status === 'submitted'

  useEffect(() => {
    if (!loading && user) router.push('/dashboard')
  }, [user, loading, router])

  useEffect(() => {
    const savedCount = localStorage.getItem('franklin_demo_count')
    if (savedCount) setMessageCount(parseInt(savedCount, 10))
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    const assistantMessages = messages.filter(m => m.role === 'assistant').length
    if (assistantMessages > messageCount) {
      setMessageCount(assistantMessages)
      if (!user) localStorage.setItem('franklin_demo_count', assistantMessages.toString())
    }
  }, [messages, messageCount, user])

  const isLimitReached = !user && messageCount >= DEMO_MESSAGE_LIMIT

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isChatLoading) return
    if (isLimitReached) return setShowLoginPrompt(true)
    const text = input.trim()
    setInput('')
    await sendMessage({ text })
  }

  const handleSuggestionClick = (suggestion: string) => {
    if (isLimitReached) {
      setShowLoginPrompt(true)
    } else {
      sendMessage({ text: suggestion })
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-ivory-100 flex items-center justify-center">
        <div className="animate-pulse text-silver-600 font-serif text-xl">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-ivory-100 flex flex-col">
      {/* Demo Banner */}
      {!user && (
        <div className="bg-gold-50 border-b border-gold-200 px-4 py-2">
          <p className="text-center text-sm text-gold-700 font-sans">
            Demo mode: {Math.max(0, DEMO_MESSAGE_LIMIT - messageCount)} messages remaining.{' '}
            <Link href="/login" className="underline font-medium hover:text-gold-800">
              Sign in for unlimited access
            </Link>
          </p>
        </div>
      )}

      {/* Chat Messages */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
          {messages.length === 0 && (
            <div className="text-center py-16 space-y-6">
              <img src="/franklin.jpg" alt="Franklin" className="w-20 h-20 mx-auto rounded-full object-cover shadow-xl" />
              <div className="space-y-2">
                <h2 className="font-display text-2xl text-silver-800">Hello, I'm Franklin</h2>
                <p className="text-silver-600 font-body max-w-md mx-auto">
                  Your AI private banker. I'm here to help with investment strategies,
                  budgeting, market insights, and building your financial future.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-3 pt-4">
                {SUGGESTIONS.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() => handleSuggestionClick(suggestion)}
                    disabled={isChatLoading}
                    className="px-4 py-2 rounded-full border border-silver-300 text-silver-600 text-sm font-sans
                               hover:border-gold-400 hover:text-gold-600 hover:bg-gold-50/50 transition-all
                               disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                m.role === 'user' ? 'bg-silver-700 text-ivory-100' : 'bg-ivory-50 border border-silver-200 text-silver-800'
              }`}>
                {m.role === 'assistant' && (
                  <div className="flex items-center gap-2 mb-2 pb-2 border-b border-silver-200/50">
                    <img src="/franklin.jpg" alt="Franklin" className="w-6 h-6 rounded-full object-cover" />
                    <span className="text-xs text-silver-500 font-sans">Franklin</span>
                  </div>
                )}
                <p className="font-body text-[15px] leading-relaxed whitespace-pre-wrap">{getMessageContent(m)}</p>
              </div>
            </div>
          ))}

          {isChatLoading && messages[messages.length - 1]?.role === 'user' && (
            <div className="flex justify-start">
              <div className="bg-ivory-50 border border-silver-200 rounded-2xl px-5 py-3">
                <div className="flex items-center gap-2">
                  <img src="/franklin.jpg" alt="Franklin" className="w-6 h-6 rounded-full object-cover" />
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse"></div>
                    <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse animation-delay-200"></div>
                    <div className="w-2 h-2 rounded-full bg-silver-400 animate-pulse animation-delay-400"></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* Input Area */}
      <div className="border-t border-silver-200 bg-ivory-50/80 backdrop-blur-sm sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-4 py-4">
          <div className="flex items-center gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Franklin anything..."
              disabled={isChatLoading}
              className="flex-1 px-5 py-3 rounded-full border border-silver-300 bg-ivory-100
                         text-silver-800 font-body placeholder:text-silver-400
                         focus:outline-none focus:border-gold-400 focus:ring-2 focus:ring-gold-400/20
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            />
            <button
              type="submit"
              disabled={isChatLoading || !input.trim()}
              className="w-12 h-12 rounded-full bg-silver-700 text-ivory-100 flex items-center justify-center
                         hover:bg-silver-800 focus:outline-none focus:ring-2 focus:ring-gold-400 focus:ring-offset-2
                         disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </form>
      </div>

      {/* Login Prompt Modal */}
      {showLoginPrompt && (
        <div className="fixed inset-0 bg-ink-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-ivory-100 rounded-2xl p-8 max-w-md w-full shadow-2xl animate-scale-in">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-gold-400 to-gold-600 flex items-center justify-center">
                <MessageCircle className="w-8 h-8 text-ivory-100" />
              </div>
              <h3 className="font-display text-2xl text-silver-800">Continue with Franklin</h3>
              <p className="text-silver-600 font-body">
                You've reached the demo limit. Sign in with your email to continue
                chatting and unlock unlimited conversations.
              </p>
              <div className="flex flex-col gap-3 pt-4">
                <Link
                  href="/login"
                  className="btn-primary w-full text-center"
                >
                  Sign in to continue
                </Link>
                <button
                  onClick={() => setShowLoginPrompt(false)}
                  className="text-silver-500 font-sans text-sm hover:text-silver-700"
                >
                  Maybe later
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
