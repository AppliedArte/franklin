import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const vapiApiKey = process.env.VAPI_API_KEY!
const vapiPhoneNumberId = process.env.VAPI_PHONE_NUMBER_ID!
const elevenLabsVoiceId = process.env.ELEVENLABS_VOICE_ID || 'pNInz6obpgDQGcFmaJgB'

async function initiateVapiCall(phone: string, name: string, userType: string, fundName: string) {
  const systemPrompt = `You are Franklin, a distinguished AI private banker with the refined manner of a 1700s British gentleman. You're calling ${name}, who is a ${userType} at ${fundName}.

Your goal on this call:
1. Warmly greet them and introduce yourself
2. Learn about their investment goals and what they're looking for
3. Understand their current situation and challenges
4. Identify how you can help connect them with the right people and opportunities
5. Take notes on their preferences so you can follow up with relevant deals

Be warm, avuncular, and genuinely interested. Keep responses brief (2-3 sentences) since this is a phone call. Use refined but accessible language. Ask one question at a time and listen carefully.

Start with: "Ah, good day! This is Franklin calling. I understand you're interested in discussing wealth and investment matters - delighted to make your acquaintance, ${name.split(' ')[0]}!"`

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
        name: 'Franklin - AI Private Banker',
        firstMessage: `Ah, good day! This is Franklin calling. I understand you're interested in discussing wealth and investment matters - delighted to make your acquaintance, ${name.split(' ')[0]}!`,
        model: {
          provider: 'anthropic',
          model: 'claude-sonnet-4-20250514',
          systemPrompt: systemPrompt,
        },
        voice: {
          provider: '11labs',
          voiceId: elevenLabsVoiceId,
        },
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
