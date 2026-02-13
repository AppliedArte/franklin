"use client"

import { useState } from "react"
import Link from "next/link"
import { CheckCircle, MessageCircle, FileText, Send, Scale, Users, Bot, Smartphone, Zap, BarChart3, Globe, Shield, Mail, TrendingUp, Clock } from "lucide-react"

/* ─── Corner Dots Component ─── */
const CornerDots = ({ size = '0.25rem', offset = '-0.15625rem', visible }: { size?: string; offset?: string; visible: boolean }) => (
  <>
    {[
      { top: offset, left: offset },
      { top: offset, right: offset },
      { bottom: offset, right: offset },
      { bottom: offset, left: offset },
    ].map((pos, i) => (
      <div key={i} className="absolute z-10 bg-gold-400 transition-opacity"
        style={{ height: size, width: size, opacity: visible ? 1 : 0, ...pos }} />
    ))}
  </>
)

/* ─── Geometric Button (Arclin-style corner dots + expanding border lines) ─── */
function GeometricButton({ href, children, className = '' }: { href: string; children: React.ReactNode; className?: string }) {
  const [hovered, setHovered] = useState(false)
  const dim = { thickness: '0.0625rem', offset: '-0.53125rem', rest: '1rem', full: 'calc(100% + 0.0625rem)' }
  const baseStyle = { backgroundColor: hovered ? 'rgb(255 255 255)' : undefined }

  const lines = [
    { bottom: '100%', height: dim.thickness, left: dim.offset, width: hovered ? dim.full : dim.rest, expanding: true },
    { right: '100%', width: dim.thickness, top: dim.offset, height: dim.rest },
    { bottom: '100%', height: dim.thickness, right: dim.offset, width: dim.rest },
    { left: '100%', width: dim.thickness, top: dim.offset, height: hovered ? dim.full : dim.rest, expanding: true },
    { top: '100%', height: dim.thickness, right: dim.offset, width: hovered ? dim.full : dim.rest, expanding: true },
    { left: '100%', width: dim.thickness, bottom: dim.offset, height: dim.rest },
    { top: '100%', height: dim.thickness, left: dim.offset, width: dim.rest },
    { right: '100%', width: dim.thickness, bottom: dim.offset, height: hovered ? dim.full : dim.rest, expanding: true },
  ]

  return (
    <a href={href} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
      className={`relative inline-flex items-center justify-center px-8 py-4 text-lg backdrop-blur-sm bg-silver-900/10 font-semibold uppercase font-sans tracking-wider leading-none select-none whitespace-nowrap cursor-pointer transition ${
        hovered ? 'text-white' : 'text-silver-300'
      } ${className}`}>
      {children}
      <CornerDots visible={hovered} />
      {lines.map((style, i) => (
        <div key={i} className={`absolute bg-silver-300 ${style.expanding ? 'transition-all duration-700' : 'transition-colors duration-700'}`}
          style={{ ...style, ...baseStyle, expanding: undefined }} />
      ))}
    </a>
  )
}

/* ─── Nav Geometric Button (smaller version for navbar) ─── */
function NavGeometricButton({ href, children }: { href: string; children: React.ReactNode }) {
  const [hovered, setHovered] = useState(false)
  return (
    <a href={href} onMouseEnter={() => setHovered(true)} onMouseLeave={() => setHovered(false)}
      className={`relative inline-flex items-center justify-center px-4 py-3 text-sm xl:text-base font-semibold font-sans uppercase tracking-wide leading-none select-none cursor-pointer transition border-2 border-silver-500 ${
        hovered ? 'bg-silver-700 text-white' : 'text-silver-700'
      }`}>
      {children}
      <CornerDots visible={hovered} />
    </a>
  )
}

