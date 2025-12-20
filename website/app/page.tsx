"use client"

import { useState, useEffect, useRef } from "react"
import {
  Phone,
  ArrowRight,
  ChevronDown
} from "lucide-react"

// Video Player Component with autoplay fix
function VideoPlayer() {
  const videoRef = useRef<HTMLVideoElement>(null)

  useEffect(() => {
    const video = videoRef.current
    if (video) {
      video.muted = true
      video.play().catch(() => {
        // Autoplay was prevented, try again on user interaction
        const playOnInteraction = () => {
          video.play()
          document.removeEventListener('click', playOnInteraction)
          document.removeEventListener('touchstart', playOnInteraction)
        }
        document.addEventListener('click', playOnInteraction)
        document.addEventListener('touchstart', playOnInteraction)
      })
    }
  }, [])

  return (
    <video
      ref={videoRef}
      autoPlay
      loop
      muted
      playsInline
      preload="auto"
      className="absolute inset-0 w-full h-full object-cover"
    >
      <source src="/franklin.webm" type="video/webm" />
      <source src="/franklin.mp4" type="video/mp4" />
    </video>
  )
}

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
          ? "bg-silver-700 text-ivory-100 border-silver-600 hover:bg-silver-600"
          : "bg-white text-silver-800 border-silver-700/20 hover:border-silver-700/40 hover:bg-silver-50"
      }`}
    >
      <span className="text-[14px] font-medium">{label}</span>
    </button>
  )
}

// Form Input Component
function FormInput({
  label,
  placeholder,
  value,
  onChange,
  type = "text",
  optional = false,
  error = false
}: {
  label: string
  placeholder: string
  value: string
  onChange: (value: string) => void
  type?: string
  optional?: boolean
  error?: boolean
}) {
  return (
    <div className="space-y-0.5">
      <label className="text-[10px] font-medium text-white/70 uppercase tracking-wide">
        {label}{optional && <span className="text-white/50"> (opt.)</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full px-2.5 py-1.5 text-[13px] bg-white border rounded-md focus:outline-none transition-all text-silver-800 placeholder:text-silver-400 ${
          error
            ? "border-red-500 ring-2 ring-red-500/30 shadow-[0_0_10px_rgba(239,68,68,0.3)]"
            : "border-silver-300 focus:border-silver-500 focus:ring-1 focus:ring-silver-500/20"
        }`}
      />
    </div>
  )
}

