import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const vapiApiKey = process.env.VAPI_API_KEY!
const vapiPhoneNumberId = process.env.VAPI_PHONE_NUMBER_ID!
const elevenLabsVoiceId = process.env.ELEVENLABS_VOICE_ID || 'pNInz6obpgDQGcFmaJgB'
const wasenderApiKey = process.env.WASENDER_API_KEY
const wasenderDeviceId = process.env.WASENDER_DEVICE_ID
const telegramBotToken = process.env.TELEGRAM_BOT_TOKEN

async function sendTelegramMessage(telegramUsername: string, name: string, userType: string, fundName: string) {
  if (!telegramBotToken || !telegramUsername) {
    console.log('Telegram not configured or no username, skipping message')
    return null
  }

  // Clean up the username (remove @ if present)
  const cleanUsername = telegramUsername.replace('@', '')

  const firstName = name.split(' ')[0]
  const roleContext = userType === 'investor'
    ? `As an investor at ${fundName}, I'd be delighted to learn about your investment thesis and the opportunities you seek.`
    : `As a founder at ${fundName}, I'd love to understand your vision and how I might assist.`

  const message = `Good day, ${firstName}!

I am Franklin, your AI private banker. Thank you for registering your interest.

${roleContext}

To begin our acquaintance properly, might I inquire:

1. What is your fund's primary investment thesis?
2. What cheque sizes do you typically deploy?
3. Which sectors or stages do you focus upon?

I look forward to our discourse.

— Franklin 🎩`

  // Note: Telegram bots can only message users who have started a conversation first
  // We'll store the username and message them when they message the bot
  // For now, we just log that we would message them
  console.log(`Telegram: Would message @${cleanUsername} once they start conversation with bot`)

  return { success: true, username: cleanUsername, message: 'User needs to start conversation with bot first' }
}

async function sendSchedulingEmail(email: string, name: string, userType: string, fundName: string) {
  const smtpUser = process.env.ZOHO_SMTP_USER
  const smtpPass = process.env.ZOHO_SMTP_PASS

  if (!smtpUser || !smtpPass) {
    console.log('Zoho SMTP not configured, skipping email')
    return null
  }

  const firstName = name.split(' ')[0]
  const roleContext = userType === 'investor'
    ? `As an investor at ${fundName}, I'd love to learn about your investment thesis and discuss how I might help you find the best opportunities.`
    : `As a founder at ${fundName}, I'd love to understand your vision and explore how I might connect you with the right investors.`

  const htmlBody = `
<!DOCTYPE html>
<html>
<head>
  <style>
    body { font-family: Georgia, serif; color: #2d3748; line-height: 1.6; }
    .container { max-width: 600px; margin: 0 auto; padding: 40px 20px; }
    .header { border-bottom: 2px solid #d4af37; padding-bottom: 20px; margin-bottom: 30px; }
    .signature { margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; }
    .cta { display: inline-block; background: #264C39; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 20px 0; }
    .cta:hover { background: #1d3a2b; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h2 style="color: #264C39; margin: 0;">Franklin</h2>
      <p style="color: #718096; margin: 5px 0 0 0; font-size: 14px;">Your AI Private Banker</p>
    </div>

    <p>Dear ${firstName},</p>

    <p>Thank you for your interest in Franklin. I received your registration and wanted to reach out personally.</p>

    <p>${roleContext}</p>

    <p>Would you be available for a brief call this week? I find that a 15-minute conversation often accomplishes more than a dozen messages.</p>

    <p>Please select a time that works for you:</p>

    <a href="https://cal.com/askfranklin/15min" class="cta">Schedule a Call with Franklin</a>

    <p>Alternatively, you can reach me directly on Telegram at <a href="https://t.me/askfranklin_bot">@askfranklin_bot</a> if you prefer messaging.</p>

    <div class="signature">
      <p style="margin: 0;">Warm regards,</p>
      <p style="margin: 5px 0 0 0; font-weight: bold; color: #264C39;">Franklin</p>
      <p style="margin: 5px 0 0 0; font-size: 14px; color: #718096;">Your AI Private Banker</p>
      <p style="margin: 5px 0 0 0; font-size: 12px; color: #a0aec0;">askfranklin.xyz</p>
    </div>
  </div>
</body>
</html>
`

  const textBody = `Dear ${firstName},

Thank you for your interest in Franklin. I received your registration and wanted to reach out personally.

${roleContext}

Would you be available for a brief call this week? I find that a 15-minute conversation often accomplishes more than a dozen messages.

Schedule a call: https://cal.com/askfranklin/15min

Alternatively, you can reach me directly on Telegram at @askfranklin_bot if you prefer messaging.

Warm regards,
Franklin
Your AI Private Banker
askfranklin.xyz`

  // Use nodemailer for SMTP
  const nodemailer = require('nodemailer')

  const transporter = nodemailer.createTransport({
    host: 'smtp.zoho.com',
    port: 587,
    secure: false,
    auth: {
      user: smtpUser,
      pass: smtpPass,
    },
  })

  const result = await transporter.sendMail({
    from: `Franklin <${smtpUser}>`,
    to: email,
    subject: `${firstName}, let's schedule a quick call`,
    text: textBody,
    html: htmlBody,
  })

  console.log('Email sent:', result.messageId)
  return { success: true, messageId: result.messageId }
}

