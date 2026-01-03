"use client"

import { useState } from "react"
import Link from "next/link"
import { ArrowLeft, ArrowRight, Sparkles, Zap, Moon, Sun, Leaf } from "lucide-react"

// Theme definitions
const themes = [
  {
    id: "glassmorphism",
    name: "Glassmorphism",
    tagline: "Frosted elegance",
    description: "Translucent layers, blur effects, and depth through transparency. Modern and futuristic.",
    icon: Sparkles,
    colors: {
      bg: "from-slate-900 via-purple-900/50 to-slate-900",
      card: "bg-white/10 backdrop-blur-xl border border-white/20",
      accent: "text-purple-400",
      text: "text-white",
      button: "bg-white/20 hover:bg-white/30 backdrop-blur-sm border border-white/30",
    },
  },
  {
    id: "neubrutalism",
    name: "Neubrutalism",
    tagline: "Bold & unapologetic",
    description: "Thick borders, harsh shadows, saturated colors. For brands that refuse to blend in.",
    icon: Zap,
    colors: {
      bg: "bg-[#FFFBEB]",
      card: "bg-[#FF6B6B] border-4 border-black shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]",
      accent: "text-black",
      text: "text-black",
      button: "bg-[#4ECDC4] border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] hover:translate-x-[2px] hover:translate-y-[2px]",
    },
  },
  {
    id: "neon-cyber",
    name: "Neon Cyberpunk",
    tagline: "Electric nights",
    description: "Glowing neons on deep black. High-tech, high-energy, unmistakably futuristic.",
    icon: Zap,
    colors: {
      bg: "bg-black",
      card: "bg-gray-900/80 border border-cyan-500/50 shadow-[0_0_30px_rgba(6,182,212,0.3)]",
      accent: "text-cyan-400",
      text: "text-white",
      button: "bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 shadow-[0_0_20px_rgba(6,182,212,0.5)]",
    },
  },
  {
    id: "minimal-dark",
    name: "Minimal Dark",
    tagline: "Less is more",
    description: "Clean lines, high contrast, zero noise. Sophistication through simplicity.",
    icon: Moon,
    colors: {
      bg: "bg-[#0a0a0a]",
      card: "bg-[#141414] border border-[#262626]",
      accent: "text-white",
      text: "text-gray-300",
      button: "bg-white text-black hover:bg-gray-200",
    },
  },
  {
    id: "warm-earth",
    name: "Warm Earth",
    tagline: "Grounded luxury",
    description: "Organic tones, natural textures, warm hospitality. Trust built through warmth.",
    icon: Leaf,
    colors: {
      bg: "bg-gradient-to-br from-amber-50 via-orange-50 to-amber-100",
      card: "bg-white/80 border border-amber-200/50 shadow-xl shadow-amber-900/5",
      accent: "text-amber-700",
      text: "text-stone-700",
      button: "bg-amber-600 hover:bg-amber-700 text-white",
    },
  },
]

// Hero card for each theme
function ThemeCard({ theme, isActive, onClick }: {
  theme: typeof themes[0]
  isActive: boolean
  onClick: () => void
}) {
  const Icon = theme.icon

  return (
    <button
      onClick={onClick}
      className={`relative p-6 rounded-2xl text-left transition-all duration-300 ${
        isActive
          ? "ring-2 ring-offset-2 ring-offset-ivory-100 ring-gold-500 scale-[1.02]"
          : "hover:scale-[1.01]"
      } ${theme.colors.card} ${theme.colors.text}`}
    >
      <div className="flex items-start justify-between mb-4">
        <div className={`p-2 rounded-lg ${theme.id === 'neubrutalism' ? 'bg-black text-white' : 'bg-white/20'}`}>
          <Icon className="w-5 h-5" />
        </div>
        {isActive && (
          <span className="text-xs font-bold uppercase tracking-wider bg-gold-500 text-white px-2 py-1 rounded">
            Active
          </span>
        )}
      </div>
      <h3 className={`font-display text-xl mb-1 ${theme.colors.accent}`}>{theme.name}</h3>
      <p className="text-sm opacity-70">{theme.tagline}</p>
    </button>
  )
}

