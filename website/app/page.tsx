"use client"

import { useState, useEffect, useRef } from "react"
import Link from "next/link"
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
  // Debug logging
  if (error) {
    console.log(`🔴 FormInput ERROR: ${label} has error=${error}, value="${value}"`)
  }

  return (
    <div className="space-y-0.5">
      <label className={`text-[11px] font-bold uppercase tracking-wide flex items-center gap-1 ${
        error ? "text-red-600" : "text-white/70"
      }`}>
        {label}
        {error && <span className="text-red-600 font-bold text-lg">*</span>}
        {optional && <span className="text-white/50"> (opt.)</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`w-full px-3 py-2 text-[14px] border-3 rounded-lg focus:outline-none transition-all text-gray-900 font-medium placeholder:text-gray-400 ${
          error
            ? "border-red-600 bg-red-100 ring-4 ring-red-500/60 shadow-lg shadow-red-500/30"
            : "border-gray-300 bg-white focus:border-green-600 focus:ring-2 focus:ring-green-600/20"
        }`}
        style={error ? { borderWidth: '3px', borderColor: '#dc2626' } : {}}
      />
      {error && <p className="text-red-600 text-[11px] font-bold mt-1">⚠️ This field is required</p>}
    </div>
  )
}

// Country codes for phone selector
const countryCodes = [
  { code: '+1', country: 'US', flag: '🇺🇸' },
  { code: '+1', country: 'CA', flag: '🇨🇦' },
  { code: '+44', country: 'UK', flag: '🇬🇧' },
  { code: '+49', country: 'DE', flag: '🇩🇪' },
  { code: '+33', country: 'FR', flag: '🇫🇷' },
  { code: '+41', country: 'CH', flag: '🇨🇭' },
  { code: '+971', country: 'AE', flag: '🇦🇪' },
  { code: '+65', country: 'SG', flag: '🇸🇬' },
  { code: '+852', country: 'HK', flag: '🇭🇰' },
  { code: '+81', country: 'JP', flag: '🇯🇵' },
  { code: '+86', country: 'CN', flag: '🇨🇳' },
  { code: '+91', country: 'IN', flag: '🇮🇳' },
  { code: '+61', country: 'AU', flag: '🇦🇺' },
  { code: '+972', country: 'IL', flag: '🇮🇱' },
  { code: '+55', country: 'BR', flag: '🇧🇷' },
  { code: '+52', country: 'MX', flag: '🇲🇽' },
]

// Phone Input with Country Selector
function PhoneInput({
  value,
  countryCode,
  onChange,
  onCountryChange,
  error = false
}: {
  value: string
  countryCode: string
  onChange: (value: string) => void
  onCountryChange: (code: string) => void
  error?: boolean
}) {
  // Debug logging
  if (error) {
    console.log(`🔴 PhoneInput ERROR: Phone has error=${error}, value="${value}"`)
  }

  return (
    <div className="space-y-0.5">
      <label className={`text-[11px] font-bold uppercase tracking-wide flex items-center gap-1 ${
        error ? "text-red-600" : "text-white/70"
      }`}>
        Phone
        {error && <span className="text-red-600 font-bold text-lg">*</span>}
      </label>
      <div className="flex gap-1">
        <select
          value={countryCode}
          onChange={(e) => onCountryChange(e.target.value)}
          className={`w-[80px] px-2 py-2 text-[14px] border-2 rounded-lg focus:outline-none text-gray-900 font-medium ${
            error ? "border-red-600 bg-red-100" : "border-gray-300 bg-white focus:border-green-600 focus:ring-2 focus:ring-green-600/20"
          }`}
          style={error ? { borderWidth: '3px', borderColor: '#dc2626' } : {}}
        >
          {countryCodes.map((c, i) => (
            <option key={`${c.country}-${i}`} value={c.code}>
              {c.flag} {c.code}
            </option>
          ))}
        </select>
        <input
          type="tel"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="000 000 0000"
          className={`flex-1 px-3 py-2 text-[14px] border-2 rounded-lg focus:outline-none transition-all text-gray-900 font-medium placeholder:text-gray-400 ${
            error
              ? "border-red-600 bg-red-100 ring-4 ring-red-500/60 shadow-lg shadow-red-500/30"
              : "border-gray-300 bg-white focus:border-green-600 focus:ring-2 focus:ring-green-600/20"
          }`}
          style={error ? { borderWidth: '3px', borderColor: '#dc2626' } : {}}
        />
      </div>
      {error && <p className="text-red-600 text-[11px] font-bold mt-1">⚠️ This field is required</p>}
    </div>
  )
}