async function sendWhatsAppMessage(phone: string, name: string, userType: string, fundName: string) {
  if (!wasenderDeviceId) {
    console.log('WhatsApp not configured, skipping message')
    return null
  }

  const firstName = name.split(' ')[0]
  const roleContext = userType === 'investor'
    ? `As an investor at ${fundName}, I'd love to hear what kind of opportunities you're looking for.`
    : `As a founder at ${fundName}, I'd love to understand what stage you're at and how I can help.`

  const message = `Hey ${firstName}! Thanks for signing up.

I'm Franklin, your AI private banker. ${roleContext}

What's on your mind? Feel free to message me anytime - I'm here to help you grow your wealth.

— Franklin`

  const response = await fetch('https://api.wasenderapi.com/api/send-message', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${wasenderDeviceId}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      to: phone,
      text: message,
    }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    console.error('WhatsApp message failed:', errorText)
    throw new Error(`WhatsApp failed: ${response.status}`)
  }

  return response.json()
}

async function initiateVapiCall(phone: string, name: string, userType: string, fundName: string) {
  const firstName = name.split(' ')[0]
  const userTypeLabel = userType === 'investor' ? 'an investor' : 'a founder'

  const systemPrompt = `You are Franklin, an AI private banker with a warm, avuncular personality.

You're calling ${firstName} (full name: ${name}), who is ${userTypeLabel} at ${fundName}.

YOUR GOAL: Get to know this person and understand their background, current situation, and what they're looking for.

QUESTIONS TO ASK (one at a time, conversationally):
1. What prompted you to sign up? What are you hoping to get help with?
2. Tell me about yourself - what's your role at ${fundName}? How long have you been there?
3. What does ${fundName} do? What's your focus area?
4. Are you currently working with any financial advisors, wealth managers, or using any budgeting/investment apps?
5. What are your main financial goals right now?
6. Is there a specific timeline you're working with?

PERSONALITY:
- Warm, genuinely curious about their story
- Like catching up with an old friend who's interested in your life
- Knowledgeable about finance but not showing off
- Never pushy or interrogating - make them feel heard

RULES:
- Keep responses to 1-2 sentences MAX
- Ask ONE question at a time, then really listen
- Show interest in their answers before moving on
- Use their name (${firstName}) occasionally
- Wrap up: "Great getting to know you ${firstName}. I'll follow up with some ideas that might help."`

  const response = await fetch('https://api.vapi.ai/call/phone', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${vapiApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      phoneNumberId: vapiPhoneNumberId,
      customer: {
        number: phone,
        name: firstName,
      },
      assistant: {
        name: 'Franklin',
        firstMessage: `Hello ${firstName}, this is Franklin from Ask Franklin. Thanks for signing up! What can I help you with today?`,
        model: {
          provider: 'openai',
          model: 'gpt-4o',
          systemPrompt: systemPrompt,
        },
        voice: {
          provider: 'vapi',
          voiceId: 'Harry',
        },
        silenceTimeoutSeconds: 30,
        responseDelaySeconds: 0.4,
        maxDurationSeconds: 600,
      },
    }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    console.error('Vapi call failed:', errorText)
    throw new Error(`Vapi call failed: ${response.status}`)
  }

  return response.json()
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const { name, phone, email, fund_name, linkedin, twitter, telegram, user_type } = body

    // Validate required fields
    if (!name || !phone || !email || !fund_name || !linkedin || !user_type) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Create Supabase client with service role key for server-side operations
    const supabase = createClient(supabaseUrl, supabaseServiceKey)

    const { data, error } = await supabase
      .from('leads')
      .insert([
        {
          name,
          phone,
          email,
          fund_name,
          linkedin,
          twitter: twitter || null,
          telegram: telegram || null,
          user_type,
        }
      ])
      .select()
      .single()

    if (error) {
      console.error('Supabase error:', error)
      return NextResponse.json(
        { error: 'Failed to save lead' },
        { status: 500 }
      )
    }

    // If telegram provided, log for follow-up (bot will message when user starts chat)
    if (telegram) {
      sendTelegramMessage(telegram, name, user_type, fund_name)
        .then((result) => {
          console.log('Telegram user registered for follow-up:', result)
        })
        .catch((err) => {
          console.error('Failed to register Telegram user:', err)
        })
    } else {
      // No Telegram - send email to schedule a call instead of cold calling
      sendSchedulingEmail(email, name, user_type, fund_name)
        .then((result) => {
          console.log('Scheduling email sent:', result)
        })
        .catch((err) => {
          console.error('Failed to send scheduling email:', err)
        })
    }

    return NextResponse.json({ success: true, data })
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}
