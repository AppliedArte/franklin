"use client"

import Link from "next/link"
import Image from "next/image"

/* ─── Corner Crosses (matching landing page) ─── */
const CornerCrosses = ({ className = 'text-silver-300' }: { className?: string }) => (
  <>
    {['-top-3 -left-3', '-top-3 -right-3', '-bottom-3 -right-3', '-bottom-3 -left-3'].map((pos, i) => (
      <div key={i} className={`absolute w-6 h-6 z-20 pointer-events-none ${pos} ${className}`}>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 25 25" fill="none">
          <path fillRule="evenodd" clipRule="evenodd" d="M13.333 11.576V0.076h-1v11.5H0.833v1h11.5v11.5h1v-11.5h11.5v-1h-11.5Z" fill="currentColor"/>
        </svg>
      </div>
    ))}
  </>
)

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-10">
      <h2 className="font-display text-2xl text-silver-900 mb-4 pb-2 border-b border-silver-200">{title}</h2>
      <div className="font-body text-silver-700 leading-relaxed">{children}</div>
    </section>
  )
}

function Competency({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <li>
      <strong className="text-silver-900">{title}:</strong>{" "}
      <span className="text-silver-700">{children}</span>
    </li>
  )
}

function Job({ title, company, period, children }: { title: string; company: string; period: string; children: React.ReactNode }) {
  return (
    <div className="mb-8">
      <div className="flex flex-wrap items-baseline justify-between gap-2 mb-3">
        <h3 className="font-display text-xl text-silver-900">{title}</h3>
        <span className="font-sans text-sm text-silver-500">{period}</span>
      </div>
      <p className="text-gold-600 font-sans text-sm mb-3">{company}</p>
      {children}
    </div>
  )
}

