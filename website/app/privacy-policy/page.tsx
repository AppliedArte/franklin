"use client"

import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function PrivacyPolicyPage() {
  return (
    <div className="min-h-screen bg-ivory-100">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-40 bg-ivory-100/80 backdrop-blur-md border-b border-silver-700/10">
        <div className="max-w-4xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link href="/" className="flex items-center gap-2 text-silver-700 hover:text-gold-500 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              <span className="font-sans text-sm">Back to Home</span>
            </Link>
            <Link href="/" className="font-display text-xl text-silver-700">Franklin</Link>
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-6 lg:px-8 pt-32 pb-24">
        <div className="mb-12">
          <h1 className="font-display text-4xl md:text-5xl text-silver-700 tracking-tight mb-4">
            Privacy Policy
          </h1>
          <p className="text-silver-600">Last updated: December 2024</p>
        </div>

        <div className="prose prose-silver max-w-none space-y-8">
          {/* Introduction */}
          <Section title="Introduction">
            <p>
              Franklin ("Ask Franklin," "we," "us," or "our") is your AI private banker, designed to help you grow your wealth by connecting you with the right people, deals, and opportunities. Your privacy is central to our operations, and we are committed to protecting your personal information.
            </p>
            <p>
              This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our services, including our website at askfranklin.io and related communications via WhatsApp, email, or other channels.
            </p>
          </Section>

          {/* Data Collection */}
          <Section title="Data Collection">
            <p>We collect personal information directly from you, including:</p>
            <ul>
              <li>Name and contact information (email address, phone number)</li>
              <li>Professional details (company name, fund name, LinkedIn profile, Twitter/X handle)</li>
              <li>Investment preferences and interests</li>
              <li>Communications and conversation history with Franklin</li>
            </ul>
            <p>
              By providing your contact information through our platform or via LinkedIn and similar services, you consent to receive communications through email, SMS, and WhatsApp. We do not intentionally collect sensitive personal data such as racial origin, religious beliefs, or health information, though you may voluntarily share such information during conversations.
            </p>
          </Section>

          {/* Legal Basis */}
          <Section title="Legal Basis for Processing">
            <p>We process your data under the following legal frameworks:</p>
            <ul>
              <li><strong>Consent:</strong> For marketing communications, newsletters, and deal flow updates</li>
              <li><strong>Contract Performance:</strong> For providing our wealth advisory and networking services</li>
              <li><strong>Legitimate Interests:</strong> For service improvement, security, and fraud prevention</li>
              <li><strong>Legal Obligation:</strong> For regulatory compliance and legal requirements</li>
            </ul>
          </Section>

          {/* Data Usage */}
          <Section title="How We Use Your Data">
            <p>Your personal data is used to:</p>
            <ul>
              <li>Facilitate introductions to relevant investors, founders, and opportunities</li>
              <li>Provide personalized deal flow and investment recommendations</li>
              <li>Improve our AI advisory services</li>
              <li>Send marketing communications about relevant opportunities</li>
              <li>Ensure platform security and prevent fraud</li>
            </ul>
          </Section>

          {/* Third-Party Services */}
          <Section title="Third-Party Services">
            <p>
              We partner with trusted third-party services to provide and improve our offerings. These may include:
            </p>
            <ul>
              <li><strong>AI Processing:</strong> Anthropic (Claude) for AI-powered advisory services</li>
              <li><strong>Communications:</strong> Twilio for WhatsApp and SMS messaging</li>
              <li><strong>Database:</strong> Supabase for secure data storage</li>
              <li><strong>Analytics:</strong> Privacy-focused analytics tools</li>
            </ul>
            <p>
              These partners may process your data according to their own privacy policies. We ensure all partners maintain appropriate security standards.
            </p>
          </Section>

          {/* Data Sharing */}
          <Section title="Data Sharing">
            <p>
              We may share your contact information with other users only after mutual opt-in consent. For example, if you express interest in connecting with another investor or founder, we will facilitate that introduction only with both parties' agreement.
            </p>
            <p>
              We do not sell your personal data. We may share data with service partners as necessary to provide our services, and with legal authorities when required by law.
            </p>
          </Section>

          {/* Data Retention */}
          <Section title="Data Retention">
            <ul>
              <li><strong>User Profiles:</strong> Retained during active use plus 2 years after account deletion</li>
              <li><strong>Communications:</strong> Retained for 3 years</li>
              <li><strong>Marketing Data:</strong> Until you opt out, then deleted within 30 days</li>
              <li><strong>Legal Records:</strong> As required by applicable law</li>
            </ul>
          </Section>

          {/* Security */}
          <Section title="Security">
            <p>We implement robust security measures to protect your data, including:</p>
            <ul>
              <li>Encryption of data in transit and at rest</li>
              <li>Secure authentication protocols</li>
              <li>Regular security audits</li>
              <li>Role-based access controls</li>
              <li>Secure cloud infrastructure</li>
            </ul>
            <p>
              In the event of a data breach posing high risk to your rights and freedoms, we commit to notifying affected users without undue delay.
            </p>
          </Section>

          {/* User Rights */}
          <Section title="Your Rights">
            <p>Under applicable data protection laws (including GDPR), you have the right to:</p>
            <ul>
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
              <li><strong>Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
              <li><strong>Restrict Processing:</strong> Limit how we use your data</li>
              <li><strong>Data Portability:</strong> Receive your data in a portable format</li>
              <li><strong>Object:</strong> Object to automated decision-making</li>
            </ul>
            <p>
              To exercise these rights, contact us at privacy@askfranklin.io. We commit to responding within one month.
            </p>
          </Section>

          {/* Consent Withdrawal */}
          <Section title="Withdrawing Consent">
            <p>You can withdraw your consent for marketing communications at any time by:</p>
            <ul>
              <li>Clicking the unsubscribe link in any email</li>
              <li>Replying "STOP" to any SMS message</li>
              <li>Messaging Franklin directly to opt out</li>
              <li>Contacting us at privacy@askfranklin.io</li>
            </ul>
          </Section>

          {/* Policy Updates */}
          <Section title="Policy Updates">
            <p>
              We may update this Privacy Policy from time to time. For material changes, we will provide at least 30 days' notice via email or platform notification. Continued use of our services after such notice implies acceptance of the updated policy.
            </p>
          </Section>

          {/* Contact */}
          <Section title="Contact Us">
            <p>For privacy-related inquiries:</p>
            <ul>
              <li><strong>Email:</strong> privacy@askfranklin.io</li>
              <li><strong>Website:</strong> askfranklin.io</li>
            </ul>
          </Section>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 bg-silver-700 text-ivory-100">
        <div className="max-w-4xl mx-auto px-6 lg:px-8 text-center">
          <p className="text-sm text-ivory-100/60">
            &copy; {new Date().getFullYear()} Ask Franklin. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="pb-6 border-b border-silver-200">
      <h2 className="font-display text-2xl text-silver-700 mb-4">{title}</h2>
      <div className="text-silver-600 leading-relaxed space-y-3 [&_ul]:list-disc [&_ul]:list-outside [&_ul]:ml-5 [&_ul]:space-y-2 [&_li]:text-silver-600">
        {children}
      </div>
    </div>
  )
}
