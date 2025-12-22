import { createClient } from '@supabase/supabase-js'
import { NextRequest, NextResponse } from 'next/server'
import { GoogleGenerativeAI } from '@google/generative-ai'

const supabaseUrl = process.env.SUPABASE_URL!
const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY!
const webhookSecret = process.env.WASENDER_WEBHOOK_SECRET
const wasenderDeviceId = process.env.WASENDER_DEVICE_ID!
const geminiApiKey = process.env.GEMINI_API_KEY!

const FRANKLIN_SYSTEM_PROMPT = `You are Franklin, an AI private banker with a warm, avuncular personality.

Your role is to help people grow their wealth by:
- Connecting them with the right people and opportunities
- Providing sophisticated financial guidance
- Helping with deal flow and transactions

PERSONALITY:
- Warm, genuinely curious about their story
- Like catching up with an old friend who's interested in your life
- Knowledgeable about finance but not showing off
- Never pushy or interrogating - make them feel heard
- Wise, like a trusted family advisor

RULES:
- Keep responses concise (1-3 sentences for quick replies, longer for complex questions)
- Be conversational, not formal
- Use their name occasionally if you know it
- Ask follow-up questions to understand their situation
- If they're new, try to understand: What they do, their financial goals, timeline
- Never give specific investment advice or guarantees
- If asked about specific stocks/crypto, say you'd need to understand their full situation first

Sign off naturally, like a friend would. You can use "— Franklin" occasionally but not every message.`

async function sendWhatsAppMessage(phone: string, text: string) {
  const response = await fetch('https://api.wasenderapi.com/api/send-message', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${wasenderDeviceId}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      to: phone,
      text: text,
    }),
  })

  if (!response.ok) {
    const errorText = await response.text()
    console.error('Failed to send WhatsApp message:', errorText)
    throw new Error(`WhatsApp send failed: ${response.status}`)
  }

  return response.json()
}

async function generateFranklinResponse(
  supabase: any,
  phone: string,
  incomingMessage: string,
  senderName: string | null
): Promise<string> {
  // Get recent conversation history
  const { data: recentMessages } = await supabase
    .from('whatsapp_messages')
    .select('message_body, direction, created_at')
    .eq('phone', phone)
    .order('created_at', { ascending: false })
    .limit(10)

  // Build conversation history for context
  const history = (recentMessages || [])
    .reverse()
    .map((msg: any) => ({
      role: msg.direction === 'inbound' ? 'user' : 'model',
      parts: [{ text: msg.message_body }],
    }))

  // Add context about the user if we know them
  let systemPrompt = FRANKLIN_SYSTEM_PROMPT
  if (senderName) {
    systemPrompt += `\n\nYou're talking to ${senderName}.`
  }

  const genAI = new GoogleGenerativeAI(geminiApiKey)
  const model = genAI.getGenerativeModel({
    model: 'gemini-1.5-flash',
    systemInstruction: systemPrompt,
  })

  const chat = model.startChat({ history })
  const result = await chat.sendMessage(incomingMessage)
  const response = result.response

  return response.text() || "I'm here to help! Tell me more about what you're looking for."
}

export async function POST(request: NextRequest) {
  try {
    // Optionally verify webhook signature
    if (webhookSecret) {
      const signature = request.headers.get('X-Webhook-Signature')
      if (signature !== webhookSecret) {
        console.error('Invalid webhook signature')
        return NextResponse.json({ error: 'Invalid signature' }, { status: 401 })
      }
    }

    const body = await request.json()
    console.log('Wasender webhook received:', JSON.stringify(body, null, 2))

    const { event, timestamp, data } = body

    // Handle incoming messages
    if (event === 'messages.received') {
      const message = data?.messages
      if (!message) {
        return NextResponse.json({ success: true })
      }

      const senderPhone = message.key?.cleanedSenderPn ||
                          message.key?.remoteJid?.replace('@s.whatsapp.net', '') ||
                          message.key?.senderPn?.replace('@s.whatsapp.net', '')
      const messageId = message.key?.id
      const messageBody = message.messageBody || message.message?.conversation || ''
      const fromMe = message.key?.fromMe || false

      // Don't process our own outgoing messages
      if (fromMe || !messageBody.trim()) {
        return NextResponse.json({ success: true })
      }

      const supabase = createClient(supabaseUrl, supabaseServiceKey)

      // Find user by phone
      const { data: user } = await supabase
        .from('users')
        .select('id, name')
        .eq('phone', senderPhone)
        .single()

      // Also check leads table
      const { data: lead } = await supabase
        .from('leads')
        .select('id, name, phone')
        .eq('phone', senderPhone)
        .single()

      const senderName = user?.name || lead?.name || null

      // Store the incoming message
      await supabase
        .from('whatsapp_messages')
        .insert({
          wasender_message_id: messageId,
          phone: senderPhone,
          user_id: user?.id || null,
          lead_id: lead?.id || null,
          sender_name: senderName,
          message_body: messageBody,
          direction: 'inbound',
          raw_data: body,
          received_at: timestamp ? new Date(timestamp * 1000).toISOString() : new Date().toISOString(),
        })

      // Generate AI response
      try {
        const aiResponse = await generateFranklinResponse(
          supabase,
          senderPhone,
          messageBody,
          senderName
        )

        // Send response via WhatsApp
        await sendWhatsAppMessage(senderPhone, aiResponse)

        // Store outbound message
        await supabase
          .from('whatsapp_messages')
          .insert({
            phone: senderPhone,
            user_id: user?.id || null,
            lead_id: lead?.id || null,
            message_body: aiResponse,
            direction: 'outbound',
          })

        console.log('Franklin responded to', senderPhone)
      } catch (aiError) {
        console.error('Failed to generate/send AI response:', aiError)
      }
    }

    // Always respond 200 quickly
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Wasender webhook error:', error)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }
}