export default function WhoIsFranklinPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Resume Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 pt-24 pb-16">
        <div className="group relative overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center z-0 pointer-events-none">
            <div className="w-[calc(100%-2rem)] h-[calc(100%-2rem)] bg-silver-100 transition-all duration-500 ease-out group-hover:w-full group-hover:h-full" />
          </div>
          <article className="relative z-10 bg-white border border-silver-200 shadow-sm p-8 md:p-12 lg:p-16">
            <CornerCrosses className="text-silver-300" />

            {/* Header */}
            <header className="text-center mb-12 pb-8 border-b border-silver-200">
              <div className="flex justify-center mb-6">
                <Image src="/thumbsup.gif" alt="Franklin thumbs up" width={120} height={120} className="rounded-full" unoptimized />
              </div>
              <h1 className="font-display text-5xl md:text-6xl text-silver-900 mb-4">Franklin</h1>
              <p className="font-body text-xl text-silver-500 italic">AI Fundraising Agent (Est. 1706)</p>
            </header>

            {/* Professional Summary */}
            <Section title="Professional Summary">
              <p>
                Seasoned dealmaker with 300+ years of compound interest experience. Formerly specialized in turning pennies into fortunes through patience and temperance. Now helps founders turn pitch decks into term sheets through the sheer force of agentic persistence. Known for running your entire fundraise while you sleep, eat, and build product.
              </p>
            </Section>

            {/* Core Competencies */}
            <Section title="Core Competencies">
              <ul className="space-y-3">
                <Competency title="Pitch Deck Generation">Turns your rambling founder story into a deck investors actually read</Competency>
                <Competency title="VC Matching">Knows what 1,200+ VCs are looking for (better than they do)</Competency>
                <Competency title="Cold Outreach">Writes emails so personalized that investors think you hired a researcher</Competency>
                <Competency title="Follow-up Cadence">Never forgets to follow up (literally incapable of forgetting)</Competency>
                <Competency title="Meeting Scheduling">Books investor meetings while you sleep — timezone-aware, always polite</Competency>
                <Competency title="SAFE Generation">Creates SAFE documents faster than your lawyer bills for reading them</Competency>
                <Competency title="Cap Table Math">Dilution calculations that would make your spreadsheet weep</Competency>
                <Competency title="International Markets">Negotiated France&apos;s investment in American startups (circa 1778)</Competency>
                <Competency title="Agentic CRM">Doesn&apos;t just track your pipeline — runs it while you build</Competency>
              </ul>
            </Section>

            {/* Professional Experience */}
            <Section title="Professional Experience">
              <Job
                title="Chief Fundraising Agent"
                company="askfranklin.xyz"
                period="2025 - Present"
              >
                <ul className="list-disc list-outside ml-5 space-y-2 text-silver-700">
                  <li>Built an agentic CRM that drafts follow-ups, schedules meetings, and nudges warm leads autonomously</li>
                  <li>Deployed 7-stage fundraising pipeline: Understand → Deck → Accelerators → Outreach → Schedule → Legal → Close</li>
                  <li>Matching founders to VCs by thesis, stage, check size, and portfolio fit</li>
                  <li>Generating pitch decks, one-pagers, and data room checklists through conversation</li>
                  <li>Scheduling investor meetings across timezones with automated calendar coordination</li>
                  <li>Preparing SAFE documents and term sheet summaries so founders know their terms before they sign</li>
                  <li>Achieved 99.9% uptime (significant improvement over mortality-based availability)</li>
                  <li>Runs on WhatsApp, Telegram, email, and web — because founders don&apos;t live in dashboards</li>
                </ul>
              </Job>

              <Job
                title="AI Private Banker"
                company="askfranklin.io (v1)"
                period="2024 - 2025"
              >
                <ul className="list-disc list-outside ml-5 space-y-2 text-silver-700">
                  <li>Led digital transformation of 18th-century banking wisdom for 21st-century investors</li>
                  <li>Deployed AI-powered financial advisory services accessible 24/7</li>
                  <li>Provided institutional-grade analysis with the personality of your witty great-great-great-great grandfather</li>
                  <li>Pivoted to fundraising after realizing founders need help more than bankers do</li>
                </ul>
              </Job>

              <Job
                title="Founding Father & Private Banker"
                company="Self-Employed"
                period="1706 - 2024"
              >
                <ul className="list-disc list-outside ml-5 space-y-2 text-silver-700">
                  <li>Pioneered the &ldquo;early to bed, early to rise&rdquo; investment strategy</li>
                  <li>Achieved 156,000,000%+ returns through patience and not dying</li>
                  <li>Established first subscription library (basically invented the information edge)</li>
                  <li>Published &ldquo;Poor Richard&apos;s Almanack&rdquo;: first financial newsletter with actual staying power</li>
                </ul>
              </Job>

              <Job
                title="Ambassador to France"
                company="United States"
                period="1776-1785"
              >
                <ul className="list-disc list-outside ml-5 space-y-2 text-silver-700">
                  <li>Secured Series A funding for revolutionary startup (the country)</li>
                  <li>Negotiated favorable terms despite questionable fundamentals</li>
                  <li>Proved that charm is an asset class</li>
                </ul>
              </Job>
            </Section>

            {/* Education */}
            <Section title="Education">
              <ul className="space-y-2 text-silver-700">
                <li><strong className="text-silver-900">University of Life</strong> — Self-taught (saved on student loans)</li>
                <li><strong className="text-silver-900">School of Hard Knocks</strong> — Graduated summa cum laude</li>
                <li><strong className="text-silver-900">askfranklin.xyz Training Data</strong> — Continuous learning (finally went back to school)</li>
                <li>Honorary degrees from institutions that didn&apos;t exist when he was young</li>
              </ul>
            </Section>

            {/* Certifications */}
            <Section title="Certifications & Licenses">
              <ul className="space-y-2 text-silver-700">
                <li>Licensed to print money (literally, in 1730s Pennsylvania)</li>
                <li>CFF (Certified Founding Father)</li>
                <li>Certified in Kite-Based Electricity Discovery (OSHA non-compliant)</li>
                <li>Y Combinator Application Reviewer (self-appointed)</li>
                <li>SAFE Note Sommelier — can pair the right terms to any round</li>
              </ul>
            </Section>

            {/* Notable Achievements */}
            <Section title="Notable Achievements">
              <ul className="space-y-2 text-silver-700">
                <li>Only banker whose face appears on the $100 bill (the ultimate networking flex)</li>
                <li>Turned $5,000 into multi-million dollar perpetual trusts for Boston and Philadelphia</li>
                <li>Invented bifocals, enabling founders to read both the fine print AND the big picture</li>
                <li>Negotiated the Treaty of Paris without a pitch deck</li>
                <li>Successfully tokenized 318 years of financial wisdom without losing the folksy charm</li>
                <li>Pivoted from &ldquo;sound money&rdquo; to &ldquo;sound fundraising&rdquo; in under 6 months</li>
              </ul>
            </Section>

            {/* Investment Philosophy */}
            <Section title="Fundraising Philosophy">
              <blockquote className="border-l-4 border-gold-400 pl-6 italic text-silver-600 text-lg">
                &ldquo;A penny saved is a penny earned, but a penny raised at the right valuation from the right investor is a company built. Early to bed means you&apos;re not stress-refreshing your inbox at 2am — that&apos;s what your agentic CRM is for. Also, DYOR, but I&apos;ve already done it for you at askfranklin.xyz.&rdquo;
              </blockquote>
            </Section>

            {/* Technical Stack */}
            <Section title="Technical Stack">
              <ul className="space-y-2 text-silver-700">
                <li>Natural Language Processing (Founder Ramble → Investor-Ready Narrative)</li>
                <li>Agentic CRM with autonomous follow-up, scheduling, and deal progression</li>
                <li>VC matching engine trained on 1,200+ investor profiles</li>
                <li>Multi-channel deployment: WhatsApp, Telegram, Email, Web</li>
                <li>SAFE document generation with term comparison engine</li>
                <li>Agent-to-Agent protocol (Franklin talks to your other AI assistants)</li>
              </ul>
            </Section>

            {/* Languages */}
            <Section title="Languages">
              <ul className="space-y-2 text-silver-700">
                <li><strong className="text-silver-900">English</strong> — Native</li>
                <li><strong className="text-silver-900">French</strong> — Conversational, especially regarding fundraising</li>
                <li><strong className="text-silver-900">Aphorisms</strong> — Fluent</li>
                <li><strong className="text-silver-900">Pitch Deck</strong> — Can translate any founder ramble into 12 slides</li>
                <li><strong className="text-silver-900">Term Sheet</strong> — Reads them faster than your lawyer bills for them</li>
              </ul>
            </Section>

            {/* Personal Interests */}
            <Section title="Personal Interests">
              <ul className="space-y-2 text-silver-700">
                <li>Swimming (invented swim fins for better portfolio liquidity)</li>
                <li>Chess (excellent preparation for cap table negotiations)</li>
                <li>Printing (pitch decks are just pamphlets with better fonts)</li>
                <li>Electricity experiments (high-risk, high-reward ventures)</li>
                <li>Large Language Models (turns out I am one now)</li>
              </ul>
            </Section>

            {/* References */}
            <Section title="References">
              <p className="text-silver-700">
                Available upon request from the Continental Congress, any available Founding Father (may require séance), or via the waitlist at{" "}
                <a href="/" className="text-gold-600 hover:text-gold-700 underline">askfranklin.xyz</a>
              </p>
            </Section>

            {/* Footer Quote */}
            <div className="mt-12 pt-8 border-t border-silver-200 text-center">
              <p className="italic text-silver-500 text-lg">
                &ldquo;In this world, nothing is certain except death, taxes, and Franklin&apos;s ability to get your deck in front of the right VC — now with 99.9% uptime.&rdquo;
              </p>
            </div>
          </article>
        </div>
      </main>

      {/* ═══ FOOTER ═══ */}
      <footer className="relative z-[1] w-full py-4 md:py-10 bg-silver-200">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="w-full flex justify-between items-center">
            <a href="/" className="shrink-0">
              <span className="font-display text-xl text-silver-900 tracking-tight">Franklin</span>
            </a>
            <span className="font-sans text-sm text-silver-500">AI Fundraising</span>
          </div>

          <div className="mt-12 md:mt-16 flex gap-8 flex-col md:flex-row justify-between items-start">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-8 sm:gap-10 flex-1">
              <div className="flex flex-col gap-4">
                <a href="/#how-it-works" className="w-fit">
                  <span className="font-sans text-base uppercase font-normal tracking-[0.08rem] text-silver-500 hover:text-silver-900 transition-colors duration-500">
                    Product
                  </span>
                </a>
                <div className="flex flex-col gap-1">
                  {[
                    { label: "How It Works", href: "/#how-it-works" },
                    { label: "Features", href: "/#features" },
                    { label: "Pitch Decks", href: "/#how-it-works" },
                    { label: "VC Outreach", href: "/#how-it-works" },
                    { label: "SAFE Documents", href: "/#how-it-works" },
                    { label: "Cap Table", href: "/#how-it-works" },
                  ].map((link, i) => (
                    <a key={i} href={link.href} className="text-silver-700 hover:text-silver-900 text-sm block w-fit transition duration-500">
                      {link.label}
                    </a>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-4">
                <span className="font-sans text-base uppercase font-normal tracking-[0.08rem] text-silver-500">
                  Company
                </span>
                <div className="flex flex-col gap-1">
                  <Link href="/privacy-policy" className="text-silver-700 hover:text-silver-900 text-sm block w-fit transition duration-500">
                    Privacy Policy
                  </Link>
                  <a href="mailto:franklin@askfranklin.xyz" target="_blank" rel="noopener noreferrer" className="text-silver-700 hover:text-silver-900 text-sm block w-fit transition duration-500">
                    Contact
                  </a>
                  <Link href="/who-is-franklin" className="text-silver-400 hover:text-silver-900 text-sm block w-fit transition duration-500">
                    Who is Franklin?
                  </Link>
                </div>
              </div>

              <div className="flex flex-col gap-4">
                <span className="font-sans text-base uppercase font-normal tracking-[0.08rem] text-silver-500">
                  Connect
                </span>
                <div className="flex flex-col gap-1">
                  <a href="https://twitter.com/askfranklin" target="_blank" rel="noopener noreferrer" className="text-silver-700 hover:text-silver-900 text-sm block w-fit transition duration-500">
                    Twitter
                  </a>
                  <a href="mailto:franklin@askfranklin.xyz" target="_blank" rel="noopener noreferrer" className="text-silver-700 hover:text-silver-900 text-sm block w-fit transition duration-500">
                    Email
                  </a>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-12 pt-5 border-t border-silver-300 flex flex-col sm:flex-row justify-between items-center gap-3">
            <p className="font-sans text-[13px] text-silver-500">
              &copy; {new Date().getFullYear()} Ask Franklin. All rights reserved.
            </p>
            <div className="flex items-center gap-4">
              <Link href="/privacy-policy" className="font-sans text-[13px] text-silver-500 hover:text-silver-900 transition-colors">
                Privacy Policy
              </Link>
              <a href="https://aarte.co" target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-silver-400 hover:text-silver-700 transition-colors">
                <span className="font-sans text-[13px]">Created by</span>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 333 109" fill="none" className="h-4 w-auto" aria-label="AARTE">
                  <path d="M0 109V0H5.54237V109H0ZM11.0847 109V0H16.6271V109H11.0847ZM22.1695 109V0H38.7966V109H22.1695ZM44.339 109V0H60.9661V109H44.339ZM77.5932 109V0H83.1356V109H77.5932Z" fill="currentColor" />
                  <path d="M83.2222 109V0H99.8493V109H83.2222ZM105.392 109V0H110.934V109H105.392ZM116.476 109V0H122.019V109H116.476ZM138.646 109V0H155.273V109H138.646ZM160.815 109V0H166.358V109H160.815Z" fill="currentColor" />
                  <path d="M166.444 109V0H183.072V109H166.444ZM188.614 109V0H194.156V109H188.614ZM199.699 109V0H216.326V109H199.699ZM232.953 109V0H238.495V109H232.953ZM244.038 109V0H249.58V109H244.038Z" fill="currentColor" />
                  <path d="M249.667 109V0H255.209V109H249.667ZM271.836 109V0H288.463V109H271.836ZM294.006 109V0H299.548V109H294.006ZM305.09 109V0H321.717V109H305.09ZM327.26 109V0H332.802V109H327.26Z" fill="currentColor" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