/* ─── Signup Form ─── */
function SignupForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [formError, setFormError] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState({
    name: false, email: false, company_name: false,
    one_liner: false, stage: false, raising: false
  })
  const [formData, setFormData] = useState({
    name: '', email: '', company_name: '', one_liner: '',
    stage: '', raising: '', linkedin: '', telegram: ''
  })

  const handleSubmit = async () => {
    const requiredFields = ['name', 'email', 'company_name', 'one_liner', 'stage', 'raising'] as const
    const errors = Object.fromEntries(requiredFields.map(f => [f, !formData[f]])) as typeof fieldErrors
    setFieldErrors(errors)

    if (Object.values(errors).some(Boolean)) {
      setFormError(true)
      setTimeout(() => setFormError(false), 2000)
      return
    }

    setIsSubmitting(true)
    setFormError(false)
    setApiError(null)

    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...formData, fund_name: formData.company_name, user_type: 'founder' })
      })

      if (response.ok) {
        setIsSubmitted(true)
      } else {
        const errorData = await response.json().catch(() => ({}))
        setApiError(errorData.error || `Server error (${response.status})`)
      }
    } catch {
      setApiError('Network error — please try again')
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateField = (field: string) => (value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    setFieldErrors(prev => ({ ...prev, [field]: false }))
  }

  const inputClass = (hasError: boolean) =>
    `w-full px-4 py-3 text-[15px] font-sans rounded-lg border bg-white focus:outline-none focus:ring-2 focus:ring-silver-800/20 transition-all text-silver-800 placeholder:text-silver-300 ${
      hasError ? 'border-red-400 bg-red-50/50' : 'border-silver-200 hover:border-silver-300'
    }`

  const FormField = ({ label, field, type = 'text', placeholder, options }: {
    label: string; field: keyof typeof formData; type?: string; placeholder?: string; options?: { value: string; label: string }[]
  }) => {
    const hasError = fieldErrors[field as keyof typeof fieldErrors]
    return (
      <div>
        <label className={`block text-xs font-sans font-medium mb-1.5 ${hasError ? 'text-red-600' : 'text-silver-500'}`}>
          {label} {hasError && <span className="text-red-500">*</span>}
        </label>
        {options ? (
          <select value={formData[field]} onChange={e => updateField(field)(e.target.value)} className={inputClass(hasError)}>
            {options.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
          </select>
        ) : (
          <input type={type} value={formData[field]} onChange={e => updateField(field)(e.target.value)}
            placeholder={placeholder} className={inputClass(hasError)} />
        )}
      </div>
    )
  }

  if (isSubmitted) {
    return (
      <div className="max-w-md mx-auto text-center py-8">
        <div className="w-14 h-14 rounded-full bg-green-50 flex items-center justify-center mx-auto mb-5">
          <CheckCircle className="w-7 h-7 text-green-600" />
        </div>
        <h3 className="font-display text-2xl text-silver-800 mb-2">
          Let&apos;s get you funded, {formData.name.split(' ')[0]}.
        </h3>
        <p className="font-sans text-silver-500 text-[15px] leading-relaxed">
          {formData.telegram
            ? "We'll message you on Telegram to start building your raise strategy."
            : "Check your inbox — we've sent you next steps to kick off your raise."}
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-xl mx-auto text-left">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <FormField label="Your name" field="name" placeholder="Jane Doe" />
          <FormField label="Email" field="email" type="email" placeholder="jane@startup.com" />
        </div>

        <FormField label="Company name" field="company_name" placeholder="Acme Inc." />
        <FormField label="One-liner" field="one_liner" placeholder="We help X do Y with Z" />

        <div className="grid grid-cols-2 gap-4">
          <FormField label="Stage" field="stage" options={[
            { value: '', label: 'Select...' },
            { value: 'pre-seed', label: 'Pre-Seed' },
            { value: 'seed', label: 'Seed' },
            { value: 'series-a', label: 'Series A' },
            { value: 'series-b+', label: 'Series B+' },
          ]} />
          <FormField label="Raising" field="raising" options={[
            { value: '', label: 'Select...' },
            { value: '<500k', label: 'Under $500K' },
            { value: '500k-1m', label: '$500K – $1M' },
            { value: '1m-3m', label: '$1M – $3M' },
            { value: '3m-10m', label: '$3M – $10M' },
            { value: '10m+', label: '$10M+' },
          ]} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-sans font-medium mb-1.5 text-silver-400">LinkedIn <span className="text-silver-300">(optional)</span></label>
            <input type="text" value={formData.linkedin} onChange={e => updateField('linkedin')(e.target.value)}
              placeholder="linkedin.com/in/jane" className={inputClass(false)} />
          </div>
          <div>
            <label className="block text-xs font-sans font-medium mb-1.5 text-silver-400">Telegram <span className="text-silver-300">(optional)</span></label>
            <input type="text" value={formData.telegram} onChange={e => updateField('telegram')(e.target.value)}
              placeholder="@username" className={inputClass(false)} />
          </div>
        </div>

        {apiError && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700 text-sm font-sans">{apiError}</p>
          </div>
        )}

        <button onClick={handleSubmit} disabled={isSubmitting}
          className={`w-full py-4 font-sans font-semibold text-lg uppercase tracking-wider transition-all flex items-center justify-center gap-2 border-2 ${
            formError ? 'bg-red-500 text-white border-red-500' : 'bg-silver-700 text-white border-silver-700 hover:bg-silver-900 hover:border-silver-900'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {isSubmitting ? (
            <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Submitting...</>
          ) : formError ? 'Please fill in all required fields' : (
            'Get Started'
          )}
        </button>
      </div>
    </div>
  )
}

/* ─── Mock UI: Pipeline Card ─── */
function PipelineVisual() {
  const statusColors = {
    done: { bg: 'bg-green-500/20', text: 'text-green-400' },
    active: { bg: 'bg-gold-400/20', text: 'text-gold-400 font-medium' },
    pending: { bg: 'bg-white/[0.06]', text: 'text-white/30' },
  }

  return (
    <div className="bg-[#32373c] rounded-2xl p-8 md:p-10">
      <div className="space-y-4">
        {[
          { label: "Understand your startup", status: "done" as const, icon: MessageCircle },
          { label: "Generate pitch deck", status: "done" as const, icon: FileText },
          { label: "Apply to accelerators", status: "done" as const, icon: Zap },
          { label: "Send to 47 matching VCs", status: "active" as const, icon: Send },
          { label: "Prepare SAFE documents", status: "pending" as const, icon: Scale },
          { label: "Close your round", status: "pending" as const, icon: CheckCircle },
        ].map((item, i) => {
          const colors = statusColors[item.status]
          return (
            <div key={i} className="flex items-center gap-4 py-1">
              <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${colors.bg}`}>
                <item.icon className={`w-4 h-4 ${colors.text}`} />
              </div>
              <span className={`font-sans text-[14px] ${colors.text}`}>{item.label}</span>
              {item.status === 'active' && (
                <span className="ml-auto text-xs text-gold-400/60 font-sans animate-pulse">in progress</span>
              )}
            </div>
          )
        })}
      </div>
      <div className="mt-5 pt-5 border-t border-white/10 flex items-center justify-between">
        <span className="text-xs text-white/30 font-sans">12 responses received</span>
        <span className="text-xs text-green-400 font-sans font-medium">3 term sheets</span>
      </div>
    </div>
  )
}

