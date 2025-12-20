"use client"

import { useState, useEffect } from "react"
import {
  Phone,
  ArrowRight,
  ChevronDown
} from "lucide-react"

// Option Button Component
function OptionButton({
  label,
  onClick,
  variant = "default"
}: {
  label: string
  onClick?: () => void
  variant?: "default" | "primary"
}) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left px-4 py-3 rounded-xl border transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] ${
        variant === "primary"
          ? "bg-forest-700 text-ivory-100 border-forest-600 hover:bg-forest-600"
          : "bg-white text-forest-800 border-forest-700/20 hover:border-forest-700/40 hover:bg-forest-50"
      }`}
    >
      <span className="text-[14px] font-medium">{label}</span>
    </button>
  )
}

// iPhone Mockup Component - Full Width with Onboarding
function IPhoneMockup() {
  return (
    <div className="relative w-full max-w-md mx-auto">
      {/* Phone Device */}
      <div className="relative">
        {/* Outer frame with gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#2a2a2a] via-[#1a1a1a] to-[#0a0a0a] rounded-[3rem] shadow-2xl" />

        {/* Side buttons */}
        <div className="absolute -left-[3px] top-24 w-[4px] h-8 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[3px] top-36 w-[4px] h-14 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[3px] top-52 w-[4px] h-14 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -right-[3px] top-32 w-[4px] h-20 bg-[#2a2a2a] rounded-r-sm" />

        {/* Inner bezel */}
        <div className="relative bg-[#1a1a1a] rounded-[3rem] p-3">
          {/* Screen */}
          <div className="relative bg-ivory-50 rounded-[2.25rem] overflow-hidden">
            {/* Dynamic Island */}
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20">
              <div className="w-28 h-8 bg-black rounded-full flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-[#1a1a1a] ring-1 ring-[#333]" />
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center justify-between px-8 pt-4 pb-2">
              <span className="text-sm font-semibold text-forest-800">9:41</span>
              <div className="flex items-center gap-1.5">
                {/* Signal */}
                <div className="flex items-end gap-[2px]">
                  {[4, 6, 8, 10].map((h, i) => (
                    <div key={i} className="w-[3px] bg-forest-800 rounded-sm" style={{ height: `${h}px` }} />
                  ))}
                </div>
                {/* Wifi */}
                <svg className="w-4 h-3 text-forest-800" viewBox="0 0 16 12" fill="currentColor">
                  <path d="M8 9.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM8 6c-1.7 0-3.2.7-4.3 1.8l1.4 1.4c.8-.8 1.8-1.2 2.9-1.2s2.1.4 2.9 1.2l1.4-1.4C11.2 6.7 9.7 6 8 6zm0-4C5 2 2.4 3.2.6 5.2l1.4 1.4C3.5 5 5.6 4 8 4s4.5 1 6 2.6l1.4-1.4C13.6 3.2 11 2 8 2z"/>
                </svg>
                {/* Battery */}
                <div className="flex items-center">
                  <div className="w-6 h-3 border border-forest-800 rounded p-[2px]">
                    <div className="w-full h-full bg-forest-800 rounded-sm" />
                  </div>
                  <div className="w-[2px] h-[5px] bg-forest-800 rounded-r-sm ml-[1px]" />
                </div>
              </div>
            </div>

            {/* Chat Header */}
            <div className="flex items-center gap-3 px-5 py-3 bg-white/80 backdrop-blur-sm border-b border-black/5">
              <div className="w-11 h-11 rounded-full bg-gradient-to-br from-forest-600 to-forest-800 flex items-center justify-center shadow-md">
                <span className="font-display text-gold-400 font-bold text-lg">F</span>
              </div>
              <div className="flex-1">
                <h4 className="text-base font-semibold text-forest-800">Franklin</h4>
                <p className="text-xs text-forest-600/70">Your Private Banker</p>
              </div>
              <Phone className="w-5 h-5 text-forest-700" />
            </div>

            {/* Messages Container - Onboarding Flow */}
            <div className="min-h-[420px] bg-gradient-to-b from-[#f5f5f5] to-[#ebebeb] px-4 py-5">
              {/* Franklin's Avatar + Message */}
              <div className="flex gap-3 items-start">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-forest-600 to-forest-800 flex-shrink-0 flex items-center justify-center shadow-sm">
                  <span className="font-display text-gold-400 text-xs font-bold">F</span>
                </div>
                <div className="flex-1 space-y-4">
                  {/* Message bubble */}
                  <div className="bg-white px-4 py-4 rounded-2xl rounded-tl-sm shadow-sm border border-forest-700/5">
                    <h3 className="font-display text-lg text-forest-800 mb-2">
                      Hey, I'm Franklin, your AI private banker.
                    </h3>
                    <p className="text-[14px] text-forest-700/80 leading-relaxed">
                      I help you grow your wealth by reaching the right people, getting the right advice, and closing deals with expert input.
                    </p>
                    <p className="text-[14px] text-forest-700/80 mt-3">
                      How would you describe yourself?
                    </p>
                  </div>

                  {/* Option Buttons */}
                  <div className="space-y-2.5 pt-1">
                    <OptionButton label="(A) I am an Investor" variant="primary" />
                    <OptionButton label="(B) I am a Founder" />
                  </div>
                </div>
              </div>
            </div>

            {/* Input Bar */}
            <div className="bg-white px-4 py-3 border-t border-black/5">
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-[#f0f0f0] rounded-full px-5 py-2.5 border border-black/5">
                  <span className="text-sm text-forest-700/40">Message Franklin...</span>
                </div>
                <div className="w-10 h-10 bg-forest-700 rounded-full flex items-center justify-center shadow-sm">
                  <ArrowRight className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            {/* Home Indicator */}
            <div className="flex justify-center py-2 bg-white">
              <div className="w-32 h-1 bg-black/20 rounded-full" />
            </div>
          </div>
        </div>
      </div>

      {/* Decorative shadow */}
      <div className="absolute -z-10 inset-8 bg-forest-700/30 blur-3xl rounded-full" />
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
            </div>

            {/* CTA */}
            <a href="#chat" className="btn-primary text-xs sm:text-sm">
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

              {/* CTA */}
              <div className="pt-4">
                <a href="#chat" className="btn-gold group">
                  <span>Start a Conversation</span>
                  <ArrowRight className="ml-2 w-4 h-4 group-hover:translate-x-1 transition-transform" />
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

      {/* ===== CHAT SECTION ===== */}
      <section id="chat" className="py-24 bg-ivory-200/50 grain">
        <div className="max-w-2xl mx-auto px-6 lg:px-8">
          <IPhoneMockup />
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
