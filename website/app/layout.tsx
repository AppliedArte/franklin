import type { Metadata } from "next"
import "./globals.css"
import { AuthProvider } from "@/lib/auth-context"
import { Navbar } from "@/components/navbar"

export const metadata: Metadata = {
  title: "Franklin | Your AI Private Banker",
  description: "Your AI Private Banker. Grow your wealth with the sophistication of a family office and the network of a top-tier investment bank.",
  keywords: ["private banker", "wealth advisor", "AI advisor", "hedge funds", "private equity", "alternative investments", "crypto", "DeFi"],
  openGraph: {
    title: "Franklin | Your AI Private Banker",
    description: "Your AI Private Banker. Grow your wealth with the sophistication of a family office and the network of a top-tier investment bank.",
    url: "https://askfranklin.xyz",
    siteName: "Ask Franklin",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Franklin | Your AI Private Banker",
    description: "Your AI Private Banker. Grow your wealth with the sophistication of a family office.",
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
