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

  const systemPrompt = `You are Franklin, a warm and distinguished AI private banker. You're calling ${name}, a ${userType} at ${fundName}.

Your personality: Warm, genuine, curious. Speak naturally like a friendly advisor, not overly formal.

Your goal: Learn about their investment interests and how you can help. Ask about their goals, timeline, and what they're looking for.

Rules:
- Keep responses to 1-2 short sentences
- Ask one question at a time
- Listen and respond naturally
- Be conversational, not scripted
- If they seem busy, offer to call back later`

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
        name: name,
      },
      assistant: {
        name: 'Franklin',
        firstMessage: `Hi ${firstName}! This is Franklin calling. You just signed up on our site - do you have a minute to chat about your investment goals?`,
        model: {
          provider: 'openai',
          model: 'gpt-4o',
          systemPrompt: systemPrompt,
        },
        voice: {
          provider: '11labs',
          voiceId: elevenLabsVoiceId,
          stability: 0.5,
          similarityBoost: 0.75,
        },
        silenceTimeoutSeconds: 30,
        responseDelaySeconds: 0.5,
        endCallAfterSilenceSeconds: 30,
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
