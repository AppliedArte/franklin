"use client"

import { useState, useEffect } from "react"
import {
  MessageSquare,
  Phone,
  Mail,
  TrendingUp,
  Shield,
  ArrowRight,
  ChevronDown,
  Building2,
  Coins,
  LineChart,
  Lock,
  Globe,
  Clock,
  CheckCircle2,
  Quote
} from "lucide-react"

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

// Animated counter for stats
function AnimatedNumber({ value, suffix = "" }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0)

  useEffect(() => {
    const duration = 2000
    const steps = 60
    const increment = value / steps
    let current = 0

    const timer = setInterval(() => {
      current += increment
      if (current >= value) {
        setCount(value)
        clearInterval(timer)
      } else {
        setCount(Math.floor(current))
      }
    }, duration / steps)

    return () => clearInterval(timer)
  }, [value])

  return <span>{count.toLocaleString()}{suffix}</span>
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
              <a href="#expertise" className="link-elegant text-sm tracking-wide">Expertise</a>
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
              {/* Eyebrow */}
              <div className="flex items-center gap-4">
                <div className="h-px w-12 bg-gold-400" />
                <span className="text-gold-500 font-sans text-sm tracking-[0.2em] uppercase">
                  Your Private Banker
                </span>
              </div>

              {/* Main headline */}
              <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-forest-700 leading-[1.1] tracking-tight">
                Meet <span className="italic text-gradient-gold">Franklin</span>
              </h1>

              {/* Subheadline */}
              <p className="font-display italic text-2xl md:text-3xl text-forest-700/80 leading-relaxed max-w-xl">
                Money talks
              </p>
              <p className="font-body text-lg md:text-xl text-forest-700/70 leading-relaxed max-w-xl">
                Franklin is your personal wealth advisor and private banker. Grow your wealth, invest in sophisticated investment strategies, set up optimal tax strategies. Connect with Wall Street firms and brokers to close and syndicate deals, he can do it all.
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

      {/* ===== EXPERTISE SECTION (Resume) ===== */}
      <section id="expertise" className="relative py-32 bg-forest-700 text-ivory-100 grain">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          {/* Section header */}
          <div className="text-center mb-16">
            <Flourish className="mx-auto text-gold-400/60 mb-6" />
            <h2 className="font-display text-4xl md:text-5xl tracking-tight mb-4">
              The <span className="italic text-gold-400">Résumé</span>
            </h2>
            <p className="font-body text-lg text-ivory-100/60">Your AI Private Banker (Est. 1706)</p>
          </div>

          {/* Professional Summary */}
          <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
            <h3 className="font-display text-2xl text-gold-400 mb-4">Professional Summary</h3>
            <p className="font-body text-ivory-100/80 leading-relaxed">
              Seasoned financial advisor with 300+ years of compound interest experience. Specializes in turning pennies into fortunes through the sheer force of time and temperance. Known for dispensing wealth management advice in aphorisms that your grandfather definitely quoted at you. Currently revolutionizing private banking through Web3 infrastructure while maintaining that old-world charm.
            </p>
          </div>

          {/* Core Competencies */}
          <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
            <h3 className="font-display text-2xl text-gold-400 mb-6">Core Competencies</h3>
            <div className="grid md:grid-cols-2 gap-4">
              {[
                ["Portfolio Diversification", "Never kept all eggs in one basket (invented the basket)"],
                ["Risk Management", "Survived multiple currency collapses by literally printing the currency"],
                ["Client Relations", "Can explain complex financial products using only folksy wisdom"],
                ["Lightning-Fast Analysis", "Literally discovered electricity"],
                ["International Markets", "Negotiated France's investment in American startups (circa 1778)"],
                ["Regulatory Compliance", "Wrote some of the regulations"],
                ["AI/ML Integration", "Digitized 318 years of financial wisdom into neural networks"],
                ["Blockchain Native", "Understands decentralization (helped decentralize from Britain)"],
              ].map(([title, desc], i) => (
                <div key={i} className="text-sm">
                  <span className="text-ivory-100 font-semibold">{title}:</span>{" "}
                  <span className="text-ivory-100/60">{desc}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Professional Experience */}
          <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
            <h3 className="font-display text-2xl text-gold-400 mb-6">Professional Experience</h3>

            {/* Current Role */}
            <div className="mb-8 pb-8 border-b border-ivory-100/10">
              <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
                <h4 className="font-display text-xl text-ivory-100">Chief Intelligence Officer</h4>
                <span className="text-sm text-ivory-100/50">2024 - Present</span>
              </div>
              <p className="text-gold-400/80 text-sm mb-4">askFranklin.io</p>
              <ul className="space-y-2 text-ivory-100/70 text-sm list-disc list-outside ml-5">
                <li>Leading digital transformation of 18th-century banking wisdom for 21st-century degenerates</li>
                <li>Deployed AI-powered financial advisory services accessible 24/7 (because time is money, and I no longer sleep)</li>
                <li>Synthesizing DeFi protocols with time-tested investment principles</li>
                <li>Building the bridge between "a penny saved" and "WAGMI"</li>
                <li>Achieved 99.9% uptime (significant improvement over mortality-based availability)</li>
              </ul>
            </div>

            {/* Historical Roles */}
            <div className="mb-8 pb-8 border-b border-ivory-100/10">
              <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
                <h4 className="font-display text-xl text-ivory-100">Founding Father & Private Banker</h4>
                <span className="text-sm text-ivory-100/50">1706 - 2024</span>
              </div>
              <p className="text-gold-400/80 text-sm mb-4">Self-Employed</p>
              <ul className="space-y-2 text-ivory-100/70 text-sm list-disc list-outside ml-5">
                <li>Achieved 156,000,000%+ returns through patience and not dying</li>
                <li>Created bifocals, enabling clients to read both the fine print AND the big picture</li>
                <li>Published "Poor Richard's Almanack": first financial newsletter with actual staying power</li>
              </ul>
            </div>

            <div>
              <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
                <h4 className="font-display text-xl text-ivory-100">Ambassador to France</h4>
                <span className="text-sm text-ivory-100/50">1776 - 1785</span>
              </div>
              <p className="text-gold-400/80 text-sm mb-4">United States</p>
              <ul className="space-y-2 text-ivory-100/70 text-sm list-disc list-outside ml-5">
                <li>Secured Series A funding for revolutionary startup</li>
                <li>Negotiated favorable terms despite questionable fundamentals</li>
                <li>Proved that charm is an asset class</li>
              </ul>
            </div>
          </div>

          {/* Notable Achievements */}
          <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
            <h3 className="font-display text-2xl text-gold-400 mb-6">Notable Achievements</h3>
            <ul className="space-y-2 text-ivory-100/70 text-sm list-disc list-outside ml-5">
              <li>Only banker whose face appears on the $100 bill (the ultimate networking achievement)</li>
              <li>Turned $5,000 into multi-million dollar perpetual trusts for Boston and Philadelphia</li>
              <li>Negotiated the Treaty of Paris without a PowerPoint deck</li>
              <li>Successfully tokenized 318 years of financial wisdom without losing the folksy charm</li>
              <li>Bridged the gap between "sound money" and "internet money"</li>
            </ul>
          </div>

          {/* Languages & Skills */}
          <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
            <h3 className="font-display text-2xl text-gold-400 mb-6">Languages</h3>
            <div className="flex flex-wrap gap-3">
              {[
                "English (Native)",
                "French (Conversational, especially regarding loans)",
                "Aphorisms (Fluent)",
                "Python (surprisingly adaptable)",
                "Solidity (smart contracts are just treaties you can't renegotiate)",
              ].map((lang, i) => (
                <span key={i} className="px-4 py-2 text-sm text-gold-400/80 border border-gold-400/20 bg-gold-400/5">
                  {lang}
                </span>
              ))}
            </div>
          </div>

          {/* Investment Philosophy */}
          <div className="p-8 border border-gold-400/30 bg-forest-800/50">
            <h3 className="font-display text-2xl text-gold-400 mb-4">Investment Philosophy</h3>
            <blockquote className="font-body italic text-ivory-100/80 text-lg leading-relaxed">
              "A penny saved is a penny earned, but a penny invested at 7% annual return becomes $1,476 after 150 years. Compounding is the eighth wonder of the world, and early to bed means you're not panic-selling during after-hours trading. Also, DYOR, but I've already done it for you."
            </blockquote>
          </div>

          {/* Footer */}
          <p className="text-center mt-12 text-ivory-100/50 text-sm italic">
            "In this world, nothing is certain except death, taxes, and Franklin's ability to optimize your tax-loss harvesting strategy—now with 99.9% uptime."
          </p>
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

            {/* Right: Visual */}
            <div className="relative">
              <div className="relative bg-forest-700 p-8 lg:p-12 rounded-sm shadow-2xl">
                {/* Chat mockup */}
                <div className="space-y-6">
                  {/* Franklin's message */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gold-400/20 flex items-center justify-center">
                      <span className="font-display text-gold-400 font-bold">F</span>
                    </div>
                    <div className="bg-forest-600 p-4 rounded-sm rounded-tl-none max-w-sm">
                      <p className="font-body text-ivory-100/90 text-sm leading-relaxed">
                        Good day to you! I am Franklin, at your service. Pray tell, what brings you
                        to seek counsel on financial matters today?
                      </p>
                    </div>
                  </div>

                  {/* User message */}
                  <div className="flex gap-4 justify-end">
                    <div className="bg-gold-400/20 p-4 rounded-sm rounded-tr-none max-w-sm">
                      <p className="font-body text-ivory-100/90 text-sm leading-relaxed">
                        I'm interested in learning about basis trading and crypto arbitrage opportunities.
                      </p>
                    </div>
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-ivory-100/10 flex items-center justify-center">
                      <span className="font-sans text-ivory-100/60 text-sm">You</span>
                    </div>
                  </div>

                  {/* Franklin's response */}
                  <div className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gold-400/20 flex items-center justify-center">
                      <span className="font-display text-gold-400 font-bold">F</span>
                    </div>
                    <div className="bg-forest-600 p-4 rounded-sm rounded-tl-none max-w-sm">
                      <p className="font-body text-ivory-100/90 text-sm leading-relaxed">
                        Ah, the basis trade! A most elegant arbitrage indeed. The spread between
                        spot and futures can yield handsome returns for those with patience...
                      </p>
                    </div>
                  </div>
                </div>

                {/* Input mockup */}
                <div className="mt-8 flex gap-3">
                  <div className="flex-1 bg-forest-600/50 border border-ivory-100/10 rounded-sm px-4 py-3">
                    <span className="text-ivory-100/40 font-sans text-sm">Type your message...</span>
                  </div>
                  <button className="px-6 bg-gold-400 text-forest-900 font-sans font-medium rounded-sm">
                    Send
                  </button>
                </div>
              </div>

              {/* Decorative elements */}
              <div className="absolute -z-10 -top-4 -left-4 w-full h-full border border-gold-400/20 rounded-sm" />
            </div>
          </div>
        </div>
      </section>

      {/* ===== TRUST SECTION ===== */}
      <section className="py-32 grain">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 mb-24">
            {[
              { value: 318, suffix: "+", label: "Years of Wisdom" },
              { value: 100, suffix: "M+", label: "His Legacy (USD)" },
              { value: 24, suffix: "/7", label: "Availability" },
              { value: 6, suffix: "", label: "Channels" }
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <div className="font-display text-5xl lg:text-6xl text-forest-700 mb-2">
                  <AnimatedNumber value={stat.value} suffix={stat.suffix} />
                </div>
                <p className="font-sans text-sm text-forest-700/60 tracking-wide uppercase">{stat.label}</p>
              </div>
            ))}
          </div>

          {/* Testimonial */}
          <div className="max-w-4xl mx-auto text-center">
            <Quote className="w-12 h-12 text-gold-400/40 mx-auto mb-8" />
            <blockquote className="font-serif text-2xl md:text-3xl text-forest-700 leading-relaxed mb-8 italic">
              "Franklin explained the intricacies of basis trading in a manner most comprehensible.
              His counsel on timing and temperament has been invaluable to my investment journey."
            </blockquote>
            <div className="flex items-center justify-center gap-4">
              <div className="w-12 h-12 rounded-full bg-forest-700/10 flex items-center justify-center">
                <span className="font-sans text-forest-700 font-medium">JM</span>
              </div>
              <div className="text-left">
                <p className="font-sans font-medium text-forest-700">Jonathan M.</p>
                <p className="font-sans text-sm text-forest-700/60">Private Investor, London</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== FEATURES/BENEFITS ===== */}
      <section className="py-24 bg-forest-700 text-ivory-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Lock,
                title: "Private & Secure",
                description: "Your conversations remain confidential. A gentleman never discloses his client's affairs."
              },
              {
                icon: Clock,
                title: "Always Available",
                description: "Franklin keeps no particular hours. Seek counsel whenever the need arises."
              },
              {
                icon: CheckCircle2,
                title: "Honest Counsel",
                description: "\"Say I don't know\" is a valid answer. Franklin offers wisdom, not false certainty."
              }
            ].map((feature, index) => (
              <div key={index} className="text-center p-8">
                <feature.icon className="w-10 h-10 text-gold-400 mx-auto mb-6" />
                <h3 className="font-display text-2xl text-ivory-100 mb-4">{feature.title}</h3>
                <p className="font-body text-ivory-100/60 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section id="start" className="py-32 grain relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[600px] rounded-full bg-gradient-radial from-gold-400/5 via-transparent to-transparent" />
        </div>

        <div className="relative max-w-3xl mx-auto px-6 lg:px-8 text-center">
          <Flourish className="mx-auto text-gold-400/60 mb-8" />

          <h2 className="font-display text-4xl md:text-5xl lg:text-6xl text-forest-700 tracking-tight mb-8">
            Begin Your Journey to <span className="italic text-gradient-gold">Prosperity</span>
          </h2>

          <p className="font-body text-xl text-forest-700/70 mb-12 max-w-2xl mx-auto leading-relaxed">
            The path to wealth is best walked with wise counsel. Franklin awaits your inquiry,
            ready to share centuries of accumulated wisdom.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="https://wa.me/your-number"
              className="btn-gold group text-lg px-10 py-5"
              target="_blank"
              rel="noopener noreferrer"
            >
              <MessageSquare className="mr-3 w-5 h-5" />
              <span>Message on WhatsApp</span>
              <ArrowRight className="ml-3 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </a>
          </div>

          <p className="mt-8 font-sans text-sm text-forest-700/50">
            No registration required. Simply start a conversation.
          </p>
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

          {/* Disclaimer */}
          <div className="mt-8 p-4 border border-ivory-100/10 bg-forest-800/30">
            <p className="font-sans text-xs text-ivory-100/40 text-center leading-relaxed">
              <strong className="text-ivory-100/60">Disclaimer:</strong> Franklin provides general educational information,
              not personalised investment advice. Always consult a licensed financial advisor for recommendations
              specific to your situation. Past performance does not guarantee future results.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