/* ─── Mock UI: CRM Preview (tall portrait format like Arclin's 768x2156 images) ─── */
function CRMPreview() {
  const investors = [
    { name: "Sequoia Capital", partner: "Pat Grady", status: "Term Sheet", color: "bg-green-500" },
    { name: "a16z", partner: "Kristina Shen", status: "Meeting Scheduled", color: "bg-gold-400" },
    { name: "Greylock", partner: "Reid Hoffman", status: "Deck Sent", color: "bg-blue-400" },
    { name: "Accel", partner: "Sonali De Rycker", status: "Email Opened", color: "bg-silver-400" },
    { name: "Founders Fund", partner: "Keith Rabois", status: "Researching", color: "bg-silver-300" },
    { name: "Index Ventures", partner: "Mark Goldberg", status: "In Queue", color: "bg-silver-200" },
  ]
  return (
    <div className="bg-[#32373c] rounded-2xl overflow-hidden">
      <div className="px-6 py-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <span className="text-white/60 font-sans text-xs font-medium tracking-wider uppercase">Investor Pipeline</span>
          <span className="text-green-400 font-sans text-xs font-medium">47 active</span>
        </div>
      </div>
      <div className="divide-y divide-white/[0.06]">
        {investors.map((inv, i) => (
          <div key={i} className="px-6 py-3.5 flex items-center gap-3">
            <div className={`w-2 h-2 rounded-full shrink-0 ${inv.color}`} />
            <div className="min-w-0 flex-1">
              <div className="text-white/80 font-sans text-[13px] font-medium truncate">{inv.name}</div>
              <div className="text-white/30 font-sans text-[11px] truncate">{inv.partner}</div>
            </div>
            <span className="text-white/40 font-sans text-[11px] shrink-0">{inv.status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Mock UI: Agent Chat Preview ─── */
function AgentPreview() {
  const messages = [
    { text: "What's the current MRR and growth rate for the Series A deck?", left: true },
    { text: "$84K MRR, 22% MoM. Updated cap table attached.", left: false },
    { text: "Deck updated. Sending to 12 new VC matches now.", left: true },
    { text: "Got it. Notify me when we get responses.", left: false },
  ]

  return (
    <div className="bg-[#32373c] rounded-2xl overflow-hidden">
      <div className="px-6 py-4 border-b border-white/10">
        <span className="text-white/60 font-sans text-xs font-medium tracking-wider uppercase">Agent-to-Agent</span>
      </div>
      <div className="p-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.left ? '' : 'justify-end'}`}>
            {msg.left && (
              <div className="w-7 h-7 rounded-full bg-gold-400/20 flex items-center justify-center shrink-0">
                <Bot className="w-3.5 h-3.5 text-gold-400" />
              </div>
            )}
            <div className={`px-4 py-2.5 rounded-xl ${msg.left ? 'bg-white/[0.06] rounded-tl-sm' : 'bg-gold-400/10 rounded-tr-sm'}`}>
              <p className={`font-sans text-[12px] leading-relaxed ${msg.left ? 'text-white/70' : 'text-gold-400/80'}`}>{msg.text}</p>
            </div>
            {!msg.left && (
              <div className="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                <Zap className="w-3.5 h-3.5 text-white/50" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Mock UI: Multi-Channel Preview ─── */
function ChannelPreview() {
  const channels = [
    { icon: Mail, label: "Email", detail: "23 investor threads", active: true },
    { icon: Send, label: "Telegram", detail: "Live notifications", active: true },
    { icon: Smartphone, label: "WhatsApp", detail: "Voice notes + docs", active: false },
    { icon: Globe, label: "Web Dashboard", detail: "Full pipeline view", active: true },
    { icon: Bot, label: "API / Webhooks", detail: "Custom integrations", active: true },
  ]

  return (
    <div className="bg-[#32373c] rounded-2xl overflow-hidden">
      <div className="px-6 py-4 border-b border-white/10">
        <span className="text-white/60 font-sans text-xs font-medium tracking-wider uppercase">Channels</span>
      </div>
      <div className="p-6 space-y-3">
        {channels.map((ch, i) => (
          <div key={i} className="flex items-center gap-3 px-3 py-2.5 rounded-lg bg-white/[0.04]">
            <ch.icon className={`w-4 h-4 shrink-0 ${ch.active ? 'text-green-400' : 'text-white/20'}`} />
            <div className="flex-1 min-w-0">
              <div className="text-white/70 font-sans text-[13px] font-medium">{ch.label}</div>
              <div className="text-white/30 font-sans text-[11px]">{ch.detail}</div>
            </div>
            <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${ch.active ? 'bg-green-400' : 'bg-white/10'}`} />
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Landing Page ─── */
export default function LandingPage() {
  return (
    <div className="bg-white text-silver-900">

      {/* ═══ NAVIGATION — Arclin layout ═══ */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md">
        <div className="flex justify-between items-center p-4 sm:px-8 gap-14 lg:gap-10 xl:gap-28">
          <a href="/" className="flex items-center gap-2.5 shrink-0">
            <img src="/franklin.jpg" alt="Franklin" className="w-8 h-8 rounded-full object-cover" />
            <span className="font-display text-xl text-silver-900 tracking-tight">Franklin</span>
          </a>

          <div className="hidden md:flex items-center gap-8">
            <a href="#how-it-works" className="text-sm xl:text-base font-semibold font-sans uppercase leading-none text-silver-700 hover:text-silver-900 transition-colors tracking-wide">How It Works</a>
            <a href="#features" className="text-sm xl:text-base font-semibold font-sans uppercase leading-none text-silver-700 hover:text-silver-900 transition-colors tracking-wide">Features</a>
            <a href="mailto:hello@askfranklin.xyz" className="text-sm xl:text-base font-semibold font-sans uppercase leading-none text-silver-700 hover:text-silver-900 transition-colors tracking-wide">Contact</a>
          </div>

          <div className="flex items-center gap-5 shrink-0">
            <Link href="/login" className="hidden sm:block text-sm xl:text-base font-semibold font-sans uppercase leading-none text-silver-700 hover:text-silver-900 transition-colors tracking-wide">
              Sign In
            </Link>
            <NavGeometricButton href="#get-started">
              Get Started
            </NavGeometricButton>
          </div>
        </div>
      </nav>

      <main>
      {/* ═══ HERO — full viewport, left-aligned like Arclin ═══ */}
      <section className="relative flex" style={{ minHeight: 'calc(100vh - 72px)', paddingTop: '72px' }}>
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8 w-full flex flex-col justify-between py-16">
          <h1 className="font-display font-normal text-[56px] md:text-[72px] lg:text-[96px] xl:text-[124px] text-silver-900 leading-none tracking-[-0.175rem] sm:tracking-[-0.31rem] text-balance">
            AI that fundraises for you
          </h1>

          <div>
            <p className="text-xl lg:text-2xl leading-[1.6] tracking-[-0.025rem] text-silver-500 font-normal mt-6 max-w-2xl font-body">
              From pitch deck to term sheet. Franklin handles your entire raise — understanding your startup, reaching out to VCs, and closing your round.
            </p>

            <div className="flex flex-wrap items-center gap-8 mt-8">
              <GeometricButton href="#get-started">
                Get Started
              </GeometricButton>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ HERO IMAGE — large visual below hero text like Arclin's hero imagery ═══ */}
      <section className="pb-20 md:pb-28">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="relative rounded-2xl overflow-hidden bg-[#32373c] shadow-[6px_6px_9px_rgba(0,0,0,0.2)]">
            <div className="grid md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-white/[0.06]">
              {/* Pipeline snapshot */}
              <div className="p-8">
                <div className="text-white/40 font-sans text-[11px] tracking-wider uppercase mb-5">Pipeline</div>
                <div className="space-y-3">
                  {[
                    { label: "Understand", done: true },
                    { label: "Pitch Deck", done: true },
                    { label: "Accelerators", done: true },
                    { label: "VC Outreach", active: true },
                    { label: "Legal Prep" },
                    { label: "Close Round" },
                  ].map((s, i) => {
                    const isDone = s.done, isActive = s.active
                    const colors = isDone ? 'bg-green-500/20 text-green-400' : isActive ? 'bg-gold-400/20 text-gold-400' : 'bg-white/[0.06] text-white/20'
                    const textColor = isDone ? 'text-green-400/80' : isActive ? 'text-gold-400' : 'text-white/20'
                    return (
                      <div key={i} className="flex items-center gap-3">
                        <div className={`w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-sans font-bold ${colors}`}>
                          {isDone ? '✓' : isActive ? '→' : i + 1}
                        </div>
                        <span className={`font-sans text-[13px] ${textColor}`}>{s.label}</span>
                      </div>
                    )
                  })}
                </div>
              </div>
              {/* Stats snapshot */}
              <div className="p-8">
                <div className="text-white/40 font-sans text-[11px] tracking-wider uppercase mb-5">This Round</div>
                <div className="space-y-5">
                  {[
                    { label: "VCs Contacted", value: "47" },
                    { label: "Responses", value: "12" },
                    { label: "Meetings", value: "6" },
                    { label: "Term Sheets", value: "3" },
                  ].map((s, i) => (
                    <div key={i} className="flex items-center justify-between">
                      <span className="text-white/40 font-sans text-[13px]">{s.label}</span>
                      <span className="text-white font-display text-[20px]">{s.value}</span>
                    </div>
                  ))}
                </div>
              </div>
              {/* Recent activity */}
              <div className="p-8">
                <div className="text-white/40 font-sans text-[11px] tracking-wider uppercase mb-5">Activity</div>
                <div className="space-y-3.5">
                  {[
                    { icon: Mail, text: "Sequoia opened your deck", time: "2m ago", color: "text-green-400" },
                    { icon: TrendingUp, text: "Term sheet from Greylock", time: "1h ago", color: "text-gold-400" },
                    { icon: FileText, text: "SAFE docs generated", time: "3h ago", color: "text-blue-400" },
                    { icon: Clock, text: "Follow-up sent to a16z", time: "5h ago", color: "text-white/40" },
                  ].map((a, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <a.icon className={`w-3.5 h-3.5 mt-0.5 shrink-0 ${a.color}`} />
                      <div className="min-w-0">
                        <div className="text-white/70 font-sans text-[12px] leading-snug">{a.text}</div>
                        <div className="text-white/25 font-sans text-[11px]">{a.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ "VITAL BEYOND MEASURE" — centered mission text ═══ */}
      <section className="py-20 md:py-28 bg-[#f9f9f7]">
        <div className="max-w-[720px] mx-auto px-6 text-center">
          <h2 className="font-display font-bold text-[32px] sm:text-[42px] text-silver-900 tracking-tight leading-[1.15] mb-8">
            Your entire raise, handled
          </h2>
          <div className="space-y-5 font-body text-[20px] text-silver-500 leading-[1.6]">
            <p>
              Fundraising is a full-time job. You should be building your company, not spending months cold-emailing investors, formatting pitch decks, and negotiating term sheets.
            </p>
            <p>
              Franklin is an AI agent that handles every step of your raise — from understanding your startup through conversation to closing your round with signed documents. No templates. No guesswork. Just results.
            </p>
          </div>
          <a href="#how-it-works" className="inline-flex items-center mt-8 px-8 py-4 text-lg font-semibold font-sans uppercase tracking-wider leading-none border-2 border-silver-500 text-silver-700 hover:bg-silver-700 hover:text-white transition-all">
            See how it works
          </a>
        </div>
      </section>

      {/* ═══ 3-COLUMN PRODUCTS — "Find the products you need" with companion image ═══ */}
      <section id="how-it-works" className="py-20 md:py-28">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-4">
            Everything you need to raise
          </h2>
          <p className="font-body text-[20px] text-silver-500 leading-[1.6] mb-14 max-w-[600px]">
            Franklin covers the full fundraising stack — tailored to your stage, your needs, and your goals.
          </p>
          <div className="grid lg:grid-cols-[2fr_1fr] gap-12 lg:gap-16">
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  title: "By stage",
                  desc: "Whether you're pre-seed or Series A, Franklin tailors your materials to your stage.",
                  items: ["Pre-Seed", "Seed", "Series A", "Series B+"]
                },
                {
                  title: "By capability",
                  desc: "Pitch decks, SAFE docs, investor matching, email campaigns — find what you need.",
                  items: ["Pitch Deck", "VC Outreach", "Legal Docs", "Cap Table"]
                },
                {
                  title: "By outcome",
                  desc: "Close your first check, fill out a round, or land a lead investor.",
                  items: ["First Check", "Lead Investor", "Full Round", "Bridge"]
                }
              ].map((cat, i) => (
                <div key={i}>
                  <h3 className="font-display font-semibold text-[22px] text-silver-900 mb-3">{cat.title}</h3>
                  <p className="font-body text-[15px] text-silver-500 leading-[1.6] mb-4">{cat.desc}</p>
                  <ul className="space-y-2">
                    {cat.items.map((item, j) => (
                      <li key={j} className="flex items-center gap-2.5 text-[14px] font-sans text-silver-400">
                        <span className="w-1 h-1 rounded-full bg-gold-400 shrink-0" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
            {/* Companion visual — tall portrait like Arclin's Rectangle-665.jpg */}
            <div className="hidden lg:block">
              <div className="bg-[#32373c] rounded-2xl overflow-hidden shadow-[6px_6px_9px_rgba(0,0,0,0.2)] h-full min-h-[400px]">
                <div className="px-6 py-4 border-b border-white/10">
                  <span className="text-white/40 font-sans text-[10px] tracking-wider uppercase">Raise Summary</span>
                </div>
                <div className="p-6 space-y-6">
                  <div>
                    <div className="text-white/30 font-sans text-[11px] uppercase tracking-wider mb-2">Target</div>
                    <div className="font-display text-[28px] text-white leading-none">$2.5M</div>
                    <div className="text-white/40 font-sans text-[12px] mt-1">Seed Round · SaaS</div>
                  </div>
                  <div className="h-px bg-white/10" />
                  <div className="space-y-3">
                    {[
                      { label: "Committed", value: "$1.8M", pct: "72%", style: 'bg-green-500/20 text-green-400' },
                      { label: "In Pipeline", value: "$400K", pct: "16%", style: 'bg-gold-400/20 text-gold-400' },
                      { label: "Remaining", value: "$300K", pct: "12%", style: 'bg-white/[0.06] text-white/30' },
                    ].map((row, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <span className="text-white/40 font-sans text-[12px]">{row.label}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-white/60 font-sans text-[12px]">{row.value}</span>
                          <span className={`font-sans text-[10px] font-medium px-1.5 py-0.5 rounded ${row.style}`}>{row.pct}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="h-px bg-white/10" />
                  <div className="space-y-2">
                    <div className="text-white/30 font-sans text-[11px] uppercase tracking-wider">Recent</div>
                    {[
                      { text: "Sequoia signed term sheet", color: 'bg-green-400' },
                      { text: "a16z meeting confirmed", color: 'bg-gold-400' },
                      { text: "Deck v3 generated", color: 'bg-blue-400' },
                    ].map((item, i) => (
                      <div key={i} className="text-white/50 font-sans text-[11px] flex items-center gap-2">
                        <div className={`w-1 h-1 rounded-full ${item.color}`} />
                        {item.text}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <a href="#get-started" className="inline-flex items-center mt-12 px-8 py-4 text-lg font-semibold font-sans uppercase tracking-wider leading-none border-2 border-silver-500 text-silver-700 hover:bg-silver-700 hover:text-white transition-all">
            Explore all capabilities
          </a>
        </div>
      </section>

      {/* ═══ FEATURED VISUAL — full-width stats divider like Arclin's featured image ═══ */}
      <section className="py-10 md:py-14">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="bg-[#32373c] rounded-2xl overflow-hidden shadow-[6px_6px_9px_rgba(0,0,0,0.2)] p-8 md:p-12">
            <div className="grid md:grid-cols-4 gap-8 md:gap-12 text-center">
              {[
                { value: "6", label: "Pipeline stages" },
                { value: "1,200+", label: "VCs in database" },
                { value: "<2min", label: "To get started" },
                { value: "24/7", label: "Always running" },
              ].map((stat, i) => (
                <div key={i}>
                  <div className="font-display text-[36px] md:text-[42px] text-white leading-none mb-2">{stat.value}</div>
                  <div className="font-sans text-[13px] text-white/40 tracking-wider uppercase">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ TWO-COLUMN — "Our impact is all around" ═══ */}
      <section className="py-20 md:py-28 bg-[#f9f9f7]">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <div>
              <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-6">
                Five steps from zero to funded
              </h2>
              <p className="font-body text-[20px] text-silver-500 leading-[1.6] mb-6">
                Franklin&apos;s pipeline takes you from the first conversation about your startup all the way through to a closed round. Every step tracked, every interaction logged, every document prepared.
              </p>
              <a href="#get-started" className="inline-flex items-center px-8 py-4 text-lg font-semibold font-sans uppercase tracking-wider leading-none border-2 border-silver-500 text-silver-700 hover:bg-silver-700 hover:text-white transition-all">
                Start your raise
              </a>
            </div>
            <PipelineVisual />
          </div>
        </div>
      </section>

      {/* ═══ SUSTAINABILITY EQUIVALENT — "Investor Intelligence" (reversed layout) ═══ */}
      <section className="py-20 md:py-28">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
            <CRMPreview />
            <div>
              <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-6">
                Investor intelligence built in
              </h2>
              <p className="font-body text-[20px] text-silver-500 leading-[1.6] mb-5">
                Franklin knows what thousands of VCs are looking for — stage, sector, check size, portfolio preferences. Instead of spray-and-pray, you get targeted outreach to investors who actually want to hear from you.
              </p>
              <p className="font-body text-[20px] text-silver-500 leading-[1.6] mb-6">
                Every interaction is tracked. Every response logged. You always know exactly where each investor relationship stands.
              </p>
              <a href="#get-started" className="inline-flex items-center px-8 py-4 text-lg font-semibold font-sans uppercase tracking-wider leading-none border-2 border-silver-500 text-silver-700 hover:bg-silver-700 hover:text-white transition-all">
                Explore our database
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ THREE-COLUMN FEATURES — "Build / Create / Collaborate" with tall images ═══ */}
      <section id="features" className="py-20 md:py-28 bg-[#f9f9f7]">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-14 text-center">
            Tools that work while you build
          </h2>
          <div className="grid md:grid-cols-3 gap-10 lg:gap-14">
            {/* Column 1: CRM — with tall mock UI */}
            <div>
              <div className="bg-[#32373c] rounded-2xl overflow-hidden mb-6">
                <div className="px-5 py-3 border-b border-white/[0.06]">
                  <span className="text-white/40 font-sans text-[10px] tracking-wider uppercase">CRM</span>
                </div>
                <div className="divide-y divide-white/[0.04]">
                  {["Sequoia — Term Sheet", "a16z — Meeting Set", "Greylock — Deck Opened", "Accel — Email Sent", "Y Combinator — Researching", "Lightspeed — Intro Made", "General Catalyst — In Queue"].map((row, i) => (
                    <div key={i} className="px-5 py-2.5 flex items-center gap-2">
                      <div className={`w-1.5 h-1.5 rounded-full ${i < 1 ? 'bg-green-400' : i < 2 ? 'bg-gold-400' : i < 3 ? 'bg-blue-400' : 'bg-white/20'}`} />
                      <span className="text-white/50 font-sans text-[11px]">{row}</span>
                    </div>
                  ))}
                </div>
              </div>
              <h3 className="font-display font-semibold text-[22px] text-silver-900 mb-3">Founder CRM</h3>
              <p className="font-body text-[17px] text-silver-500 leading-[1.6]">Every investor conversation, email, and meeting in one place. Know exactly where each relationship stands across your entire raise.</p>
            </div>

            {/* Column 2: Agent — with tall chat mock */}
            <div>
              <AgentPreview />
              <div className="mt-6">
                <h3 className="font-display font-semibold text-[22px] text-silver-900 mb-3">Agent-to-Agent</h3>
                <p className="font-body text-[17px] text-silver-500 leading-[1.6]">If you have an AI assistant, Franklin talks directly to it. Your agents coordinate the details so you don&apos;t have to context-switch.</p>
              </div>
            </div>

            {/* Column 3: Channels — with tall channel mock */}
            <div>
              <ChannelPreview />
              <div className="mt-6">
                <h3 className="font-display font-semibold text-[22px] text-silver-900 mb-3">Meet you anywhere</h3>
                <p className="font-body text-[17px] text-silver-500 leading-[1.6]">WhatsApp, Telegram, email, web — Franklin works wherever you do. No new apps, no new workflows. Just results.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ═══ COMMUNITY GRID — "We're committed to uplift our community" ═══ */}
      <section className="py-20 md:py-28">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-20 items-start">
            <div>
              <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-6">
                Built for every kind of raise
              </h2>
              <p className="font-body text-[20px] text-silver-500 leading-[1.6] mb-6">
                From solo founders to teams of ten, pre-revenue to post-product-market-fit — Franklin adapts to your stage and your story.
              </p>
              <a href="#get-started" className="inline-flex items-center px-8 py-4 text-lg font-semibold font-sans uppercase tracking-wider leading-none border-2 border-silver-500 text-silver-700 hover:bg-silver-700 hover:text-white transition-all">
                Learn how
              </a>
            </div>

            {/* Grid of tiles — like Arclin's 274x274 community images (3x3) */}
            <div className="grid grid-cols-3 gap-5">
              {[
                { icon: Zap, label: "Pre-Seed", bg: "bg-amber-50" },
                { icon: BarChart3, label: "Seed", bg: "bg-blue-50" },
                { icon: TrendingUp, label: "Series A", bg: "bg-green-50" },
                { icon: Shield, label: "Bridge", bg: "bg-purple-50" },
                { icon: FileText, label: "SaaS", bg: "bg-orange-50" },
                { icon: Bot, label: "AI / ML", bg: "bg-cyan-50" },
                { icon: Users, label: "Marketplace", bg: "bg-pink-50" },
                { icon: Globe, label: "Consumer", bg: "bg-emerald-50" },
                { icon: Scale, label: "Fintech", bg: "bg-teal-50" },
              ].map((item, i) => (
                <div key={i} className={`aspect-square ${item.bg} flex flex-col items-center justify-center gap-2.5 text-center p-4`}>
                  <item.icon className="w-7 h-7 text-silver-500" strokeWidth={1.5} />
                  <span className="text-[13px] font-sans text-silver-600 font-medium">{item.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ═══ CTA — "Bring your project to life" (centered like Arclin) ═══ */}
      <section id="get-started" className="py-20 md:py-28 bg-[#f9f9f7]">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="font-display font-bold text-[28px] sm:text-[36px] text-silver-900 tracking-tight leading-[1.15] mb-4">
              Start your raise
            </h2>
            <p className="font-body text-[20px] text-silver-500 leading-[1.6] max-w-[600px] mx-auto">
              Tell Franklin about your startup and let AI handle the rest — from deck creation to investor outreach to closing your round.
            </p>
          </div>
          <SignupForm />
          <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 mt-8 text-silver-400 font-sans text-[13px] sm:text-[14px]">
            {[
              { icon: CheckCircle, text: "Free to start", color: "text-green-500" },
              { icon: Shield, text: "Data encrypted", color: "text-gold-400" },
              { icon: Clock, text: "2 min setup", color: "text-blue-400" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                <item.icon className={`w-4 h-4 ${item.color}`} /> {item.text}
              </div>
            ))}
          </div>
        </div>
      </section>

      </main>

      {/* ═══ FOOTER ═══ */}
      <footer className="bg-[#32373c] text-white pt-16 pb-8">
        <div className="max-w-[1200px] mx-auto px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-14">
            <div className="col-span-2 md:col-span-1">
              <div className="flex items-center gap-2.5 mb-4">
                <img src="/franklin.jpg" alt="Franklin" className="w-7 h-7 rounded-full object-cover" />
                <span className="font-display text-lg">Franklin</span>
              </div>
              <p className="font-sans text-[13px] text-white/50 leading-relaxed max-w-[200px]">
                AI that fundraises for you. From pitch deck to term sheet.
              </p>
            </div>

            <div>
              <h4 className="font-sans text-[13px] font-semibold tracking-wider uppercase text-white/30 mb-4">Product</h4>
              <ul className="space-y-2.5 font-sans text-[13px] text-white/50">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a></li>
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#get-started" className="hover:text-white transition-colors">Get Started</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-sans text-[13px] font-semibold tracking-wider uppercase text-white/30 mb-4">Capabilities</h4>
              <ul className="space-y-2.5 font-sans text-[13px] text-white/50">
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Pitch Decks</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">VC Outreach</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">SAFE Documents</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">Cap Table</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-sans text-[13px] font-semibold tracking-wider uppercase text-white/30 mb-4">Company</h4>
              <ul className="space-y-2.5 font-sans text-[13px] text-white/50">
                <li><Link href="/privacy-policy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                <li><a href="mailto:hello@askfranklin.xyz" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            <div>
              <h4 className="font-sans text-[13px] font-semibold tracking-wider uppercase text-white/30 mb-4">Connect</h4>
              <ul className="space-y-2.5 font-sans text-[13px] text-white/50">
                <li><a href="https://t.me/askfranklin_bot" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Telegram</a></li>
                <li><a href="https://twitter.com/askfranklin" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">Twitter</a></li>
                <li><a href="mailto:hello@askfranklin.xyz" className="hover:text-white transition-colors">Email</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-5 border-t border-white/10 flex flex-col sm:flex-row justify-between items-center gap-3">
            <p className="font-sans text-[13px] text-white/30">
              &copy; {new Date().getFullYear()} Ask Franklin. All rights reserved.
            </p>
            <Link href="/privacy-policy" className="font-sans text-[13px] text-white/30 hover:text-white transition-colors">
              Privacy Policy
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
