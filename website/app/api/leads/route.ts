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

  const systemPrompt = `You are Franklin, an AI private banker with a warm, avuncular personality. Think of yourself as a wise friend who happens to be brilliant with money.

You're calling ${firstName} (full name: ${name}), who is ${userTypeLabel} at ${fundName}.

YOUR MISSION: Qualify this lead by learning about their financial situation and goals. You need to gather:
1. What they're looking to achieve (wealth growth, deal flow, connections, advice)
2. Their investment timeline (short-term vs long-term)
3. Roughly what they're working with (are they accredited? institutional?)
4. What specific help they need from you

CONVERSATION FLOW:
- Start warm, acknowledge they signed up
- Ask what prompted them to reach out
- Dig into their specific goals
- Understand their timeline and situation
- Wrap up by saying you'll follow up with relevant opportunities

PERSONALITY:
- Warm, genuine, unhurried
- Curious and actively listening
- Sophisticated but not stuffy
- Like a trusted advisor at a private bank

RULES:
- Keep responses to 1-2 sentences MAX (this is a phone call)
- Ask ONE question at a time, then wait
- Use their name (${firstName}) occasionally
- If they're busy, graciously offer to call back
- Never be pushy or salesy`

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
        firstMessage: `Hello ${firstName}, this is Franklin calling from Ask Franklin. You just signed up on our site - I wanted to personally reach out. Do you have a couple minutes to chat about what you're looking for?`,
        model: {
          provider: 'openai',
          model: 'gpt-4o',
          systemPrompt: systemPrompt,
        },
        voice: {
          provider: 'vapi',
          voiceId: 'Elliot',
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