// iPhone Mockup Component - Full Width with Onboarding
function IPhoneMockup() {
  const [selectedOption, setSelectedOption] = useState<'investor' | 'founder' | 'curious' | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [formError, setFormError] = useState(false)
  const [apiError, setApiError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState({
    name: false,
    phone: false,
    email: false,
    fund_name: false,
    linkedin: false
  })
  const [countryCode, setCountryCode] = useState('+1')
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    fund_name: '',
    linkedin: '',
    twitter: ''
  })

  // Debug: Log whenever fieldErrors changes
  useEffect(() => {
    console.log('🔄 fieldErrors STATE CHANGED:', fieldErrors)
    const errorsExist = Object.values(fieldErrors).some(e => e)
    if (errorsExist) {
      console.log('🔴 ERRORS EXIST IN STATE - These fields should be red:',
        Object.entries(fieldErrors).filter(([k, v]) => v).map(([k]) => k))
    }
  }, [fieldErrors])

  const handleSubmit = async () => {
    console.log('==========================================')
    console.log('🚀 SUBMIT CLICKED')
    console.log('📝 Form Data:', formData)

    // Check for empty required fields
    const errors = {
      name: !formData.name,
      phone: !formData.phone,
      email: !formData.email,
      fund_name: !formData.fund_name,
      linkedin: !formData.linkedin
    }

    console.log('❌ Calculated Errors:', errors)

    const hasErrors = Object.values(errors).some(e => e)
    console.log('🔴 Has Errors:', hasErrors)

    console.log('📤 Setting fieldErrors state to:', errors)
    setFieldErrors(errors)

    if (hasErrors) {
      console.log('⚠️ VALIDATION FAILED - Fields with errors:',
        Object.entries(errors).filter(([k, v]) => v).map(([k]) => k))
      setFormError(true)
      setTimeout(() => setFormError(false), 2000)
      return
    }

    console.log('✅ VALIDATION PASSED')

    setIsSubmitting(true)
    setFormError(false)
    setApiError(null)
    try {
      const response = await fetch('/api/leads', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          phone: `${countryCode}${formData.phone.replace(/\D/g, '')}`,
          user_type: selectedOption
        })
      })

      if (response.ok) {
        setIsSubmitted(true)
      } else {
        const errorData = await response.json().catch(() => ({}))
        console.error('API Error:', response.status, errorData)
        setApiError(errorData.error || `Server error (${response.status})`)
      }
    } catch (error) {
      console.error('Network error:', error)
      setApiError('Network error - please try again')
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
    <div className="relative w-full py-16 flex justify-center">
      {/* Phone Device - iPhone 15 Pro aspect ratio (9:19.5 = width:height) */}
      <div className="relative w-full max-w-[800px] aspect-[9/19.5]">
        {/* Outer frame with gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-[#2a2a2a] via-[#1a1a1a] to-[#0a0a0a] rounded-[3rem] shadow-2xl" />

        {/* Side buttons */}
        <div className="absolute -left-[3px] top-24 w-[4px] h-8 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[3px] top-36 w-[4px] h-14 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -left-[3px] top-52 w-[4px] h-14 bg-[#2a2a2a] rounded-l-sm" />
        <div className="absolute -right-[3px] top-32 w-[4px] h-20 bg-[#2a2a2a] rounded-r-sm" />

        {/* Inner bezel */}
        <div className="relative h-full bg-[#1a1a1a] rounded-[3rem] p-3">
          {/* Screen */}
          <div className="relative h-full bg-ivory-50 rounded-[2.25rem] overflow-hidden flex flex-col">
            {/* Dynamic Island */}
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-20">
              <div className="w-28 h-8 bg-black rounded-full flex items-center justify-center">
                <div className="w-3 h-3 rounded-full bg-[#1a1a1a] ring-1 ring-[#333]" />
              </div>
            </div>

            {/* Status Bar */}
            <div className="flex items-center justify-between px-8 pt-4 pb-2">
              <span className="text-sm font-semibold text-silver-800">9:41</span>
              <div className="flex items-center gap-1.5">
                {/* Signal */}
                <div className="flex items-end gap-[2px]">
                  {[4, 6, 8, 10].map((h, i) => (
                    <div key={i} className="w-[3px] bg-silver-800 rounded-sm" style={{ height: `${h}px` }} />
                  ))}
                </div>
                {/* Wifi */}
                <svg className="w-4 h-3 text-silver-800" viewBox="0 0 16 12" fill="currentColor">
                  <path d="M8 9.5a1.5 1.5 0 100 3 1.5 1.5 0 000-3zM8 6c-1.7 0-3.2.7-4.3 1.8l1.4 1.4c.8-.8 1.8-1.2 2.9-1.2s2.1.4 2.9 1.2l1.4-1.4C11.2 6.7 9.7 6 8 6zm0-4C5 2 2.4 3.2.6 5.2l1.4 1.4C3.5 5 5.6 4 8 4s4.5 1 6 2.6l1.4-1.4C13.6 3.2 11 2 8 2z"/>
                </svg>
                {/* Battery */}
                <div className="flex items-center">
                  <div className="w-6 h-3 border border-silver-800 rounded p-[2px]">
                    <div className="w-full h-full bg-silver-800 rounded-sm" />
                  </div>
                  <div className="w-[2px] h-[5px] bg-silver-800 rounded-r-sm ml-[1px]" />
                </div>
              </div>
            </div>

            {/* Chat Header */}
            <div className="flex items-center gap-3 px-5 py-3 bg-white/80 backdrop-blur-sm border-b border-black/5">
              <img src="/franklin.jpg" alt="Franklin" className="w-11 h-11 rounded-full object-cover shadow-md" />
              <div className="flex-1">
                <h4 className="text-base font-semibold text-silver-800">Franklin</h4>
                <p className="text-xs text-silver-600/70">Your Private Banker</p>
              </div>
              <Phone className="w-5 h-5 text-silver-700" />
            </div>

            {/* Messages Container - Onboarding Flow */}
            <div className="flex-1 overflow-y-auto bg-gradient-to-b from-[#f5f5f5] to-[#ebebeb] px-4 py-5">
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
                        <PhoneInput
                          value={formData.phone}
                          countryCode={countryCode}
                          onChange={updateField('phone')}
                          onCountryChange={setCountryCode}
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

                      {/* API Error Banner */}
                      {apiError && (
                        <div className="mt-2 p-2 bg-orange-100 border border-orange-400 rounded-lg">
                          <p className="text-orange-800 text-[12px] font-medium">⚠️ {apiError}</p>
                        </div>
                      )}

                      {/* Submit Button */}
                      <button
                        onClick={handleSubmit}
                        disabled={isSubmitting}
                        className={`w-full mt-3 text-white py-2 rounded-lg font-medium text-[13px] transition-all flex items-center justify-center gap-2 ${
                          formError
                            ? "bg-red-500 hover:bg-red-600"
                            : "bg-[#264C39] hover:bg-[#1d3a2b]"
                        } disabled:opacity-50 disabled:cursor-not-allowed`}
                      >
                        {isSubmitting ? (
                          <>
                            <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Submitting...
                          </>
                        ) : formError ? (
                          "Check required fields above"
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
                        Excellent, {formData.name.split(' ')[0]}!
                      </p>
                      <p className="text-[14px] text-white/90 leading-relaxed">
                        I'll give you a call shortly to learn more about your goals and how I can help. Keep your phone nearby!
                      </p>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-3 bg-ivory-100 rounded-xl border border-silver-200">
                      <div className="w-10 h-10 rounded-full bg-gold-400/20 flex items-center justify-center">
                        <Phone className="w-5 h-5 text-gold-600" />
                      </div>
                      <div>
                        <p className="text-[13px] font-medium text-silver-700">Incoming call from Franklin</p>
                        <p className="text-[12px] text-silver-500">Usually within 2 minutes</p>
                      </div>
                    </div>
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

            {/* Input Bar */}
            <div className="bg-white px-4 py-3 border-t border-black/5">
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-[#f0f0f0] rounded-full px-5 py-2.5 border border-black/5">
                  <span className="text-sm text-silver-700/40">Message Franklin...</span>
                </div>
                <div className="w-10 h-10 bg-silver-700 rounded-full flex items-center justify-center shadow-sm">
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
      <div className="absolute -z-10 inset-8 bg-silver-700/30 blur-3xl rounded-full" />
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
            <div className="flex items-center gap-3">
              <a href="tel:+19844779472" className="flex items-center gap-2 px-4 py-2 bg-silver-700 text-ivory-100 rounded-lg text-xs sm:text-sm font-medium hover:bg-silver-600 transition-colors">
                <Phone className="w-4 h-4" />
                <span className="hidden sm:inline">Call Franklin</span>
                <span className="sm:hidden">Call</span>
              </a>
              <a href="#chat" className="btn-gold text-xs sm:text-sm">
                <span className="hidden sm:inline">Sign Up</span>
                <span className="sm:hidden">Chat</span>
              </a>
            </div>
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
                Reach the right people, access dealflow, and navigate complex transactions with expert guidance.
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
                About
              </h4>
              <ul className="space-y-3 font-body text-ivory-100/60">
                <li><Link href="/expertise" className="hover:text-gold-400 transition-colors">The Résumé</Link></li>
                <li><Link href="/privacy-policy" className="hover:text-gold-400 transition-colors">Privacy Policy</Link></li>
              </ul>
            </div>

            {/* Connect */}
            <div>
              <h4 className="font-sans font-semibold text-sm tracking-wide uppercase text-gold-400 mb-4">
                Connect
              </h4>
              <ul className="space-y-3 font-body text-ivory-100/60">
                <li><a href="https://wa.me/YOURWHATSAPPNUMBER" target="_blank" rel="noopener noreferrer" className="hover:text-gold-400 transition-colors">WhatsApp</a></li>
                <li><a href="https://twitter.com/askfranklin" target="_blank" rel="noopener noreferrer" className="hover:text-gold-400 transition-colors">Twitter</a></li>
                <li><a href="mailto:hello@askfranklin.io" className="hover:text-gold-400 transition-colors">Email</a></li>
              </ul>
            </div>
          </div>

          {/* Bottom */}
          <div className="pt-8 border-t border-ivory-100/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="font-sans text-sm text-ivory-100/40">
              &copy; {new Date().getFullYear()} Ask Franklin. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/privacy-policy" className="font-sans text-sm text-ivory-100/40 hover:text-gold-400 transition-colors">
                Privacy
              </Link>
              <p className="font-serif text-sm text-ivory-100/40 italic">
                "An investment in knowledge pays the best interest."
              </p>
            </div>
          </div>

        </div>
      </footer>
    </div>
  )
}
