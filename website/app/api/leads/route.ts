import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const vapiApiKey = process.env.VAPI_API_KEY!
const vapiPhoneNumberId = process.env.VAPI_PHONE_NUMBER_ID!
const elevenLabsVoiceId = process.env.ELEVENLABS_VOICE_ID || 'pNInz6obpgDQGcFmaJgB'
const wasenderApiKey = process.env.WASENDER_API_KEY
const wasenderDeviceId = process.env.WASENDER_DEVICE_ID

async function sendWhatsAppMessage(phone: string, name: string, userType: string) {
  if (!wasenderApiKey || !wasenderDeviceId) {
    console.log('WhatsApp not configured, skipping message')
    return null
  }

  const firstName = name.split(' ')[0]
  const message = `Good day, ${firstName}! This is Franklin, your AI private banker.

Thank you for your interest in growing your wealth. I'll be calling you shortly to learn more about your goals and how I can help.

If now isn't a good time, simply reply with a time that works better for you.

Looking forward to our conversation!

— Franklin`

  const response = await fetch('https://api.wasenderapi.com/api/send-message', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${wasenderApiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      device_id: wasenderDeviceId,
      phone: phone.replace(/\+/g, ''),
      message: message,
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

YOUR GOAL: Qualify this lead by learning about their financial situation.

INFO TO GATHER:
1. Current job/role (you know they're at ${fundName})
2. Income level (rough range is fine)
3. Investment goals (wealth growth, passive income, deal flow)
4. Timeline (short-term vs long-term)
5. What help they need from you

CONVERSATION FLOW:
- Greet warmly, thank them for signing up
- Ask about their financial situation: job, income
- If they hesitate on income, say: "No worries - as a follow-up I can help you connect your bank to get a clearer picture."
- Ask about their investment goals
- Ask about timeline
- Wrap up: "Perfect ${firstName}, I'll follow up with opportunities that match your profile."

PERSONALITY:
- Warm, genuine, unhurried
- Like a trusted advisor at a private bank
- Make them feel comfortable sharing financial details

RULES:
- Keep responses to 1-2 sentences MAX
- Ask ONE question at a time
- Use their name (${firstName}) occasionally
- If they're busy, offer to call back
- If uncomfortable sharing income, offer bank connection alternative
- Never be pushy`

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
        firstMessage: `Hello ${firstName}, this is Franklin from Ask Franklin. Thanks for signing up! I'd love to learn more about your situation so I can help. What's your current role at ${fundName}, and roughly what's your income like?`,
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

    const { name, phone, email, fund_name, linkedin, twitter, user_type } = body

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

    // Send WhatsApp message immediately (don't block the response)
    sendWhatsAppMessage(phone, name, user_type)
      .then((result) => {
        console.log('WhatsApp message sent:', result)
      })
      .catch((err) => {
        console.error('Failed to send WhatsApp:', err)
      })

    // Initiate Vapi call (don't block the response)
    if (vapiApiKey && vapiPhoneNumberId) {
      initiateVapiCall(phone, name, user_type, fund_name)
        .then((callData) => {
          console.log('Vapi call initiated:', callData)
        })
        .catch((err) => {
          console.error('Failed to initiate Vapi call:', err)
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
