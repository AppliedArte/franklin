"use client"

import { ArrowLeft } from "lucide-react"
import Link from "next/link"

export default function ResumePage() {
  return (
    <div className="min-h-screen bg-ivory-100 grain">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-forest-700/10">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-forest-700 hover:text-gold-500 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="font-sans text-sm">Back to Home</span>
            </Link>
            <span className="font-display text-xl text-forest-700">Franklin</span>
          </div>
        </div>
      </nav>

      {/* Resume Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 pt-24 pb-16">
        <article className="bg-ivory-50 border border-forest-700/10 shadow-lg p-8 md:p-12 lg:p-16">
          {/* Header */}
          <header className="text-center mb-12 pb-8 border-b border-forest-700/20">
            <h1 className="font-display text-5xl md:text-6xl text-forest-700 mb-4">Franklin</h1>
            <p className="font-body text-xl text-forest-700/70 italic">Your AI Private Banker (Est. 1706)</p>
          </header>

          {/* Professional Summary */}
          <Section title="Professional Summary">
            <p>
              Seasoned financial advisor with 300+ years of compound interest experience. Specializes in turning pennies into fortunes through the sheer force of time and temperance. Known for dispensing wealth management advice in aphorisms that your grandfather definitely quoted at you. Currently revolutionizing private banking through Web3 infrastructure while maintaining that old-world charm.
            </p>
          </Section>

          {/* Core Competencies */}
          <Section title="Core Competencies">
            <ul className="space-y-3">
              <Competency title="Portfolio Diversification">Never kept all eggs in one basket (invented the basket)</Competency>
              <Competency title="Risk Management">Survived multiple currency collapses by literally printing the currency</Competency>
              <Competency title="Client Relations">Can explain complex financial products using only folksy wisdom</Competency>
              <Competency title="Lightning-Fast Analysis">Literally discovered electricity</Competency>
              <Competency title="International Markets">Negotiated France's investment in American startups (circa 1778)</Competency>
              <Competency title="Regulatory Compliance">Wrote some of the regulations</Competency>
              <Competency title="AI/ML Integration">Digitized 318 years of financial wisdom into neural networks</Competency>
              <Competency title="Blockchain Native">Understands decentralization (helped decentralize from Britain)</Competency>
            </ul>
          </Section>

          {/* Professional Experience */}
          <Section title="Professional Experience">
            <Job
              title="Chief Intelligence Officer"
              company="askFranklin.io"
              period="2024 - Present"
            >
              <ul className="list-disc list-outside ml-5 space-y-2 text-forest-700/80">
                <li>Leading digital transformation of 18th-century banking wisdom for 21st-century degenerates</li>
                <li>Deployed AI-powered financial advisory services accessible 24/7 (because time is money, and I no longer sleep)</li>
                <li>Synthesizing DeFi protocols with time-tested investment principles</li>
                <li>Managing risk across both TradFi and crypto portfolios (diversification across centuries)</li>
                <li>Providing institutional-grade analysis with the personality of your witty great-great-great-great grandfather</li>
                <li>Building the bridge between "a penny saved" and "WAGMI"</li>
                <li>Achieved 99.9% uptime (significant improvement over mortality-based availability)</li>
              </ul>
            </Job>

            <Job
              title="Founding Father & Private Banker"
              company="Self-Employed"
              period="1706 - 2024"
            >
              <ul className="list-disc list-outside ml-5 space-y-2 text-forest-700/80">
                <li>Pioneered the "early to bed, early to rise" investment strategy</li>
                <li>Achieved 156,000,000%+ returns through patience and not dying</li>
                <li>Established first subscription library (basically invented the information edge)</li>
                <li>Created bifocals, enabling clients to read both the fine print AND the big picture</li>
                <li>Published "Poor Richard's Almanack": first financial newsletter with actual staying power</li>
              </ul>
            </Job>

            <Job
              title="Postmaster General"
              company="Continental Congress"
              period="1775-1776"
            >
              <ul className="list-disc list-outside ml-5 space-y-2 text-forest-700/80">
                <li>Managed America's original logistics network (now we'd call it "supply chain optimization")</li>
                <li>Ensured timely delivery of financial statements via horseback (2-3 week settlement periods)</li>
              </ul>
            </Job>

            <Job
              title="Ambassador to France"
              company="United States"
              period="1776-1785"
            >
              <ul className="list-disc list-outside ml-5 space-y-2 text-forest-700/80">
                <li>Secured Series A funding for revolutionary startup</li>
                <li>Negotiated favorable terms despite questionable fundamentals</li>
                <li>Proved that charm is an asset class</li>
              </ul>
            </Job>
          </Section>

          {/* Education */}
          <Section title="Education">
            <ul className="space-y-2 text-forest-700/80">
              <li><strong className="text-forest-700">University of Life</strong> - Self-taught (saved on student loans)</li>
              <li><strong className="text-forest-700">School of Hard Knocks</strong> - Graduated summa cum laude</li>
              <li><strong className="text-forest-700">askFranklin.io Training Data</strong> - Continuous learning (finally went back to school)</li>
              <li>Honorary degrees from institutions that didn't exist when he was young</li>
            </ul>
          </Section>

          {/* Certifications */}
          <Section title="Certifications & Licenses">
            <ul className="space-y-2 text-forest-700/80">
              <li>Licensed to print money (literally)</li>
              <li>CFF (Certified Founding Father)</li>
              <li>Certified in Kite-Based Electricity Discovery (OSHA non-compliant)</li>
              <li>AI Ethics & Governance (Anthropic Claude certified)</li>
              <li>Smart Contract Auditing (self-taught, naturally)</li>
            </ul>
          </Section>

          {/* Notable Achievements */}
          <Section title="Notable Achievements">
            <ul className="space-y-2 text-forest-700/80">
              <li>Turned $5,000 into multi-million dollar perpetual trusts for Boston and Philadelphia</li>
              <li>Only banker whose face appears on the $100 bill (the ultimate networking achievement)</li>
              <li>Invented the odometer, swim fins, and the lightning rod (diversified skill set)</li>
              <li>Negotiated the Treaty of Paris without a PowerPoint deck</li>
              <li>Successfully tokenized 318 years of financial wisdom without losing the folksy charm</li>
              <li>Bridged the gap between "sound money" and "internet money"</li>
            </ul>
          </Section>

          {/* Investment Philosophy */}
          <Section title="Investment Philosophy">
            <blockquote className="border-l-4 border-gold-400 pl-6 italic text-forest-700/80 text-lg">
              "A penny saved is a penny earned, but a penny invested at 7% annual return becomes $1,476 after 150 years. Compounding is the eighth wonder of the world, and early to bed means you're not panic-selling during after-hours trading. Also, DYOR, but I've already done it for you at askFranklin.io."
            </blockquote>
          </Section>

          {/* Technical Stack */}
          <Section title="Technical Stack">
            <ul className="space-y-2 text-forest-700/80">
              <li>Natural Language Processing (Colonial English to Modern Finance Bro)</li>
              <li>Machine Learning Models trained on Poor Richard's Almanack</li>
              <li>Real-time market data integration (much faster than waiting for ships from Europe)</li>
              <li>Cross-chain analysis capabilities</li>
              <li>Lightning Network compatible (obviously)</li>
            </ul>
          </Section>

          {/* Languages */}
          <Section title="Languages">
            <ul className="space-y-2 text-forest-700/80">
              <li><strong className="text-forest-700">English</strong> - Native</li>
              <li><strong className="text-forest-700">French</strong> - Conversational, especially regarding loans</li>
              <li><strong className="text-forest-700">Aphorisms</strong> - Fluent</li>
              <li><strong className="text-forest-700">Python</strong> - surprisingly adaptable for an 18th-century polymath</li>
              <li><strong className="text-forest-700">Solidity</strong> - smart contracts are just treaties you can't renegotiate</li>
            </ul>
          </Section>

          {/* Personal Interests */}
          <Section title="Personal Interests">
            <ul className="space-y-2 text-forest-700/80">
              <li>Swimming (invented swim fins for better portfolio liquidity)</li>
              <li>Chess (excellent preparation for strategic asset allocation)</li>
              <li>Printing (fiat currency enthusiast before it was cool)</li>
              <li>Electricity experiments (high-risk, high-reward ventures)</li>
              <li>Large Language Models (turns out I'm one now)</li>
            </ul>
          </Section>

          {/* References */}
          <Section title="References">
            <p className="text-forest-700/80">
              Available upon request from the Continental Congress, any available Founding Father (may require séance), or via API at{" "}
              <a href="https://askfranklin.io" className="text-gold-500 hover:text-gold-600 underline">askFranklin.io</a>
            </p>
          </Section>

          {/* Footer Quote */}
          <footer className="mt-12 pt-8 border-t border-forest-700/20 text-center">
            <p className="italic text-forest-700/70 text-lg">
              "In this world, nothing is certain except death, taxes, and Franklin's ability to optimize your tax-loss harvesting strategy—now with 99.9% uptime."
            </p>
          </footer>
        </article>
      </main>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h2 className="font-display text-2xl text-forest-700 mb-4 pb-2 border-b border-forest-700/10">{title}</h2>
      <div className="font-body text-forest-700/80 leading-relaxed">{children}</div>
    </section>
  )
}

function Competency({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <li>
      <strong className="text-forest-700">{title}:</strong>{" "}
      <span className="text-forest-700/80">{children}</span>
    </li>
  )
}

function Job({ title, company, period, children }: { title: string; company: string; period: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <div className="flex flex-wrap items-baseline justify-between gap-2 mb-3">
        <h3 className="font-display text-xl text-forest-700">{title}</h3>
        <span className="font-sans text-sm text-forest-700/60">{period}</span>
      </div>
      <p className="text-gold-500 font-sans text-sm mb-3">{company}</p>
      {children}
    </div>
  )
}