// Full theme demo
function ThemeDemo({ theme }: { theme: typeof themes[0] }) {
  return (
    <div className={`min-h-[600px] rounded-3xl overflow-hidden bg-gradient-to-br ${theme.colors.bg} p-8 lg:p-12`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-12">
        <div className={`font-display text-2xl ${theme.colors.accent}`}>
          Franklin
        </div>
        <div className="flex items-center gap-4">
          <span className={`text-sm ${theme.colors.text} opacity-60`}>Themes</span>
          <button className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${theme.colors.button} ${theme.colors.text}`}>
            Get Started
          </button>
        </div>
      </div>

      {/* Hero */}
      <div className="grid lg:grid-cols-2 gap-12 items-center">
        {/* Left - Content */}
        <div className="space-y-6">
          <p className={`text-sm uppercase tracking-widest ${theme.colors.accent} opacity-80`}>
            Your AI Private Banker
          </p>
          <h1 className={`font-display text-4xl lg:text-5xl ${theme.colors.text} leading-tight`}>
            AI that moves money, not just monitors it.
          </h1>
          <p className={`text-lg ${theme.colors.text} opacity-70 leading-relaxed`}>
            From insights to action—autonomously. Set your thesis. Franklin runs the playbook.
          </p>

          <div className="space-y-3 pt-4">
            {[
              "Family office access. No family office required.",
              "Real-time portfolio intelligence across every chain.",
              "One agent. Every account. Zero friction."
            ].map((feature, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className={`w-1.5 h-1.5 rounded-full ${
                  theme.id === 'neubrutalism' ? 'bg-black' : theme.colors.accent.replace('text-', 'bg-')
                }`} />
                <p className={`text-sm ${theme.colors.text} opacity-80`}>{feature}</p>
              </div>
            ))}
          </div>

          {/* CTA */}
          <div className="flex gap-4 pt-4">
            <button className={`px-6 py-3 rounded-xl font-medium transition-all flex items-center gap-2 ${theme.colors.button} ${theme.id === 'minimal-dark' ? '' : theme.colors.text}`}>
              Start a Conversation
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right - Card */}
        <div className={`rounded-2xl p-6 ${theme.colors.card}`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-200 to-amber-400 flex items-center justify-center text-xl">
              🎩
            </div>
            <div>
              <h4 className={`font-semibold ${theme.colors.text}`}>Franklin</h4>
              <p className={`text-xs ${theme.colors.text} opacity-60`}>Your Private Banker</p>
            </div>
          </div>

          <div className={`rounded-xl p-4 mb-4 ${
            {
              neubrutalism: 'bg-[#4ECDC4] border-2 border-black',
              glassmorphism: 'bg-white/10 backdrop-blur-sm',
              'neon-cyber': 'bg-cyan-500/10 border border-cyan-500/30',
              'minimal-dark': 'bg-white/5',
              'warm-earth': 'bg-amber-100/50'
            }[theme.id]
          }`}>
            <p className={`text-sm ${theme.id === 'neubrutalism' ? 'text-black font-bold' : theme.colors.text}`}>
              Connect your accounts, define your goals, and I'll find opportunities, make introductions, and execute—autonomously.
            </p>
          </div>

          <div className="space-y-2">
            {["I am an Investor", "I am a Founder", "Just curious"].map((option, i) => (
              <button
                key={i}
                className={`w-full text-left px-4 py-3 rounded-xl transition-all ${
                  {
                    neubrutalism: 'bg-white border-2 border-black hover:bg-yellow-300 font-bold',
                    glassmorphism: 'bg-white/10 hover:bg-white/20 border border-white/20',
                    'neon-cyber': 'bg-gray-800 hover:bg-gray-700 border border-cyan-500/30',
                    'minimal-dark': 'bg-[#1a1a1a] hover:bg-[#222] border border-[#333]',
                    'warm-earth': 'bg-white hover:bg-amber-50 border border-amber-200'
                  }[theme.id]
                } ${theme.colors.text}`}
              >
                {option}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function VariationsPage() {
  const [activeTheme, setActiveTheme] = useState(themes[0])

  return (
    <div className="min-h-screen bg-ivory-100">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-silver-700/10">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <Link href="/" className="flex items-center gap-3 group">
              <ArrowLeft className="w-4 h-4 text-silver-600 group-hover:-translate-x-1 transition-transform" />
              <span className="font-display text-2xl text-silver-700 tracking-tight">
                Franklin
              </span>
            </Link>
            <span className="text-sm text-silver-600">Theme Variations</span>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="max-w-2xl mb-12">
            <p className="font-sans text-sm tracking-widest uppercase text-gold-500 mb-4">
              Design Explorations
            </p>
            <h1 className="font-display text-4xl lg:text-5xl text-silver-700 mb-6">
              Five Ways to Say <span className="italic text-gradient-gold">Franklin</span>
            </h1>
            <p className="text-lg text-silver-600 leading-relaxed">
              Explore different visual identities for Franklin—from frosted glass elegance to bold brutalism.
              Each theme reflects a different brand personality while maintaining the same powerful AI capabilities.
            </p>
          </div>

          {/* Theme Selector */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-12">
            {themes.map((theme) => (
              <ThemeCard
                key={theme.id}
                theme={theme}
                isActive={activeTheme.id === theme.id}
                onClick={() => setActiveTheme(theme)}
              />
            ))}
          </div>

          {/* Active Theme Info */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-display text-2xl text-silver-700">{activeTheme.name}</h2>
              <p className="text-silver-600">{activeTheme.description}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const idx = themes.findIndex(t => t.id === activeTheme.id)
                  setActiveTheme(themes[(idx - 1 + themes.length) % themes.length])
                }}
                className="p-2 rounded-lg border border-silver-300 hover:bg-silver-100 transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-silver-600" />
              </button>
              <button
                onClick={() => {
                  const idx = themes.findIndex(t => t.id === activeTheme.id)
                  setActiveTheme(themes[(idx + 1) % themes.length])
                }}
                className="p-2 rounded-lg border border-silver-300 hover:bg-silver-100 transition-colors"
              >
                <ArrowRight className="w-5 h-5 text-silver-600" />
              </button>
            </div>
          </div>

          {/* Theme Demo */}
          <ThemeDemo theme={activeTheme} />
        </div>
      </section>

      {/* Trend Info */}
      <section className="py-16 px-6 lg:px-8 bg-white/50">
        <div className="max-w-7xl mx-auto">
          <h2 className="font-display text-3xl text-silver-700 mb-8">2025 Design Trends</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-silver-700">Glassmorphism</h3>
              <p className="text-sm text-silver-600 leading-relaxed">
                Uses frosted-glass effects, blurred backgrounds, and layered translucency.
                Ideal for futuristic, tech-driven brands. CSS backdrop-filter makes it smooth and performant.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-[#FF6B6B] border-2 border-black flex items-center justify-center">
                <Zap className="w-6 h-6 text-black" />
              </div>
              <h3 className="font-semibold text-silver-700">Neubrutalism</h3>
              <p className="text-sm text-silver-600 leading-relaxed">
                Embraces deliberate harshness: rigid grids, mismatched fonts, thick outlines, saturated colors.
                For brands that want to stand out and break conventions.
              </p>
            </div>

            <div className="space-y-3">
              <div className="w-12 h-12 rounded-xl bg-black flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.5)]">
                <Moon className="w-6 h-6 text-cyan-400" />
              </div>
              <h3 className="font-semibold text-silver-700">Dark Mode + Neon</h3>
              <p className="text-sm text-silver-600 leading-relaxed">
                Dark mode is now a standard expectation. Combined with neon highlights and bold typography,
                it creates a modern, high-end look that reduces eye strain.
              </p>
            </div>
          </div>

          <div className="mt-12 p-6 bg-silver-100/50 rounded-2xl">
            <p className="text-sm text-silver-600">
              <strong>Sources:</strong>{" "}
              <a href="https://blog.thegencode.com/posts/web-design-trends-2025-the-rise-of-dark-mode-and-glassmorphism" className="text-gold-600 hover:underline" target="_blank" rel="noopener">TheGenCode</a>,{" "}
              <a href="https://www.cccreative.design/blogs/differences-in-ui-design-trends-neumorphism-glassmorphism-and-neubrutalism" className="text-gold-600 hover:underline" target="_blank" rel="noopener">CC Creative</a>,{" "}
              <a href="https://blog.depositphotos.com/web-design-trends-2025.html" className="text-gold-600 hover:underline" target="_blank" rel="noopener">DepositPhotos</a>
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 lg:px-8 bg-silver-700 text-ivory-100">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="font-sans text-sm text-ivory-100/60">
            &copy; {new Date().getFullYear()} Ask Franklin. Theme exploration.
          </p>
          <Link href="/" className="flex items-center gap-2 text-gold-400 hover:text-gold-300 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to main site
          </Link>
        </div>
      </footer>
    </div>
  )
}
