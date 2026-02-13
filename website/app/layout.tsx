import type { Metadata } from "next"
import "./globals.css"
import { AuthProvider } from "@/lib/auth-context"
import { Navbar } from "@/components/navbar"

export const metadata: Metadata = {
  title: "Franklin | AI That Fundraises For You",
  description: "From pitch deck to term sheet. Franklin handles your entire raise — understanding your startup, creating decks, applying to accelerators, reaching out to VCs, and closing your round.",
  keywords: ["fundraising", "AI fundraising", "pitch deck", "VC outreach", "SAFE", "startup fundraising", "raise capital", "investor matching", "accelerator application", "YC application"],
  openGraph: {
    title: "Franklin | AI That Fundraises For You",
    description: "From pitch deck to term sheet. Franklin handles your entire raise.",
    url: "https://askfranklin.xyz",
    siteName: "Ask Franklin",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Franklin | AI That Fundraises For You",
    description: "From pitch deck to term sheet. Franklin handles your entire raise.",
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
