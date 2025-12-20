"use client"

import Link from "next/link"
import { ArrowLeft } from "lucide-react"

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

export default function ExpertisePage() {
  return (
    <div className="min-h-screen bg-forest-700 text-ivory-100 grain">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-forest-700/80 backdrop-blur-md border-b border-ivory-100/10">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-ivory-100 hover:text-gold-400 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="font-sans text-sm">Back to Home</span>
            </Link>
            <span className="font-display text-xl text-ivory-100">Franklin</span>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 pt-32 pb-24">
        {/* Section header */}
        <div className="text-center mb-16">
          <Flourish className="mx-auto text-gold-400/60 mb-6" />
          <h1 className="font-display text-4xl md:text-5xl tracking-tight mb-4">
            The <span className="italic text-gold-400">Résumé</span>
          </h1>
          <p className="font-body text-lg text-ivory-100/60">Your AI Private Banker (Est. 1706)</p>
        </div>

        {/* Professional Summary */}
        <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
          <h2 className="font-display text-2xl text-gold-400 mb-4">Professional Summary</h2>
          <p className="font-body text-ivory-100/80 leading-relaxed">
            Seasoned financial advisor with 300+ years of compound interest experience. Specializes in turning pennies into fortunes through the sheer force of time and temperance. Known for dispensing wealth management advice in aphorisms that your grandfather definitely quoted at you. Currently revolutionizing private banking through Web3 infrastructure while maintaining that old-world charm.
          </p>
        </div>

        {/* Core Competencies */}
        <div className="mb-12 p-8 border border-ivory-100/10 bg-forest-800/30">
          <h2 className="font-display text-2xl text-gold-400 mb-6">Core Competencies</h2>
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
          <h2 className="font-display text-2xl text-gold-400 mb-6">Professional Experience</h2>

          {/* Current Role */}
          <div className="mb-8 pb-8 border-b border-ivory-100/10">
            <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
              <h3 className="font-display text-xl text-ivory-100">Chief Intelligence Officer</h3>
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
              <h3 className="font-display text-xl text-ivory-100">Founding Father & Private Banker</h3>
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
              <h3 className="font-display text-xl text-ivory-100">Ambassador to France</h3>
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
          <h2 className="font-display text-2xl text-gold-400 mb-6">Notable Achievements</h2>
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
          <h2 className="font-display text-2xl text-gold-400 mb-6">Languages</h2>
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
          <h2 className="font-display text-2xl text-gold-400 mb-4">Investment Philosophy</h2>
          <blockquote className="font-body italic text-ivory-100/80 text-lg leading-relaxed">
            "A penny saved is a penny earned, but a penny invested at 7% annual return becomes $1,476 after 150 years. Compounding is the eighth wonder of the world, and early to bed means you're not panic-selling during after-hours trading. Also, DYOR, but I've already done it for you."
          </blockquote>
        </div>

        {/* Footer */}
        <p className="text-center mt-12 text-ivory-100/50 text-sm italic">
          "In this world, nothing is certain except death, taxes, and Franklin's ability to optimize your tax-loss harvesting strategy—now with 99.9% uptime."
        </p>
      </main>
    </div>
  )
}