// iPhone Mockup Component - Full Width with Onboarding
function IPhoneMockup() {
  const [selectedOption, setSelectedOption] = useState<'investor' | 'founder' | 'curious' | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [hasError, setHasError] = useState(false)
  const [fieldErrors, setFieldErrors] = useState({
    name: false,
    phone: false,
    email: false,
    fund_name: false,
    linkedin: false
  })
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    fund_name: '',
    linkedin: '',
    twitter: ''
  })

  const handleSubmit = async () => {
    // Check for empty required fields
    const errors = {
      name: !formData.name,
      phone: !formData.phone,
      email: !formData.email,
      fund_name: !formData.fund_name,
      linkedin: !formData.linkedin
    }

    const hasErrors = Object.values(errors).some(e => e)
    setFieldErrors(errors)

    if (hasErrors) {
      setHasError(true)
      setTimeout(() => setHasError(false), 2000)
      return
    }

    setIsSubmitting(true)
    setHasError(false)
    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          user_type: selectedOption
        })
      })

      if (response.ok) {
        setIsSubmitted(true)
      } else {
        setHasError(true)
        setTimeout(() => setHasError(false), 2000)
      }
    } catch (error) {
      console.error('Submit error:', error)
      setHasError(true)
      setTimeout(() => setHasError(false), 2000)
    } finally {
      setIsSubmitting(false)
    }
  }

  const updateField = (field: string) => (value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error for this field when user types
    if (fieldErrors[field as keyof typeof fieldErrors]) {
      setFieldErrors(prev => ({ ...prev, [field]: false }))
    }
  }

  return (
    <div className="w-full bg-gradient-to-b from-[#e8e8e8] to-[#d8d8d8]">
      {/* Chat Header */}
      <div className="flex items-center gap-4 px-6 py-4 bg-silver-700 border-b border-silver-600">
        <img src="/franklin.jpg" alt="Franklin" className="w-12 h-12 rounded-full object-cover shadow-md ring-2 ring-white/20" />
        <div className="flex-1">
          <h4 className="text-lg font-semibold text-white">Franklin</h4>
          <p className="text-sm text-white/70">Your Private Banker</p>
        </div>
        <Phone className="w-6 h-6 text-white/70" />
      </div>

      {/* Messages Container - Onboarding Flow */}
      <div className="min-h-[500px] px-6 py-8 max-w-4xl mx-auto">
              {/* Franklin's Avatar + Message */}
              <div className="flex gap-3 items-start">
                <img src="/franklin.jpg" alt="Franklin" className="w-9 h-9 rounded-full object-cover flex-shrink-0 shadow-sm" />
                <div className="flex-1 space-y-4">
                  {/* Message bubble */}
                  <div className="bg-silver-600 px-4 py-4 rounded-2xl rounded-tl-sm shadow-sm">
                    <h3 className="font-display text-lg text-white mb-2">
                      Hey, I'm Franklin, your AI private banker.
                    </h3>
                    <p className="text-[14px] text-white/90 leading-relaxed">
                      I help you grow your wealth by reaching the right people, getting the right advice, and closing deals with expert input.
                    </p>
                    <p className="text-[14px] text-white/90 mt-3">
                      How would you describe yourself?
                    </p>
                  </div>

                  {/* Option Buttons */}
                  {!selectedOption && (
                    <div className="space-y-2.5 pt-1">
                      <OptionButton label="(A) I am an Investor" variant="primary" onClick={() => setSelectedOption('investor')} />
                      <OptionButton label="(B) I am a Founder" onClick={() => setSelectedOption('founder')} />
                      <OptionButton label="(C) Other. Just curious" onClick={() => setSelectedOption('curious')} />
                    </div>
                  )}

                  {/* User's selected response */}
                  {selectedOption && (
                    <div className="flex justify-end">
                      <div className="bg-[#264C39] text-white px-4 py-2 rounded-2xl rounded-tr-sm shadow-sm max-w-[80%]">
                        <p className="text-[14px]">
                          {selectedOption === 'investor' && "I am an Investor"}
                          {selectedOption === 'founder' && "I am a Founder"}
                          {selectedOption === 'curious' && "Just curious"}
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Response for Investor or Founder - Show Form */}
              {(selectedOption === 'investor' || selectedOption === 'founder') && !isSubmitted && (
                <div className="flex gap-2 items-start mt-3 animate-fade-in">
                  <img src="/franklin.jpg" alt="Franklin" className="w-8 h-8 rounded-full object-cover flex-shrink-0 shadow-sm" />
                  <div className="flex-1">
                    <div className="bg-silver-600 px-3 py-3 rounded-2xl rounded-tl-sm shadow-sm">
                      <p className="text-[13px] text-white font-medium">Great to meet you!</p>
                      <p className="text-[12px] text-white/80 leading-snug mb-2">
                        This helps me send you the right deals. Takes 2 min!
                      </p>

                      {/* Form Fields */}
                      <div className="space-y-2">
                        <FormInput
                          label="Name"
                          placeholder="John Doe"
                          value={formData.name}
                          onChange={updateField('name')}
                          error={fieldErrors.name}
                        />
                        <FormInput
                          label="Phone"
                          placeholder="(000) 000-0000"
                          value={formData.phone}
                          onChange={updateField('phone')}
                          type="tel"
                          error={fieldErrors.phone}
                        />
                        <FormInput
                          label="Email"
                          placeholder="john@company.com"
                          value={formData.email}
                          onChange={updateField('email')}
                          type="email"
                          error={fieldErrors.email}
                        />
                        <FormInput
                          label={selectedOption === 'investor' ? "Fund Name" : "Company"}
                          placeholder={selectedOption === 'investor' ? "Example Fund" : "Example Inc."}
                          value={formData.fund_name}
                          onChange={updateField('fund_name')}
                          error={fieldErrors.fund_name}
                        />
                        <FormInput
                          label="LinkedIn"
                          placeholder="linkedin.com/in/john"
                          value={formData.linkedin}
                          onChange={updateField('linkedin')}
                          type="url"
                          error={fieldErrors.linkedin}
                        />
                        <FormInput
                          label="Twitter/X"
                          placeholder="x.com/john"
                          value={formData.twitter}
                          onChange={updateField('twitter')}
                          type="url"
                          optional
                        />
                      </div>

                      {/* Submit Button */}
                      <button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className={`w-full mt-3 text-white py-2 rounded-lg font-medium text-[13px] transition-all flex items-center justify-center gap-2 ${
                          hasError
                            ? "bg-red-500 hover:bg-red-600"
                            : "bg-[#264C39] hover:bg-[#1d3a2b]"
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {isSubmitting ? (
                          <>
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Submitting...
                          </>
                        ) : hasError ? (
                          "Error - Check fields"
                        ) : (
                          <>
                            Submit
                            <ArrowRight className="w-3.5 h-3.5" />
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Success Message after form submission */}
              {isSubmitted && (
                <div className="flex gap-3 items-start mt-4 animate-fade-in">
                  <img src="/franklin.jpg" alt="Franklin" className="w-9 h-9 rounded-full object-cover flex-shrink-0 shadow-sm" />
                  <div className="flex-1 space-y-3">
                    <div className="bg-silver-600 px-4 py-4 rounded-2xl rounded-tl-sm shadow-sm">
                      <p className="text-[14px] text-white font-medium mb-2">
                        Perfect, thanks {formData.name.split(' ')[0]}!
                      </p>
                      <p className="text-[14px] text-white/90 leading-relaxed">
                        I'll be in touch soon with relevant opportunities. In the meantime, feel free to message me on WhatsApp anytime.
                      </p>
                    </div>
                    <a
                      href="https://wa.me/YOURWHATSAPPNUMBER"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 bg-[#25D366] text-white px-4 py-2.5 rounded-xl text-[14px] font-medium hover:bg-[#20bd5a] transition-colors shadow-sm"
                    >
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                      Message Me on WhatsApp
                    </a>
                  </div>
                </div>
              )}

              {/* Response for "Just Curious" option */}
              {selectedOption === 'curious' && (
                <div className="flex gap-3 items-start mt-4 animate-fade-in">
                  <img src="/franklin.jpg" alt="Franklin" className="w-9 h-9 rounded-full object-cover flex-shrink-0 shadow-sm" />
                  <div className="flex-1 space-y-3">
                    <div className="bg-silver-600 px-4 py-4 rounded-2xl rounded-tl-sm shadow-sm">
                      <p className="text-[14px] text-white font-medium mb-2">
                        Great to meet you!
                      </p>
                      <p className="text-[14px] text-white/90 leading-relaxed">
                        I'm always up for connecting curious, ambitious people. Whatever you're working on, message me!
                      </p>
                    </div>
                    <a
                      href="https://wa.me/YOURWHATSAPPNUMBER"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 bg-[#25D366] text-white px-4 py-2.5 rounded-xl text-[14px] font-medium hover:bg-[#20bd5a] transition-colors shadow-sm"
                    >
                      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                      Message Me on WhatsApp
                    </a>
                  </div>
                </div>
              )}
      </div>
    </div>
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
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-silver-700/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <a href="/" className="group">
              <span className="font-display text-2xl text-silver-700 tracking-tight">
                Franklin
              </span>
            </a>

            {/* Nav Links */}
            <div className="hidden md:flex items-center gap-8">
              <a href="/expertise" className="link-elegant text-sm tracking-wide">Expertise</a>
            </div>

            {/* CTA */}
            <a href="#chat" className="btn-gold text-xs sm:text-sm">
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
          <div className="absolute -bottom-32 -left-32 w-[600px] h-[600px] rounded-full bg-gradient-radial from-silver-700/5 via-transparent to-transparent" />
        </div>

        <div className="relative max-w-7xl mx-auto px-6 lg:px-8 py-24 lg:py-32">
          <div className="grid lg:grid-cols-[1.2fr_1fr] gap-12 lg:gap-16 items-center">
            {/* Left: Franklin Video - 20% wider */}
            <div className={`relative ${isVisible ? 'animate-fade-in animation-delay-300' : 'opacity-0'}`}>
              <div className="relative w-full max-w-3xl mx-auto">
                {/* Ornate frame - hidden on mobile */}
                <div className="hidden md:block absolute -inset-3 border-2 border-gold-400/30 rounded-sm pointer-events-none" />
                <div className="hidden md:block absolute -inset-1 border border-silver-700/20 rounded-sm pointer-events-none" />

                {/* Franklin Video */}
                <div className="relative aspect-[16/9] overflow-hidden rounded-sm shadow-2xl">
                  <VideoPlayer />
                  {/* Subtle overlay for elegance */}
                  <div className="absolute inset-0 bg-gradient-to-t from-silver-700/20 via-transparent to-transparent pointer-events-none" />
                </div>

              </div>
            </div>

            {/* Right: Content */}
            <div className={`space-y-8 ${isVisible ? 'animate-fade-in-up' : 'opacity-0'}`}>
              {/* Eyebrow */}
              <p className="font-sans text-sm tracking-widest uppercase text-gold-500">
                Your AI Private Banker
              </p>

              {/* Main headline */}
              <h1 className="font-display text-4xl sm:text-5xl md:text-6xl lg:text-7xl text-silver-700 leading-[1.1] tracking-tight">
                Meet <span className="italic text-gradient-gold">Franklin</span>
              </h1>

              {/* Subheadline */}
              <p className="font-body text-lg md:text-xl text-silver-700/80 leading-relaxed max-w-xl">
                Grow your wealth with the sophistication of a family office and the network of a top-tier investment bank.
              </p>
              <p className="font-body text-lg md:text-xl text-silver-700/60 leading-relaxed max-w-xl">
                Reach the right people, get access to the right dealflow, and close deals with expert input.
              </p>
              {/* Quote */}
              <blockquote className="relative pl-6 border-l-2 border-gold-400/60 italic text-silver-700/70 font-serif text-lg">
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
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-silver-700/40">
            <span className="text-xs font-sans tracking-widest uppercase">Scroll</span>
            <ChevronDown className="w-5 h-5 animate-bounce" />
          </div>
        </div>
      </section>

      {/* ===== CHAT SECTION ===== */}
      <section id="chat" className="bg-ivory-200/50 grain">
        <IPhoneMockup />
      </section>

      {/* ===== FOOTER ===== */}
      <footer className="py-16 bg-silver-700 text-ivory-100">
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
