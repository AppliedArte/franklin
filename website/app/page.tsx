"use client"

import { useState, useEffect } from "react"
import {
  MessageSquare,
  Phone,
  Mail,
  ArrowRight,
  ChevronDown,
  Quote
} from "lucide-react"

// Chat Message Component
function ChatMessage({
  sender,
  text,
  isUser = false
}: {
  sender?: string
  text: string
  isUser?: boolean
}) {
  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="bg-forest-700 text-ivory-100 px-3.5 py-2.5 rounded-[18px] rounded-br-[4px] max-w-[80%] shadow-sm">
          <p className="text-[13px] leading-[1.35]">{text}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-2 items-end">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-forest-600 to-forest-800 flex-shrink-0 flex items-center justify-center shadow-sm">
        <span className="font-display text-gold-400 text-[10px] font-bold">F</span>
      </div>
      <div className="bg-white px-3.5 py-2.5 rounded-[18px] rounded-bl-[4px] max-w-[80%] shadow-sm border border-forest-700/5">
        <p className="text-[13px] leading-[1.35] text-forest-800">{text}</p>
      </div>
    </div>
  )
}

// iPhone Mockup Component
function IPhoneMockup() {
  const messages = [
    { text: "Good day! I am Franklin, your private banker. How may I assist you today?", isUser: false },
    { text: "I'm looking to diversify into alternatives", isUser: true },
    { text: "Excellent taste. I can connect you with our pre-IPO and private credit specialists. Shall I arrange an introduction?", isUser: false },
    { text: "Yes please, that would be great", isUser: true },
    { text: "Consider it done. I've notified our team - expect an email within the hour.", isUser: false },
  ]

  return (
    <div className="relative">
      {/* Phone Device */}
      <div className="relative w-[280px] sm:w-[300px]">
        {/* Outer frame with gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#2a2a2a] via-[#1a1a1a] to-[#0a0a0a] rounded-[50px] shadow-2xl" />

        {/* Side buttons */}
        <div className="absolute -left-[2px] top-28 w-[3px] h-8 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[2px] top-40 w-[3px] h-12 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[2px] top-56 w-[3px] h-12 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -right-[2px] top-36 w-[3px] h-16 bg-[#2a2a2a] rounded-r-sm" />

        {/* Inner bezel */}
        <div className="relative bg-[#1a1a1a] rounded-[50px] p-[10px]">
          {/* Screen */}
          <div className="relative bg-[#f8f8f8] rounded-[40px] overflow-hidden">
            {/* Dynamic Island */}
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20">
              <div className="w-[90px] h-[28px] bg-black rounded-full flex items-center justify-center gap-2">
                <div className="w-[10px] h-[10px] rounded-full bg-[#1a1a1a] ring-1 ring-[#333]" />
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center justify-between px-7 pt-3 pb-1">
              <span className="text-[13px] font-semibold text-forest-800">9:41</span>
              <div className="flex items-center gap-1.5">
                {/* Signal */}
                <div className="flex items-end gap-[2px]">
                  {[40, 55, 70, 85].map((h, i) => (
                    <div key={i} className="w-[3px] bg-forest-800 rounded-sm" style={{ height: `${h / 10}px` }} />
                  ))}
                </div>
                {/* Wifi */}
                <svg className="w-[15px] h-[11px] text-forest-800" viewBox="0 0 16 12" fill="currentColor">
                  <path d="M8 9.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM8 6c-1.7 0-3.2.7-4.3 1.8l1.4 1.4c.8-.8 1.8-1.2 2.9-1.2s2.1.4 2.9 1.2l1.4-1.4C11.2 6.7 9.7 6 8 6zm0-4C5 2 2.4 3.2.6 5.2l1.4 1.4C3.5 5 5.6 4 8 4s4.5 1 6 2.6l1.4-1.4C13.6 3.2 11 2 8 2z"/>
                </svg>
                {/* Battery */}
                <div className="flex items-center">
                  <div className="w-[22px] h-[11px] border border-forest-800 rounded-[3px] p-[1px]">
                    <div className="w-full h-full bg-forest-800 rounded-[1px]" />
                  </div>
                  <div className="w-[1px] h-[4px] bg-forest-800 rounded-r-sm ml-[1px]" />
                </div>
              </div>
            </div>

            {/* Chat Header */}
            <div className="flex items-center gap-3 px-4 py-2.5 bg-white/80 backdrop-blur-sm border-b border-black/5">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-forest-600 to-forest-800 flex items-center justify-center shadow-sm">
                <span className="font-display text-gold-400 font-bold text-sm">F</span>
              </div>
              <div className="flex-1">
                <h4 className="text-[15px] font-semibold text-forest-800">Franklin</h4>
                <p className="text-[11px] text-forest-600/70">Private Banker</p>
              </div>
              <Phone className="w-5 h-5 text-forest-700" />
            </div>

            {/* Messages Container */}
            <div className="h-[340px] sm:h-[360px] bg-gradient-to-b from-[#f0f0f0] to-[#e8e8e8] px-3 py-3 space-y-2.5 overflow-hidden">
              {messages.map((msg, i) => (
                <ChatMessage key={i} text={msg.text} isUser={msg.isUser} />
              ))}
            </div>

            {/* Input Bar */}
            <div className="bg-white px-3 py-2 border-t border-black/5">
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-[#f0f0f0] rounded-full px-4 py-2 border border-black/5">
                  <span className="text-[13px] text-forest-700/40">Message</span>
                </div>
                <div className="w-8 h-8 bg-forest-700 rounded-full flex items-center justify-center">
                  <ArrowRight className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>

            {/* Home Indicator */}
            <div className="flex justify-center py-2 bg-white">
              <div className="w-28 h-1 bg-black/20 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Decorative shadow */}
      <div className="absolute -z-10 inset-4 bg-forest-700/20 blur-2xl rounded-full" />
    </div>
  )
}

// Decorative flourish component
function Flourish({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 100 20"
      className={`w-24 h-5 ${className}`}
      fill="currentColor"
    >
      <path d="M0 10 Q 25 0, 50 10 T 100 10" stroke="currentColor" strokeWidth="1" fill="none" />
      <circle cx="50" cy="10" r="3" />
      <circle cx="30" cy="8" r="1.5" />
      <circle cx="70" cy="8" r="1.5" />
    </svg>
  )
}

export default function LandingPage() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    setIsVisible(true)
  }, [])

  return (
    <div className="relative">
      {/* ===== NAVIGATION ===== */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-forest-700/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <a href="/" className="group">
              <span className="font-display text-2xl text-forest-700 tracking-tight">
                Franklin
              </span>
            </a>

            {/* Nav Links */}
            <div className="hidden md:flex items-center gap-8">
              <a href="/expertise" className="link-elegant text-sm tracking-wide">Expertise</a>
              <a href="#channels" className="link-elegant text-sm tracking-wide">Channels</a>
            </div>

            {/* CTA */}
            <a href="#start" className="btn-primary text-xs sm:text-sm">
              <span className="hidden sm:inline">Speak with Franklin</span>
              <span className="sm:hidden">Chat</span>
            </a>
          </div>
        </div>
      </nav>

      {/* ===== HERO SECTION ===== */}
      <section className="relative min-h-screen flex items-center pt-20 overflow-hidden grain">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/4 -right-64 w-[800px] h-[800px] rounded-full bg-gradient-radial from-gold-400/5 via-transparent to-transparent" />
          <div className="absolute -bottom-32 -left-32 w-[600px] h-[600px] rounded-full bg-gradient-radial from-forest-700/5 via-transparent to-transparent" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 lg:px-8 py-24 lg:py-32">
          <div className="grid lg:grid-cols-[1.2fr_1fr] gap-12 lg:gap-16 items-center">
            {/* Left: Franklin Video - 20% wider */}
            <div className={`relative ${isVisible ? 'animate-fade-in animation-delay-300' : 'opacity-0'}`}>
              <div className="relative w-full max-w-3xl mx-auto">
                {/* Ornate frame - hidden on mobile */}
                <div className="hidden md:block absolute -inset-3 border-2 border-gold-400/30 rounded-sm pointer-events-none" />
                <div className="hidden md:block absolute -inset-1 border border-forest-700/20 rounded-sm pointer-events-none" />

                {/* Franklin Video */}
                <div className="relative aspect-[16/9] overflow-hidden rounded-sm shadow-2xl">
                  <video
                    autoPlay
                    loop
                    muted
                    playsInline
                    className="absolute inset-0 w-full h-full object-cover"
                  >
                    <source src="/franklin.webm" type="video/webm" />
                    <source src="/franklin.gif" type="image/gif" />
                  </video>
                  {/* Subtle overlay for elegance */}
                  <div className="absolute inset-0 bg-gradient-to-t from-forest-700/20 via-transparent to-transparent pointer-events-none" />
                </div>

              </div>
            </div>

            {/* Right: Content */}
            <div className={`space-y-8 ${isVisible ? 'animate-fade-in-up' : 'opacity-0'}`}>
              {/* Main headline */}
              <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-forest-700 leading-[1.1] tracking-tight">
                Meet <span className="italic text-gradient-gold">Franklin</span>
              </h1>

              {/* Subheadline */}
              <p className="font-body text-lg md:text-xl text-forest-700/80 leading-relaxed max-w-xl">
                Franklin is your AI private banker who manages your wealth with the sophistication of a family office and the network of a top-tier investment bank.
              </p>
              <p className="font-body text-lg md:text-xl text-forest-700/60 leading-relaxed max-w-xl">
                Franklin works with a team of professionals to orchestrate solutions to grow your wealth. Reach the right people, get the right advice, and close deals with expert input.
              </p>

              {/* Quote */}
              <blockquote className="relative pl-6 border-l-2 border-gold-400/60 italic text-forest-700/70 font-serif text-lg">
                "An investment in knowledge pays the best interest."
                <footer className="mt-2 not-italic text-sm text-gold-500 font-sans">
                  — Benjamin Franklin
                </footer>
              </blockquote>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <a href="#start" className="btn-gold group">
                  <span>Start a Conversation</span>
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </a>
                <a href="#expertise" className="btn-secondary group">
                  <span>Discover His Expertise</span>
                  <ChevronDown className="ml-2 w-4 h-4 group-hover:translate-y-1 transition-transform" />
                </a>
              </div>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-forest-700/40">
            <span className="text-xs font-sans tracking-widest uppercase">Scroll</span>
            <ChevronDown className="w-5 h-5 animate-bounce" />
          </div>
        </div>
      </section>

      {/* ===== CHANNELS SECTION ===== */}
      <section id="channels" className="py-32 bg-ivory-200/50 grain">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            {/* Left: Content */}
            <div>
              <Flourish className="text-gold-400/60 mb-6" />
              <h2 className="font-display text-4xl md:text-5xl text-forest-700 tracking-tight mb-6">
                Converse at Your <span className="italic text-gradient-gold">Convenience</span>
              </h2>
              <p className="font-body text-xl text-forest-700/70 mb-12 leading-relaxed">
                Whether by letter, voice, or modern messaging, Franklin is at your service
                through whichever channel suits your preference.
              </p>

              <div className="space-y-6">
                {[
                  {
                    icon: MessageSquare,
                    title: "WhatsApp",
                    description: "Converse naturally, as you would with a trusted advisor. Available any time.",
                    badge: "Most Popular"
                  },
                  {
                    icon: Phone,
                    title: "Voice Call",
                    description: "Speak directly with Franklin. His dulcet tones bring comfort to complex matters.",
                    badge: "Coming Soon"
                  },
                  {
                    icon: Mail,
                    title: "Email",
                    description: "For those who prefer considered correspondence and detailed counsel.",
                    badge: null
                  }
                ].map((channel, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-5 p-6 card-luxury"
                  >
                    <div className="flex-shrink-0 w-14 h-14 rounded-full bg-forest-700/5 flex items-center justify-center">
                      <channel.icon className="w-6 h-6 text-forest-700" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-display text-xl text-forest-700">{channel.title}</h3>
                        {channel.badge && (
                          <span className="px-2 py-0.5 text-xs font-sans tracking-wide text-gold-600 bg-gold-400/20 rounded-full">
                            {channel.badge}
                          </span>
                        )}
                      </div>
                      <p className="font-body text-forest-700/60">{channel.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right: iPhone Visual */}
            <div className="flex justify-center">
              <IPhoneMockup />
            </div>
          </div>
        </div>
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="py-16 bg-forest-700 text-ivory-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12 mb-16">
            {/* Brand */}
            <div className="md:col-span-2">
              <div className="mb-6">
                <span className="font-display text-2xl text-ivory-100 tracking-tight">
                  Franklin
                </span>
              </div>
              <p className="font-body text-ivory-100/60 max-w-sm leading-relaxed">
                Your personal private banker, offering sophisticated wealth guidance
                through the wisdom of centuries past and the technology of today.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-sans font-semibold text-sm tracking-wide uppercase text-gold-400 mb-4">
                Expertise
              </h4>
              <ul className="space-y-3 font-body text-ivory-100/60">
                <li><a href="#" className="hover:text-gold-400 transition-colors">Alternatives</a></li>
                <li><a href="#" className="hover:text-gold-400 transition-colors">Digital Assets</a></li>
                <li><a href="#" className="hover:text-gold-400 transition-colors">Fixed Income</a></li>
                <li><a href="#" className="hover:text-gold-400 transition-colors">Pre-IPO</a></li>
              </ul>
            </div>

            {/* Connect */}
            <div>
              <h4 className="font-sans font-semibold text-sm tracking-wide uppercase text-gold-400 mb-4">
                Connect
              </h4>
              <ul className="space-y-3 font-body text-ivory-100/60">
                <li><a href="#" className="hover:text-gold-400 transition-colors">WhatsApp</a></li>
                <li><a href="#" className="hover:text-gold-400 transition-colors">Twitter</a></li>
                <li><a href="#" className="hover:text-gold-400 transition-colors">Email</a></li>
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div className="pt-8 border-t border-ivory-100/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="font-sans text-sm text-ivory-100/40">
              &copy; {new Date().getFullYear()} Ask Franklin. All rights reserved.
            </p>
            <p className="font-serif text-sm text-ivory-100/40 italic">
              "An investment in knowledge pays the best interest."
            </p>
          </div>

        </div>
      </footer>
    </div>
  )
}
