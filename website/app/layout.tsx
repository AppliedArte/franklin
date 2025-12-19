import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "Franklin | Your Personal Private Banker",
  description: "Meet Franklin, a distinguished wealth advisor who brings centuries of financial wisdom to modern investing. Sophisticated counsel on hedge funds, private equity, crypto, and alternative investments.",
  keywords: ["private banker", "wealth advisor", "AI advisor", "hedge funds", "private equity", "alternative investments", "crypto", "DeFi"],
  openGraph: {
    title: "Franklin | Your Personal Private Banker",
    description: "Sophisticated wealth guidance from a distinguished gentleman. Hedge funds, private equity, crypto, and beyond.",
    url: "https://askfranklin.io",
    siteName: "Ask Franklin",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Franklin | Your Personal Private Banker",
    description: "Sophisticated wealth guidance from a distinguished gentleman.",
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

        {children}
      </body>
    </html>
  )
}
