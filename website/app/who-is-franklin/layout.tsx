import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Who is Franklin?",
  description: "Meet Franklin — AI fundraising agent with 300+ years of experience. From pitch deck to term sheet, Franklin handles your entire raise.",
  openGraph: {
    title: "Who is Franklin? | AI Fundraising Agent",
    description: "Meet Franklin — AI fundraising agent with 300+ years of experience.",
    url: "https://askfranklin.xyz/who-is-franklin",
  },
}

export default function WhoIsFranklinLayout({ children }: { children: React.ReactNode }) {
  return children
}
