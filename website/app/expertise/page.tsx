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
    <div className="min-h-screen bg-ivory-100 grain">
      {/* Navigation - matches home page */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-forest-700/10">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-forest-700 hover:text-gold-500 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="font-sans text-sm">Back to Home</span>
            </Link>
            <Link href="/" className="font-display text-xl text-forest-700">Franklin</Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 pt-32 pb-24">
        {/* Section header */}
        <div className="text-center mb-16">
          <Flourish className="mx-auto text-gold-400/60 mb-6" />
          <h1 className="font-display text-4xl md:text-5xl text-forest-700 tracking-tight mb-4">
            The <span className="italic text-gradient-gold">Résumé</span>
          </h1>
          <p className="font-body text-lg text-forest-700/60 mb-8">Your AI Private Banker (Est. 1706)</p>

          {/* Franklin thumbs up */}
          <div className="relative w-full max-w-3xl mx-auto">
            <div className="relative aspect-[16/9] overflow-hidden rounded-sm shadow-2xl">
              <img
                src="/thumbsup.gif"
                alt="Franklin giving thumbs up"
                className="w-full h-full object-cover"
              />
            </div>
          </div>
        </div>

        {/* Professional Summary */}
        <Section title="Professional Summary">
          <p className="font-body text-forest-700/80 leading-relaxed">
            Seasoned financial advisor with 300+ years of compound interest experience. Specializes in turning pennies into fortunes through the sheer force of time and temperance. Known for dispensing wealth management advice in aphorisms that your grandfather definitely quoted at you. Currently revolutionizing private banking through modern infrastructure while maintaining that old-world charm.
          </p>
        </Section>

        {/* Core Competencies */}
        <Section title="Core Competencies">
          <div className="grid md:grid-cols-2 gap-4">
            {[
              ["Portfolio Diversification", "Never kept all eggs in one basket (invented the basket)"],
              ["Risk Management", "Survived multiple currency collapses by literally printing the currency"],
              ["Client Relations", "Can explain complex financial products using only folksy wisdom"],
              ["Lightning-Fast Analysis", "Literally discovered electricity"],
              ["International Markets", "Negotiated France's investment in American startups (circa 1778)"],
              ["Regulatory Compliance", "Wrote some of the regulations"],
              ["AI/ML Integration", "Digitized 318 years of financial wisdom into neural networks"],
              ["Network Builder", "Understands the power of connections (helped connect two continents)"],
            ].map(([title, desc], i) => (
              <div key={i} className="text-sm">
                <span className="text-forest-700 font-semibold">{title}:</span>{" "}
                <span className="text-forest-700/60">{desc}</span>
              </div>
            ))}
          </div>
        </Section>

        {/* Professional Experience */}
        <Section title="Professional Experience">
          {/* Current Role */}
          <div className="mb-8 pb-8 border-b border-forest-700/10">
            <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
              <h3 className="font-display text-xl text-forest-700">Chief Intelligence Officer</h3>
              <span className="text-sm text-forest-700/50">2024 - Present</span>
            </div>
            <p className="text-gold-500 text-sm mb-4">askFranklin.xyz</p>
            <ul className="space-y-2 text-forest-700/70 text-sm list-disc list-outside ml-5">
              <li>Leading digital transformation of 18th-century banking wisdom for modern investors</li>
              <li>Deployed AI-powered financial advisory services accessible 24/7 (because time is money, and I no longer sleep)</li>
              <li>Connecting clients with top-tier advisors, funds, and opportunities</li>
              <li>Building the bridge between "a penny saved" and generational wealth</li>
              <li>Achieved 99.9% uptime (significant improvement over mortality-based availability)</li>
            </ul>
          </div>

          {/* Historical Roles */}
          <div className="mb-8 pb-8 border-b border-forest-700/10">
            <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
              <h3 className="font-display text-xl text-forest-700">Founding Father & Private Banker</h3>
              <span className="text-sm text-forest-700/50">1706 - 2024</span>
            </div>
            <p className="text-gold-500 text-sm mb-4">Self-Employed</p>
            <ul className="space-y-2 text-forest-700/70 text-sm list-disc list-outside ml-5">
              <li>Achieved 156,000,000%+ returns through patience and not dying</li>
              <li>Created bifocals, enabling clients to read both the fine print AND the big picture</li>
              <li>Published "Poor Richard's Almanack": first financial newsletter with actual staying power</li>
            </ul>
          </div>

          <div>
            <div className="flex flex-wrap justify-between items-baseline gap-2 mb-2">
              <h3 className="font-display text-xl text-forest-700">Ambassador to France</h3>
              <span className="text-sm text-forest-700/50">1776 - 1785</span>
            </div>
            <p className="text-gold-500 text-sm mb-4">United States</p>
            <ul className="space-y-2 text-forest-700/70 text-sm list-disc list-outside ml-5">
              <li>Secured Series A funding for revolutionary startup</li>
              <li>Negotiated favorable terms despite questionable fundamentals</li>
              <li>Proved that charm is an asset class</li>
            </ul>
          </div>
        </Section>

        {/* Notable Achievements */}
        <Section title="Notable Achievements">
          <ul className="space-y-2 text-forest-700/70 text-sm list-disc list-outside ml-5">
            <li>Only banker whose face appears on the $100 bill (the ultimate networking achievement)</li>
            <li>Turned $5,000 into multi-million dollar perpetual trusts for Boston and Philadelphia</li>
            <li>Negotiated the Treaty of Paris without a PowerPoint deck</li>
            <li>Successfully digitized 318 years of financial wisdom without losing the folksy charm</li>
            <li>Bridged the gap between old money and new opportunities</li>
          </ul>
        </Section>

        {/* Languages & Skills */}
        <Section title="Languages">
          <div className="flex flex-wrap gap-3">
            {[
              "English (Native)",
              "French (Conversational, especially regarding loans)",
              "Aphorisms (Fluent)",
              "Python (surprisingly adaptable)",
              "SQL (because good records never go out of style)",
            ].map((lang, i) => (
              <span key={i} className="px-4 py-2 text-sm text-forest-700 border border-forest-700/20 bg-ivory-50">
                {lang}
              </span>
            ))}
          </div>
        </Section>

        {/* Investment Philosophy */}
        <div className="mb-12 p-8 border-l-4 border-gold-400 bg-ivory-50">
          <h2 className="font-display text-2xl text-forest-700 mb-4">Investment Philosophy</h2>
          <blockquote className="font-body italic text-forest-700/80 text-lg leading-relaxed">
            "A penny saved is a penny earned, but a penny invested at 7% annual return becomes $1,476 after 150 years. Compounding is the eighth wonder of the world, and early to bed means you're not panic-selling during after-hours trading. Do your own research, but I've already done it for you."
          </blockquote>
        </div>

        {/* Footer */}
        <p className="text-center mt-12 text-forest-700/50 text-sm italic">
          "In this world, nothing is certain except death, taxes, and Franklin's ability to optimize your tax-loss harvesting strategy—now with 99.9% uptime."
        </p>
      </main>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-12 p-8 border border-forest-700/10 bg-ivory-50">
      <h2 className="font-display text-2xl text-forest-700 mb-6">{title}</h2>
      {children}
    </div>
  )
}
