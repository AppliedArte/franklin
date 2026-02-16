import type { Metadata } from "next"
import "./globals.css"
import { AuthProvider } from "@/lib/auth-context"
import { Navbar } from "@/components/navbar"

export const metadata: Metadata = {
  metadataBase: new URL("https://askfranklin.xyz"),
  title: {
    default: "Franklin | AI Fundraiser",
    template: "%s | Franklin",
  },
  description: "From pitch deck to term sheet. Franklin handles your entire raise — understanding your startup, creating decks, applying to accelerators, matching you with VCs, scheduling investor meetings, and closing your round.",
  keywords: ["fundraising", "AI fundraising", "pitch deck", "VC outreach", "SAFE", "startup fundraising", "raise capital", "investor matching", "accelerator application", "YC application", "agentic CRM", "schedule investor meetings", "AI fundraising agent"],
  authors: [{ name: "Ask Franklin" }],
  creator: "AARTE",
  openGraph: {
    title: "Franklin | AI Fundraiser",
    description: "From pitch deck to term sheet. Franklin handles your entire raise with an agentic CRM that finds VCs, sends outreach, schedules meetings, and closes your round.",
    url: "https://askfranklin.xyz",
    siteName: "Ask Franklin",
    type: "website",
    locale: "en_US",
    images: [{ url: "/franklin.jpg", width: 1200, height: 630, alt: "Franklin — AI Fundraiser" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "Franklin | AI Fundraiser",
    description: "From pitch deck to term sheet. Franklin handles your entire raise.",
    creator: "@askfranklin",
    images: ["/franklin.jpg"],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true },
  },
  alternates: {
    canonical: "https://askfranklin.xyz",
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className="min-h-screen">
        {/* Subtle noise overlay for texture */}
        <div className="noise-overlay" aria-hidden="true" />

        <AuthProvider>
          <Navbar />
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}
